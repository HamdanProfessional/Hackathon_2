"""
Conversation Manager for AI Chat

Handles conversation persistence using the existing database models.
This replaces the openai-chatkit-sdk which doesn't exist yet.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID

from app.models.conversation import Conversation
from app.models.message import Message


class ConversationManager:
    """
    Manages conversation persistence using the database.

    This class provides methods to:
    - Create new conversations
    - Retrieve conversation history
    - Save messages to conversations
    - List user's conversations
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize conversation manager with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_conversation(self, user_id: UUID) -> UUID:
        """
        Create a new conversation for a user.

        Args:
            user_id: The user's UUID

        Returns:
            The UUID of the new conversation
        """
        conversation = Conversation(user_id=user_id)
        self.db.add(conversation)
        await self.db.flush()  # Get the ID without committing
        await self.db.refresh(conversation)
        return conversation.id

    async def get_history(
        self,
        conversation_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, str]]:
        """
        Retrieve conversation history as a list of messages.

        Args:
            conversation_id: The conversation ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages in format [{"role": "user|assistant", "content": "..."}]
        """
        # Query messages for this conversation
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
        )
        messages = result.scalars().all()

        # Convert to OpenAI format
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    async def save_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str
    ) -> None:
        """
        Save a message to the conversation.

        Args:
            conversation_id: The conversation ID
            role: Either "user" or "assistant"
            content: The message content
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.db.add(message)

        # Update the conversation's updated_at timestamp
        await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = (await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )).scalar_one_or_none()

        if conversation:
            conversation.updated_at = datetime.utcnow()

        await self.db.commit()

    async def get_user_conversations(
        self,
        user_id: UUID,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user.

        Args:
            user_id: The user's UUID
            limit: Maximum number of conversations to retrieve

        Returns:
            List of conversations with metadata
        """
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
        )
        conversations = result.scalars().all()

        # Get first message for each conversation as title
        conversations_with_titles = []
        for conv in conversations:
            # Get the first user message as a title
            title_result = await self.db.execute(
                select(Message)
                .where(
                    Message.conversation_id == conv.id,
                    Message.role == "user"
                )
                .order_by(Message.created_at)
                .limit(1)
            )
            first_message = title_result.scalar_one_or_none()

            title = "New Chat"
            if first_message:
                # Truncate long titles
                title = first_message.content[:50]
                if len(first_message.content) > 50:
                    title += "..."

            conversations_with_titles.append({
                "id": conv.id,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "title": title
            })

        return conversations_with_titles

    async def verify_conversation_ownership(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Verify that a user owns a conversation.

        Args:
            conversation_id: The conversation ID
            user_id: The user's UUID

        Returns:
            True if the user owns the conversation, False otherwise
        """
        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def delete_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: The conversation ID to delete
            user_id: The user's UUID (for ownership verification)

        Returns:
            True if deleted successfully, False if not found or unauthorized
        """
        # Verify ownership
        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            return False

        # Delete conversation (messages will cascade delete due to FK constraint)
        await self.db.delete(conversation)
        await self.db.commit()

        return True