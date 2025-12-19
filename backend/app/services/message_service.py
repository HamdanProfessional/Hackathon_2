"""
Message Service Layer

This module provides CRUD operations for messages within conversations.
Supports formatting message history for OpenAI Agents SDK.
"""

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, desc, update

from app.models.message import Message
from app.models.conversation import Conversation


class MessageService:
    """
    Service for managing messages within conversations.

    Responsibilities:
    - Add messages to conversations (user and assistant)
    - Retrieve conversation history
    - Format messages for OpenAI Agents SDK
    - Update conversation.updated_at timestamp
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize MessageService with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str
    ) -> Message:
        """
        Add a message to a conversation.

        This also updates the conversation's updated_at timestamp.

        Args:
            conversation_id: ID of the conversation
            role: Message role - "user" or "assistant"
            content: Message content (text or JSON string)

        Returns:
            Created Message object

        Raises:
            ValueError: If role is not "user" or "assistant"

        Example:
            message = await service.add_message(
                conversation_id=456,
                role="user",
                content="Add buy milk to my todo list"
            )
        """
        # Validate role
        if role not in ("user", "assistant"):
            raise ValueError(f"Invalid role: {role}. Must be 'user' or 'assistant'")

        # Create message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )

        self.session.add(message)

        # Update conversation's updated_at timestamp
        await self.session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(updated_at=datetime.utcnow())
        )

        await self.session.commit()
        await self.session.refresh(message)

        return message

    async def get_history(
        self,
        conversation_id: int,
        limit: int = 50,
        offset: int = 0,
        order: str = "asc"
    ) -> List[Message]:
        """
        Get conversation history (messages) in chronological order.

        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return (default: 50)
            offset: Number of messages to skip for pagination (default: 0)
            order: Sort order - "asc" (oldest first) or "desc" (newest first) (default: "asc")

        Returns:
            List of Message objects

        Example:
            history = await service.get_history(conversation_id=456, limit=50)
        """
        order_by = asc(Message.created_at) if order == "asc" else desc(Message.created_at)

        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(order_by)
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        messages = result.scalars().all()

        return list(messages)

    async def get_history_for_agent(
        self,
        conversation_id: int,
        max_messages: int = 50
    ) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for OpenAI Agents SDK.

        Returns messages in the format expected by the Agent:
        [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."},
            ...
        ]

        Args:
            conversation_id: ID of the conversation
            max_messages: Maximum number of messages to include (default: 50)

        Returns:
            List of message dictionaries for Agent SDK

        Example:
            history = await service.get_history_for_agent(conversation_id=456)
            # Pass to Agent: agent.run(messages=history + [new_user_message])
        """
        messages = await self.get_history(
            conversation_id=conversation_id,
            limit=max_messages,
            order="asc"
        )

        # Format for OpenAI Agents SDK
        agent_history = [
            {
                "role": message.role,
                "content": message.content
            }
            for message in messages
        ]

        return agent_history

    async def count_messages(self, conversation_id: int) -> int:
        """
        Count total number of messages in a conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            Count of messages

        Example:
            count = await service.count_messages(conversation_id=456)
        """
        from sqlalchemy import func

        query = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )

        result = await self.session.execute(query)
        count = result.scalar_one()

        return count

    async def get_last_message(
        self,
        conversation_id: int
    ) -> Optional[Message]:
        """
        Get the most recent message in a conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            Most recent Message object, or None if no messages

        Example:
            last_msg = await service.get_last_message(conversation_id=456)
            if last_msg and last_msg.role == "assistant":
                print("Last response:", last_msg.content)
        """
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )

        result = await self.session.execute(query)
        message = result.scalar_one_or_none()

        return message

    async def bulk_add_messages(
        self,
        conversation_id: int,
        messages: List[Dict[str, str]]
    ) -> List[Message]:
        """
        Add multiple messages to a conversation in bulk.

        Useful for saving Agent responses that include multiple tool call messages.

        Args:
            conversation_id: ID of the conversation
            messages: List of message dicts with "role" and "content" keys

        Returns:
            List of created Message objects

        Example:
            new_messages = await service.bulk_add_messages(
                conversation_id=456,
                messages=[
                    {"role": "assistant", "content": "I'll add that task for you."},
                    {"role": "assistant", "content": "Task added successfully!"}
                ]
            )
        """
        created_messages = []

        for msg_dict in messages:
            role = msg_dict.get("role")
            content = msg_dict.get("content")

            if role not in ("user", "assistant"):
                raise ValueError(f"Invalid role in message: {role}")

            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                created_at=datetime.utcnow()
            )

            self.session.add(message)
            created_messages.append(message)

        # Update conversation's updated_at timestamp
        await self.session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(updated_at=datetime.utcnow())
        )

        await self.session.commit()

        # Refresh all messages to get their IDs
        for message in created_messages:
            await self.session.refresh(message)

        return created_messages
