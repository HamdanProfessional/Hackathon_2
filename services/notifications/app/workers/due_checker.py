"""Due date checker worker for notification service."""
import asyncio
import logging
from datetime import date, datetime, timedelta
from typing import List, Tuple
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.task import Task
from app.models.user import User
from app.models.task_event_log import TaskEventLog
from app.services.notification import notification_service
from app.config import settings

logger = logging.getLogger(__name__)


async def get_tasks_due_soon(db: AsyncSession) -> List[Tuple[Task, User]]:
    """
    Get tasks that are due within the threshold and haven't been notified.

    Args:
        db: Database session

    Returns:
        List of tuples containing (task, user)
    """
    due_threshold = date.today() + timedelta(days=settings.DUE_THRESHOLD_HOURS // 24)

    query = (
        select(Task, User)
        .join(User, Task.user_id == User.id)
        .where(
            and_(
                Task.due_date <= due_threshold,
                Task.due_date >= date.today(),  # Only future or today's tasks
                Task.notified == False,
                Task.completed == False
            )
        )
    )

    result = await db.execute(query)
    return result.all()


async def mark_task_notified(db: AsyncSession, task_id: int) -> bool:
    """
    Mark a task as notified.

    Args:
        db: Database session
        task_id: Task ID

    Returns:
        True if marked successfully, False otherwise
    """
    try:
        await db.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(notified=True)
        )
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to mark task {task_id} as notified: {e}")
        await db.rollback()
        return False


async def log_task_event(db: AsyncSession, task_id: int, event_type: str, event_data: dict) -> bool:
    """
    Log a task event to the database.

    Args:
        db: Database session
        task_id: Task ID
        event_type: Event type (e.g., 'due_soon')
        event_data: Event payload

    Returns:
        True if logged successfully, False otherwise
    """
    try:
        event_log = TaskEventLog(
            task_id=task_id,
            event_type=event_type,
            event_data=event_data
        )
        db.add(event_log)
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to log event for task {task_id}: {e}")
        await db.rollback()
        return False


async def check_and_notify_due_tasks() -> int:
    """
    Check for due tasks and send notifications.

    Returns:
        Number of tasks notified
    """
    notified_count = 0

    async with AsyncSessionLocal() as db:
        try:
            tasks_users = await get_tasks_due_soon(db)

            for task, user in tasks_users:
                # Calculate hours until due
                due_datetime = datetime.combine(task.due_date, datetime.min.time())
                hours_until_due = int((due_datetime - datetime.now()).total_seconds() / 3600)

                # Skip if already past due
                if hours_until_due < 0:
                    continue

                logger.info(
                    f"Task {task.id} '{task.title}' is due in {hours_until_due} hours. "
                    f"User: {user.email}"
                )

                # Send notification
                notification_sent = await notification_service.send_task_due_notification(
                    user_email=user.email,
                    user_name=user.name,
                    task_title=task.title,
                    task_description=task.description,
                    due_date=task.due_date,
                    hours_until_due=hours_until_due,
                    task_id=task.id
                )

                if notification_sent:
                    # Mark as notified
                    if await mark_task_notified(db, task.id):
                        # Log event
                        await log_task_event(db, task.id, "due_soon", {
                            "user_id": str(task.user_id),
                            "due_date": task.due_date.isoformat(),
                            "hours_until_due": hours_until_due
                        })
                        notified_count += 1
                        logger.info(f"Successfully notified user for task {task.id}")
                else:
                    logger.warning(f"Failed to send notification for task {task.id}")

        except Exception as e:
            logger.error(f"Error in due checker: {e}")

    return notified_count


async def due_checker_worker():
    """
    Run the due checker worker.

    Checks for tasks due within the threshold every interval.
    """
    logger.info("Starting due checker worker...")
    logger.info(f"Checking for tasks due within {settings.DUE_THRESHOLD_HOURS} hours every {settings.DUE_CHECK_INTERVAL_SECONDS} seconds")

    while True:
        try:
            notified_count = await check_and_notify_due_tasks()
            if notified_count > 0:
                logger.info(f"Due checker cycle complete: {notified_count} tasks notified")
            else:
                logger.debug("Due checker cycle complete: no tasks to notify")

        except Exception as e:
            logger.error(f"Due checker worker error: {e}", exc_info=True)

        await asyncio.sleep(settings.DUE_CHECK_INTERVAL_SECONDS)


async def run_due_checker_once():
    """
    Run the due checker once (for testing).

    Returns:
        Number of tasks notified
    """
    return await check_and_notify_due_tasks()
