"""Analytics Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Optional


class DailyCompletionCount(BaseModel):
    """Schema for a single day's completion count in the heatmap."""

    date: str = Field(
        ...,
        description="Date in ISO format (YYYY-MM-DD)",
        examples=["2025-01-15"]
    )
    count: int = Field(
        ...,
        ge=0,
        description="Number of tasks completed on this date",
        examples=[5]
    )

    class Config:
        from_attributes = True


class StreakHeatmapResponse(BaseModel):
    """Schema for streak heatmap response."""

    data: List[DailyCompletionCount] = Field(
        ...,
        description="Array of daily completion counts"
    )
    total_days: int = Field(
        ...,
        description="Total number of days in the requested range"
    )
    total_completions: int = Field(
        ...,
        description="Total number of task completions in the range"
    )


class AnalyticsSummaryResponse(BaseModel):
    """Schema for analytics summary statistics."""

    total_tasks: int = Field(
        ...,
        ge=0,
        description="Total number of tasks for the user"
    )
    completed_tasks: int = Field(
        ...,
        ge=0,
        description="Number of completed tasks"
    )
    pending_tasks: int = Field(
        ...,
        ge=0,
        description="Number of pending (incomplete) tasks"
    )
    completion_rate: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of completed tasks (0-100)"
    )
    current_streak: int = Field(
        ...,
        ge=0,
        description="Current consecutive day completion streak"
    )
    longest_streak: int = Field(
        ...,
        ge=0,
        description="Longest consecutive day completion streak achieved"
    )
