"""Event logging service for database audit trail."""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task_event_log import TaskEventLog

logger = logging.getLogger(__name__)


class EventLogger:
    """
    Service for logging events to task_event_log table.

    This provides an audit trail of all task events in the database,
    separate from the Dapr event publishing for real-time processing.
    """

    @staticmethod
    async def log_event(
        db: AsyncSession,
        task_id: int,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None
    ) -> Optional[TaskEventLog]:
        """
        Log event to task_event_log table.

        Args:
            db: Database session
            task_id: Task ID that triggered the event
            event_type: Event type (created, updated, completed, deleted, due_soon)
            event_data: Optional event payload data

        Returns:
            Created TaskEventLog instance, or None if logging fails
        """
        try:
            event_log = TaskEventLog(
                task_id=task_id,
                event_type=event_type,
                event_data=event_data or {}
            )

            db.add(event_log)
            await db.commit()
            await db.refresh(event_log)

            logger.debug(
                f"Event logged: task_id={task_id}, "
                f"event_type={event_type}, log_id={event_log.id}"
            )

            return event_log

        except Exception as e:
            logger.error(f"Failed to log event to database: {e}")
            await db.rollback()
            return None

    @staticmethod
    async def log_task_created(
        db: AsyncSession,
        task_id: int,
        event_data: Dict[str, Any]
    ) -> Optional[TaskEventLog]:
        """Log task created event."""
        return await EventLogger.log_event(db, task_id, "created", event_data)

    @staticmethod
    async def log_task_updated(
        db: AsyncSession,
        task_id: int,
        event_data: Dict[str, Any]
    ) -> Optional[TaskEventLog]:
        """Log task updated event."""
        return await EventLogger.log_event(db, task_id, "updated", event_data)

    @staticmethod
    async def log_task_completed(
        db: AsyncSession,
        task_id: int,
        event_data: Dict[str, Any]
    ) -> Optional[TaskEventLog]:
        """Log task completed event."""
        return await EventLogger.log_event(db, task_id, "completed", event_data)

    @staticmethod
    async def log_task_deleted(
        db: AsyncSession,
        task_id: int,
        event_data: Dict[str, Any]
    ) -> Optional[TaskEventLog]:
        """Log task deleted event."""
        return await EventLogger.log_event(db, task_id, "deleted", event_data)

    @staticmethod
    async def log_task_due_soon(
        db: AsyncSession,
        task_id: int,
        event_data: Dict[str, Any]
    ) -> Optional[TaskEventLog]:
        """Log task due soon event."""
        return await EventLogger.log_event(db, task_id, "due_soon", event_data)


# Global singleton instance
event_logger = EventLogger()
