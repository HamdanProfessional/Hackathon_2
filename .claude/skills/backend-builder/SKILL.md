---
name: backend-builder
description: Scaffold complete FastAPI backend features by creating vertical slices: SQLModel in backend/app/models/[resource].py with user_id foreign key, Pydantic schemas in backend/app/schemas/[resource].py (Create, Update, Response classes), FastAPI routers in backend/app/routers/[resource].py with GET/POST/PATCH/DELETE endpoints protected by Depends(get_current_user), and pytest tests in backend/tests/test_[resource].py. Use when adding resources like tasks, comments, tags that need POST /api/tasks, GET /api/tasks, PATCH /api/tasks/{id}, DELETE /api/tasks/{id} endpoints with JWT authentication from Authorization headers.
---

# Backend Builder Skill

Scaffold complete FastAPI backend features with vertical slices: Model → Schema → Router → Tests.

## File Structure

```
backend/
├── app/
│   ├── models/
│   │   └── task.py          # SQLModel: Task table definition
│   ├── schemas/
│   │   └── task.py          # Pydantic: TaskCreate, TaskUpdate, TaskResponse
│   ├── routers/
│   │   └── task.py          # FastAPI: POST/GET/PATCH/DELETE endpoints
│   ├── auth/
│   │   └── jwt.py           # get_current_user dependency
│   └── main.py              # Router registration
├── tests/
│   └── test_task.py         # pytest tests
└── alembic/
    └── versions/            # Database migrations
```

## Quick Reference

| Action | Command | File |
|--------|---------|------|
| Create model file | `touch backend/app/models/task.py` | `backend/app/models/task.py` |
| Create schema file | `touch backend/app/schemas/task.py` | `backend/app/schemas/task.py` |
| Create router file | `touch backend/app/routers/task.py` | `backend/app/routers/task.py` |
| Generate migration | `alembic revision --autogenerate -m "Add tasks"` | `alembic/versions/XXX_add_tasks.py` |
| Apply migration | `alembic upgrade head` | PostgreSQL database |
| Run tests | `pytest backend/tests/test_task.py -v` | Test output |
| Register router | Add `app.include_router(task.router)` to main.py | `backend/app/main.py` |
| View docs | Open `http://localhost:8000/docs` | Swagger UI |

## When to Use This Skill

| User Request | Action | Files to Create |
|--------------|--------|-----------------|
| "Add tasks resource" | Create Task CRUD | `backend/app/models/task.py`, `backend/app/schemas/task.py`, `backend/app/routers/task.py` |
| "Add comments to tasks" | Create Comment with FK | `backend/app/models/comment.py`, etc. |
| "Add bulk update endpoint" | Add custom router method | `backend/app/routers/task.py` |
| "Fix 404 on tasks endpoint" | Check router registration | `backend/app/main.py` |
| "Run tests for tasks" | Execute pytest | `backend/tests/test_task.py` |
| "Create migration" | Generate Alembic migration | `alembic/versions/` |

---

## Part 1: SQLModel (backend/app/models/task.py)

```python
"""
Task SQLModel for TODO application.
File: backend/app/models/task.py
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Field, SQLModel, Index


class Task(SQLModel, table=True):
    """
    Task model for multi-user TODO application.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table (owner)
        title: Task title
        description: Optional detailed description
        status: Task status (pending, in_progress, completed)
        priority: Task priority (low, normal, high, urgent)
        due_date: Optional due date
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last modified
    """
    __tablename__ = "tasks"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign key to users table
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="User who owns this task"
    )

    # Task fields
    title: str = Field(max_length=255, description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    status: str = Field(default="pending", description="pending, in_progress, or completed")
    priority: str = Field(default="normal", description="low, normal, high, or urgent")
    due_date: Optional[datetime] = Field(default=None, description="Task due date")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Indexes for performance
    __table_args__ = (
        Index("ix_tasks_user_status", "user_id", "status"),
        Index("ix_tasks_user_created", "user_id", "created_at"),
    )
```

### Create Migration

```bash
cd backend
alembic revision --autogenerate -m "Add tasks table"
alembic upgrade head
```

---

## Part 2: Pydantic Schemas (backend/app/schemas/task.py)

```python
"""
Task Pydantic schemas for API validation.
File: backend/app/schemas/task.py
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator


class TaskBase(BaseModel):
    """Base schema with common fields."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: str = Field("pending", description="pending, in_progress, or completed")
    priority: str = Field("normal", description="low, normal, high, or urgent")
    due_date: Optional[datetime] = Field(None, description="Task due date")

    @validator("status")
    def validate_status(cls, v):
        """Validate status is one of the allowed values."""
        allowed = ["pending", "in_progress", "completed"]
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v

    @validator("priority")
    def validate_priority(cls, v):
        """Validate priority is one of the allowed values."""
        allowed = ["low", "normal", "high", "urgent"]
        if v not in allowed:
            raise ValueError(f"Priority must be one of {allowed}")
        return v


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass  # All fields from TaskBase are required/optional as defined


class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskResponse(TaskBase):
    """Schema for task responses (includes auto-generated fields)."""
    id: int
    user_id: str  # UUID as string for JSON serialization
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2: allows ORM mode


class TaskListResponse(BaseModel):
    """Schema for paginated task list."""
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int


class TaskStatsResponse(BaseModel):
    """Schema for task statistics."""
    total: int
    pending: int
    in_progress: int
    completed: int
    completion_rate: float
```

---

## Part 3: FastAPI Router (backend/app/routers/task.py)

```python
"""
Task API routes with CRUD operations.
File: backend/app/routers/task.py
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, func
from uuid import UUID

from app.database import get_session
from app.models.task import Task
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskStatsResponse
)
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


# === CREATE ===
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new task for authenticated user.

    Endpoint: POST /api/tasks

    Flow:
    1. Extract user_id from JWT token
    2. Create Task instance with user_id and form data
    3. Save to database
    4. Return created task with id and timestamps
    """
    task = Task(user_id=current_user["id"], **data.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# === READ LIST ===
@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    List all tasks for authenticated user with pagination.

    Endpoint: GET /api/tasks?page=1&page_size=20&status_filter=pending

    Returns paginated list of user's tasks.
    """
    # Build query
    statement = select(Task).where(Task.user_id == current_user["id"])

    # Apply status filter if provided
    if status_filter:
        statement = statement.where(Task.status == status_filter)

    # Get total count
    total_statement = select(func.count()).select_from(Task).where(Task.user_id == current_user["id"])
    if status_filter:
        total_statement = total_statement.where(Task.status == status_filter)
    total = session.exec(total_statement).one()

    # Apply pagination
    offset = (page - 1) * page_size
    statement = statement.order_by(Task.created_at.desc()).offset(offset).limit(page_size)

    tasks = session.exec(statement).all()

    return TaskListResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size
    )


# === READ SINGLE ===
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a single task by ID.

    Endpoint: GET /api/tasks/{task_id}

    Returns task only if it belongs to authenticated user.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user["id"]
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


# === UPDATE ===
@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing task.

    Endpoint: PATCH /api/tasks/{task_id}

    Only updates fields provided in request body.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user["id"]
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update only provided fields
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    # Update timestamp
    from datetime import datetime
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


# === DELETE ===
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a task.

    Endpoint: DELETE /api/tasks/{task_id}

    Permanently removes task from database.
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user["id"]
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()

    return None  # 204 No Content


# === STATISTICS ===
@router.get("/stats/summary", response_model=TaskStatsResponse)
async def get_task_statistics(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Get task statistics for authenticated user.

    Endpoint: GET /api/tasks/stats/summary

    Returns counts by status and completion rate.
    """
    # Total tasks
    total = session.exec(
        select(func.count(Task.id)).where(Task.user_id == current_user["id"])
    ).one()

    # Count by status
    pending = session.exec(
        select(func.count(Task.id)).where(
            Task.user_id == current_user["id"],
            Task.status == "pending"
        )
    ).one()

    in_progress = session.exec(
        select(func.count(Task.id)).where(
            Task.user_id == current_user["id"],
            Task.status == "in_progress"
        )
    ).one()

    completed = session.exec(
        select(func.count(Task.id)).where(
            Task.user_id == current_user["id"],
            Task.status == "completed"
        )
    ).one()

    # Calculate completion rate
    completion_rate = (completed / total * 100) if total > 0 else 0.0

    return TaskStatsResponse(
        total=total,
        pending=pending,
        in_progress=in_progress,
        completed=completed,
        completion_rate=round(completion_rate, 2)
    )


# === SEARCH ===
@router.get("/search", response_model=TaskListResponse)
async def search_tasks(
    query: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Search tasks by title or description.

    Endpoint: GET /api/tasks/search?query=keyword&page=1

    Case-insensitive search in title and description fields.
    """
    from sqlmodel import or_

    # Build search query
    statement = select(Task).where(
        Task.user_id == current_user["id"],
        or_(
            Task.title.ilike(f"%{query}%"),
            Task.description.ilike(f"%{query}%")
        )
    )

    # Get total
    total = len(session.exec(statement).all())

    # Apply pagination
    offset = (page - 1) * page_size
    tasks = session.exec(
        statement.offset(offset).limit(page_size)
    ).all()

    return TaskListResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size
    )
```

---

## Part 4: Register Router (backend/app/main.py)

```python
"""
FastAPI application main entry point.
File: backend/app/main.py
"""
from fastapi import FastAPI
from app.routers import task  # Import task router

# ... other imports

app = FastAPI(title="TODO API")

# Include task router
app.include_router(task.router)

# ... other routers and middleware

@app.get("/")
def read_root():
    return {"message": "TODO API"}
```

---

## Part 5: Authentication Dependency (backend/app/auth/jwt.py)

```python
"""
JWT authentication utilities.
File: backend/app/auth/jwt.py
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Extract and verify JWT token from Authorization header.

    Returns user dict with id and email if token is valid.
    Raises 401 if token is invalid or expired.
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user_id, "email": payload.get("email")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## Part 6: Pytest Tests (backend/tests/test_task.py)

```python
"""
Tests for Task API endpoints.
File: backend/tests/test_task.py
"""
import pytest
from httpx import AsyncClient
from app.models.task import Task


class TestTaskCRUD:
    """Test CRUD operations for tasks."""

    @pytest.mark.asyncio
    async def test_create_task(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test POST /api/tasks creates a new task."""
        response = await async_client.post(
            "/api/tasks/",
            json={
                "title": "Test Task",
                "description": "Test description",
                "priority": "high"
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_list_tasks(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_task: Task
    ):
        """Test GET /api/tasks returns user's tasks."""
        response = await async_client.get(
            "/api/tasks/",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_get_task_by_id(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_task: Task
    ):
        """Test GET /api/tasks/{id} returns task."""
        response = await async_client.get(
            f"/api/tasks/{test_task.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task.id

    @pytest.mark.asyncio
    async def test_update_task(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_task: Task
    ):
        """Test PATCH /api/tasks/{id} updates task."""
        response = await async_client.patch(
            f"/api/tasks/{test_task.id}",
            json={"status": "completed"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_delete_task(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_task: Task
    ):
        """Test DELETE /api/tasks/{id} removes task."""
        response = await async_client.delete(
            f"/api/tasks/{test_task.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify task is deleted
        get_response = await async_client.get(
            f"/api/tasks/{test_task.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_unauthorized_access(
        self,
        async_client: AsyncClient
    ):
        """Test that requests without JWT token are rejected."""
        response = await async_client.get("/api/tasks/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_task_statistics(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test GET /api/tasks/stats/summary returns stats."""
        response = await async_client.get(
            "/api/tasks/stats/summary",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "completion_rate" in data

    @pytest.mark.asyncio
    async def test_search_tasks(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_task: Task
    ):
        """Test GET /api/tasks/search finds tasks by title."""
        response = await async_client.get(
            f"/api/tasks/search?query={test_task.title}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0


# === Fixtures ===
@pytest.fixture
async def test_task(
    async_session,
    test_user_id: str
) -> Task:
    """Create a test task in database."""
    task = Task(
        title="Test Task",
        description="Test description",
        user_id=test_user_id
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    return task
```

### Run Tests

```bash
cd backend
pytest tests/test_task.py -v
```

---

## Part 7: Common Scenarios

### Scenario 1: Add a "Comment" Resource

**User Request**: "Allow users to add comments to tasks"

**Commands**:
```bash
# Create files
touch backend/app/models/comment.py
touch backend/app/schemas/comment.py
touch backend/app/routers/comment.py

# Generate migration
cd backend
alembic revision --autogenerate -m "Add comments table"
alembic upgrade head

# Run tests
pytest tests/test_comment.py -v
```

**File: backend/app/models/comment.py**
```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Scenario 2: Add Bulk Operations

**User Request**: "Add endpoint to mark multiple tasks complete at once"

**Add to backend/app/routers/task.py**:
```python
from pydantic import BaseModel

class TaskBulkCompleteRequest(BaseModel):
    task_ids: list[int]

class TaskBulkCompleteResponse(BaseModel):
    updated_count: int
    failed_ids: list[int]

@router.post("/bulk-complete", response_model=TaskBulkCompleteResponse)
async def bulk_complete_tasks(
    request: TaskBulkCompleteRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Mark multiple tasks as completed."""
    updated_count = 0
    failed_ids = []

    for task_id in request.task_ids:
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user["id"]
        )
        task = session.exec(statement).first()

        if task:
            task.status = "completed"
            session.add(task)
            updated_count += 1
        else:
            failed_ids.append(task_id)

    session.commit()

    return TaskBulkCompleteResponse(
        updated_count=updated_count,
        failed_ids=failed_ids
    )
```

### Scenario 3: Add Foreign Key Relationship

**User Request**: "Tasks should have a category"

**Commands**:
```bash
# Create category model first
touch backend/app/models/category.py

# Add category to Task model
# Edit backend/app/models/task.py: add category_id: int = Field(foreign_key="categories.id")

# Generate migration
alembic revision --autogenerate -m "Add categories to tasks"
alembic upgrade head
```

---

## Quality Checklist

Before finalizing backend resource:

- [ ] **Model**: SQLModel with `user_id` foreign key and proper Field constraints
- [ ] **Timestamps**: `created_at` and `updated_at` fields included
- [ ] **Indexes**: Added on `user_id` and frequently queried columns
- [ ] **Schemas**: Create, Update, Response classes defined in schemas file
- [ ] **Validation**: Pydantic validators for enum values (status, priority)
- [ ] **Router**: All endpoints use `Depends(get_current_user)`
- [ ] **Tenant Isolation**: All queries filter by `user_id`
- [ ] **Error Handling**: HTTPException with appropriate status codes
- [ ] **Tests**: pytest tests for CRUD operations
- [ ] **Migration**: `alembic upgrade head` applied successfully
- [ ] **Router Registration**: `app.include_router(router)` in main.py
- [ ] **Swagger Docs**: Accessible at `http://localhost:8000/docs`
- [ ] **UUID Serialization**: Response schemas convert UUID to string
- [ ] **Pagination**: List endpoints support page/page_size parameters
- [ ] **Soft Delete**: If applicable, use `deleted_at` instead of hard delete
