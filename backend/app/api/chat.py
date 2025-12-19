"""Chat API endpoints for AI-powered task management."""
from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import time
from collections import defaultdict

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.ai.agent import AgentService
from app.config import settings

router = APIRouter()

# Simple in-memory rate limiter (for production, use Redis)
rate_limit_cache = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # 60 seconds
RATE_LIMIT_MAX_REQUESTS = 10  # 10 requests per minute


def check_rate_limit(user_id: int):
    """
    Check if user has exceeded rate limit.

    Rate limit: 10 requests per minute per user.

    Raises HTTPException if rate limit exceeded.
    """
    now = time.time()
    user_requests = rate_limit_cache[user_id]

    # Remove old requests outside the time window
    user_requests[:] = [req_time for req_time in user_requests if now - req_time < RATE_LIMIT_WINDOW]

    # Check if limit exceeded
    if len(user_requests) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX_REQUESTS} requests per minute. Please try again later."
        )

    # Add current request
    user_requests.append(now)
    rate_limit_cache[user_id] = user_requests


# Request/Response Schemas
class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    conversation_id: int
    response: str
    tool_calls: List[dict] = []


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message to the AI assistant",
    description="Process user message through AI agent and return response with tool invocations",
)
async def send_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a chat message to the AI task management assistant.

    - **message**: User's natural language message (required)
    - **conversation_id**: Existing conversation ID (optional, creates new if null)

    Returns:
    - **conversation_id**: ID of conversation (new or existing)
    - **response**: AI assistant's response message
    - **tool_calls**: List of tools invoked (e.g., task creation)

    Flow:
    1. T050: Check rate limit (10 requests per minute per user)
    2. T019: Verify JWT authentication (done via get_current_user dependency)
    3. T018: Get or create conversation
    4. T053: Load message history (last 20-30 messages to prevent context overflow)
    5. Run AI agent with tool calling support (T049: with error handling)
    6. T020: Save user message and agent response to database
    7. Return response with conversation ID
    """
    # Step 1: Check rate limit (T050)
    check_rate_limit(current_user.id)

    # Initialize services
    conversation_service = ConversationService(db)
    message_service = MessageService(db)

    # Step 1 & 2: Get or create conversation (T018)
    if request.conversation_id:
        # Load existing conversation
        conversation = await conversation_service.get_conversation(
            conversation_id=request.conversation_id,
            user_id=current_user.id
        )
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found or does not belong to user"
            )
    else:
        # Create new conversation
        conversation = await conversation_service.create_conversation(user_id=current_user.id)

    # Step 3: Load message history (T053 - limit to 30 messages to prevent context overflow)
    history = await message_service.get_history_for_agent(
        conversation_id=conversation.id,
        max_messages=30  # Limit to 30 messages to stay within LLM context window
    )

    # Step 4: Process message through AI agent (T014, T015)
    agent = AgentService()

    result = await agent.run_agent(
        db=db,
        user_id=current_user.id,
        user_message=request.message,
        history=history
    )

    # Step 5: Save messages to database (T020)
    # Save user message
    await message_service.add_message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )

    # Save assistant response
    await message_service.add_message(
        conversation_id=conversation.id,
        role="assistant",
        content=result["response"]
    )

    # Step 6: Return response
    return ChatResponse(
        conversation_id=conversation.id,
        response=result["response"],
        tool_calls=result.get("tool_calls", []),
    )


@router.get(
    "/conversations",
    response_model=List[ConversationResponse],
    summary="Get user's conversations",
    description="Retrieve all conversations for the authenticated user",
)
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all conversations for the current user.

    Returns list of conversations ordered by most recent activity (updated_at desc).
    """
    conversations = await conversation_crud.get_user_conversations(db, current_user.id, limit=50)
    return conversations


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=List[MessageResponse],
    summary="Get conversation messages",
    description="Retrieve all messages for a specific conversation",
)
async def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all messages for a conversation.

    - **conversation_id**: ID of the conversation

    Returns messages ordered chronologically (oldest first).

    Raises 404 if conversation not found or doesn't belong to user.
    """
    # Verify conversation belongs to user
    conversation = await conversation_crud.get_conversation_by_id(
        db, conversation_id, current_user.id
    )
    if not conversation:
        raise NotFoundException(detail="Conversation not found or does not belong to user")

    # Load messages
    messages = await message_crud.get_conversation_messages(db, conversation_id, limit=50)
    return messages
