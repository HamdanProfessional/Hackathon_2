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

    async def create_conversation(self, user_id: str) -> UUID:
        """
        Create a new conversation for a user.

        Args:
            user_id: The user's UUID (as string)

        Returns:
            The UUID of the new conversation
        """
        # Convert string to UUID if needed
        if isinstance(user_id, str):
            from uuid import UUID
            user_id = UUID(user_id)

        conversation = Conversation(user_id=user_id)
        self.db.add(conversation)
        await self.db.flush()  # Get the ID without committing
        await self.db.refresh(conversation)
        return conversation.id

    async def get_history(
        self,
        conversation_id: str,  # Accept string UUID
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
        # Convert string to UUID if needed
        if isinstance(conversation_id, str):
            from uuid import UUID
            conversation_id = UUID(conversation_id)

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
        conversation_id: str,  # Accept string UUID
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
        # Convert string to UUID if needed
        if isinstance(conversation_id, str):
            from uuid import UUID
            conversation_uuid = UUID(conversation_id)
        else:
            conversation_uuid = conversation_id

        message = Message(
            conversation_id=conversation_uuid,
            role=role,
            content=content
        )
        self.db.add(message)

        # Update the conversation's updated_at timestamp
        conversation_result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_uuid)
        )
        conversation = conversation_result.scalar_one_or_none()

        if conversation:
            conversation.updated_at = datetime.utcnow()

        # Don't commit here - let the main transaction handle it
        await self.db.flush()

    async def get_user_conversations(
        self,
        user_id: str,  # Accept string UUID
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
        # Convert string to UUID if needed
        if isinstance(user_id, str):
            from uuid import UUID
            user_uuid = UUID(user_id)
        else:
            user_uuid = user_id

        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_uuid)
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
        conversation_id: str,  # Accept string UUID
        user_id: str  # Accept string UUID
    ) -> bool:
        """
        Verify that a user owns a conversation.

        Args:
            conversation_id: The conversation ID
            user_id: The user's UUID

        Returns:
            True if the user owns the conversation, False otherwise
        """
        # Convert strings to UUIDs if needed
        from uuid import UUID

        if isinstance(conversation_id, str):
            conversation_uuid = UUID(conversation_id)
        else:
            conversation_uuid = conversation_id

        if isinstance(user_id, str):
            user_uuid = UUID(user_id)
        else:
            user_uuid = user_id

        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.id == conversation_uuid,
                Conversation.user_id == user_uuid
            )
        )
        return result.scalar_one_or_none() is not None

    async def delete_conversation(
        self,
        conversation_id: str,  # Accept string UUID
        user_id: str  # Accept string UUID
    ) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: The conversation ID to delete
            user_id: The user's UUID (for ownership verification)

        Returns:
            True if deleted successfully, False if not found or unauthorized
        """
        # Convert strings to UUIDs if needed
        from uuid import UUID

        if isinstance(conversation_id, str):
            conversation_uuid = UUID(conversation_id)
        else:
            conversation_uuid = conversation_id

        if isinstance(user_id, str):
            user_uuid = UUID(user_id)
        else:
            user_uuid = user_id

        # Verify ownership
        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.id == conversation_uuid,
                Conversation.user_id == user_uuid
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            return False

        # Delete conversation (messages will cascade delete due to FK constraint)
        await self.db.delete(conversation)
        await self.db.flush()

        return True