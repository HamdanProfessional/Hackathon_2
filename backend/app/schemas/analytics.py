"""Analytics Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


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


# ============================================================================
# Chat/Conversation Analytics Schemas
# ============================================================================


class ChatOverviewStats(BaseModel):
    """Schema for chat/conversation overview statistics."""

    total_conversations: int = Field(
        ...,
        ge=0,
        description="Total number of conversations for the current user"
    )
    total_messages: int = Field(
        ...,
        ge=0,
        description="Total number of messages across all conversations"
    )
    avg_messages_per_conversation: float = Field(
        ...,
        ge=0,
        description="Average number of messages per conversation"
    )
    total_tool_calls: int = Field(
        ...,
        ge=0,
        description="Total number of tool calls made by the AI"
    )


class TimelineDataPoint(BaseModel):
    """Schema for a single data point on the timeline."""

    date: str = Field(
        ...,
        description="Date in ISO format (YYYY-MM-DD) or period label",
        examples=["2025-01-15", "2025-W03", "2025-01"]
    )
    count: int = Field(
        ...,
        ge=0,
        description="Number of conversations created in this period"
    )


class ConversationsTimelineResponse(BaseModel):
    """Schema for conversations timeline response."""

    period: str = Field(
        ...,
        description="Time period granularity (daily, weekly, monthly)",
        pattern="^(daily|weekly|monthly)$"
    )
    data: List[TimelineDataPoint] = Field(
        ...,
        description="Array of timeline data points"
    )
    total_conversations: int = Field(
        ...,
        ge=0,
        description="Total conversations in the period"
    )


class ToolUsageStats(BaseModel):
    """Schema for individual tool usage statistics."""

    tool_name: str = Field(
        ...,
        description="Name of the tool/function"
    )
    call_count: int = Field(
        ...,
        ge=0,
        description="Number of times the tool was called"
    )


class ToolUsageResponse(BaseModel):
    """Schema for tool usage statistics response."""

    total_tool_calls: int = Field(
        ...,
        ge=0,
        description="Total number of tool calls across all tools"
    )
    tool_stats: List[ToolUsageStats] = Field(
        ...,
        description="Array of tool usage statistics, sorted by call count descending"
    )
    most_used_tool: Optional[str] = Field(
        None,
        description="Name of the most frequently called tool"
    )


class MessageRoleStats(BaseModel):
    """Schema for message count by role."""

    role: str = Field(
        ...,
        description="Message role (user, assistant, system, tool)",
        pattern="^(user|assistant|system|tool)$"
    )
    count: int = Field(
        ...,
        ge=0,
        description="Number of messages with this role"
    )
    percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of total messages (0-100)"
    )


class MessageDistributionResponse(BaseModel):
    """Schema for message distribution by role response."""

    total_messages: int = Field(
        ...,
        ge=0,
        description="Total number of messages"
    )
    distribution: List[MessageRoleStats] = Field(
        ...,
        description="Array of message counts by role"
    )
