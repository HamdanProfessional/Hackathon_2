"""Task Pydantic schemas for request/response validation."""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from app.models.task import TaskPriority


class TaskCreate(BaseModel):
    """Schema for task creation request."""

    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: str = Field(default="", max_length=10000, description="Task description (optional)")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority level")
    tags: str = Field(default="", max_length=500, description="Comma-separated tags")


class TaskUpdate(BaseModel):
    """Schema for task update request."""

    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Updated task title")
    description: Optional[str] = Field(None, max_length=10000, description="Updated task description")
    priority: Optional[TaskPriority] = Field(None, description="Updated task priority")
    tags: Optional[str] = Field(None, max_length=500, description="Updated tags (comma-separated)")


class TaskResponse(BaseModel):
    """Schema for task data in responses."""

    id: int
    user_id: int
    title: str
    description: str
    completed: bool
    priority: TaskPriority
    tags: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
