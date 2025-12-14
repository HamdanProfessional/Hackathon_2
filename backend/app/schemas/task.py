"""Task Pydantic schemas for request/response validation."""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class TaskCreate(BaseModel):
    """Schema for task creation request."""

    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: str = Field(default="", max_length=10000, description="Task description (optional)")


class TaskUpdate(BaseModel):
    """Schema for task update request."""

    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Updated task title")
    description: Optional[str] = Field(None, max_length=10000, description="Updated task description")


class TaskResponse(BaseModel):
    """Schema for task data in responses."""

    id: int
    user_id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
