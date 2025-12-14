"""Chat API endpoints for AI-powered task management."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.message import MessageResponse
from app.schemas.conversation import ConversationResponse
from app.crud import conversation as conversation_crud
from app.crud import message as message_crud
from app.api.deps import get_current_user
from app.services.agent_service import AgentService
from app.utils.exceptions import NotFoundException

router = APIRouter()


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
    1. Create or load conversation
    2. Load message history (last 50 messages)
    3. Process message through AI agent with MCP tools
    4. Save user message and agent response to database
    5. Return response with conversation ID
    """
    # Step 1: Get or create conversation
    if request.conversation_id:
        # Load existing conversation
        conversation = await conversation_crud.get_conversation_by_id(
            db, request.conversation_id, current_user.id
        )
        if not conversation:
            raise NotFoundException(detail="Conversation not found or does not belong to user")
    else:
        # Create new conversation
        conversation = await conversation_crud.create_conversation(db, current_user.id)

    # Step 2: Load message history (last 50 messages in chronological order)
    messages = await message_crud.get_conversation_messages(db, conversation.id, limit=50)

    # Convert to format expected by agent
    message_history = [{"role": msg.role, "content": msg.content} for msg in messages]

    # Step 3: Process message through AI agent
    agent = AgentService(user_id=current_user.id)
    result = await agent.process_message(message_history, request.message)

    # Step 4: Save messages to database
    # Save user message
    await message_crud.create_message(
        db, conversation_id=conversation.id, role="user", content=request.message
    )

    # Save assistant response
    await message_crud.create_message(
        db, conversation_id=conversation.id, role="assistant", content=result["response"]
    )

    # Step 5: Return response
    return ChatResponse(
        conversation_id=conversation.id,
        response=result["response"],
        tool_calls=result["tool_calls"],
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
