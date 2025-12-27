"""Task notification service for due-soon alerts.

This module provides utilities for publishing task-due-soon events
when background jobs detect tasks approaching their due dates.
"""
import logging
from typing import List
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.task import Task
from app.services.event_publisher import dapr_event_publisher
from app.services.event_logger import event_logger

logger = logging.getLogger(__name__)


async def publish_due_soon_events(
    db: AsyncSession,
    hours_threshold: int = 24
) -> int:
    """
    Publish task-due-soon events for tasks approaching their due date.

    This is designed to be called by a background job/cron scheduler
    to notify users of tasks due within the specified threshold.

    Args:
        db: Database session
        hours_threshold: Hours within due date to trigger notification (default: 24)

    Returns:
        Number of events published

    Example:
        # Run every hour to check for tasks due within 24 hours
        await publish_due_soon_events(db, hours_threshold=24)
    """
    threshold_time = datetime.utcnow() + timedelta(hours=hours_threshold)
    threshold_date = threshold_time.date()

    try:
        # Find tasks that:
        # 1. Are not completed
        # 2. Have a due_date set
        # 3. Are due within the threshold
        # 4. Haven't been notified yet (notified=False)
        result = await db.execute(
            select(Task).where(
                and_(
                    Task.completed == False,
                    Task.due_date.isnot(None),
                    Task.due_date <= threshold_date,
                    Task.notified == False
                )
            )
        )
        due_soon_tasks = result.scalars().all()

        events_published = 0

        for task in due_soon_tasks:
            try:
                # Calculate hours until due
                if task.due_date:
                    due_datetime = datetime.combine(task.due_date, datetime.min.time())
                    hours_until_due = (due_datetime - datetime.utcnow()).total_seconds() / 3600
                else:
                    hours_until_due = 0

                event_data = {
                    "task_id": task.id,
                    "user_id": str(task.user_id),
                    "title": task.title,
                    "description": task.description,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority_id": task.priority_id,
                    "hours_until_due": int(hours_until_due)
                }

                # Publish event
                await dapr_event_publisher.publish_task_due_soon(event_data)
                await event_logger.log_task_due_soon(db, task.id, event_data)

                # Mark task as notified (prevent duplicate notifications)
                task.notified = True
                await db.commit()

                events_published += 1
                logger.info(
                    f"Published due-soon event for task {task.id} "
                    f"(due in {int(hours_until_due)} hours)"
                )

            except Exception as e:
                logger.error(f"Failed to publish due-soon event for task {task.id}: {e}")
                await db.rollback()

        if events_published > 0:
            logger.info(f"Published {events_published} due-soon task events")

        return events_published

    except Exception as e:
        logger.error(f"Failed to publish due-soon events: {e}")
        return 0


async def reset_notified_flag_after_due(db: AsyncSession) -> int:
    """
    Reset the notified flag for tasks that have passed their due date.

    This allows tasks to be notified again if they become overdue
    (e.g., for a different notification type).

    Args:
        db: Database session

    Returns:
        Number of tasks updated
    """
    try:
        yesterday = date.today() - timedelta(days=1)

        result = await db.execute(
            select(Task).where(
                and_(
                    Task.notified == True,
                    Task.due_date < yesterday
                )
            )
        )
        overdue_tasks = result.scalars().all()

        for task in overdue_tasks:
            task.notified = False

        await db.commit()

        logger.info(f"Reset notified flag for {len(overdue_tasks)} overdue tasks")
        return len(overdue_tasks)

    except Exception as e:
        logger.error(f"Failed to reset notified flags: {e}")
        await db.rollback()
        return 0
