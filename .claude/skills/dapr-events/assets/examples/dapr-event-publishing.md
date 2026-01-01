# Dapr Event-Driven Architecture - Evolution of TODO Edition

This guide documents the actual event publishing patterns used in the Evolution of TODO project.

## Event Publishing Pattern (Fire-and-Forget)

The project uses a fire-and-forget pattern for event publishing. Events are published after database operations succeed, but failures don't affect the main operation.

### Event Publisher Service

```python
# backend/app/services/event_publisher.py
import httpx
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DaprEventPublisher:
    """Dapr event publisher with fire-and-forget pattern."""

    def __init__(self):
        self.dapr_http_port = os.getenv("DAPR_HTTP_PORT", "3500")
        self.dapr_host = os.getenv("DAPR_HOST", "localhost")
        self.pubsub_name = os.getenv("DAPR_PUBSUB_NAME", "todo-pubsub")

    async def publish_task_created(self, event_data: Dict[str, Any]):
        """Publish task-created event."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://{self.dapr_host}:{self.dapr_http_port}/v1.0/publish/{self.pubsub_name}/task-created",
                    json=event_data,
                    timeout=5.0
                )
                if response.status_code == 200:
                    logger.info(f"Published task-created event: {event_data.get('task_id')}")
                else:
                    logger.warning(f"Failed to publish event: HTTP {response.status_code}")
        except Exception as e:
            # Log but don't raise - fire and forget
            logger.error(f"Failed to publish task-created event: {e}")

    async def publish_task_updated(self, event_data: Dict[str, Any]):
        """Publish task-updated event."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://{self.dapr_host}:{self.dapr_http_port}/v1.0/publish/{self.pubsub_name}/task-updated",
                    json=event_data,
                    timeout=5.0
                )
                if response.status_code == 200:
                    logger.info(f"Published task-updated event: {event_data.get('task_id')}")
        except Exception as e:
            logger.error(f"Failed to publish task-updated event: {e}")

    async def publish_task_completed(self, event_data: Dict[str, Any]):
        """Publish task-completed event."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://{self.dapr_host}:{self.dapr_http_port}/v1.0/publish/{self.pubsub_name}/task-completed",
                    json=event_data,
                    timeout=5.0
                )
                if response.status_code == 200:
                    logger.info(f"Published task-completed event: {event_data.get('task_id')}")
        except Exception as e:
            logger.error(f"Failed to publish task-completed event: {e}")

    async def publish_task_deleted(self, event_data: Dict[str, Any]):
        """Publish task-deleted event."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://{self.dapr_host}:{self.dapr_http_port}/v1.0/publish/{self.pubsub_name}/task-deleted",
                    json=event_data,
                    timeout=5.0
                )
                if response.status_code == 200:
                    logger.info(f"Published task-deleted event: {event_data.get('task_id')}")
        except Exception as e:
            logger.error(f"Failed to publish task-deleted event: {e}")


# Singleton instance
dapr_event_publisher = DaprEventPublisher()
```

## Using Event Publisher in CRUD

```python
# backend/app/crud/task.py
from app.services.event_publisher import dapr_event_publisher


async def create_task(db: AsyncSession, task_data: TaskCreate, user_id: str) -> Task:
    """Create a new task with event publishing."""
    db_task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description or "",
        priority_id=task_data.priority_id,
        due_date=task_data.due_date,
    )

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    # Re-fetch with eager loading
    stmt = select(Task).where(Task.id == db_task.id).options(selectinload(Task.priority_obj))
    result = await db.execute(stmt)
    task = result.scalar_one()

    # Publish task-created event (fire and forget)
    try:
        event_data = {
            "task_id": task.id,
            "user_id": user_id,
            "title": task.title,
            "priority_id": task.priority_id,
            "created_at": task.created_at.isoformat()
        }
        await dapr_event_publisher.publish_task_created(event_data)
    except Exception as e:
        logger.error(f"Failed to publish task-created event: {e}")

    return task


async def update_task(db: AsyncSession, task: Task, task_data: TaskUpdate) -> Task:
    """Update task with event publishing."""
    was_completed = task.completed

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.completed is not None:
        task.completed = task_data.completed

    await db.commit()
    await db.refresh(task)

    # Re-fetch with eager loading
    stmt = select(Task).where(Task.id == task.id).options(selectinload(Task.priority_obj))
    result = await db.execute(stmt)
    updated_task = result.scalar_one()

    # Publish appropriate event
    try:
        event_data = {
            "task_id": updated_task.id,
            "user_id": str(updated_task.user_id),
            "title": updated_task.title,
            "completed": updated_task.completed,
        }

        if not was_completed and updated_task.completed:
            await dapr_event_publisher.publish_task_completed(event_data)
        else:
            await dapr_event_publisher.publish_task_updated(event_data)
    except Exception as e:
        logger.error(f"Failed to publish task event: {e}")

    return updated_task
```

## Event Logger Service

Events are also logged to the database for audit trails and analytics.

```python
# backend/app/services/event_logger.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task_event_log import TaskEventLog
import logging

logger = logging.getLogger(__name__)


async def log_task_created(db: AsyncSession, task_id: int, event_data: dict):
    """Log task creation to database."""
    try:
        event_log = TaskEventLog(
            task_id=task_id,
            event_type="created",
            event_data=event_data
        )
        db.add(event_log)
        await db.flush()  # Don't commit, just flush
    except Exception as e:
        logger.warning(f"Event logging failed for created: {e}")


async def log_task_completed(db: AsyncSession, task_id: int, event_data: dict):
    """Log task completion to database."""
    try:
        event_log = TaskEventLog(
            task_id=task_id,
            event_type="completed",
            event_data=event_data
        )
        db.add(event_log)
        await db.flush()
    except Exception as e:
        logger.warning(f"Event logging failed for completed: {e}")


async def log_task_updated(db: AsyncSession, task_id: int, event_data: dict):
    """Log task update to database."""
    try:
        event_log = TaskEventLog(
            task_id=task_id,
            event_type="updated",
            event_data=event_data
        )
        db.add(event_log)
        await db.flush()
    except Exception as e:
        logger.warning(f"Event logging failed for updated: {e}")
```

## Event Data Model

```python
# backend/app/models/task_event_log.py
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlmodel import Field, SQLModel


class TaskEventLog(SQLModel, table=True):
    """Audit log for task events."""
    __tablename__ = "task_event_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(index=True)
    event_type: str = Field(index=True)  # created, updated, completed, deleted
    event_data: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

## Dapr Component Configuration

```yaml
# dapr/components/pubsub.yaml
apiVersion: dapr.io/v1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

Or for Kafka:

```yaml
# dapr/components/pubsub-kafka.yaml
apiVersion: dapr.io/v1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: consumerGroup
    value: "todo-group"
  - name: authRequired
    value: "false"
```

## Event Subscriber Service

```python
# backend/app/subscribers/email_subscriber.py
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)


def register_email_subscriber(app: FastAPI):
    """Register email notification subscriber."""

    @app.post("/dapr/subscribe")
    async def subscribe():
        """Dapr subscription endpoint."""
        return [
            {
                "pubsubname": "todo-pubsub",
                "topic": "task-created",
                "route": "events/task-created"
            },
            {
                "pubsubname": "todo-pubsub",
                "topic": "task-updated",
                "route": "events/task-updated"
            },
            {
                "pubsubname": "todo-pubsub",
                "topic": "task-completed",
                "route": "events/task-completed"
            },
            {
                "pubsubname": "todo-pubsub",
                "topic": "task-deleted",
                "route": "events/task-deleted"
            },
        ]

    @app.post("/events/task-created")
    async def handle_task_created(event_data: dict):
        """Handle task-created event."""
        logger.info(f"Task created: {event_data.get('task_id')}")
        # Send email notification
        # ...

    @app.post("/events/task-completed")
    async def handle_task_completed(event_data: dict):
        """Handle task-completed event."""
        logger.info(f"Task completed: {event_data.get('task_id')}")
        # Send email notification
        # ...
```

## Background Task Alternative (No Dapr)

For email notifications without Dapr, the project uses FastAPI's BackgroundTasks:

```python
# backend/app/api/tasks.py
from fastapi import BackgroundTasks


async def _send_email_notification(event_type: str, task_data: dict, user_email: str):
    """Send email notification in background."""
    try:
        from app.utils.email_notifier import send_task_created_email

        if event_type == "created":
            await send_task_created_email(user_email, task_data)
        # ...
    except Exception as e:
        print(f"Email sending failed: {e}")


@router.post("")
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create task with background email."""
    new_task = await task_crud.create_task(db, task_data, str(current_user.id))

    # Send email notification (fire and forget)
    background_tasks.add_task(
        _send_email_notification,
        "created",
        _task_to_dict(new_task),
        current_user.email
    )

    return new_task
```

## Key Patterns

### 1. Fire-and-Forget Publishing
- Don't let event publishing failures block the main operation
- Log errors but don't raise exceptions
- Use try/except around all publish calls

### 2. Event Data Structure
- Include all relevant data in the event
- Use ISO format for dates
- Include user_id for tenant isolation

### 3. Database Event Logging
- Log all events to database for audit trail
- Use flush() instead of commit() to avoid transaction issues
- Handle logging failures gracefully

### 4. Background Tasks Alternative
- Use FastAPI BackgroundTasks for simple async operations
- Good for email notifications, webhooks
- No need for full pub/sub infrastructure

### 5. Dapr Sidecar
- Dapr sidecar runs alongside your application
- HTTP port 3500 for Dapr API
- gRPC port 50001 for Dapr gRPC API
