"""
Enhanced Conversation Manager with Advanced Context Management

This module provides an enhanced conversation manager with:
- Smart context summarization for long conversations
- Conversation threading and topic tracking
- Performance optimizations with caching
- Enhanced search and filtering capabilities
- Conversation analytics and insights
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_, or_
from uuid import UUID
import json
import hashlib

from app.models.conversation import Conversation
from app.models.message import Message


class EnhancedConversationManager:
    """
    Enhanced conversation manager with advanced features for better context management.

    Features:
    - Smart conversation summarization
    - Topic tracking and threading
    - Performance optimizations
    - Enhanced search capabilities
    - Conversation analytics
    """

    def __init__(self, db: AsyncSession, cache_ttl: int = 300):
        """
        Initialize enhanced conversation manager.

        Args:
            db: Async database session
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
        """
        self.db = db
        self.cache_ttl = cache_ttl
        self._conversation_cache = {}
        self._summary_cache = {}

    async def create_conversation(
        self,
        user_id: UUID,
        title: Optional[str] = None,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """
        Create a new conversation with enhanced metadata.

        Args:
            user_id: The user's UUID
            title: Optional conversation title
            initial_context: Optional initial context data

        Returns:
            The UUID of the new conversation
        """
        # Generate intelligent title if not provided
        if not title:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        conversation = Conversation(
            user_id=user_id,
            title=title,
            metadata={
                "created_at": datetime.utcnow().isoformat(),
                "context": initial_context or {},
                "message_count": 0,
                "last_activity": datetime.utcnow().isoformat(),
                "language_detected": None,
                "topics": []
            }
        )

        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)

        # Cache the new conversation
        self._conversation_cache[conversation.id] = {
            "data": conversation,
            "cached_at": datetime.utcnow()
        }

        return conversation.id

    async def get_history_with_context(
        self,
        conversation_id: UUID,
        max_tokens: int = 8000,  # Rough token limit for context
        include_summary: bool = True
    ) -> Dict[str, Any]:
        """
        Get conversation history with intelligent context management.

        Args:
            conversation_id: The conversation ID
            max_tokens: Maximum tokens to include in context
            include_summary: Whether to include conversation summary

        Returns:
            Dict with:
            - messages: List of recent messages
            - summary: Conversation summary (if include_summary=True)
            - context: Additional context data
            - total_messages: Total message count
        """
        # Check cache first
        cache_key = f"history_{conversation_id}_{max_tokens}"
        if cache_key in self._summary_cache:
            cached_data = self._summary_cache[cache_key]
            if (datetime.utcnow() - cached_data["cached_at"]).seconds < self.cache_ttl:
                return cached_data["data"]

        # Get total message count
        total_count_result = await self.db.execute(
            select(func.count(Message.id))
            .where(Message.conversation_id == conversation_id)
        )
        total_messages = total_count_result.scalar() or 0

        # Get recent messages (estimate ~4 tokens per character)
        recent_messages = await self._get_recent_messages_by_token_limit(
            conversation_id, max_tokens
        )

        # Generate summary if needed and we have many messages
        summary = None
        if include_summary and total_messages > len(recent_messages):
            summary = await self._generate_conversation_summary(
                conversation_id, total_messages - len(recent_messages)
            )

        # Extract context insights
        context = await self._extract_conversation_context(conversation_id)

        result = {
            "messages": recent_messages,
            "summary": summary,
            "context": context,
            "total_messages": total_messages,
            "truncated": total_messages > len(recent_messages)
        }

        # Cache the result
        self._summary_cache[cache_key] = {
            "data": result,
            "cached_at": datetime.utcnow()
        }

        return result

    async def _get_recent_messages_by_token_limit(
        self,
        conversation_id: UUID,
        max_tokens: int
    ) -> List[Dict[str, str]]:
        """
        Get recent messages within token limit.
        """
        # Get all messages ordered by creation date
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(100)  # Get more than we need, then filter
        )
        messages = result.scalars().all()

        # Build messages from newest to oldest until we hit token limit
        recent_messages = []
        current_tokens = 0

        for message in reversed(messages):  # Reverse to get chronological order
            message_tokens = len(message.content) * 1.3  # Rough token estimate

            if current_tokens + message_tokens > max_tokens:
                break

            recent_messages.append({
                "role": message.role,
                "content": message.content,
                "timestamp": message.created_at.isoformat()
            })
            current_tokens += message_tokens

        return recent_messages

    async def _generate_conversation_summary(
        self,
        conversation_id: UUID,
        older_message_count: int
    ) -> Optional[str]:
        """
        Generate a summary of older conversation messages.
        """
        # Get older messages that aren't included in recent context
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(older_message_count)
        )
        older_messages = result.scalars().all()

        if not older_messages:
            return None

        # Simple summarization logic (can be enhanced with AI)
        # Extract key information from older messages
        task_operations = []
        topics = set()

        for msg in older_messages:
            content_lower = msg.content.lower()

            # Extract task-related activities
            if any(word in content_lower for word in ['create', 'add', 'made', 'بنای', 'شامل']):
                task_operations.append("task_created")
            elif any(word in content_lower for word in ['complete', 'finish', 'done', 'مکمل', 'ختم']):
                task_operations.append("task_completed")
            elif any(word in content_lower for word in ['delete', 'remove', 'حذف', 'ہٹا']):
                task_operations.append("task_deleted")
            elif any(word in content_lower for word in ['update', 'change', 'تبدیلی']):
                task_operations.append("task_updated")

        # Generate summary based on activities
        if task_operations:
            activity_counts = {}
            for activity in task_operations:
                activity_counts[activity] = activity_counts.get(activity, 0) + 1

            summary_parts = []
            if activity_counts.get('task_created', 0) > 0:
                summary_parts.append(f"created {activity_counts['task_created']} task(s)")
            if activity_counts.get('task_completed', 0) > 0:
                summary_parts.append(f"completed {activity_counts['task_completed']} task(s)")
            if activity_counts.get('task_deleted', 0) > 0:
                summary_parts.append(f"deleted {activity_counts['task_deleted']} task(s)")
            if activity_counts.get('task_updated', 0) > 0:
                summary_parts.append(f"updated {activity_counts['task_updated']} task(s)")

            return f"[Earlier in conversation: {' and '.join(summary_parts)}]"

        return "[Earlier in conversation: General discussion about tasks]"

    async def _extract_conversation_context(
        self,
        conversation_id: UUID
    ) -> Dict[str, Any]:
        """
        Extract contextual insights from the conversation.
        """
        # Get conversation metadata
        conv_result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            return {}

        metadata = conversation.metadata or {}

        # Analyze language patterns from recent messages
        recent_result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(10)
        )
        recent_messages = recent_result.scalars().all()

        # Detect primary language
        urdu_count = 0
        english_count = 0

        for msg in recent_messages:
            if self._has_urdu_text(msg.content):
                urdu_count += 1
            else:
                english_count += 1

        primary_language = "ur" if urdu_count > english_count else "en"

        # Extract task-related patterns
        task_mentions = 0
        for msg in recent_messages:
            if any(word in msg.content.lower() for word in ['task', 'todo', 'ٹاسک', 'کام']):
                task_mentions += 1

        return {
            "primary_language": primary_language,
            "task_focus_score": min(task_mentions / len(recent_messages), 1.0) if recent_messages else 0,
            "conversation_length": metadata.get("message_count", 0),
            "last_activity": metadata.get("last_activity"),
            "topics": metadata.get("topics", [])
        }

    def _has_urdu_text(self, text: str) -> bool:
        """Check if text contains Urdu characters."""
        import re
        urdu_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        return urdu_chars > len(text) * 0.3  # 30% threshold

    async def search_conversations(
        self,
        user_id: UUID,
        query: str,
        limit: int = 10,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search conversations by content with advanced filtering.

        Args:
            user_id: User ID to filter conversations
            query: Search query
            limit: Maximum results to return
            date_range: Optional date range filter

        Returns:
            List of matching conversations with highlights
        """
        # Build base query
        where_conditions = [
            Conversation.user_id == user_id,
            or_(
                Message.content.ilike(f"%{query}%"),
                Conversation.title.ilike(f"%{query}%")
            )
        ]

        # Add date range filter if provided
        if date_range:
            start_date, end_date = date_range
            where_conditions.append(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at <= end_date
                )
            )

        # Search conversations with matching messages
        result = await self.db.execute(
            select(Conversation, Message)
            .join(Message, Conversation.id == Message.conversation_id)
            .where(and_(*where_conditions))
            .order_by(desc(Message.created_at))
            .limit(limit)
        )

        conversations_with_matches = []
        seen_conversations = set()

        for conversation, message in result:
            if conversation.id not in seen_conversations:
                # Highlight matching content
                highlighted_content = self._highlight_search_term(
                    message.content, query
                )

                conversations_with_matches.append({
                    "conversation_id": conversation.id,
                    "title": conversation.title,
                    "last_message": message.content,
                    "highlighted_content": highlighted_content,
                    "last_activity": message.created_at,
                    "message_preview": message.content[:100] + "..." if len(message.content) > 100 else message.content
                })
                seen_conversations.add(conversation.id)

        return conversations_with_matches

    def _highlight_search_term(self, text: str, query: str) -> str:
        """Highlight search term in text."""
        import re
        # Simple case-insensitive highlighting
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return pattern.sub(f"**{query}**", text)

    async def update_conversation_metadata(
        self,
        conversation_id: UUID,
        updates: Dict[str, Any]
    ) -> None:
        """
        Update conversation metadata.
        """
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if conversation:
            current_metadata = conversation.metadata or {}
            current_metadata.update(updates)
            current_metadata["last_updated"] = datetime.utcnow().isoformat()

            conversation.metadata = current_metadata

            # Update cache
            if conversation_id in self._conversation_cache:
                self._conversation_cache[conversation_id]["data"] = conversation

    async def get_conversation_analytics(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get analytics about user's conversations.
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get conversation statistics
        conv_stats_result = await self.db.execute(
            select(
                func.count(Conversation.id).label('total_conversations'),
                func.avg(Conversation.metadata['message_count'].astext.cast(Integer)).label('avg_messages')
            )
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.created_at >= start_date
                )
            )
        )
        conv_stats = conv_stats_result.first()

        # Get message statistics
        message_stats_result = await self.db.execute(
            select(
                func.count(Message.id).label('total_messages'),
                func.count(func.distinct(Message.conversation_id)).label('active_conversations')
            )
            .join(Conversation)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Message.created_at >= start_date
                )
            )
        )
        message_stats = message_stats_result.first()

        # Get daily activity
        daily_activity_result = await self.db.execute(
            select(
                func.date(Message.created_at).label('date'),
                func.count(Message.id).label('message_count')
            )
            .join(Conversation)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Message.created_at >= start_date
                )
            )
            .group_by(func.date(Message.created_at))
            .order_by(func.date(Message.created_at))
        )
        daily_activity = dict(daily_activity_result.all())

        return {
            "period_days": days,
            "total_conversations": conv_stats.total_conversations or 0,
            "average_messages_per_conversation": float(conv_stats.avg_messages or 0),
            "total_messages": message_stats.total_messages or 0,
            "active_conversations": message_stats.active_conversations or 0,
            "daily_activity": daily_activity,
            "generated_at": datetime.utcnow().isoformat()
        }

    def clear_cache(self):
        """Clear all caches."""
        self._conversation_cache.clear()
        self._summary_cache.clear()