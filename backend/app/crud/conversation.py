"""Conversation CRUD operations."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.conversation import Conversation


async def create_conversation(db: AsyncSession, user_id: int) -> Conversation:
    """
    Create a new conversation for a user.

    Args:
        db: Database session
        user_id: Owner user ID

    Returns:
        Created conversation instance
    """
    db_conversation = Conversation(user_id=user_id)

    db.add(db_conversation)
    await db.commit()
    await db.refresh(db_conversation)

    return db_conversation


async def get_conversation_by_id(
    db: AsyncSession, conversation_id: int, user_id: int
) -> Optional[Conversation]:
    """
    Get a specific conversation by ID, ensuring it belongs to the user.

    Args:
        db: Database session
        conversation_id: Conversation ID
        user_id: User ID to verify ownership

    Returns:
        Conversation instance if found and owned by user, None otherwise
    """
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def get_user_conversations(
    db: AsyncSession, user_id: int, limit: int = 50
) -> List[Conversation]:
    """
    Get all conversations for a specific user, ordered by most recent activity.

    Args:
        db: Database session
        user_id: User ID to filter by
        limit: Maximum number of conversations to return (default: 50)

    Returns:
        List of user's conversations ordered by updated_at desc
    """
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def delete_conversation(db: AsyncSession, conversation: Conversation) -> None:
    """
    Delete a conversation (cascade deletes all messages).

    Args:
        db: Database session
        conversation: Conversation instance to delete
    """
    await db.delete(conversation)
    await db.commit()
