"""Message CRUD operations."""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.message import Message


async def create_message(
    db: AsyncSession, conversation_id: int, role: str, content: str
) -> Message:
    """
    Create a new message in a conversation.

    Args:
        db: Database session
        conversation_id: ID of the conversation this message belongs to
        role: Message role ('user' or 'assistant')
        content: Message content

    Returns:
        Created message instance
    """
    db_message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)

    return db_message


async def get_conversation_messages(
    db: AsyncSession, conversation_id: int, limit: int = 50
) -> List[Message]:
    """
    Get messages for a conversation, ordered chronologically.

    Args:
        db: Database session
        conversation_id: Conversation ID to filter by
        limit: Maximum number of messages to return (default: 50, most recent)

    Returns:
        List of messages ordered by created_at ascending (chronological)
    """
    # Get the most recent N messages in reverse chronological order, then reverse
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()

    # Reverse to get chronological order (oldest first)
    return list(reversed(messages))


async def delete_conversation_messages(db: AsyncSession, conversation_id: int) -> None:
    """
    Delete all messages in a conversation.

    Args:
        db: Database session
        conversation_id: Conversation ID
    """
    await db.execute(
        delete(Message).where(Message.conversation_id == conversation_id)
    )
    await db.commit()
