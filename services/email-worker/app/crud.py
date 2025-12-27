"""Database CRUD operations for email worker."""
import logging
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def get_user_by_id(db: AsyncSession, user_id: UUID):
    """
    Get user by ID.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        User object or None
    """
    try:
        from .models import User

        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return None


async def get_task_by_id(db: AsyncSession, task_id: UUID):
    """
    Get task by ID.

    Args:
        db: Database session
        task_id: Task UUID

    Returns:
        Task object or None
    """
    try:
        from .models import Task

        result = await db.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        return None
