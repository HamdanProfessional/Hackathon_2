# Data Model: Cloud Deployment with Event-Driven Architecture

**Feature**: 005-cloud-deployment

---

## Database Schema Changes

### New Tables

#### 1. RecurringTask

Stores recurring task configurations.

```sql
CREATE TABLE recurringtask (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 2, -- 1=high, 2=medium, 3=low
    recurrence_type VARCHAR(20) NOT NULL, -- daily, weekly, monthly, yearly
    recurrence_interval INTEGER DEFAULT 1, -- Every N days/weeks/months
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP, -- Optional end date
    last_created_at TIMESTAMP, -- Last occurrence created
    next_due_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_recurringtask_user_id ON recurringtask(user_id);
CREATE INDEX idx_recurringtask_next_due_at ON recurringtask(next_due_at);
CREATE INDEX idx_recurringtask_is_active ON recurringtask(is_active);
```

#### 2. TaskEventLog

Audit log for task events.

```sql
CREATE TABLE taskeventlog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- created, updated, completed, deleted, due
    event_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_taskeventlog_task_id ON taskeventlog(task_id);
CREATE INDEX idx_taskeventlog_event_type ON taskeventlog(event_type);
CREATE INDEX idx_taskeventlog_created_at ON taskeventlog(created_at);
```

### Modified Tables

#### Task

Add due date support and recurring task relationship.

```sql
-- Add new columns
ALTER TABLE tasks
ADD COLUMN due_date TIMESTAMP,
ADD COLUMN notified BOOLEAN DEFAULT FALSE,
ADD COLUMN recurring_task_id UUID REFERENCES recurringtask(id) ON DELETE SET NULL;

-- Indexes
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_notified ON tasks(notified);
CREATE INDEX idx_tasks_recurring_task_id ON tasks(recurring_task_id);
```

---

## SQLAlchemy Models

### RecurringTask Model

```python
# backend/app/models/recurring_task.py
from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class RecurringTask(Base):
    """Recurring task configuration."""
    __tablename__ = "recurringtask"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=2)  # 1=high, 2=medium, 3=low
    recurrence_type = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    recurrence_interval = Column(Integer, default=1)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    last_created_at = Column(DateTime, nullable=True)
    next_due_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### Task Model (Updated)

```python
# backend/app/models/task.py (additions)
class Task(Base):
    # ... existing fields ...
    due_date = Column(DateTime, nullable=True)
    notified = Column(Boolean, default=False)
    recurring_task_id = Column(UUID(as_uuid=True), ForeignKey("recurringtask.id", ondelete="SET NULL"), nullable=True)
```

### TaskEventLog Model

```python
# backend/app/models/task_event_log.py
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base


class TaskEventLog(Base):
    """Audit log for task events."""
    __tablename__ = "taskeventlog"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False)  # created, updated, completed, deleted, due
    event_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

---

## Pydantic Schemas

### Recurring Task Schemas

```python
# backend/app/schemas/recurring_task.py
from typing import Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class RecurringTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: int = Field(default=2, ge=1, le=3)
    recurrence_type: str = Field(..., pattern="^(daily|weekly|monthly|yearly)$")
    recurrence_interval: int = Field(default=1, ge=1)
    start_date: datetime
    end_date: Optional[datetime] = None


class RecurringTaskCreate(RecurringTaskBase):
    pass


class RecurringTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=3)
    is_active: Optional[bool] = None
    end_date: Optional[datetime] = None


class RecurringTaskResponse(RecurringTaskBase):
    id: uuid.UUID
    user_id: uuid.UUID
    last_created_at: Optional[datetime]
    next_due_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### Task Schemas (Updated)

```python
# backend/app/schemas/task.py (additions)
class TaskBase(BaseModel):
    # ... existing fields ...
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    # ... existing fields ...
    due_date: Optional[datetime] = None
    recurring_task_id: Optional[uuid.UUID] = None


class TaskUpdate(BaseModel):
    # ... existing fields ...
    due_date: Optional[datetime] = None


class TaskResponse(TaskBase):
    # ... existing fields ...
    due_date: Optional[datetime]
    notified: bool
    recurring_task_id: Optional[uuid.UUID]
```

---

## Event Schemas

### Task Created Event

```python
{
    "event_type": "task-created",
    "task_id": "uuid",
    "user_id": "uuid",
    "title": "Task title",
    "description": "Task description",
    "priority": 2,
    "due_date": "2025-01-15T17:00:00Z",
    "recurring_task_id": null,
    "timestamp": "2025-01-01T00:00:00Z"
}
```

### Task Due Event

```python
{
    "event_type": "task-due-soon",
    "task_id": "uuid",
    "user_id": "uuid",
    "title": "Task title",
    "due_date": "2025-01-15T17:00:00Z",
    "hours_until_due": 12,
    "timestamp": "2025-01-15T05:00:00Z"
}
```

### Recurring Task Due Event

```python
{
    "event_type": "recurring-task-due",
    "recurring_task_id": "uuid",
    "user_id": "uuid",
    "title": "Recurring task title",
    "next_due_at": "2025-01-08T09:00:00Z",
    "recurrence_type": "weekly",
    "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## Kafka Topics

### Topic Configuration

| Topic | Partitions | Replication Factor | Retention |
|-------|-----------|-------------------|-----------|
| task-created | 3 | 3 | 7 days |
| task-updated | 3 | 3 | 7 days |
| task-completed | 3 | 3 | 7 days |
| task-due-soon | 3 | 3 | 1 day |
| recurring-task-due | 3 | 3 | 7 days |

---

## State Store (Redis - Optional)

### Key Patterns

```
# User session cache
user:session:{user_id} -> JSON

# Task cache
task:{task_id} -> JSON

# Recurring task next due
recurring:next_due:{recurring_task_id} -> ISO timestamp

# Rate limiting
rate_limit:{user_id}:{endpoint} -> count
```

---

## Migration Script

```bash
# backend/alembic/versions/005_add_recurring_tasks.py
"""Add recurring tasks and due dates

Revision ID: 005
Revises: 004
Create Date: 2025-01-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


def upgrade():
    # Create recurringtask table
    op.create_table(
        'recurringtask',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), server_default='2'),
        sa.Column('recurrence_type', sa.String(20), nullable=False),
        sa.Column('recurrence_interval', sa.Integer(), server_default='1'),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('last_created_at', sa.DateTime(), nullable=True),
        sa.Column('next_due_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create taskeventlog table
    op.create_table(
        'taskeventlog',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('task_id', UUID(as_uuid=True), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Add columns to tasks table
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('notified', sa.Boolean(), server_default='false'))
    op.add_column('tasks', sa.Column('recurring_task_id', UUID(as_uuid=True), sa.ForeignKey('recurringtask.id', ondelete='SET NULL'), nullable=True))

    # Create indexes
    op.create_index('idx_recurringtask_user_id', 'recurringtask', ['user_id'])
    op.create_index('idx_recurringtask_next_due_at', 'recurringtask', ['next_due_at'])
    op.create_index('idx_recurringtask_is_active', 'recurringtask', ['is_active'])
    op.create_index('idx_taskeventlog_task_id', 'taskeventlog', ['task_id'])
    op.create_index('idx_taskeventlog_event_type', 'taskeventlog', ['event_type'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('idx_tasks_notified', 'tasks', ['notified'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_tasks_notified', 'tasks')
    op.drop_index('idx_tasks_due_date', 'tasks')
    op.drop_index('idx_taskeventlog_event_type', 'taskeventlog')
    op.drop_index('idx_taskeventlog_task_id', 'taskeventlog')
    op.drop_index('idx_recurringtask_is_active', 'recurringtask')
    op.drop_index('idx_recurringtask_next_due_at', 'recurringtask')
    op.drop_index('idx_recurringtask_user_id', 'recurringtask')

    # Drop columns from tasks
    op.drop_column('tasks', 'recurring_task_id')
    op.drop_column('tasks', 'notified')
    op.drop_column('tasks', 'due_date')

    # Drop tables
    op.drop_table('taskeventlog')
    op.drop_table('recurringtask')
```
