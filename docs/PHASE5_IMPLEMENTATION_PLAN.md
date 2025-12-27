# Implementation Plan: Phase V - Cloud Deployment with Event-Driven Architecture

**Spec**: `specs/005-cloud-deployment/spec.md`
**Phase**: V - Event-Driven Microservices
**Estimated Complexity**: Very Complex
**Timeline**: 10-14 days
**Current Cluster**: DigitalOcean Kubernetes (DOKS) - Frankfurt Region

---

## Executive Summary

Phase V transforms the Todo application into an event-driven microservices architecture deployed on DigitalOcean Kubernetes. The system leverages Dapr for event streaming, Redpanda (Kafka-compatible) for message brokering, and introduces a new notification service for handling due date reminders and recurring task processing.

**Success Criteria**:
- [ ] All services deployed on DOKS with 2+ replicas
- [ ] Event publishing/subscribing working via Dapr + Redpanda
- [ ] Notification service processing due tasks and recurring tasks
- [ ] CI/CD pipeline automatically deploying on push to main
- [ ] Prometheus + Grafana monitoring operational
- [ ] Event latency <100ms, notification delivery <5 seconds
- [ ] kubectl-ai and kagent tools integrated

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DigitalOcean Kubernetes (DOKS)                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    DigitalOcean Load Balancers (3x)                   │  │
│  │  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────────┐   │  │
│  │  │  Frontend LB   │  │   Backend LB    │  │  Notification LB     │   │  │
│  │  └────────┬───────┘  └────────┬────────┘  └──────────┬───────────┘   │  │
│  │           │                    │                       │             │  │
│  │  ┌────────▼────────┐  ┌───────▼──────────┐  ┌────────▼───────────┐  │  │
│  │  │ Frontend Pod    │  │  Backend Pod     │  │  Notification Pod   │  │  │
│  │  │ (Next.js 14)    │  │  (FastAPI)       │  │  (FastAPI Worker)   │  │  │
│  │  │ Port: 3000      │  │  Port: 8000      │  │  Port: 8001         │  │  │
│  │  │ + Dapr Sidecar  │  │  + Dapr Sidecar  │  │  + Dapr Sidecar     │  │  │
│  │  └─────────────────┘  └──────────────────┘  └─────────────────────┘  │  │
│  │                                                                        │  │
│  │  ┌────────────────────────────────────────────────────────────────┐   │  │
│  │  │                   Dapr Event Infrastructure                      │   │  │
│  │  │  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │   │  │
│  │  │  │   Redpanda     │  │ DO Managed      │  │ Neon PostgreSQL   │ │   │  │
│  │  │  │   Cluster      │  │ Redis (Valkey)  │  │ (External DB)     │ │   │  │
│  │  │  │ (3 Replicas)   │  │ (1GB)           │  │                   │ │   │  │
│  │  │  │ Kafka Topics:  │  │ State Store     │  │ Primary Data      │ │   │  │
│  │  │  │ task-created   │  │ Cache           │  │                   │ │   │  │
│  │  │  │ task-updated   │  └─────────────────┘  └──────────────────┘ │   │  │
│  │  │  │ task-completed │                                            │   │  │
│  │  │  │ task-deleted   │  ┌─────────────────┐  ┌──────────────────┐ │   │  │
│  │  │  │ task-due-soon  │  │ Prometheus      │  │ Grafana           │ │   │  │
│  │  │  │ recurring-task │  │ Metrics Store   │  │ Dashboards        │ │   │  │
│  │  │  └────────────────┘  └─────────────────┘  └──────────────────┘ │   │  │
│  │  └────────────────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘

Event Flow:
┌──────────┐         ┌──────────┐         ┌──────────────────┐
│ Backend  │ Publish │ Redpanda  │ Subscribe│ Notification     │
│          │-------->│ (Kafka)  │-------->│ Service          │
│          │         │          │         │ - Send reminders │
│          │         │          │         │ - Create tasks   │
└──────────┘         └──────────┘         └──────────────────┘
     │                    │
     | Publish            | Consume
     v                    v
┌──────────┐         ┌──────────┐
│ Events   │         │ Future   │
│          │         │ Services │
│ - task-  │         │ (Analytics,
│   created│         │  Audit,  │
│ - task-  │         │  etc.)   │
│   updated│         └──────────┘
│ - task-  │
│   completed
└──────────┘
```

### Component Responsibilities

**1. Frontend Service** (Next.js 14)
- Location: `frontend/`
- Responsibility: User interface for task management, recurring tasks, dashboard
- Dependencies: Backend API endpoints
- Key Files:
  - `frontend/app/recurring-tasks/page.tsx` - Recurring tasks management
  - `frontend/app/dashboard/page.tsx` - Dashboard with due date indicators
  - `frontend/lib/api.ts` - API client with JWT authentication
- Dapr Integration: None (frontend talks to backend directly)

**2. Backend Service** (FastAPI)
- Location: `backend/`
- Responsibility: REST API, event publishing, recurring task management
- Dependencies: PostgreSQL, Redpanda (via Dapr), Neon DB
- Key Files:
  - `backend/app/models/recurring_task.py` - Recurring task model
  - `backend/app/api/recurring_tasks.py` - Recurring task CRUD endpoints
  - `backend/app/services/event_publisher.py` - Dapr event publisher
  - `backend/app/api/tasks.py` - Updated with event publishing
- Dapr Integration: Publisher only (publishes events to Redpanda)

**3. Notification Service** (FastAPI - NEW)
- Location: `services/notifications/`
- Responsibility: Subscribe to events, process due tasks, handle recurring tasks, send notifications
- Dependencies: Redpanda (via Dapr), PostgreSQL
- Key Files:
  - `services/notifications/app/main.py` - FastAPI app
  - `services/notifications/app/subscribers.py` - Dapr event subscribers
  - `services/notifications/app/workers/due_date_checker.py` - Background worker
  - `services/notifications/app/workers/recurring_processor.py` - Recurring task worker
- Dapr Integration: Subscriber only (subscribes to Redpanda topics)

**4. Dapr Sidecars** (Auto-injected)
- Location: Each pod gets a Dapr sidecar container
- Responsibility: Event pub/sub abstraction, service-to-service communication
- Configuration: `k8s/dapr-components/pubsub-redpanda.yaml`, `statestore-redis.yaml`

**5. Redpanda Cluster** (Kafka-compatible)
- Location: `redpanda-system` namespace
- Responsibility: Message broker for event streaming
- Topics:
  - `task-created` - New task created
  - `task-updated` - Task modified
  - `task-completed` - Task marked complete
  - `task-deleted` - Task deleted
  - `task-due-soon` - Task due within 24 hours
  - `recurring-task-due` - Recurring task needs new occurrence

**6. Monitoring Stack**
- Prometheus: Metrics collection and storage
- Grafana: Visualization dashboards
- ServiceMonitors: Kubernetes service scraping

---

## Data Model

### New Tables

#### RecurringTask (`recurring_tasks`)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, Default=gen_random_uuid() | Unique identifier |
| user_id | UUID | FK→users.id, NOT NULL, Indexed | Owner of recurring task |
| title | String(500) | NOT NULL | Task title |
| description | Text | DEFAULT='' | Task description |
| priority_id | Integer | FK→priorities.id | Priority level |
| recurrence_type | String(20) | NOT NULL | daily, weekly, monthly, yearly |
| recurrence_interval | Integer | NOT NULL, DEFAULT=1 | Every N days/weeks/months |
| start_date | Date | NOT NULL | When to start generating tasks |
| end_date | Date | NULLABLE | When to stop (optional) |
| last_created_at | DateTime | NULLABLE | Last time a task was created |
| next_due_at | Date | NOT NULL, Indexed | Next occurrence date |
| is_active | Boolean | NOT NULL, DEFAULT=true | Active or paused |
| created_at | DateTime | NOT NULL, DEFAULT=now() | Creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT=now() | Last update timestamp |

**Indexes**:
- Primary: `id`
- Foreign: `user_id` (for user isolation queries)
- Composite: `(user_id, next_due_at)` (for finding due tasks)
- Composite: `(user_id, is_active)` (for listing active recurring tasks)

**Relationships**:
- Many-to-One: `RecurringTask` → `User`
- Many-to-One: `RecurringTask` → `Priority`
- One-to-Many: `RecurringTask` → `Task` (generated task instances)

#### TaskEventLog (`task_event_log`)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, Default=gen_random_uuid() | Unique identifier |
| task_id | Integer | FK→tasks.id, NOT NULL, Indexed | Related task |
| event_type | String(50) | NOT NULL | created, updated, completed, deleted, due |
| event_data | JSONB | NOT NULL | Event payload |
| created_at | DateTime | NOT NULL, DEFAULT=now() | Event timestamp |

**Indexes**:
- Primary: `id`
- Foreign: `task_id`
- Composite: `(task_id, created_at)` (for task event history)
- Composite: `(event_type, created_at)` (for analytics)

**Relationships**:
- Many-to-One: `TaskEventLog` → `Task`

### Existing Table Updates

#### Task (`tasks`) - Already Updated
Existing columns (already in database):
- `due_date` (Date, NULLABLE) - Task due date
- `is_recurring` (Boolean, DEFAULT=false) - Whether task is recurring
- `recurrence_pattern` (String(100), NULLABLE) - Legacy field (use RecurringTask instead)

New column to add:
- `notified` (Boolean, DEFAULT=false) - Whether due date notification sent
- `recurring_task_id` (UUID, NULLABLE, FK→recurring_tasks.id) - Parent recurring task

---

## API Design

### Recurring Tasks Endpoints

#### POST /api/recurring-tasks
Create a new recurring task.

```http
POST /api/recurring-tasks
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request Body:
{
  "title": "Weekly Team Meeting",
  "description": "Standup with the team every Monday",
  "priority_id": 2,
  "recurrence_type": "weekly",
  "recurrence_interval": 1,
  "start_date": "2025-01-06",
  "end_date": "2025-12-31"
}

Response 201 Created:
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Weekly Team Meeting",
  "description": "Standup with the team every Monday",
  "priority_id": 2,
  "recurrence_type": "weekly",
  "recurrence_interval": 1,
  "start_date": "2025-01-06",
  "end_date": "2025-12-31",
  "last_created_at": null,
  "next_due_at": "2025-01-06",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}

Errors:
  - 400: Validation error (invalid recurrence pattern)
  - 401: Unauthorized
```

#### GET /api/recurring-tasks
List all recurring tasks for current user.

```http
GET /api/recurring-tasks
Authorization: Bearer <jwt_token>

Query Parameters:
  - is_active: boolean (optional) - Filter by active status
  - sort_by: string (optional) - Sort field (next_due_at, created_at)
  - sort_order: string (optional) - asc or desc (default: asc)
  - limit: integer (optional) - Pagination limit (default: 20)
  - offset: integer (optional) - Pagination offset (default: 0)

Response 200 OK:
{
  "items": [
    {
      "id": "uuid",
      "title": "Weekly Team Meeting",
      "recurrence_type": "weekly",
      "next_due_at": "2025-01-06",
      "is_active": true
    }
  ],
  "total": 5,
  "limit": 20,
  "offset": 0
}
```

#### GET /api/recurring-tasks/{id}
Get recurring task details.

```http
GET /api/recurring-tasks/{id}
Authorization: Bearer <jwt_token>

Response 200 OK:
{
  "id": "uuid",
  "title": "Weekly Team Meeting",
  ...
}

Errors:
  - 404: Recurring task not found
```

#### PUT /api/recurring-tasks/{id}
Update recurring task.

```http
PUT /api/recurring-tasks/{id}
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request Body:
{
  "title": "Updated title",
  "end_date": "2025-06-30"
}

Response 200 OK:
{
  "id": "uuid",
  "title": "Updated title",
  ...
}

Errors:
  - 400: Validation error
  - 404: Not found
```

#### DELETE /api/recurring-tasks/{id}
Delete recurring task (does not delete generated task instances).

```http
DELETE /api/recurring-tasks/{id}
Authorization: Bearer <jwt_token>

Response 204 No Content

Errors:
  - 404: Not found
```

#### POST /api/recurring-tasks/{id}/pause
Pause recurring task (stop generating new instances).

```http
POST /api/recurring-tasks/{id}/pause
Authorization: Bearer <jwt_token>

Response 200 OK:
{
  "id": "uuid",
  "is_active": false
}
```

#### POST /api/recurring-tasks/{id}/resume
Resume recurring task.

```http
POST /api/recurring-tasks/{id}/resume
Authorization: Bearer <jwt_token>

Response 200 OK:
{
  "id": "uuid",
  "is_active": true
}
```

### Event Schema

All events published to Kafka have this structure:

```json
{
  "event_id": "uuid",
  "event_type": "task-created",
  "event_timestamp": "2025-01-01T00:00:00Z",
  "data": {
    "task_id": 123,
    "user_id": "uuid",
    "title": "Task title",
    "due_date": "2025-01-15",
    ...
  }
}
```

Event Types:
- `task-created` - New task created
- `task-updated` - Task modified
- `task-completed` - Task marked complete
- `task-deleted` - Task deleted
- `task-due-soon` - Task due within 24 hours (published by notification worker)
- `recurring-task-due` - Recurring task needs new occurrence (published by notification worker)

---

## Implementation Tasks

### Task 1: Database Schema & Migration
**Complexity**: Simple
**Dependencies**: None

**Acceptance Criteria**:
- [ ] SQLModel class created: `backend/app/models/recurring_task.py`
- [ ] SQLModel class created: `backend/app/models/task_event_log.py`
- [ ] Update Task model: Add `notified`, `recurring_task_id` columns
- [ ] All fields, constraints, and relationships defined
- [ ] Indexes created for performance
- [ ] Alembic migration generated: `alembic revision --autogenerate -m "add_recurring_tasks_and_event_log"`
- [ ] Migration tested locally: `alembic upgrade head`
- [ ] Migration tested rollback: `alembic downgrade -1`

**Files**:
- `backend/app/models/recurring_task.py`
- `backend/app/models/task_event_log.py`
- `backend/app/models/task.py` (updated)
- `backend/alembic/versions/XXX_add_recurring_tasks_and_event_log.py`

**Implementation Notes**:
```python
# backend/app/models/recurring_task.py
from datetime import date, datetime
from sqlalchemy import Column, String, Boolean, Integer, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class RecurringTask(Base):
    __tablename__ = "recurring_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(String, default="", nullable=False)
    priority_id = Column(Integer, ForeignKey("priorities.id"), nullable=True)
    recurrence_type = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    recurrence_interval = Column(Integer, nullable=False, default=1)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    last_created_at = Column(DateTime, nullable=True)
    next_due_at = Column(Date, nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="recurring_tasks")
    priority_obj = relationship("Priority")
    task_instances = relationship("Task", back_populates="recurring_task")
```

---

### Task 2: Recurring Task Pydantic Schemas
**Complexity**: Simple
**Dependencies**: Task 1

**Acceptance Criteria**:
- [ ] Request schemas created (Create, Update)
- [ ] Response schemas created (Single, List)
- [ ] Validation rules match spec requirements
- [ ] Type hints on all fields

**Files**:
- `backend/app/schemas/recurring_task.py`

**Implementation Notes**:
```python
# backend/app/schemas/recurring_task.py
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from uuid import UUID

class RecurringTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(default="", max_length=2000)
    priority_id: Optional[int] = Field(default=2)
    recurrence_type: str = Field(..., pattern="^(daily|weekly|monthly|yearly)$")
    recurrence_interval: int = Field(..., ge=1, le=52)
    start_date: date
    end_date: Optional[date] = None

class RecurringTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    priority_id: Optional[int] = None
    end_date: Optional[date] = None

class RecurringTaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: str
    priority_id: Optional[int]
    recurrence_type: str
    recurrence_interval: int
    start_date: date
    end_date: Optional[date]
    last_created_at: Optional[datetime]
    next_due_at: date
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

### Task 3: Recurring Task CRUD Operations
**Complexity**: Moderate
**Dependencies**: Task 1

**Acceptance Criteria**:
- [ ] CRUD functions created: `backend/app/crud/recurring_task.py`
- [ ] `calculate_next_due_at()` function implements recurrence logic
- [ ] `create_recurring_task()` calculates initial next_due_at
- [ ] `get_due_recurring_tasks()` queries by next_due_at
- [ ] All functions use async/await
- [ ] User isolation enforced (user_id filtering)

**Files**:
- `backend/app/crud/recurring_task.py`

**Implementation Notes**:
```python
# backend/app/crud/recurring_task.py
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.recurring_task import RecurringTask

def calculate_next_due_at(
    current_due_at: date,
    recurrence_type: str,
    recurrence_interval: int = 1
) -> date:
    """Calculate next occurrence based on recurrence pattern."""
    if recurrence_type == "daily":
        return current_due_at + timedelta(days=recurrence_interval)
    elif recurrence_type == "weekly":
        return current_due_at + timedelta(weeks=recurrence_interval)
    elif recurrence_type == "monthly":
        # Add months (handle year rollover)
        year = current_due_at.year + (current_due_at.month + recurrence_interval - 1) // 12
        month = (current_due_at.month + recurrence_interval - 1) % 12 + 1
        return date(year, month, min(current_due_at.day, [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]))
    elif recurrence_type == "yearly":
        return date(current_due_at.year + recurrence_interval, current_due_at.month, current_due_at.day)
    raise ValueError(f"Invalid recurrence_type: {recurrence_type}")

async def create_recurring_task(
    db: AsyncSession,
    user_id: str,
    task_data: RecurringTaskCreate
) -> RecurringTask:
    """Create recurring task with calculated next_due_at."""
    db_task = RecurringTask(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        priority_id=task_data.priority_id,
        recurrence_type=task_data.recurrence_type,
        recurrence_interval=task_data.recurrence_interval,
        start_date=task_data.start_date,
        end_date=task_data.end_date,
        next_due_at=task_data.start_date  # First occurrence is start_date
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def get_due_recurring_tasks(
    db: AsyncSession,
    due_date: date
) -> list[RecurringTask]:
    """Get all recurring tasks due on or before given date."""
    result = await db.execute(
        select(RecurringTask).where(
            RecurringTask.is_active == True,
            RecurringTask.next_due_at <= due_date
        )
    )
    return result.scalars().all()
```

---

### Task 4: Recurring Tasks API Endpoints
**Complexity**: Moderate
**Dependencies**: Task 2, Task 3

**Acceptance Criteria**:
- [ ] All 7 endpoints implemented (CRUD + pause/resume)
- [ ] JWT authentication on all endpoints
- [ ] User_id validation (can only access own recurring tasks)
- [ ] Pagination on list endpoint
- [ ] Error handling with proper status codes
- [ ] Registered in `backend/app/main.py`

**Files**:
- `backend/app/api/recurring_tasks.py`

---

### Task 5: Dapr Event Publisher
**Complexity**: Moderate
**Dependencies**: None (can be done in parallel)

**Acceptance Criteria**:
- [ ] `dapr` added to requirements.txt
- [ ] Event publisher created: `backend/app/services/event_publisher.py`
- [ ] Functions for each event type (created, updated, completed, deleted)
- [ ] Error handling (log failures, don't break main flow)
- [ ] Event schema validation

**Files**:
- `backend/app/requirements.txt` (add dapr>=1.12.0)
- `backend/app/services/event_publisher.py`

**Implementation Notes**:
```python
# backend/app/services/event_publisher.py
import json
from typing import Dict, Any
from dapr.clients import DaprClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EventPublisher:
    """Publishes events to Dapr pub/sub."""

    def __init__(self):
        self.dapr_client = DaprClient()

    async def publish_task_created(self, task_data: Dict[str, Any]):
        """Publish task-created event."""
        await self._publish("task-created", task_data)

    async def publish_task_updated(self, task_data: Dict[str, Any]):
        """Publish task-updated event."""
        await self._publish("task-updated", task_data)

    async def publish_task_completed(self, task_data: Dict[str, Any]):
        """Publish task-completed event."""
        await self._publish("task-completed", task_data)

    async def publish_task_deleted(self, task_data: Dict[str, Any]):
        """Publish task-deleted event."""
        await self._publish("task-deleted", task_data)

    async def _publish(self, topic: str, data: Dict[str, Any]):
        """Internal publish method."""
        try:
            event = {
                "event_id": str(uuid.uuid4()),
                "event_type": topic,
                "event_timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            await self.dapr_client.publish_event(
                pubsub_name="todo-pubsub",
                topic_name=topic,
                data=json.dumps(event),
                data_content_type="application/json"
            )
            logger.info(f"Published event {topic} for task {data.get('task_id')}")
        except Exception as e:
            logger.error(f"Failed to publish event {topic}: {e}")
            # Don't raise - events are best-effort
```

---

### Task 6: Integrate Event Publishing into Task Endpoints
**Complexity**: Simple
**Dependencies**: Task 5

**Acceptance Criteria**:
- [ ] Task creation publishes `task-created` event
- [ ] Task update publishes `task-updated` event
- [ ] Task completion publishes `task-completed` event
- [ ] Task deletion publishes `task-deleted` event
- [ ] Events include all relevant task data

**Files**:
- `backend/app/api/tasks.py` (updated)

**Implementation Notes**:
```python
# In create_task function
from app.services.event_publisher import EventPublisher

event_publisher = EventPublisher()

@router.post("")
async def create_task(...):
    new_task = await task_crud.create_task(db, task_data, str(current_user.id))

    # Publish event (non-blocking, best-effort)
    await event_publisher.publish_task_created({
        "task_id": new_task.id,
        "user_id": str(current_user.id),
        "title": new_task.title,
        "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
        "is_recurring": new_task.is_recurring,
        "created_at": new_task.created_at.isoformat()
    })

    return new_task
```

---

### Task 7: Notification Service - Main Application
**Complexity**: Moderate
**Dependencies**: None

**Acceptance Criteria**:
- [ ] FastAPI app created: `services/notifications/app/main.py`
- [ ] Health check endpoint: GET /health
- [ ] Database connection configured (use Neon)
- [ ] Dapr subscriber endpoints configured
- [ ] Dockerfile created
- [ ] requirements.txt includes dapr, fastapi, uvicorn, sqlalchemy

**Files**:
- `services/notifications/app/main.py`
- `services/notifications/Dockerfile`
- `services/notifications/requirements.txt`

**Implementation Notes**:
```python
# services/notifications/app/main.py
from fastapi import FastAPI, BackgroundTasks
from dapr.ext.fastapi import DaprApp
from app.subscribers import handle_task_event
from app.workers.due_date_checker import check_due_tasks
from app.workers.recurring_processor import process_recurring_tasks

app = FastAPI(title="Todo Notification Service")
dapr_app = DaprApp(app)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Dapr subscriber for all task events
@dapr_app.subscribe(pubsub="todo-pubsub", topic="task-created")
def subscribe_task_created(event_data: dict):
    """Handle task-created event."""
    handle_task_event("task-created", event_data)

@dapr_app.subscribe(pubsub="todo-pubsub", topic="task-completed")
def subscribe_task_completed(event_data: dict):
    """Handle task-completed event."""
    handle_task_event("task-completed", event_data)

# Background task endpoints
@app.post("/workers/check-due-tasks")
async def trigger_due_task_check(background_tasks: BackgroundTasks):
    """Trigger due date checker (called by cron/scheduler)."""
    background_tasks.add_task(check_due_tasks)
    return {"status": "scheduled"}

@app.post("/workers/process-recurring")
async def trigger_recurring_processing(background_tasks: BackgroundTasks):
    """Trigger recurring task processor (called by cron/scheduler)."""
    background_tasks.add_task(process_recurring_tasks)
    return {"status": "scheduled"}
```

---

### Task 8: Notification Service - Due Date Checker
**Complexity**: Moderate
**Dependencies**: Task 7

**Acceptance Criteria**:
- [ ] Due date checker created: `services/notifications/app/workers/due_date_checker.py`
- [ ] Queries tasks due within 24 hours
- [ ] Sends notification for each due task
- [ ] Marks task as notified (to avoid duplicates)
- [ ] Publishes `task-due-soon` event

**Files**:
- `services/notifications/app/workers/due_date_checker.py`

**Implementation Notes**:
```python
# services/notifications/app/workers/due_date_checker.py
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from dapr.clients import DaprClient

async def check_due_tasks():
    """Check for tasks due within 24 hours and send notifications."""
    tomorrow = datetime.utcnow() + timedelta(days=1)

    async for db in get_db():
        # Get tasks due within 24h that haven't been notified
        result = await db.execute(
            select(Task).where(
                Task.due_date <= tomorrow,
                Task.notified == False,
                Task.completed == False
            )
        )
        tasks = result.scalars().all()

        for task in tasks:
            # Send notification (console for demo)
            print(f"NOTIFICATION: Task '{task.title}' is due on {task.due_date}")
            # TODO: Send email/push notification

            # Mark as notified
            task.notified = True
            await db.commit()

            # Publish task-due-soon event
            async with DaprClient() as dapr:
                await dapr.publish_event(
                    pubsub_name="todo-pubsub",
                    topic_name="task-due-soon",
                    data={"task_id": task.id, "user_id": str(task.user_id)}
                )
```

---

### Task 9: Notification Service - Recurring Task Processor
**Complexity**: Complex
**Dependencies**: Task 7, Task 3

**Acceptance Criteria**:
- [ ] Recurring processor created: `services/notifications/app/workers/recurring_processor.py`
- [ ] Finds recurring tasks where next_due_at <= today
- [ ] Creates new task instance for each
- [ ] Updates recurring task's next_due_at
- [ ] Handles end_date (stops if reached)
- [ ] Publishes `recurring-task-due` event

**Files**:
- `services/notifications/app/workers/recurring_processor.py`

**Implementation Notes**:
```python
# services/notifications/app/workers/recurring_processor.py
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.recurring_task import RecurringTask
from app.models.task import Task
from app.crud.recurring_task import calculate_next_due_at

async def process_recurring_tasks():
    """Process recurring tasks and create new occurrences."""
    today = date.today()

    async for db in get_db():
        # Get recurring tasks due today
        result = await db.execute(
            select(RecurringTask).where(
                RecurringTask.is_active == True,
                RecurringTask.next_due_at <= today
            )
        )
        recurring_tasks = result.scalars().all()

        for recurring in recurring_tasks:
            # Check if end_date reached
            if recurring.end_date and recurring.next_due_at > recurring.end_date:
                recurring.is_active = False
                await db.commit()
                continue

            # Create new task instance
            new_task = Task(
                user_id=recurring.user_id,
                title=recurring.title,
                description=recurring.description,
                priority_id=recurring.priority_id,
                due_date=recurring.next_due_at,
                recurring_task_id=recurring.id,
                is_recurring=True
            )
            db.add(new_task)

            # Calculate next due date
            next_due = calculate_next_due_at(
                recurring.next_due_at,
                recurring.recurrence_type,
                recurring.recurrence_interval
            )

            # Update recurring task
            recurring.last_created_at = datetime.utcnow()
            recurring.next_due_at = next_due

            # Deactivate if end_date reached after this
            if recurring.end_date and next_due > recurring.end_date:
                recurring.is_active = False

            await db.commit()

            # Publish event
            await publish_recurring_task_due(recurring.id, new_task.id)
```

---

### Task 10: Notification Service Helm Chart
**Complexity**: Moderate
**Dependencies**: Task 7

**Acceptance Criteria**:
- [ ] Helm chart created: `helm/notifications/`
- [ ] Chart.yaml, values.yaml created
- [ ] Deployment template with Dapr annotations
- [ ] Service template (ClusterIP)
- [ ] HPA template (optional)
- [ ] Tested locally with `helm template`

**Files**:
- `helm/notifications/Chart.yaml`
- `helm/notifications/values.yaml`
- `helm/notifications/templates/deployment.yaml`
- `helm/notifications/templates/service.yaml`

**Implementation Notes**:
```yaml
# helm/notifications/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "notifications.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ include "notifications.name" . }}
  template:
    metadata:
      labels:
        app: {{ include "notifications.name" . }}
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-notifications"
        dapr.io/app-port: "8001"
        dapr.io/config: "todo-app-config"
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - containerPort: 8001
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: database-url
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
```

---

### Task 11: CI/CD Pipeline - GitHub Actions
**Complexity**: Moderate
**Dependencies**: None

**Acceptance Criteria**:
- [ ] Workflow created: `.github/workflows/deploy.yml`
- [ ] Build stage: Build Docker images for backend, frontend, notifications
- [ ] Test stage: Run pytest tests
- [ ] Push stage: Push images to DO registry
- [ ] Deploy stage: Helm upgrade for all services
- [ ] Health check stage: Verify pods are ready
- [ ] Secrets configured in GitHub

**Files**:
- `.github/workflows/deploy.yml`

**Implementation Notes**:
```yaml
# .github/workflows/deploy.yml
name: Build and Deploy to DOKS

on:
  push:
    branches: [main]

env:
  REGISTRY: registry.digitalocean.com/todo-chatbot-reg
  BACKEND_IMAGE: todo-backend
  FRONTEND_IMAGE: todo-frontend
  NOTIFICATIONS_IMAGE: todo-notifications

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Build Backend Image
        run: |
          docker build -t $REGISTRY/$BACKEND_IMAGE:${{ github.sha }} ./backend
          docker tag $REGISTRY/$BACKEND_IMAGE:${{ github.sha }} $REGISTRY/$BACKEND_IMAGE:latest

      - name: Build Frontend Image
        run: |
          docker build -t $REGISTRY/$FRONTEND_IMAGE:${{ github.sha }} ./frontend
          docker tag $REGISTRY/$FRONTEND_IMAGE:${{ github.sha }} $REGISTRY/$FRONTEND_IMAGE:latest

      - name: Build Notifications Image
        run: |
          docker build -t $REGISTRY/$NOTIFICATIONS_IMAGE:${{ github.sha }} ./services/notifications
          docker tag $REGISTRY/$NOTIFICATIONS_IMAGE:${{ github.sha }} $REGISTRY/$NOTIFICATIONS_IMAGE:latest

      - name: Login to DO Registry
        run: docker login -u ${{ secrets.DO_REGISTRY_USERNAME }} -p ${{ secrets.DO_REGISTRY_PASSWORD }} $REGISTRY

      - name: Push Images
        run: |
          docker push $REGISTRY/$BACKEND_IMAGE:latest
          docker push $REGISTRY/$FRONTEND_IMAGE:latest
          docker push $REGISTRY/$NOTIFICATIONS_IMAGE:latest

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Save Kubeconfig
        run: doctl kubernetes cluster kubeconfig save <cluster-name>

      - name: Deploy Backend
        run: |
          helm upgrade --install backend helm/backend \
            --namespace production \
            --set image.repository=$REGISTRY/$BACKEND_IMAGE \
            --set image.tag=latest

      - name: Deploy Frontend
        run: |
          helm upgrade --install frontend helm/frontend \
            --namespace production \
            --set image.repository=$REGISTRY/$FRONTEND_IMAGE \
            --set image.tag=latest

      - name: Deploy Notifications
        run: |
          helm upgrade --install notifications helm/notifications \
            --namespace production \
            --set image.repository=$REGISTRY/$NOTIFICATIONS_IMAGE \
            --set image.tag=latest

      - name: Verify Deployment
        run: |
          kubectl rollout status deployment/backend -n production --timeout=5m
          kubectl rollout status deployment/frontend -n production --timeout=5m
          kubectl rollout status deployment/notifications -n production --timeout=5m
```

---

### Task 12: Prometheus + Grafana Installation
**Complexity**: Simple
**Dependencies**: None

**Acceptance Criteria**:
- [ ] kube-prometheus-stack Helm chart installed
- [ ] Prometheus scraping Kubernetes pods
- [ ] Grafana accessible via port-forward
- [ ] ServiceMonitors created for backend, frontend, notifications
- [ ] Dashboards imported (Kubernetes cluster, Dapr metrics, application)

**Commands**:
```bash
# Install kube-prometheus-stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

# Create ServiceMonitors
kubectl apply -f k8s/monitoring/servicemonitors.yaml

# Access Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
# Default credentials: admin / prom-operator
```

**Files**:
- `k8s/monitoring/servicemonitors.yaml`
- `k8s/monitoring/grafana-dashboards/`

---

### Task 13: kubectl-ai Installation
**Complexity**: Simple
**Dependencies**: None

**Acceptance Criteria**:
- [ ] krew installed (kubectl plugin manager)
- [ ] kubectl-ai plugin installed
- [ ] Tested with basic kubectl ai commands
- [ ] API key configured

**Commands**:
```bash
# Install krew (kubectl plugin manager)
# Linux/macOS
(
  set -x; cd "$(mktemp -d)" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/krew-linux_amd64.tar.gz" &&
  tar zxvf krew-linux_amd64.tar.gz &&
  ./krew-linux_amd64 install krew
)

# Add krew to PATH
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

# Install kubectl-ai
kubectl krew install ai

# Test
kubectl ai get pods --help
```

---

### Task 14: kagent Installation
**Complexity**: Simple
**Dependencies**: None

**Acceptance Criteria**:
- [ ] kagent CLI installed via npm
- [ ] Initialized for cluster
- [ ] Tested with basic commands
- [ ] API key configured

**Commands**:
```bash
# Install kagent
npm install -g @kagent/cli

# Initialize
kagent init --provider digitalocean

# Configure
kagent config set api-key YOUR_API_KEY

# Test
kagent cluster status
```

---

### Task 15: End-to-End Testing
**Complexity**: Complex
**Dependencies**: All previous tasks

**Acceptance Criteria**:
- [ ] Create recurring task via API
- [ ] Verify recurring task in database
- [ ] Wait for next_due_at, verify task instance created
- [ ] Create task with due date tomorrow
- [ ] Run due date checker
- [ ] Verify notification sent
- [ ] Create task via API, verify Kafka event published
- [ ] Verify event received by notification service
- [ ] Test CI/CD pipeline (push to main)
- [ ] Verify all services deployed
- [ ] Check Grafana metrics

**Files**:
- `tests/test_e2e_event_flow.py`
- `tests/test_e2e_recurring_tasks.py`
- `tests/test_e2e_cicd.py`

---

## Testing Strategy

### Unit Tests

**Backend** (`backend/tests/`):
- `test_recurring_task_crud.py` - Test CRUD operations
- `test_event_publisher.py` - Test event publishing (mock Dapr)
- `test_recurrence_calculator.py` - Test date calculation logic

**Notification Service** (`services/notifications/tests/`):
- `test_due_date_checker.py` - Test due task logic
- `test_recurring_processor.py` - Test recurrence logic

### Integration Tests

**Event Flow** (`tests/integration/`):
- `test_event_publishing.py` - Test backend publishes events
- `test_event_subscription.py` - Test notification service receives events
- `test_dapr_integration.py` - Test Dapr pub/sub functionality

### End-to-End Tests

**Complete Workflows** (`tests/e2e/`):
- `test_recurring_task_lifecycle.py` - Create recurring task, verify instances created
- `test_due_date_notification.py` - Create due task, verify notification sent
- `test_cicd_deployment.py` - Push code, verify deployment

---

## Risks & Mitigations

### Risk 1: Dapr Sidecar Connection Issues
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Test Dapr locally first: `dapr run ...`
- Verify Dapr sidecar injected: `kubectl get pods -n production` (should see 2/2 containers)
- Check Dapr logs: `kubectl logs <pod> -c daprd`
- Use Dapr dashboard for debugging

### Risk 2: Kafka Event Loss
**Probability**: Low
**Impact**: Medium
**Mitigation**:
- Use replication factor of 3 for topics
- Configure Dapr for at-least-once delivery
- Implement event replay mechanism (if needed)
- Monitor Kafka lag: `kubectl exec -n redpanda-system redpanda-0 -- rpk topic describe task-created`

### Risk 3: Recurring Task Race Conditions
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Use database transactions when creating task instances
- Lock recurring task rows during processing
- Implement idempotency (check if task already created for this date)
- Run only one instance of recurring processor

### Risk 4: CI/CD Deployment Failures
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Test Helm charts locally first
- Use separate staging environment
- Implement rolling deployments (zero downtime)
- Add rollback step in CI/CD
- Monitor deployment health checks

### Risk 5: Cost Overruns
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Set up billing alerts in DigitalOcean
- Use auto-scaling (min 2 nodes during development)
- Delete cluster when not in use
- Monitor resource usage via Grafana
- Consider using smaller nodes for development

---

## Success Metrics

**Functional**:
- [ ] All API endpoints working (recurring tasks CRUD)
- [ ] Event publishing/subscribing functional
- [ ] Notification service processes due tasks
- [ ] Recurring tasks create new instances automatically
- [ ] CI/CD deploys on push to main
- [ ] kubectl-ai and kagent working

**Non-Functional**:
- [ ] Event latency <100ms (p95)
- [ ] Notification delivery within 5 seconds
- [ ] API response time <500ms
- [ ] All services have 2+ replicas
- [ ] Uptime >99%
- [ ] Zero data loss in Kafka topics

**Testing**:
- [ ] Unit tests: 80%+ coverage
- [ ] Integration tests: All passing
- [ ] E2E tests: All passing
- [ ] Load tests: Handle 100 req/s

---

## Rollback Plan

### If Deployment Fails:
1. **Helm Rollback**: `helm rollback <release> -n production`
2. **Check Logs**: `kubectl logs <pod> -n production`
3. **Fix Issue**, then redeploy
4. **Monitor Health**: `kubectl get pods -n production -w`

### If Database Migration Fails:
1. **Rollback Migration**: `alembic downgrade -1`
2. **Fix Migration Script**
3. **Test Locally**
4. **Reapply**: `alembic upgrade head`

### If Kafka Events Fail:
1. **Check Redpanda Status**: `kubectl get pods -n redpanda-system`
2. **Check Topics**: `kubectl exec -n redpanda-system redpanda-0 -- rpk topic list`
3. **Check Dapr Components**: `kubectl get components -n production`
4. **Restart Services** if needed

### If CI/CD Pipeline Fails:
1. **Check GitHub Actions Logs**
2. **Fix Issue** in code
3. **Push Fix** to trigger new run
4. **Manual Deploy** if CI/CD blocked

**Safe Rollback Window**: 24 hours after deployment

---

## Dependencies

**External Services**:
- Neon PostgreSQL (database)
- DigitalOcean (Kubernetes, Load Balancers, Container Registry)
- Redpanda (Kafka-compatible)
- Groq API (AI features)

**Internal Dependencies**:
- User authentication (existing)
- Task CRUD operations (existing)
- Database connection pooling (existing)

**Blocking Dependencies**:
- DOKS cluster must be running
- Redpanda must be installed and topics created
- Dapr must be installed on cluster
- Container registry must be configured

---

## Execution Order

### Phase 1: Database Layer (Day 1)
1. Task 1: Database Schema & Migration
2. Task 2: Recurring Task Pydantic Schemas
3. Task 3: Recurring Task CRUD Operations
4. Task 4: Recurring Tasks API Endpoints

### Phase 2: Event Layer (Day 2-3)
5. Task 5: Dapr Event Publisher
6. Task 6: Integrate Event Publishing into Task Endpoints

### Phase 3: Notification Service (Day 3-4)
7. Task 7: Notification Service - Main Application
8. Task 8: Notification Service - Due Date Checker
9. Task 9: Notification Service - Recurring Task Processor
10. Task 10: Notification Service Helm Chart

### Phase 4: Deployment Automation (Day 5)
11. Task 11: CI/CD Pipeline - GitHub Actions

### Phase 5: Monitoring & Tools (Day 6)
12. Task 12: Prometheus + Grafana Installation
13. Task 13: kubectl-ai Installation
14. Task 14: kagent Installation

### Phase 6: Testing & Validation (Day 7)
15. Task 15: End-to-End Testing

**Critical Path**: Tasks 1-4-7-8-9-10-11-15 (must be sequential)
**Parallel Tasks**: Tasks 5-6 (can run in parallel with 7-10), Tasks 12-13-14 (can run in parallel with 11)

---

## Post-Implementation

After completing all tasks:
1. **Deploy to Staging**: Test in staging namespace first
2. **Load Testing**: Test with 1000+ tasks, 100+ recurring tasks
3. **User Acceptance Testing**: Get feedback from real users
4. **Performance Tuning**: Optimize based on metrics
5. **Documentation**: Update README, API docs, runbooks
6. **Create PHR**: Document implementation process
7. **Retrospective**: What went well? What to improve?

---

## Appendix: Quick Reference Commands

### Build & Push Images
```bash
# Backend
docker build -t registry.digitalocean.com/todo-chatbot-reg/todo-backend:latest ./backend
docker push registry.digitalocean.com/todo-chatbot-reg/todo-backend:latest

# Frontend
docker build -t registry.digitalocean.com/todo-chatbot-reg/todo-frontend:latest ./frontend
docker push registry.digitalocean.com/todo-chatbot-reg/todo-frontend:latest

# Notifications
docker build -t registry.digitalocean.com/todo-chatbot-reg/todo-notifications:latest ./services/notifications
docker push registry.digitalocean.com/todo-chatbot-reg/todo-notifications:latest
```

### Deploy to DOKS
```bash
# Backend
helm upgrade --install backend helm/backend \
  --namespace production \
  --set image.repository=registry.digitalocean.com/todo-chatbot-reg/todo-backend \
  --set image.tag=latest

# Frontend
helm upgrade --install frontend helm/frontend \
  --namespace production \
  --set image.repository=registry.digitalocean.com/todo-chatbot-reg/todo-frontend \
  --set image.tag=latest

# Notifications
helm upgrade --install notifications helm/notifications \
  --namespace production \
  --set image.repository=registry.digitalocean.com/todo-chatbot-reg/todo-notifications \
  --set image.tag=latest
```

### Verify Deployment
```bash
# Check pods
kubectl get pods -n production

# Check services
kubectl get svc -n production

# Check logs
kubectl logs -f deployment/backend -n production
kubectl logs -f deployment/notifications -n production

# Check Kafka topics
kubectl exec -n redpanda-system redpanda-0 -- rpk topic list

# Check Dapr components
kubectl get components -n production
```

---

**Implementation Plan Version**: 1.0
**Last Updated**: 2025-12-26
**Status**: Ready for Execution
