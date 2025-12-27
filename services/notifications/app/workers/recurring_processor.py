"""Recurring task processor worker for notification service."""
import asyncio
import logging
from datetime import date, datetime, timedelta
from typing import List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.task import Task, RecurringTask
from app.models.user import User
from app.models.task_event_log import TaskEventLog
from app.services.notification import notification_service
from app.config import settings

logger = logging.getLogger(__name__)


def calculate_next_due_date(current_date: date, pattern: str) -> date:
    """
    Calculate the next due date based on recurrence pattern.

    Args:
        current_date: Current due date
        pattern: Recurrence pattern ('daily', 'weekly', 'monthly', 'yearly')

    Returns:
        Next due date
    """
    if pattern == "daily":
        return current_date + timedelta(days=1)
    elif pattern == "weekly":
        return current_date + timedelta(weeks=1)
    elif pattern == "monthly":
        # Add one month (handle year rollover)
        year = current_date.year + ((current_date.month + 1) // 12)
        month = (current_date.month % 12) + 1
        day = min(current_date.day, [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return date(year, month, day)
    elif pattern == "yearly":
        # Handle leap years
        try:
            return current_date.replace(year=current_date.year + 1)
        except ValueError:
            # February 29 in non-leap year
            return current_date.replace(year=current_date.year + 1, day=28)
    else:
        logger.warning(f"Unknown recurrence pattern: {pattern}")
        return current_date + timedelta(days=1)


async def get_due_recurring_tasks(db: AsyncSession) -> List[tuple[RecurringTask, User]]:
    """
    Get recurring tasks that are due for processing.

    Args:
        db: Database session

    Returns:
        List of tuples containing (recurring_task, user)
    """
    today = date.today()

    query = (
        select(RecurringTask, User)
        .join(User, RecurringTask.user_id == User.id)
        .where(
            and_(
                RecurringTask.next_due_at <= today,
                RecurringTask.is_active == True
            )
        )
    )

    result = await db.execute(query)
    return result.all()


async def create_task_from_recurring(
    db: AsyncSession,
    recurring_task: RecurringTask,
    user: User
) -> Task | None:
    """
    Create a new task instance from a recurring task.

    Args:
        db: Database session
        recurring_task: Recurring task template
        user: User who owns the task

    Returns:
        Created task or None if failed
    """
    try:
        new_task = Task(
            user_id=user.id,
            title=recurring_task.title,
            description=recurring_task.description,
            priority_id=recurring_task.task_priority_id,
            due_date=recurring_task.next_due_at,
            is_recurring=True,
            recurring_task_id=recurring_task.id,
            completed=False,
            notified=False
        )

        db.add(new_task)
        await db.flush()  # Get the task ID without committing

        logger.info(
            f"Created task {new_task.id} from recurring task {recurring_task.id}: "
            f"'{recurring_task.title}' due {recurring_task.next_due_at}"
        )

        return new_task

    except Exception as e:
        logger.error(f"Failed to create task from recurring task {recurring_task.id}: {e}")
        return None


async def update_recurring_task_next_due(
    db: AsyncSession,
    recurring_task: RecurringTask
) -> bool:
    """
    Update the next due date for a recurring task.

    Args:
        db: Database session
        recurring_task: Recurring task to update

    Returns:
        True if updated successfully, False otherwise
    """
    try:
        # Calculate next due date
        next_due = calculate_next_due_date(
            recurring_task.next_due_at,
            recurring_task.recurrence_pattern
        )

        # Check if we've reached the end date
        if recurring_task.end_date and next_due > recurring_task.end_date:
            recurring_task.is_active = False
            logger.info(f"Recurring task {recurring_task.id} reached end date, deactivating")
        else:
            recurring_task.next_due_at = next_due
            logger.info(f"Updated recurring task {recurring_task.id} next due to {next_due}")

        await db.commit()
        return True

    except Exception as e:
        logger.error(f"Failed to update recurring task {recurring_task.id}: {e}")
        await db.rollback()
        return False


async def process_recurring_tasks() -> int:
    """
    Process all due recurring tasks.

    Returns:
        Number of tasks created
    """
    created_count = 0

    async with AsyncSessionLocal() as db:
        try:
            recurring_tasks_users = await get_due_recurring_tasks(db)

            for recurring_task, user in recurring_tasks_users:
                logger.info(
                    f"Processing recurring task {recurring_task.id}: "
                    f"'{recurring_task.title}' due {recurring_task.next_due_at}"
                )

                # Create new task instance
                new_task = await create_task_from_recurring(db, recurring_task, user)

                if new_task:
                    # Update recurring task next due date
                    if await update_recurring_task_next_due(db, recurring_task):
                        # Log event
                        event_log = TaskEventLog(
                            task_id=new_task.id,
                            event_type="recurring_task_created",
                            event_data={
                                "recurring_task_id": recurring_task.id,
                                "user_id": str(user.id),
                                "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                                "recurrence_pattern": recurring_task.recurrence_pattern
                            }
                        )
                        db.add(event_log)

                        # Send notification
                        await notification_service.send_recurring_task_notification(
                            user_email=user.email,
                            user_name=user.name,
                            task_title=new_task.title,
                            recurrence_pattern=recurring_task.recurrence_pattern,
                            next_due_date=new_task.due_date or date.today()
                        )

                        await db.commit()
                        created_count += 1

        except Exception as e:
            logger.error(f"Error in recurring processor: {e}")
            await db.rollback()

    return created_count


async def recurring_task_worker():
    """
    Run the recurring task processor worker.

    Checks for recurring tasks to process every interval.
    """
    logger.info("Starting recurring task processor worker...")
    logger.info(f"Processing recurring tasks every {settings.RECURRING_CHECK_INTERVAL_SECONDS} seconds")

    while True:
        try:
            created_count = await process_recurring_tasks()
            if created_count > 0:
                logger.info(f"Recurring processor cycle complete: {created_count} tasks created")
            else:
                logger.debug("Recurring processor cycle complete: no tasks to create")

        except Exception as e:
            logger.error(f"Recurring processor worker error: {e}", exc_info=True)

        await asyncio.sleep(settings.RECURRING_CHECK_INTERVAL_SECONDS)


async def run_recurring_processor_once():
    """
    Run the recurring processor once (for testing).

    Returns:
        Number of tasks created
    """
    return await process_recurring_tasks()
