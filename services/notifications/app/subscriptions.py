"""Dapr event subscription handlers for notification service."""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.task_event_log import TaskEventLog
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


async def log_task_event(
    task_id: int,
    event_type: str,
    event_data: Dict[str, Any]
) -> bool:
    """
    Log a task event to the database.

    Args:
        task_id: Task ID
        event_type: Event type (created, updated, completed, deleted)
        event_data: Event payload

    Returns:
        True if logged successfully
    """
    try:
        async with AsyncSessionLocal() as db:
            event_log = TaskEventLog(
                task_id=task_id,
                event_type=event_type,
                event_data=event_data
            )
            db.add(event_log)
            await db.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to log task event: {e}")
        return False


@router.post("/subscribe/task-created")
async def handle_task_created(request: Request):
    """
    Handle task-created event.

    Event payload:
        - task_id: int
        - user_id: str (UUID)
        - title: str
        - description: str
        - priority_id: int
        - due_date: Optional[str] (ISO format date)
        - completed: bool
        - is_recurring: bool
        - created_at: str (ISO format datetime)
    """
    try:
        data = await request.json()
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        title = data.get("title")

        logger.info(f"Task created event received: task_id={task_id}, user_id={user_id}, title={title}")

        # Log event to database
        if task_id:
            await log_task_event(task_id, "created", data)

        return {"status": "processed", "task_id": task_id}

    except Exception as e:
        logger.error(f"Error handling task-created event: {e}")
        raise HTTPException(status_code=500, detail="Failed to process event")


@router.post("/subscribe/task-updated")
async def handle_task_updated(request: Request):
    """
    Handle task-updated event.

    Event payload:
        - task_id: int
        - user_id: str (UUID)
        - title: str
        - description: str
        - priority_id: int
        - due_date: Optional[str] (ISO format date)
        - completed: bool
        - updated_at: str (ISO format datetime)
    """
    try:
        data = await request.json()
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        title = data.get("title")

        logger.info(f"Task updated event received: task_id={task_id}, user_id={user_id}, title={title}")

        # Log event to database
        if task_id:
            await log_task_event(task_id, "updated", data)

        return {"status": "processed", "task_id": task_id}

    except Exception as e:
        logger.error(f"Error handling task-updated event: {e}")
        raise HTTPException(status_code=500, detail="Failed to process event")


@router.post("/subscribe/task-completed")
async def handle_task_completed(request: Request):
    """
    Handle task-completed event.

    Event payload:
        - task_id: int
        - user_id: str (UUID)
        - completed: bool (always True)
        - completed_at: str (ISO format datetime)
    """
    try:
        data = await request.json()
        task_id = data.get("task_id")
        user_id = data.get("user_id")

        logger.info(f"Task completed event received: task_id={task_id}, user_id={user_id}")

        # Log event to database
        if task_id:
            await log_task_event(task_id, "completed", data)

        return {"status": "processed", "task_id": task_id}

    except Exception as e:
        logger.error(f"Error handling task-completed event: {e}")
        raise HTTPException(status_code=500, detail="Failed to process event")


@router.post("/subscribe/task-deleted")
async def handle_task_deleted(request: Request):
    """
    Handle task-deleted event.

    Event payload:
        - task_id: int
        - user_id: str (UUID)
        - deleted_at: str (ISO format datetime)
    """
    try:
        data = await request.json()
        task_id = data.get("task_id")
        user_id = data.get("user_id")

        logger.info(f"Task deleted event received: task_id={task_id}, user_id={user_id}")

        # Log event to database (task might be soft deleted)
        if task_id:
            await log_task_event(task_id, "deleted", data)

        return {"status": "processed", "task_id": task_id}

    except Exception as e:
        logger.error(f"Error handling task-deleted event: {e}")
        raise HTTPException(status_code=500, detail="Failed to process event")


@router.post("/subscribe/task-due-soon")
async def handle_task_due_soon(request: Request):
    """
    Handle task-due-soon event.

    This event is published by the due checker worker when it finds
    tasks due within the threshold. This endpoint can be used to
    trigger additional notifications or integrations.

    Event payload:
        - task_id: int
        - user_id: str (UUID)
        - title: str
        - due_date: str (ISO format date)
        - hours_until_due: int
    """
    try:
        data = await request.json()
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        title = data.get("title")
        hours_until_due = data.get("hours_until_due")

        logger.info(
            f"Task due soon event received: task_id={task_id}, title={title}, "
            f"hours_until_due={hours_until_due}"
        )

        # Log event to database
        if task_id:
            await log_task_event(task_id, "due_soon", data)

        # Additional processing can be added here (e.g., push notifications, webhooks)

        return {"status": "processed", "task_id": task_id}

    except Exception as e:
        logger.error(f"Error handling task-due-soon event: {e}")
        raise HTTPException(status_code=500, detail="Failed to process event")


@router.post("/subscribe/recurring-task-due")
async def handle_recurring_task_due(request: Request):
    """
    Handle recurring-task-due event.

    This event is published when a new task instance is created from
    a recurring task template.

    Event payload:
        - recurring_task_id: int
        - task_id: int
        - user_id: str (UUID)
        - title: str
        - next_due_at: str (ISO format date)
        - recurrence_pattern: str
    """
    try:
        data = await request.json()
        recurring_task_id = data.get("recurring_task_id")
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        title = data.get("title")

        logger.info(
            f"Recurring task due event received: recurring_task_id={recurring_task_id}, "
            f"task_id={task_id}, title={title}"
        )

        # Log event to database
        if task_id:
            await log_task_event(task_id, "recurring_task_created", data)

        return {"status": "processed", "task_id": task_id}

    except Exception as e:
        logger.error(f"Error handling recurring-task-due event: {e}")
        raise HTTPException(status_code=500, detail="Failed to process event")


@router.get("/health")
async def health_check():
    """Health check endpoint for Dapr subscription routes."""
    return {"status": "healthy", "service": "notification-subscriptions"}
