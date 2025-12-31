"""Chat API endpoints for AI-powered task management."""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import time
import sys
from collections import defaultdict

from app.database import get_db
from app.models.user import User
from app.models.message import Message
from app.api.deps import get_current_user
from app.config import settings
from app.utils.exceptions import NotFoundException

# Import schemas with error handling
try:
    from app.schemas.conversation import ConversationResponse
    from app.schemas.message import MessageResponse
except ImportError as e:
    raise ImportError(f"Failed to import chat schemas: {e}")

# Import chat components with error handling
try:
    from app.ai.conversation_manager import ConversationManager
    from app.ai.agent_mock import MockAgentService
    from app.ai.agent import AgentService
    CHAT_AVAILABLE = True

    # Always use real AI service (Groq primary, Gemini fallback)
    # Mock AI is disabled to ensure chatbot uses configured AI providers
    USE_MOCK_AI = False

    if USE_MOCK_AI:
        print("[CONFIG] Mock AI enabled - WARNING: Not recommended for production", file=sys.stderr)
    else:
        provider = "Groq" if "groq.com" in settings.AI_BASE_URL else "AI"
        print(f"[CONFIG] Real AI service enabled - Primary: {provider}, Fallback: Gemini", file=sys.stderr)
except ImportError as e:
    raise ImportError(f"Failed to import chat components: {e}")
    CHAT_AVAILABLE = False
    USE_MOCK_AI = True

router = APIRouter()

# Simple in-memory rate limiter (for production, use Redis)
rate_limit_cache = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # 60 seconds
RATE_LIMIT_MAX_REQUESTS = 10  # 10 requests per minute


def check_rate_limit(user_id: str):
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
    conversation_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    conversation_id: UUID
    response: str
    tool_calls: List[dict] = []


@router.post(
    "/",
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
    3. Process message through AI agent with conversation management
    4. Return response with conversation ID
    """
    # Check if chat components are available
    if not CHAT_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service is currently unavailable. Please try again later."
        )

    # Step 1: Check rate limit (T050)
    # current_user.id is a UUID object, convert to string for rate limiting
    check_rate_limit(str(current_user.id))

    # Step 2: Verify conversation ownership if conversation_id provided (skip for mock AI)
    if request.conversation_id and not USE_MOCK_AI:
        conversation_manager = ConversationManager(db)
        owns_conversation = await conversation_manager.verify_conversation_ownership(
            conversation_id=request.conversation_id,
            user_id=current_user.id
        )
        if not owns_conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found or does not belong to user"
            )

    # Step 3: Process message through AI agent with conversation management
    import sys
    print(f"[DEBUG] USE_MOCK_AI = {USE_MOCK_AI}", file=sys.stderr)

    try:
        if USE_MOCK_AI:
            agent = MockAgentService()
            print("[MOCK] Using mock AI service for testing", file=sys.stderr)
        else:
            agent = AgentService()
            provider = "Groq" if "groq.com" in settings.AI_BASE_URL else "AI"
            print(f"[AI] Using real AI service - Primary: {provider}, Fallback: Gemini", file=sys.stderr)

        result = await agent.process_message(
            db=db,
            user_id=str(current_user.id),  # Convert UUID to string
            user_message=request.message,
            conversation_id=request.conversation_id
        )

        print(f"[DEBUG] Agent processing completed successfully", file=sys.stderr)

        # Step 4: Return response
        return ChatResponse(
            conversation_id=result["conversation_id"],
            response=result["response"],
            tool_calls=result.get("tool_calls", []),
        )
    except Exception as e:
        print(f"[ERROR] Chat processing failed: {e}", file=sys.stderr)
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}", file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail="Failed to process message. Please try again."
        )


@router.get(
    "/conversations",
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
    if not CHAT_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service is currently unavailable. Please try again later."
        )

    conversation_manager = ConversationManager(db)
    conversations = await conversation_manager.get_user_conversations(
        user_id=current_user.id,  # Pass UUID object directly
        limit=50
    )
    return conversations


@router.get(
    "/conversations/{conversation_id}/messages",
    summary="Get conversation messages",
    description="Retrieve all messages for a specific conversation",
)
async def get_conversation_messages(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all messages for a conversation.

    - **conversation_id**: ID of the conversation

    Returns messages ordered chronologically (oldest first).

    Raises 404 if conversation not found or doesn't belong to user.
    """
    if not CHAT_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service is currently unavailable. Please try again later."
        )

    # Verify conversation belongs to user and get messages
    conversation_manager = ConversationManager(db)
    owns_conversation = await conversation_manager.verify_conversation_ownership(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    if not owns_conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found or does not belong to user"
        )

    # Load messages
    messages = await conversation_manager.get_history(
        conversation_id=conversation_id,
        limit=50
    )

    # Add timestamps to messages
    result = []
    for msg in messages:
        # Get timestamp from database
        timestamp_result = await db.execute(
            select(Message).where(
                Message.conversation_id == conversation_id,
                Message.role == msg["role"],
                Message.content == msg["content"]
            ).order_by(Message.created_at).limit(1)
        )
        db_message = timestamp_result.scalar_one_or_none()

        result.append({
            "role": msg["role"],
            "content": msg["content"],
            "created_at": db_message.created_at.isoformat() if db_message else None
        })

    return result


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation",
    description="Permanently delete a conversation and all its messages",
)
async def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a conversation permanently.

    - **conversation_id**: ID of the conversation to delete

    This will delete the conversation and all associated messages.
    This action cannot be undone.

    Raises:
    - 404: Conversation not found or does not belong to user
    - 503: Chat service unavailable
    """
    if not CHAT_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service is currently unavailable. Please try again later."
        )

    # Delete conversation
    conversation_manager = ConversationManager(db)
    deleted = await conversation_manager.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id  # Pass UUID object directly
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found or does not belong to user"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
