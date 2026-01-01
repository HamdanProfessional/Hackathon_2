# Async CRUD Example - Task Model

This example shows the actual CRUD patterns used in the Evolution of TODO project.

## Model (backend/app/models/task.py)

```python
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlmodel import Field, SQLModel

from app.models.priority import Priority


class Task(SQLModel, table=True):
    """Task model with async support."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default="", max_length=10000)
    priority_id: int = Field(foreign_key="priorities.id", default=2)
    completed: bool = Field(default=False)
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[str] = Field(default=None)
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship (eager loaded with selectinload)
    priority_obj: Optional[Priority] = relationship("Priority")
```

## CRUD Operations (backend/app/crud/task.py)

```python
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, asc, desc
from sqlalchemy.orm import selectinload

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, task_data: TaskCreate, user_id: str) -> Task:
    """Create a new task with user ownership."""
    db_task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description or "",
        priority_id=task_data.priority_id,
        due_date=task_data.due_date,
        completed=False,
        is_recurring=task_data.is_recurring if task_data.is_recurring is not None else False,
        recurrence_pattern=task_data.recurrence_pattern,
    )

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    # Re-fetch with eager loading to prevent DetachedInstanceError
    stmt = select(Task).where(Task.id == db_task.id).options(selectinload(Task.priority_obj))
    result = await db.execute(stmt)
    task = result.scalar_one()

    return task


async def get_tasks_by_user(
    db: AsyncSession,
    user_id: str,
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    limit: Optional[int] = 20,
    offset: Optional[int] = 0
) -> List[Task]:
    """Get tasks for user with filtering and pagination."""
    # Start with base query with relationship loading
    query = select(Task).options(selectinload(Task.priority_obj)).where(Task.user_id == user_id)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term)
            )
        )

    # Apply status filter
    if status == "completed":
        query = query.where(Task.completed == True)
    elif status == "pending":
        query = query.where(Task.completed == False)

    # Apply priority filter
    if priority and priority in [1, 2, 3]:
        query = query.where(Task.priority_id == priority)

    # Apply sorting with null handling
    if sort_by == "due_date":
        if sort_order == "asc":
            query = query.order_by(asc(Task.due_date).nulls_last())
        else:
            query = query.order_by(desc(Task.due_date).nulls_last())
    else:
        # Default: Sort by created_at
        if sort_order == "asc":
            query = query.order_by(asc(Task.created_at))
        else:
            query = query.order_by(desc(Task.created_at))

    # Apply pagination
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()


async def get_task_by_id(db: AsyncSession, task_id: int, user_id: str) -> Optional[Task]:
    """Get task by ID with user ownership verification."""
    result = await db.execute(
        select(Task).options(selectinload(Task.priority_obj)).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def update_task(
    db: AsyncSession,
    task: Task,
    task_data: TaskUpdate
) -> Task:
    """Update task with partial field support."""
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.priority_id is not None:
        task.priority_id = task_data.priority_id
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    if task_data.completed is not None:
        task.completed = task_data.completed

    await db.commit()
    await db.refresh(task)

    # Re-fetch with eager loading
    stmt = select(Task).where(Task.id == task.id).options(selectinload(Task.priority_obj))
    result = await db.execute(stmt)
    return result.scalar_one()


async def delete_task(db: AsyncSession, task: Task) -> None:
    """Delete a task."""
    await db.delete(task)
    await db.commit()
```

## API Router (backend/app/api/tasks.py)

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.crud import task as task_crud
from app.api.deps import get_current_user
from app.utils.exceptions import NotFoundException


router = APIRouter()


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new task with background email notification."""
    new_task = await task_crud.create_task(db, task_data, str(current_user.id))

    # Send email notification (fire and forget)
    background_tasks.add_task(
        _send_email_notification,
        "created",
        _task_to_dict(new_task),
        current_user.email
    )

    return new_task


@router.get(
    "",
    response_model=List[TaskResponse],
    summary="Get all tasks for current user",
)
async def get_tasks(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc"),
    limit: Optional[int] = Query(20, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get tasks with filtering, sorting, and pagination."""
    # Convert priority string to ID
    priority_id = None
    if priority:
        priority_map = {"low": 1, "medium": 2, "high": 3}
        priority_id = priority_map.get(priority.lower())

    tasks = await task_crud.get_tasks_by_user(
        db=db,
        user_id=str(current_user.id),
        search=search,
        status=status,
        priority=priority_id,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )
    return tasks


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a specific task",
)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get task by ID with ownership verification."""
    task = await task_crud.get_task_by_id(db, task_id, str(current_user.id))
    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update task fields."""
    task = await task_crud.get_task_by_id(db, task_id, str(current_user.id))
    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")

    updated_task = await task_crud.update_task(db, task, task_data)

    # Send email notification
    background_tasks.add_task(
        _send_email_notification,
        "updated",
        _task_to_dict(updated_task),
        current_user.email
    )

    return updated_task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
async def delete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a task permanently."""
    task = await task_crud.get_task_by_id(db, task_id, str(current_user.id))
    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")

    task_dict = _task_to_dict(task)
    await task_crud.delete_task(db, task)

    # Send email notification
    background_tasks.add_task(
        _send_email_notification,
        "deleted",
        task_dict,
        current_user.email
    )


def _task_to_dict(task) -> dict:
    """Convert Task model to dict for events."""
    return {
        "task_id": task.id,
        "user_id": str(task.user_id),
        "title": task.title,
        "description": task.description,
        "priority_id": task.priority_id,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "completed": task.completed,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }


async def _send_email_notification(event_type: str, task_data: dict, user_email: str):
    """Send email notification in background."""
    # Import here to avoid circular imports
    from app.utils.email_notifier import send_task_created_email

    if event_type == "created":
        await send_task_created_email(user_email, task_data)
```

## Key Patterns

### 1. Async Database Operations
- Use `AsyncSession` for all database operations
- Use `select()` instead of raw SQL queries
- Use `selectinload()` for eager loading relationships
- Always `await` database operations

### 2. User Isolation
- Inject `user_id` from JWT token via `get_current_user`
- Filter all queries by `user_id`
- Verify ownership on single-item operations

### 3. Background Tasks
- Use FastAPI's `BackgroundTasks` for non-blocking operations
- Fire-and-forget pattern for email notifications
- Don't let background task failures affect the main response

### 4. Error Handling
- Use custom exceptions (NotFoundException, ForbiddenException, etc.)
- Return appropriate HTTP status codes
- Provide detailed error messages in responses

### 5. Pagination & Filtering
- Support `limit` and `offset` for pagination
- Support multiple filter types (search, status, priority)
- Support flexible sorting with null handling

### 6. Event Publishing
- Convert models to dict for JSON serialization
- Publish events after database operations succeed
- Handle event publishing failures gracefully
