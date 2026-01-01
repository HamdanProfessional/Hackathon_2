# Advanced CRUD with Relationships

Task CRUD with comments, tags, and complex relationships.

## Models with Relationships

```python
# backend/app/models/task.py
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship, Text
from sqlalchemy import Index

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, sa_column=Text)
    status: str = Field(default="pending", index=True)
    priority: str = Field(default="normal")
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    comments: List["Comment"] = Relationship(back_populates="task")
    tags: List["TaskTag"] = Relationship(back_populates="task")

    __table_args__ = (
        Index("ix_tasks_user_status", "user_id", "status"),
        Index("ix_tasks_user_created", "user_id", "created_at"),
    )

class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    user_id: UUID = Field(foreign_key="users.id")
    content: str = Field(sa_column=Text)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    task: Optional[Task] = Relationship(back_populates="comments")

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True, index=True)
    color: str = Field(max_length=7, default="#3B82F6")  # Hex color
    created_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: List["TaskTag"] = Relationship(back_populates="tag")

class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    task: Optional[Task] = Relationship(back_populates="tags")
    tag: Optional[Tag] = Relationship(back_populates="tasks")
```

## Advanced Schemas

```python
# backend/app/schemas/task.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#3B82F6", regex=r"^#[0-9A-Fa-f]{6}$")

class TagResponse(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)

class CommentResponse(CommentBase):
    id: int
    task_id: int
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="normal")
    due_date: Optional[datetime] = None
    tag_ids: List[int] = Field(default_factory=list)

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
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    comments: List[CommentResponse] = []
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
```

## Advanced Router

```python
# backend/app/routers/task.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from uuid import UUID
from typing import List

from app.database import get_session
from app.models.task import Task, Comment, Tag, TaskTag
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    CommentBase, CommentResponse, TagBase, TagResponse
)
from app.auth import get_current_user_id

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# CRUD with relationships
@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    # Create task
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date
    )
    session.add(task)
    session.flush()  # Get the ID before relationships

    # Add tags
    for tag_id in task_data.tag_ids:
        tag_link = TaskTag(task_id=task.id, tag_id=tag_id)
        session.add(tag_link)

    session.commit()
    session.refresh(task)
    return task

@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    priority: str | None = None,
    search: str | None = None,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    # Build query
    statement = select(Task).where(Task.user_id == user_id)

    if status:
        statement = statement.where(Task.status == status)
    if priority:
        statement = statement.where(Task.priority == priority)
    if search:
        statement = statement.where(Task.title.icontains(search))

    # Get total count
    count_statement = select(Task).where(Task.user_id == user_id)
    total = len(session.exec(count_statement).all())

    # Apply pagination
    offset = (page - 1) * page_size
    statement = statement.offset(offset).limit(page_size)
    statement = statement.order_by(Task.created_at.desc())

    tasks = session.exec(statement).all()

    return TaskListResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    # Eager load relationships
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@router.post("/{task_id}/comments", response_model=CommentResponse, status_code=201)
async def add_comment(
    task_id: int,
    comment_data: CommentBase,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    # Verify task exists and belongs to user
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    comment = Comment(
        task_id=task_id,
        user_id=user_id,
        content=comment_data.content
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)

    # Update task timestamp
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()

    return comment

@router.post("/{task_id}/tags/{tag_id}", status_code=201)
async def add_tag_to_task(
    task_id: int,
    tag_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    # Verify ownership
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if tag exists
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Check if already tagged
    existing = session.exec(
        select(TaskTag).where(TaskTag.task_id == task_id, TaskTag.tag_id == tag_id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already added")

    # Add tag
    task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
    session.add(task_tag)
    session.commit()

    return {"message": "Tag added"}
```
