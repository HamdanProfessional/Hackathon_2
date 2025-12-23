"""Subtask Pydantic schemas for request/response validation."""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class SubtaskCreate(BaseModel):
    """Schema for subtask creation request."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Subtask title is required"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Subtask description (optional, max 2000 characters)"
    )


class SubtaskUpdate(BaseModel):
    """Schema for subtask update request."""

    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Updated subtask title")
    description: Optional[str] = Field(None, max_length=2000, description="Updated subtask description")
    completed: Optional[bool] = Field(None, description="Mark subtask as completed")
    sort_order: Optional[int] = Field(None, ge=0, description="Updated sort order")


class SubtaskResponse(BaseModel):
    """Schema for subtask data in responses."""

    id: int
    task_id: int
    title: str
    description: Optional[str]
    completed: bool
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True
