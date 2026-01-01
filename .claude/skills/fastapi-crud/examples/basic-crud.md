# Basic CRUD Example

Simple Task CRUD with FastAPI, SQLModel, and JWT authentication.

## Database Model

```python
# backend/app/models/task.py
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = None
    status: str = Field(default="pending")
    priority: str = Field(default="normal")
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## Pydantic Schemas

```python
# backend/app/schemas/task.py
from pydantic import BaseModel, Field
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

class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

## FastAPI Router

```python
# backend/app/routers/task.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from uuid import UUID

from app.database import get_session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.auth import get_current_user_id

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    task = Task(user_id=user_id, **task_data.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    status: str | None = None,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    statement = select(Task).where(Task.user_id == user_id)
    if status:
        statement = statement.where(Task.status == status)
    return session.exec(statement).all()

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404)
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404)

    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404)

    session.delete(task)
    session.commit()
```

## Database Migration

```bash
cd backend
alembic revision --autogenerate -m "Add tasks table"
alembic upgrade head
```
