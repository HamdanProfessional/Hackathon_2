"""Analytics API endpoints for task statistics and chat/conversation insights."""
from datetime import datetime, timedelta, date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date, and_, or_, text

from app.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message
from app.api.deps import get_current_user
from app.schemas.analytics import (
    DailyCompletionCount,
    ChatOverviewStats,
    TimelineDataPoint,
    ConversationsTimelineResponse,
    ToolUsageStats,
    ToolUsageResponse,
    MessageRoleStats,
    MessageDistributionResponse,
)

router = APIRouter()


@router.get(
    "/streak-heatmap",
    response_model=List[DailyCompletionCount],
    status_code=status.HTTP_200_OK,
    summary="Get streak heatmap data",
    description="Returns daily task completion counts for the specified time period. Used for rendering contribution-style streak heatmaps.",
)
async def get_streak_heatmap(
    days: int = Query(
        365,
        ge=1,
        le=730,
        description="Number of days to include in the heatmap (max 730 days / 2 years)"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get daily task completion counts for the streak heatmap visualization.

    This endpoint queries completed tasks grouped by completion date
    (updated_at when marked complete) for the specified number of days.

    - **days**: Number of days to include (default: 365, max: 730)
    - Returns array of {date: "YYYY-MM-DD", count: N} objects
    - Only includes tasks owned by the authenticated user
    - Only counts completed tasks (completed=True)

    The frontend can use this data to render a GitHub-style contribution heatmap
    showing task completion activity over time.

    US7: Data isolation - only returns completion data for current user's tasks.
    """
    # Calculate the date range
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)

    # Query completed tasks grouped by date
    # We use updated_at because that's when a task was marked as complete
    # Cast the timestamp to date for grouping
    query = (
        select(
            cast(Task.updated_at, Date).label('completion_date'),
            func.count(Task.id).label('count')
        )
        .where(
            Task.user_id == current_user.id,
            Task.completed == True,
            cast(Task.updated_at, Date) >= start_date,
            cast(Task.updated_at, Date) <= end_date
        )
        .group_by(cast(Task.updated_at, Date))
        .order_by(cast(Task.updated_at, Date))
    )

    result = await db.execute(query)
    rows = result.all()

    # Convert to response format
    heatmap_data = [
        DailyCompletionCount(
            date=str(row.completion_date),
            count=row.count
        )
        for row in rows
    ]

    return heatmap_data


@router.get(
    "/summary",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get task completion summary statistics",
    description="Returns summary statistics including total tasks, completed tasks, completion rate, and streak information.",
)
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get summary statistics for the current user's tasks.

    Returns:
    - **total_tasks**: Total number of tasks
    - **completed_tasks**: Number of completed tasks
    - **pending_tasks**: Number of pending tasks
    - **completion_rate**: Percentage of completed tasks
    - **current_streak**: Current consecutive day streak
    - **longest_streak**: Longest consecutive day streak achieved

    US7: Data isolation - only returns statistics for current user's tasks.
    """
    # Get total task count
    total_query = select(func.count(Task.id)).where(Task.user_id == current_user.id)
    total_result = await db.execute(total_query)
    total_tasks = total_result.scalar() or 0

    # Get completed task count
    completed_query = select(func.count(Task.id)).where(
        Task.user_id == current_user.id,
        Task.completed == True
    )
    completed_result = await db.execute(completed_query)
    completed_tasks = completed_result.scalar() or 0

    pending_tasks = total_tasks - completed_tasks
    completion_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)

    # Calculate streaks by getting all completion dates
    streak_query = select(
        cast(Task.updated_at, Date).label('completion_date')
    ).where(
        Task.user_id == current_user.id,
        Task.completed == True
    ).distinct().order_by(
        cast(Task.updated_at, Date).desc()
    )

    streak_result = await db.execute(streak_query)
    completion_dates = [row[0] for row in streak_result.all()]

    # Calculate current streak
    current_streak = 0
    today = date.today()
    yesterday = today - timedelta(days=1)

    if completion_dates:
        # Check if there's activity today or yesterday to start/continue streak
        if completion_dates[0] in (today, yesterday):
            current_streak = 1
            # Count consecutive days going backwards
            for i in range(len(completion_dates) - 1):
                expected_date = completion_dates[i] - timedelta(days=1)
                if completion_dates[i + 1] == expected_date:
                    current_streak += 1
                else:
                    break

    # Calculate longest streak
    longest_streak = 0
    if completion_dates:
        longest_streak = 1
        current_longest = 1

        for i in range(len(completion_dates) - 1):
            expected_date = completion_dates[i] - timedelta(days=1)
            if completion_dates[i + 1] == expected_date:
                current_longest += 1
                longest_streak = max(longest_streak, current_longest)
            else:
                current_longest = 1

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_rate": completion_rate,
        "current_streak": current_streak,
        "longest_streak": longest_streak
    }


@router.get(
    "/productivity",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get comprehensive productivity analytics",
    description="Returns productivity metrics including completion rate, priority breakdown, and daily completion trends.",
)
async def get_productivity_analytics(
    days: int = Query(
        30,
        ge=1,
        le=365,
        description="Number of days to include in the analysis (max 365 days)"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive productivity analytics for the current user.

    Returns:
    - **period_days**: Number of days in the analysis period
    - **total_completed**: Total tasks completed in the period
    - **completion_rate**: Overall task completion rate percentage
    - **priority_breakdown**: Tasks completed grouped by priority level
    - **daily_completion**: Array of daily completion counts for charting

    US7: Data isolation - only returns analytics for current user's tasks.
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    # Total tasks completed in period
    total_completed_query = select(func.count(Task.id)).where(
        Task.user_id == current_user.id,
        Task.completed == True,
        Task.updated_at >= start_date
    )
    total_completed_result = await db.execute(total_completed_query)
    total_completed = total_completed_result.scalar() or 0

    # Overall completion rate (all time)
    all_tasks_query = select(func.count(Task.id)).where(Task.user_id == current_user.id)
    all_tasks_result = await db.execute(all_tasks_query)
    total_all_time = all_tasks_result.scalar() or 0

    completion_rate = round((total_completed / total_all_time * 100) if total_all_time > 0 else 0, 1)

    # Tasks by priority completed in period
    priority_query = (
        select(Task.priority_id, func.count(Task.id))
        .where(
            Task.user_id == current_user.id,
            Task.completed == True,
            Task.updated_at >= start_date
        )
        .group_by(Task.priority_id)
    )
    priority_result = await db.execute(priority_query)
    priority_stats = priority_result.all()

    # Tasks per day for chart
    from sqlalchemy import extract
    daily_query = (
        select(
            extract('year', Task.updated_at).label('year'),
            extract('month', Task.updated_at).label('month'),
            extract('day', Task.updated_at).label('day'),
            func.count(Task.id).label('count')
        )
        .where(
            Task.user_id == current_user.id,
            Task.completed == True,
            Task.updated_at >= start_date
        )
        .group_by('year', 'month', 'day')
        .order_by('year', 'month', 'day')
    )
    daily_result = await db.execute(daily_query)
    daily_stats = daily_result.all()

    return {
        "period_days": days,
        "total_completed": total_completed,
        "completion_rate": completion_rate,
        "priority_breakdown": {str(p[0]) if p[0] is not None else "none": p[1] for p in priority_stats},
        "daily_completion": [
            {"date": f"{int(d.year)}-{int(d.month):02d}-{int(d.day):02d}", "count": d.count}
            for d in daily_stats
        ]
    }


@router.get(
    "/focus-hours",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Calculate focus hours based on completed tasks",
    description="Returns estimated focus time using the Pomodoro technique (25 minutes per completed task).",
)
async def get_focus_hours(
    days: int = Query(
        30,
        ge=1,
        le=365,
        description="Number of days to include in the analysis (max 365 days)"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate focus hours based on completed tasks using Pomodoro estimation.

    Assumes each completed task represents 25 minutes of focused work (one Pomodoro).
    This provides a rough estimate of productive focus time.

    Returns:
    - **period_days**: Number of days in the analysis period
    - **completed_tasks**: Number of tasks completed in the period
    - **focus_minutes**: Total focus time in minutes
    - **focus_hours**: Total focus time in hours

    US7: Data isolation - only returns analytics for current user's tasks.
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    # Count completed tasks in period
    completed_query = select(func.count(Task.id)).where(
        Task.user_id == current_user.id,
        Task.completed == True,
        Task.updated_at >= start_date
    )
    completed_result = await db.execute(completed_query)
    completed_tasks = completed_result.scalar() or 0

    # Calculate focus time (25 minutes per completed task = Pomodoro)
    focus_minutes = completed_tasks * 25
    focus_hours = round(focus_minutes / 60, 1)

    return {
        "period_days": days,
        "completed_tasks": completed_tasks,
        "focus_minutes": focus_minutes,
        "focus_hours": focus_hours
    }


# ============================================================================
# Chat/Conversation Analytics Endpoints
# ============================================================================


@router.get(
    "/overview",
    response_model=ChatOverviewStats,
    status_code=status.HTTP_200_OK,
    summary="Get chat overview statistics",
    description="Returns summary statistics for conversations and messages including total counts, averages, and tool calls.",
)
async def get_chat_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get overview statistics for the current user's chat conversations.

    Returns:
    - **total_conversations**: Total number of conversations
    - **total_messages**: Total number of messages across all conversations
    - **avg_messages_per_conversation**: Average messages per conversation
    - **total_tool_calls**: Total number of tool calls made by the AI

    Data isolation: Only returns statistics for current user's conversations.
    """
    # Get total conversations count
    conv_query = select(func.count(Conversation.id)).where(
        Conversation.user_id == current_user.id
    )
    conv_result = await db.execute(conv_query)
    total_conversations = conv_result.scalar() or 0

    # Get total messages count (only for user's conversations)
    msg_query = select(func.count(Message.id)).join(
        Conversation, Message.conversation_id == Conversation.id
    ).where(Conversation.user_id == current_user.id)
    msg_result = await db.execute(msg_query)
    total_messages = msg_result.scalar() or 0

    # Calculate average messages per conversation
    avg_messages = (
        round(total_messages / total_conversations, 2)
        if total_conversations > 0
        else 0.0
    )

    # Get total tool calls count
    # Tool calls are stored in the tool_calls JSONB column
    # We need to count the number of tool calls across all assistant messages
    tool_calls_query = text("""
        SELECT COUNT(*)
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE c.user_id = :user_id
        AND m.tool_calls IS NOT NULL
        AND m.tool_calls != '[]'::jsonb
        AND m.tool_calls != 'null'::jsonb
    """)

    tool_result = await db.execute(tool_calls_query, {"user_id": str(current_user.id)})
    total_tool_calls = tool_result.scalar() or 0

    return ChatOverviewStats(
        total_conversations=total_conversations,
        total_messages=total_messages,
        avg_messages_per_conversation=avg_messages,
        total_tool_calls=total_tool_calls,
    )


@router.get(
    "/conversations-timeline",
    response_model=ConversationsTimelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Get conversations timeline data",
    description="Returns time series data of conversations created grouped by day, week, or month.",
)
async def get_conversations_timeline(
    period: str = Query(
        "daily",
        regex="^(daily|weekly|monthly)$",
        description="Time period granularity: daily, weekly, or monthly",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get conversations timeline data for the current user.

    Query Parameters:
    - **period**: daily (last 30 days), weekly (last 12 weeks), or monthly (last 12 months)

    Returns an array of date/count pairs for charting conversation creation over time.

    Data isolation: Only returns data for current user's conversations.
    """
    # Determine date range based on period
    if period == "daily":
        start_date = datetime.utcnow() - timedelta(days=30)
        # Group by day
        date_format = "YYYY-MM-DD"
        date_trunc = "day"
    elif period == "weekly":
        start_date = datetime.utcnow() - timedelta(weeks=12)
        # Group by week (ISO week)
        date_format = "IYYY-IW"  # ISO year and week
        date_trunc = "week"
    else:  # monthly
        start_date = datetime.utcnow() - timedelta(days=365)
        # Group by month
        date_format = "YYYY-MM"
        date_trunc = "month"

    # Build query based on period
    if period == "daily":
        query = text("""
            SELECT
                TO_CHAR(c.created_at, :date_format) as date_label,
                COUNT(*) as count
            FROM conversations c
            WHERE c.user_id = :user_id
            AND c.created_at >= :start_date
            GROUP BY TO_CHAR(c.created_at, :date_format)
            ORDER BY date_label
        """)
    elif period == "weekly":
        query = text("""
            SELECT
                TO_CHAR(c.created_at, :date_format) as date_label,
                COUNT(*) as count
            FROM conversations c
            WHERE c.user_id = :user_id
            AND c.created_at >= :start_date
            GROUP BY TO_CHAR(c.created_at, :date_format)
            ORDER BY date_label
        """)
    else:  # monthly
        query = text("""
            SELECT
                TO_CHAR(c.created_at, :date_format) as date_label,
                COUNT(*) as count
            FROM conversations c
            WHERE c.user_id = :user_id
            AND c.created_at >= :start_date
            GROUP BY TO_CHAR(c.created_at, :date_format)
            ORDER BY date_label
        """)

    result = await db.execute(
        query,
        {
            "user_id": str(current_user.id),
            "start_date": start_date,
            "date_format": date_format,
        },
    )
    rows = result.fetchall()

    # Convert to response format
    timeline_data = [
        TimelineDataPoint(date=row.date_label, count=row.count) for row in rows
    ]

    # Get total count
    total_query = select(func.count(Conversation.id)).where(
        and_(
            Conversation.user_id == current_user.id,
            Conversation.created_at >= start_date,
        )
    )
    total_result = await db.execute(total_query)
    total_conversations = total_result.scalar() or 0

    return ConversationsTimelineResponse(
        period=period,
        data=timeline_data,
        total_conversations=total_conversations,
    )


@router.get(
    "/tool-usage",
    response_model=ToolUsageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get tool usage statistics",
    description="Returns statistics about tool/function calls made by the AI, including most used tools.",
)
async def get_tool_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get tool usage statistics for the current user's conversations.

    Returns:
    - **total_tool_calls**: Total number of tool calls
    - **tool_stats**: Array of tool names with call counts (sorted by count desc)
    - **most_used_tool**: Name of the most frequently called tool

    Tool calls are extracted from the tool_calls JSONB column in assistant messages.
    Each tool_call contains a function object with a name property.

    Data isolation: Only returns data for current user's conversations.
    """
    # Query to extract tool names and count them
    # The tool_calls column contains JSONB like:
    # [{"id": "call_abc", "type": "function", "function": {"name": "get_tasks", ...}}]
    query = text("""
        SELECT
            tool_elem->>'name' as tool_name,
            COUNT(*) as call_count
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        CROSS JOIN jsonb_array_elements(m.tool_calls) as tool_elem
        WHERE c.user_id = :user_id
        AND m.tool_calls IS NOT NULL
        GROUP BY tool_elem->>'name'
        ORDER BY call_count DESC
    """)

    result = await db.execute(query, {"user_id": str(current_user.id)})
    rows = result.fetchall()

    # Build tool stats array
    tool_stats = [
        ToolUsageStats(tool_name=row.tool_name, call_count=row.call_count)
        for row in rows
    ]

    # Calculate total
    total_tool_calls = sum(stat.call_count for stat in tool_stats)

    # Get most used tool
    most_used_tool = tool_stats[0].tool_name if tool_stats else None

    return ToolUsageResponse(
        total_tool_calls=total_tool_calls,
        tool_stats=tool_stats,
        most_used_tool=most_used_tool,
    )


@router.get(
    "/message-distribution",
    response_model=MessageDistributionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get message distribution by role",
    description="Returns breakdown of messages by role (user, assistant, system, tool) with percentages.",
)
async def get_message_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get message distribution by role for the current user's conversations.

    Returns:
    - **total_messages**: Total number of messages
    - **distribution**: Array of message counts per role with percentages

    Message roles:
    - **user**: Messages sent by the user
    - **assistant**: Responses from the AI assistant
    - **system**: System prompt messages
    - **tool**: Tool response messages

    Data isolation: Only returns data for current user's conversations.
    """
    # Get total messages count first
    total_query = select(func.count(Message.id)).join(
        Conversation, Message.conversation_id == Conversation.id
    ).where(Conversation.user_id == current_user.id)
    total_result = await db.execute(total_query)
    total_messages = total_result.scalar() or 0

    if total_messages == 0:
        return MessageDistributionResponse(
            total_messages=0,
            distribution=[],
        )

    # Get count by role
    role_query = text("""
        SELECT
            m.role,
            COUNT(*) as count
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE c.user_id = :user_id
        GROUP BY m.role
        ORDER BY count DESC
    """)

    role_result = await db.execute(role_query, {"user_id": str(current_user.id)})
    rows = role_result.fetchall()

    # Build distribution with percentages
    distribution = [
        MessageRoleStats(
            role=row.role,
            count=row.count,
            percentage=round((row.count / total_messages) * 100, 2),
        )
        for row in rows
    ]

    return MessageDistributionResponse(
        total_messages=total_messages,
        distribution=distribution,
    )
