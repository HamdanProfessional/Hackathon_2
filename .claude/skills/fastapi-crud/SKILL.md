---
name: fastapi-crud
description: Scaffold complete CRUD operations: SQLModel in backend/app/models/[resource].py with Field() constraints and user_id FK, Pydantic schemas in backend/app/schemas/[resource].py with Create/Update/Response classes using validator() decorators, FastAPI routers in backend/app/routers/[resource].py with @router.post() for create, @router.get() for list with pagination, @router.patch() for update, @router.delete() for delete, and Alembic migrations via alembic revision --autogenerate. Use when adding tasks, comments, tags resources with REST endpoints at /api/tasks.
---

# FastAPI CRUD Skill

Complete CRUD generation for FastAPI applications.

## When to Use This Skill

Use this skill when:
- User says "Create CRUD for..." or "Generate CRUD operations for [Model]"
- Scaffolding new data resources with full Create, Read, Update, Delete operations
- Adding standard database operations for a new entity
- Implementing REST API endpoints following CRUD conventions
- Phase II or later development requiring database-backed APIs

---

## Part 1: Backend Scaffolding

### Vertical Slice Generation

Complete vertical slice including Model, Schema, Router, and Tests:

```python
# backend/app/models/task.py
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None)
    status: str = Field(default="pending")
    priority: str = Field(default="normal")
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="tasks")
```

### Pydantic Schemas

```python
# backend/app/schemas/task.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="normal")
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
```

### FastAPI Router

```python
# backend/app/routers/task.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List
from uuid import UUID

from app.database import get_session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.auth import get_current_user_id

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# CREATE
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Create a new task."""
    task = Task(user_id=user_id, **task_data.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# READ (List with Pagination)
@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """List all tasks for the current user."""
    offset = (page - 1) * page_size

    count_statement = select(Task).where(Task.user_id == user_id)
    total = len(session.exec(count_statement).all())

    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .offset(offset)
        .limit(page_size)
        .order_by(Task.created_at.desc())
    )
    tasks = session.exec(statement).all()

    return {"items": tasks, "total": total, "page": page, "page_size": page_size}

# READ (Single)
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Get a specific task by ID."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task

# UPDATE
@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Update a task."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    return task

# DELETE
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Delete a task."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    session.delete(task)
    session.commit()

    return None
```

### Pytest Tests

```python
# backend/tests/test_task.py
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.models.task import Task

client = TestClient(app)

@pytest.fixture
def auth_headers(test_user):
    return {"Authorization": f"Bearer {test_user['token']}"}

def test_create_task(auth_headers, db_session):
    payload = {"title": "Test Task", "priority": "high"}
    response = client.post("/tasks/", json=payload, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"

def test_list_tasks(auth_headers):
    response = client.get("/tasks/?page=1&page_size=10", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_user_isolation(auth_headers, db_session):
    # Create task for different user
    other_user_id = uuid4()
    task = Task(user_id=other_user_id, title="Other User Task")
    db_session.add(task)
    db_session.commit()

    # Try to access with different user token
    response = client.get(f"/tasks/{task.id}", headers=auth_headers)
    assert response.status_code == 404  # Should not find other user's data
```

---

## Part 2: CRUD Builder

### CRUD Template

For any resource, generate complete CRUD:

```python
# Model
class [Resource](SQLModel, table=True):
    __tablename__ = "[resources]"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    # ... fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Schemas
class [Resource]Create(BaseModel):
    # Request fields (no user_id)

class [Resource]Update(BaseModel):
    # All optional fields

class [Resource]Response(BaseModel):
    id: int
    user_id: str
    # ... all fields
    created_at: datetime
    updated_at: datetime

# Router with 5 endpoints
# POST   /[resources]/          - Create
# GET    /[resources]/          - List (paginated)
# GET    /[resources]/{id}      - Get by ID
# PATCH  /[resources]/{id}      - Update
# DELETE /[resources]/{id}      - Delete
```

---

## Part 3: SQLModel Schema Management

### Database Migration

```bash
cd backend
alembic revision --autogenerate -m "Add [resource] table"
alembic upgrade head
```

### Migration Template

```python
def upgrade():
    op.create_table(
        '[resources]',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        # ... columns
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_[resources]_user_id', '[resources]', ['user_id'])

def downgrade():
    op.drop_table('[resources]')
```

---

## Quality Checklist

Before finalizing CRUD operations:
- [ ] SQLModel has proper table name and relationships
- [ ] All fields have appropriate constraints (max_length, nullable, etc.)
- [ ] user_id field present for user scoping
- [ ] Timestamps (created_at, updated_at) included
- [ ] Pydantic schemas have proper validation
- [ ] Create schema excludes user_id (extracted from JWT)
- [ ] Update schema has all fields as Optional
- [ ] Response schema has from_attributes = True
- [ ] Router has all 5 CRUD endpoints
- [ ] All endpoints check user_id for authorization
- [ ] List endpoint has pagination (page, page_size)
- [ ] Proper HTTP status codes (201 for create, 204 for delete, 404 for not found)
- [ ] Tests cover all CRUD operations
- [ ] Test for user isolation included
- [ ] Router registered in main.py
- [ ] Database migration created and applied
