"""RecurringTask Pydantic schemas for request/response validation."""
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID


class RecurringTaskCreate(BaseModel):
    """Schema for recurring task creation request."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Recurring task title is required"
    )
    description: str = Field(
        default="",
        max_length=5000,
        description="Recurring task description (optional, max 5000 characters)"
    )
    recurrence_pattern: str = Field(
        ...,
        pattern="^(daily|weekly|monthly|yearly)$",
        description="Recurrence pattern: daily, weekly, monthly, or yearly"
    )
    start_date: date = Field(
        ...,
        description="Start date for task generation (format: YYYY-MM-DD)"
    )
    end_date: Optional[date] = Field(
        None,
        description="Optional end date for recurrence (format: YYYY-MM-DD)"
    )
    task_priority_id: Optional[int] = Field(
        None,
        description="Task priority ID (1=Low, 2=Medium, 3=High)"
    )

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        """Ensure end_date is after start_date if provided."""
        if v is not None and 'start_date' in info.data:
            if v <= info.data['start_date']:
                raise ValueError('end_date must be after start_date')
        return v


class RecurringTaskUpdate(BaseModel):
    """Schema for recurring task update request."""

    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Updated recurring task title")
    description: Optional[str] = Field(None, max_length=5000, description="Updated recurring task description")
    recurrence_pattern: Optional[str] = Field(
        None,
        pattern="^(daily|weekly|monthly|yearly)$",
        description="Recurrence pattern: daily, weekly, monthly, or yearly"
    )
    start_date: Optional[date] = Field(None, description="Updated start date")
    end_date: Optional[date] = Field(None, description="Updated end date")
    is_active: Optional[bool] = Field(None, description="Pause or resume the recurring task")
    task_priority_id: Optional[int] = Field(None, description="Updated task priority ID")


class PriorityResponse(BaseModel):
    """Schema for priority data in responses."""

    id: int
    name: str
    level: int
    color: Optional[str]

    class Config:
        from_attributes = True


class RecurringTaskResponse(BaseModel):
    """Schema for recurring task data in responses."""

    id: int
    user_id: str  # UUID string
    title: str
    description: str
    recurrence_pattern: str
    start_date: date
    end_date: Optional[date]
    next_due_at: date
    is_active: bool
    task_priority_id: Optional[int]
    created_at: datetime
    updated_at: datetime
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


class RecurringTaskListResponse(BaseModel):
    """Schema for paginated list of recurring tasks."""

    items: list[RecurringTaskResponse]
    total: int
    limit: int
    offset: int


class RecurringTaskPauseResponse(BaseModel):
    """Schema for pause/resume response."""

    id: int
    is_active: bool
    next_due_at: Optional[date]
    message: str
