"""Background job endpoints for scheduled tasks.

This module provides endpoints that can be called by cron jobs,
Dapr cron bindings, or external schedulers for periodic maintenance tasks.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.task_notification import (
    publish_due_soon_events,
    reset_notified_flag_after_due
)
from app.crud.recurring_task import get_due_recurring_tasks, advance_recurring_task
from app.crud.task import create_task
from app.schemas.task import TaskCreate
from app.models.recurring_task import RecurringTask

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/background", tags=["Background Jobs"])


@router.post("/check-due-tasks", status_code=200)
async def check_due_tasks(
    hours_threshold: Optional[int] = 24,
    db: AsyncSession = Depends(get_db)
):
    """
    Check for tasks due within the threshold and publish due-soon events.

    This endpoint is designed to be called by a cron job or Dapr cron binding
    on a periodic schedule (e.g., every hour).

    Query Parameters:
        hours_threshold: Hours within due date to trigger notification (default: 24)

    Returns:
        JSON with count of events published

    Example with curl:
        curl -X POST "http://localhost:8000/background/check-due-tasks?hours_threshold=24"
    """
    try:
        events_published = await publish_due_soon_events(db, hours_threshold)
        return {
            "status": "success",
            "events_published": events_published,
            "hours_threshold": hours_threshold
        }
    except Exception as e:
        logger.error(f"Error in check_due_tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check due tasks: {str(e)}"
        )


@router.post("/reset-notified-flags", status_code=200)
async def reset_notified_flags(
    db: AsyncSession = Depends(get_db)
):
    """
    Reset notified flags for overdue tasks.

    This allows tasks to be notified again if they remain overdue.
    Should be run daily.

    Returns:
        JSON with count of tasks updated

    Example with curl:
        curl -X POST "http://localhost:8000/background/reset-notified-flags"
    """
    try:
        tasks_reset = await reset_notified_flag_after_due(db)
        return {
            "status": "success",
            "tasks_reset": tasks_reset
        }
    except Exception as e:
        logger.error(f"Error in reset_notified_flags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset notified flags: {str(e)}"
        )


@router.post("/process-recurring-tasks", status_code=200)
async def process_recurring_tasks(
    db: AsyncSession = Depends(get_db)
):
    """
    Process recurring tasks that are due and create actual tasks.

    This endpoint should be called by a cron job or Dapr cron binding
    on a periodic schedule (e.g., every hour or daily).

    For each due recurring task:
    1. Creates a new task instance
    2. Advances the recurring task to its next due date

    Returns:
        JSON with count of tasks created

    Example with curl:
        curl -X POST "http://localhost:8000/background/process-recurring-tasks"
    """
    try:
        # Get all recurring tasks that are due
        due_recurring_tasks = await get_due_recurring_tasks(db)

        tasks_created = 0

        for recurring_task in due_recurring_tasks:
            try:
                # Create a new task from the recurring task
                task_data = TaskCreate(
                    title=recurring_task.title,
                    description=recurring_task.description,
                    priority_id=recurring_task.task_priority_id or 2,
                    due_date=recurring_task.next_due_at,
                    is_recurring=False,  # The created task is not itself recurring
                    recurrence_pattern=None
                )

                new_task = await create_task(
                    db=db,
                    task_data=task_data,
                    user_id=str(recurring_task.user_id)
                )

                # Link the task to its parent recurring task
                new_task.recurring_task_id = recurring_task.id
                await db.commit()

                # Advance the recurring task to its next due date
                await advance_recurring_task(db, recurring_task)

                tasks_created += 1
                logger.info(
                    f"Created task {new_task.id} from recurring task "
                    f"{recurring_task.id} ({recurring_task.title})"
                )

            except Exception as e:
                logger.error(
                    f"Failed to process recurring task {recurring_task.id}: {e}"
                )
                await db.rollback()

        logger.info(f"Processed {len(due_recurring_tasks)} due recurring tasks")

        return {
            "status": "success",
            "due_recurring_tasks_found": len(due_recurring_tasks),
            "tasks_created": tasks_created
        }

    except Exception as e:
        logger.error(f"Error in process_recurring_tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process recurring tasks: {str(e)}"
        )


@router.get("/health", status_code=200)
async def background_jobs_health():
    """
    Health check endpoint for background jobs.

    Returns:
        JSON with status of background jobs service

    Example with curl:
        curl "http://localhost:8000/background/health"
    """
    return {
        "status": "healthy",
        "service": "background-jobs",
        "endpoints": [
            "/background/check-due-tasks",
            "/background/reset-notified-flags",
            "/background/process-recurring-tasks"
        ]
    }
