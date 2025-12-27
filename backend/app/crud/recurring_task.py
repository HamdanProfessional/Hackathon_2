"""RecurringTask CRUD operations."""
from typing import List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from dateutil.relativedelta import relativedelta
import logging

from app.models.recurring_task import RecurringTask
from app.schemas.recurring_task import RecurringTaskCreate, RecurringTaskUpdate
from app.services.event_publisher import dapr_event_publisher

logger = logging.getLogger(__name__)


def calculate_next_due_at(current_date: date, pattern: str) -> date:
    """
    Calculate the next due date based on recurrence pattern.

    Args:
        current_date: The current due date
        pattern: Recurrence pattern (daily, weekly, monthly, yearly)

    Returns:
        The next due date

    Raises:
        ValueError: If invalid recurrence pattern is provided
    """
    if pattern == "daily":
        return current_date + timedelta(days=1)
    elif pattern == "weekly":
        return current_date + timedelta(weeks=1)
    elif pattern == "monthly":
        return current_date + relativedelta(months=1)
    elif pattern == "yearly":
        return current_date + relativedelta(years=1)
    else:
        raise ValueError(f"Invalid recurrence pattern: {pattern}")


async def create_recurring_task(
    db: AsyncSession,
    task_data: RecurringTaskCreate,
    user_id: str
) -> RecurringTask:
    """
    Create a new recurring task for a user.

    Args:
        db: Database session
        task_data: Recurring task creation data
        user_id: Owner user ID (UUID string)

    Returns:
        Created recurring task instance
    """
    # Calculate the first due date based on start_date
    next_due_at = task_data.start_date

    db_task = RecurringTask(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description or "",
        recurrence_pattern=task_data.recurrence_pattern,
        start_date=task_data.start_date,
        end_date=task_data.end_date,
        next_due_at=next_due_at,
        is_active=True,
        task_priority_id=task_data.task_priority_id,
    )

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    # Re-fetch with eager loading to prevent DetachedInstanceError
    stmt = (
        select(RecurringTask)
        .where(RecurringTask.id == db_task.id)
        .options(selectinload(RecurringTask.priority_obj))
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_recurring_tasks_by_user(
    db: AsyncSession,
    user_id: str,
    active_only: bool = False,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 20,
    offset: int = 0
) -> List[RecurringTask]:
    """
    Get all recurring tasks for a specific user with optional filtering.

    Args:
        db: Database session
        user_id: User ID (UUID string) to filter by
        active_only: If True, only return active recurring tasks
        sort_by: Field to sort by (created_at, next_due_at, title)
        sort_order: Sort order ("asc" or "desc")
        limit: Maximum number of recurring tasks to return
        offset: Number of recurring tasks to skip

    Returns:
        List of user's recurring tasks matching the criteria
    """
    # Start with base query with relationship loading
    query = (
        select(RecurringTask)
        .options(selectinload(RecurringTask.priority_obj))
        .where(RecurringTask.user_id == user_id)
    )

    # Apply active filter
    if active_only:
        query = query.where(RecurringTask.is_active == True)

    # Apply sorting
    if sort_by == "next_due_at":
        from sqlalchemy import asc, desc
        if sort_order == "asc":
            query = query.order_by(asc(RecurringTask.next_due_at))
        else:
            query = query.order_by(desc(RecurringTask.next_due_at))
    elif sort_by == "title":
        from sqlalchemy import asc, desc
        if sort_order == "asc":
            query = query.order_by(asc(RecurringTask.title))
        else:
            query = query.order_by(desc(RecurringTask.title))
    else:
        # Default: Sort by created_at
        from sqlalchemy import asc, desc
        if sort_order == "asc":
            query = query.order_by(asc(RecurringTask.created_at))
        else:
            query = query.order_by(desc(RecurringTask.created_at))

    # Apply pagination
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()


async def get_recurring_task_by_id(
    db: AsyncSession,
    recurring_task_id: int,
    user_id: str
) -> Optional[RecurringTask]:
    """
    Get a specific recurring task by ID, ensuring it belongs to the user.

    Args:
        db: Database session
        recurring_task_id: Recurring task ID
        user_id: User ID (UUID string) to verify ownership

    Returns:
        RecurringTask instance if found and owned by user, None otherwise
    """
    result = await db.execute(
        select(RecurringTask)
        .options(selectinload(RecurringTask.priority_obj))
        .where(
            RecurringTask.id == recurring_task_id,
            RecurringTask.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def update_recurring_task(
    db: AsyncSession,
    recurring_task: RecurringTask,
    task_data: RecurringTaskUpdate
) -> RecurringTask:
    """
    Update a recurring task's details.

    Args:
        db: Database session
        recurring_task: RecurringTask instance to update
        task_data: Updated recurring task data

    Returns:
        Updated recurring task instance
    """
    if task_data.title is not None:
        recurring_task.title = task_data.title
    if task_data.description is not None:
        recurring_task.description = task_data.description
    if task_data.recurrence_pattern is not None:
        recurring_task.recurrence_pattern = task_data.recurrence_pattern
    if task_data.start_date is not None:
        recurring_task.start_date = task_data.start_date
    if task_data.end_date is not None:
        recurring_task.end_date = task_data.end_date
    if task_data.task_priority_id is not None:
        recurring_task.task_priority_id = task_data.task_priority_id
    if task_data.is_active is not None:
        recurring_task.is_active = task_data.is_active

    await db.commit()
    await db.refresh(recurring_task)

    # Re-fetch with eager loading to prevent DetachedInstanceError
    stmt = (
        select(RecurringTask)
        .where(RecurringTask.id == recurring_task.id)
        .options(selectinload(RecurringTask.priority_obj))
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def delete_recurring_task(
    db: AsyncSession,
    recurring_task: RecurringTask
) -> None:
    """
    Delete a recurring task.

    Args:
        db: Database session
        recurring_task: RecurringTask instance to delete
    """
    await db.delete(recurring_task)
    await db.commit()


async def pause_recurring_task(
    db: AsyncSession,
    recurring_task: RecurringTask
) -> RecurringTask:
    """
    Pause a recurring task by setting is_active to False.

    Args:
        db: Database session
        recurring_task: RecurringTask instance to pause

    Returns:
        Updated recurring task instance
    """
    recurring_task.is_active = False
    await db.commit()
    await db.refresh(recurring_task)

    # Re-fetch with eager loading
    stmt = (
        select(RecurringTask)
        .where(RecurringTask.id == recurring_task.id)
        .options(selectinload(RecurringTask.priority_obj))
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def resume_recurring_task(
    db: AsyncSession,
    recurring_task: RecurringTask
) -> RecurringTask:
    """
    Resume a paused recurring task by setting is_active to True
    and recalculating next_due_at if needed.

    Args:
        db: Database session
        recurring_task: RecurringTask instance to resume

    Returns:
        Updated recurring task instance
    """
    recurring_task.is_active = True

    # If next_due_at is in the past, recalculate from today
    today = date.today()
    if recurring_task.next_due_at < today:
        # Calculate next occurrence from today
        next_due = today
        while next_due <= today:
            next_due = calculate_next_due_at(next_due, recurring_task.recurrence_pattern)
        recurring_task.next_due_at = next_due

    await db.commit()
    await db.refresh(recurring_task)

    # Re-fetch with eager loading
    stmt = (
        select(RecurringTask)
        .where(RecurringTask.id == recurring_task.id)
        .options(selectinload(RecurringTask.priority_obj))
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_due_recurring_tasks(
    db: AsyncSession,
    target_date: Optional[date] = None
) -> List[RecurringTask]:
    """
    Get all recurring tasks that are due on or before the target date.

    This is used by background jobs to create actual tasks from recurring tasks.

    Args:
        db: Database session
        target_date: Target date (defaults to today)

    Returns:
        List of recurring tasks that are due
    """
    if target_date is None:
        target_date = date.today()

    result = await db.execute(
        select(RecurringTask)
        .options(selectinload(RecurringTask.priority_obj))
        .where(
            and_(
                RecurringTask.is_active == True,
                RecurringTask.next_due_at <= target_date,
                # Respect end_date if set
                (RecurringTask.end_date >= target_date) | (RecurringTask.end_date.is_(None))
            )
        )
    )
    return result.scalars().all()


async def advance_recurring_task(
    db: AsyncSession,
    recurring_task: RecurringTask
) -> RecurringTask:
    """
    Advance a recurring task to its next due date.

    After creating a task from a recurring task, this function
    calculates and sets the next due date.

    Args:
        db: Database session
        recurring_task: RecurringTask instance to advance

    Returns:
        Updated recurring task instance

    Raises:
        ValueError: If the recurring task has reached its end_date
    """
    next_due = calculate_next_due_at(
        recurring_task.next_due_at,
        recurring_task.recurrence_pattern
    )

    # Check if we've reached the end date
    if recurring_task.end_date and next_due > recurring_task.end_date:
        # Deactivate the recurring task
        recurring_task.is_active = False
    else:
        recurring_task.next_due_at = next_due

    await db.commit()
    await db.refresh(recurring_task)

    # Re-fetch with eager loading
    stmt = (
        select(RecurringTask)
        .where(RecurringTask.id == recurring_task.id)
        .options(selectinload(RecurringTask.priority_obj))
    )
    result = await db.execute(stmt)
    updated_task = result.scalar_one()

    # Publish recurring-task-due event for the next occurrence
    try:
        if updated_task.is_active:
            event_data = {
                "recurring_task_id": updated_task.id,
                "user_id": str(updated_task.user_id),
                "title": updated_task.title,
                "description": updated_task.description,
                "next_due_at": updated_task.next_due_at.isoformat(),
                "recurrence_pattern": updated_task.recurrence_pattern,
                "task_priority_id": updated_task.task_priority_id
            }
            await dapr_event_publisher.publish_recurring_task_due(event_data)
    except Exception as e:
        logger.error(f"Failed to publish recurring-task-due event: {e}")

    return updated_task


async def count_recurring_tasks_by_user(
    db: AsyncSession,
    user_id: str,
    active_only: bool = False
) -> int:
    """
    Count recurring tasks for a specific user.

    Args:
        db: Database session
        user_id: User ID (UUID string) to filter by
        active_only: If True, only count active recurring tasks

    Returns:
        Count of recurring tasks
    """
    from sqlalchemy import func

    query = select(func.count(RecurringTask.id)).where(RecurringTask.user_id == user_id)

    if active_only:
        query = query.where(RecurringTask.is_active == True)

    result = await db.execute(query)
    return result.scalar()
