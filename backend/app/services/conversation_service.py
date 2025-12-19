"""
Conversation Service Layer

This module provides CRUD operations for conversations with security enforcement.
All operations validate that conversations belong to the authenticated user.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation
from app.models.message import Message


class ConversationService:
    """
    Service for managing conversation sessions between users and AI.

    Security: All operations require user_id to enforce data isolation.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize ConversationService with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_conversation(self, user_id: int) -> Conversation:
        """
        Create a new conversation for user.

        Args:
            user_id: ID of the user creating the conversation

        Returns:
            Created Conversation object

        Example:
            conversation = await service.create_conversation(user_id=123)
        """
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)

        return conversation

    async def get_user_conversations(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """
        Get all conversations for a user, sorted by most recent activity.

        Args:
            user_id: ID of the user
            limit: Maximum number of conversations to return (default: 20)
            offset: Number of conversations to skip for pagination (default: 0)

        Returns:
            List of Conversation objects sorted by updated_at DESC

        Example:
            conversations = await service.get_user_conversations(user_id=123, limit=10)
        """
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        conversations = result.scalars().all()

        return list(conversations)

    async def get_conversation(
        self,
        conversation_id: int,
        user_id: int,
        load_messages: bool = False
    ) -> Optional[Conversation]:
        """
        Get a specific conversation by ID with security check.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for security validation)
            load_messages: If True, eagerly load all messages (default: False)

        Returns:
            Conversation object if found and owned by user, None otherwise

        Raises:
            None - returns None if not found or user doesn't own it

        Example:
            conversation = await service.get_conversation(
                conversation_id=456,
                user_id=123,
                load_messages=True
            )
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        """
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )

        # Eagerly load messages if requested
        if load_messages:
            query = query.options(selectinload(Conversation.messages))

        result = await self.session.execute(query)
        conversation = result.scalar_one_or_none()

        return conversation

    async def delete_conversation(
        self,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """
        Delete a conversation and all its messages (cascade).

        Args:
            conversation_id: ID of the conversation to delete
            user_id: ID of the user (for security validation)

        Returns:
            True if deleted successfully, False if not found or not owned by user

        Example:
            deleted = await service.delete_conversation(conversation_id=456, user_id=123)
            if not deleted:
                raise HTTPException(status_code=404, detail="Conversation not found")
        """
        # First verify conversation belongs to user
        conversation = await self.get_conversation(conversation_id, user_id)

        if not conversation:
            return False

        await self.session.delete(conversation)
        await self.session.commit()

        return True

    async def count_user_conversations(self, user_id: int) -> int:
        """
        Count total number of conversations for a user.

        Args:
            user_id: ID of the user

        Returns:
            Count of conversations

        Example:
            total = await service.count_user_conversations(user_id=123)
        """
        from sqlalchemy import func

        query = select(func.count(Conversation.id)).where(
            Conversation.user_id == user_id
        )

        result = await self.session.execute(query)
        count = result.scalar_one()

        return count
