"""Dapr event subscribers for email notifications."""
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import Request
from dapr.ext.fastapi import DaprApp
from sqlalchemy.ext.asyncio import AsyncSession

from .email_service import email_service
from .database import get_db
from .crud import get_user_by_id, get_task_by_id

logger = logging.getLogger(__name__)


# Dapr app instance (will be initialized in main.py)
dapr_app = None


async def handle_task_due_event(event_data: Dict[str, Any]):
    """
    Handle task-due-soon events.

    Event data structure:
    {
        "task_id": "uuid",
        "user_id": "uuid",
        "title": "Task title",
        "due_date": "2025-12-27T10:00:00Z",
        "priority": "high",
        "description": "Task description",
        "category": "work"
    }
    """
    try:
        task_id = event_data.get("task_id")
        user_id = event_data.get("user_id")

        logger.info(f"Processing task-due-soon event for task {task_id}")

        # Get user email from database
        async for db in get_db():
            user = await get_user_by_id(db, user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return

            # Prepare email context
            due_date = event_data.get("due_date")
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))

            context = {
                "title": event_data.get("title", "Untitled Task"),
                "due_date": due_date.strftime("%B %d, %Y at %I:%M %p") if due_date else "N/A",
                "priority": event_data.get("priority", "medium").capitalize(),
                "description": event_data.get("description", ""),
                "category": event_data.get("category", "General"),
                "app_url": "https://hackathon2.testservers.online"
            }

            # Send email
            success = await email_service.send_template_email(
                template_name="task-due.html",
                subject=f"Task Due Soon: {event_data.get('title', 'Untitled Task')}",
                email=[user.email],
                context=context
            )

            if success:
                logger.info(f"Due date email sent to {user.email} for task {task_id}")
            else:
                logger.error(f"Failed to send due date email to {user.email}")

    except Exception as e:
        logger.error(f"Error processing task-due-soon event: {e}")


async def handle_recurring_task_event(event_data: Dict[str, Any]):
    """
    Handle recurring-task-due events.

    Event data structure:
    {
        "recurring_task_id": "uuid",
        "user_id": "uuid",
        "title": "Task title",
        "recurrence_type": "daily|weekly|monthly|yearly",
        "next_due_at": "2025-12-27T10:00:00Z",
        "end_date": "2025-12-31T23:59:59Z",
        "description": "Task description"
    }
    """
    try:
        recurring_task_id = event_data.get("recurring_task_id")
        user_id = event_data.get("user_id")

        logger.info(f"Processing recurring-task-due event for recurring task {recurring_task_id}")

        # Get user email from database
        async for db in get_db():
            user = await get_user_by_id(db, user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return

            # Prepare email context
            next_due_at = event_data.get("next_due_at")
            end_date = event_data.get("end_date")

            if isinstance(next_due_at, str):
                next_due_at = datetime.fromisoformat(next_due_at.replace("Z", "+00:00"))

            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

            context = {
                "title": event_data.get("title", "Untitled Recurring Task"),
                "recurrence_type": event_data.get("recurrence_type", "daily"),
                "next_due_date": next_due_at.strftime("%B %d, %Y at %I:%M %p") if next_due_at else "N/A",
                "end_date": end_date.strftime("%B %d, %Y") if end_date else None,
                "description": event_data.get("description", ""),
                "app_url": "https://hackathon2.testservers.online"
            }

            # Send email
            success = await email_service.send_template_email(
                template_name="recurring-task-due.html",
                subject=f"Recurring Task Due: {event_data.get('title', 'Untitled Task')}",
                email=[user.email],
                context=context
            )

            if success:
                logger.info(f"Recurring task email sent to {user.email} for task {recurring_task_id}")
            else:
                logger.error(f"Failed to send recurring task email to {user.email}")

    except Exception as e:
        logger.error(f"Error processing recurring-task-due event: {e}")


async def handle_task_created_event(event_data: Dict[str, Any]):
    """Handle task-created events."""
    try:
        task_id = event_data.get("task_id")
        user_id = event_data.get("user_id")
        title = event_data.get("title", "Untitled Task")

        logger.info(f"Processing task-created event for task {task_id}")

        async for db in get_db():
            user = await get_user_by_id(db, user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return

            context = {
                "title": title,
                "description": event_data.get("description", ""),
                "priority": event_data.get("priority", "medium").capitalize(),
                "due_date": event_data.get("due_date"),
                "app_url": "https://hackathon2.testservers.online",
                "action": "created"
            }

            success = await email_service.send_template_email(
                template_name="task-crud.html",
                subject=f"Task Created: {title}",
                email=[user.email],
                context=context
            )

            if success:
                logger.info(f"Task created email sent to {user.email}")
            else:
                logger.error(f"Failed to send task created email to {user.email}")

    except Exception as e:
        logger.error(f"Error processing task-created event: {e}")


async def handle_task_updated_event(event_data: Dict[str, Any]):
    """Handle task-updated events."""
    try:
        task_id = event_data.get("task_id")
        user_id = event_data.get("user_id")
        title = event_data.get("title", "Untitled Task")

        logger.info(f"Processing task-updated event for task {task_id}")

        async for db in get_db():
            user = await get_user_by_id(db, user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return

            context = {
                "title": title,
                "description": event_data.get("description", ""),
                "priority": event_data.get("priority", "medium").capitalize(),
                "due_date": event_data.get("due_date"),
                "completed": event_data.get("completed", False),
                "app_url": "https://hackathon2.testservers.online",
                "action": "updated"
            }

            success = await email_service.send_template_email(
                template_name="task-crud.html",
                subject=f"Task Updated: {title}",
                email=[user.email],
                context=context
            )

            if success:
                logger.info(f"Task updated email sent to {user.email}")
            else:
                logger.error(f"Failed to send task updated email to {user.email}")

    except Exception as e:
        logger.error(f"Error processing task-updated event: {e}")


async def handle_task_completed_event(event_data: Dict[str, Any]):
    """Handle task-completed events."""
    try:
        task_id = event_data.get("task_id")
        user_id = event_data.get("user_id")
        title = event_data.get("title", "Untitled Task")

        logger.info(f"Processing task-completed event for task {task_id}")

        async for db in get_db():
            user = await get_user_by_id(db, user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return

            context = {
                "title": title,
                "description": event_data.get("description", ""),
                "app_url": "https://hackathon2.testservers.online",
                "action": "completed"
            }

            success = await email_service.send_template_email(
                template_name="task-crud.html",
                subject=f"Task Completed: {title}",
                email=[user.email],
                context=context
            )

            if success:
                logger.info(f"Task completed email sent to {user.email}")
            else:
                logger.error(f"Failed to send task completed email to {user.email}")

    except Exception as e:
        logger.error(f"Error processing task-completed event: {e}")


async def handle_task_deleted_event(event_data: Dict[str, Any]):
    """Handle task-deleted events."""
    try:
        task_id = event_data.get("task_id")
        user_id = event_data.get("user_id")
        title = event_data.get("title", "Untitled Task")

        logger.info(f"Processing task-deleted event for task {task_id}")

        async for db in get_db():
            user = await get_user_by_id(db, user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return

            context = {
                "title": title,
                "app_url": "https://hackathon2.testservers.online",
                "action": "deleted"
            }

            success = await email_service.send_template_email(
                template_name="task-crud.html",
                subject=f"Task Deleted: {title}",
                email=[user.email],
                context=context
            )

            if success:
                logger.info(f"Task deleted email sent to {user.email}")
            else:
                logger.error(f"Failed to send task deleted email to {user.email}")

    except Exception as e:
        logger.error(f"Error processing task-deleted event: {e}")


def register_subscribers(app):
    """
    Register Dapr event subscribers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    global dapr_app
    dapr_app = DaprApp(app)

    # Subscribe to task-due-soon events
    @dapr_app.subscribe(pubsub="todo-pubsub", topic="task-due-soon")
    async def task_due_subscriber(event_data: Dict[str, Any]):
        """Dapr subscriber for task-due-soon events."""
        await handle_task_due_event(event_data)
        return {"status": "processed"}

    # Subscribe to recurring-task-due events
    @dapr_app.subscribe(pubsub="todo-pubsub", topic="recurring-task-due")
    async def recurring_task_subscriber(event_data: Dict[str, Any]):
        """Dapr subscriber for recurring-task-due events."""
        await handle_recurring_task_event(event_data)
        return {"status": "processed"}

    # Subscribe to task-created events
    @dapr_app.subscribe(pubsub="todo-pubsub", topic="task-created")
    async def task_created_subscriber(event_data: Dict[str, Any]):
        """Dapr subscriber for task-created events."""
        await handle_task_created_event(event_data)
        return {"status": "processed"}

    # Subscribe to task-updated events
    @dapr_app.subscribe(pubsub="todo-pubsub", topic="task-updated")
    async def task_updated_subscriber(event_data: Dict[str, Any]):
        """Dapr subscriber for task-updated events."""
        await handle_task_updated_event(event_data)
        return {"status": "processed"}

    # Subscribe to task-completed events
    @dapr_app.subscribe(pubsub="todo-pubsub", topic="task-completed")
    async def task_completed_subscriber(event_data: Dict[str, Any]):
        """Dapr subscriber for task-completed events."""
        await handle_task_completed_event(event_data)
        return {"status": "processed"}

    # Subscribe to task-deleted events
    @dapr_app.subscribe(pubsub="todo-pubsub", topic="task-deleted")
    async def task_deleted_subscriber(event_data: Dict[str, Any]):
        """Dapr subscriber for task-deleted events."""
        await handle_task_deleted_event(event_data)
        return {"status": "processed"}

    logger.info("Dapr event subscribers registered successfully")
