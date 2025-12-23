"""Task Pydantic schemas for request/response validation."""
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID


class TaskCreate(BaseModel):
    """Schema for task creation request."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Task title is required"
    )
    description: str = Field(
        default="",
        max_length=2000,
        description="Task description (optional, max 2000 characters)"
    )
    priority_id: Optional[int] = Field(
        default=2,  # Default to Medium priority (id=2)
        description="Task priority ID (1=Low, 2=Medium, 3=High)"
    )
    due_date: Optional[date] = Field(
        None,
        description="Task due date (optional, format: YYYY-MM-DD)"
    )
    is_recurring: Optional[bool] = Field(
        default=False,
        description="Whether the task is recurring"
    )
    recurrence_pattern: Optional[str] = Field(
        None,
        description="Recurrence pattern: daily, weekly, monthly, or yearly"
    )


class TaskUpdate(BaseModel):
    """Schema for task update request."""

    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Updated task title")
    description: Optional[str] = Field(None, max_length=2000, description="Updated task description")
    priority_id: Optional[int] = Field(None, description="Updated task priority ID")
    due_date: Optional[date] = Field(None, description="Updated task due date")
    completed: Optional[bool] = Field(None, description="Mark task as completed")
    is_recurring: Optional[bool] = Field(None, description="Whether the task is recurring")
    recurrence_pattern: Optional[str] = Field(None, description="Recurrence pattern: daily, weekly, monthly, or yearly")


class PriorityResponse(BaseModel):
    """Schema for priority data in responses."""

    id: int
    name: str
    level: int
    color: Optional[str]

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Schema for task data in responses."""

    id: int
    user_id: str  # UUID string
    title: str
    description: str
    completed: bool
    priority_id: Optional[int]
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    is_recurring: bool
    recurrence_pattern: Optional[str]
    priority_obj: Optional[PriorityResponse] = None

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)

    @field_validator('user_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string for serialization."""
        if isinstance(v, UUID):
            return str(v)
        return v
