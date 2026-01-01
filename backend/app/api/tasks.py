"""Task API endpoints."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, status, Query, Body, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
import json
import os
import sys
import asyncio

from app.database import get_db
from app.models.user import User
from app.models.task_event_log import TaskEventLog
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.crud import task as task_crud
from app.api.deps import get_current_user
from app.utils.exceptions import NotFoundException, ForbiddenException, ValidationException

router = APIRouter()

# Event publishing helper (fire and forget)
import logging
task_logger = logging.getLogger(__name__)

async def _publish_event_later(event_type: str, task_data: Dict[str, Any]):
    """Publish event in background without blocking response."""
    print(f"[EVENT] Publishing {event_type} event for task {task_data.get('task_id')}", file=sys.stderr)
    try:
        from app.services.event_publisher import dapr_event_publisher
        if event_type == "created":
            result = await dapr_event_publisher.publish_task_created(task_data)
        elif event_type == "updated":
            result = await dapr_event_publisher.publish_task_updated(task_data)
        elif event_type == "completed":
            result = await dapr_event_publisher.publish_task_completed(task_data)
        elif event_type == "deleted":
            result = await dapr_event_publisher.publish_task_deleted(task_data)
        else:
            result = False

        if result:
            print(f"[EVENT] Successfully published {event_type} event", file=sys.stderr)
        else:
            print(f"[EVENT] Failed to publish {event_type} event (returned False)", file=sys.stderr)
    except Exception as e:
        # Log but don't fail the request
        print(f"[EVENT] Event publishing failed for {event_type}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

async def _log_event(db: AsyncSession, task_id: int, event_type: str, event_data: Dict[str, Any]):
    """Log event to TaskEventLog table."""
    try:
        event_log = TaskEventLog(
            task_id=task_id,
            event_type=event_type,
            event_data=event_data
        )
        db.add(event_log)
        await db.flush()  # Don't commit, just flush
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Event logging failed for {event_type}: {e}")

def _task_to_dict(task) -> Dict[str, Any]:
    """Convert Task model to dict for event publishing."""
    return {
        "task_id": task.id,
        "user_id": str(task.user_id),  # Convert UUID to string for JSON serialization
        "title": task.title,
        "description": task.description,
        "priority_id": task.priority_id,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "completed": task.completed,
        "is_recurring": task.is_recurring,
        "recurrence_pattern": task.recurrence_pattern,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


# Schema for quick add request
class QuickAddRequest(BaseModel):
    """Schema for quick add task request."""
    text: str = Field(..., min_length=1, max_length=500, description="Natural language task description")


# Schema for task breakdown request/response
class TaskBreakdownRequest(BaseModel):
    """Schema for task breakdown request."""
    task_title: str = Field(..., min_length=10, max_length=500, description="Task title to break down")


class SubtaskResponse(BaseModel):
    """Schema for a single subtask in breakdown response."""
    title: str = Field(..., description="Subtask title")
    description: Optional[str] = Field(None, description="Brief description of the subtask")


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the authenticated user",
)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new task.

    - **title**: Task title (required, max 500 chars)
    - **description**: Task description (optional, max 10000 chars)

    Returns the created task with completed=False by default.
    """
    print("=" * 60, file=sys.stderr)
    print("CREATE_TASK CALLED - NEW CODE WITH BackgroundTasks", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    new_task = await task_crud.create_task(db, task_data, str(current_user.id))

    # Log event to database
    task_dict = _task_to_dict(new_task)
    print("About to call _log_event...", file=sys.stderr)
    await _log_event(db, new_task.id, "created", task_dict)
    print("_log_event completed", file=sys.stderr)

    # Publish event (fire and forget - don't block response)
    print("[EVENT] Scheduling background task for event publishing", file=sys.stderr)
    background_tasks.add_task(_publish_event_later, "created", task_dict)
    print("[EVENT] Background task scheduled", file=sys.stderr)

    return new_task


@router.get(
    "",
    response_model=List[TaskResponse],
    summary="Get all tasks for current user",
    description="Retrieve all tasks belonging to the authenticated user with optional filtering and sorting",
)
async def get_tasks(
    search: Optional[str] = Query(None, description="Search term to filter by title or description"),
    status: Optional[str] = Query(None, description="Filter by status: 'completed' or 'pending'"),
    priority: Optional[str] = Query(None, description="Filter by priority: 'low', 'medium', or 'high'"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by: 'created_at', 'due_date', 'priority', or 'title'"),
    sort_order: Optional[str] = Query("desc", description="Sort order: 'asc' or 'desc'"),
    limit: Optional[int] = Query(20, ge=1, le=100, description="Number of tasks to return (max 100)"),
    offset: Optional[int] = Query(0, ge=0, description="Number of tasks to skip (for pagination)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all tasks for the current user with optional filtering and sorting.

    - **search**: Filter tasks by title or description (case-insensitive)
    - **status**: Filter by completion status ("completed" or "pending")
    - **priority**: Filter by priority level ("low", "medium", or "high")
    - **sort_by**: Field to sort tasks by (default: created_at)
    - **sort_order**: Sort direction (default: desc for newest first)

    US6: Data isolation - only returns tasks owned by current user.
    """
    # Convert priority string to ID if provided
    priority_id = None
    if priority:
        priority_map = {"low": 1, "medium": 2, "high": 3}
        priority_id = priority_map.get(priority.lower())

    tasks = await task_crud.get_tasks_by_user(
        db=db,
        user_id=str(current_user.id),
        search=search,
        status=status,
        priority=priority_id,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )
    return tasks


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a specific task",
    description="Retrieve a single task by ID (must belong to current user)",
)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific task by ID.

    - **task_id**: Task ID

    US6: Data isolation - only returns task if owned by current user.
    Returns 404 if task doesn't exist or doesn't belong to user.
    """
    task = await task_crud.get_task_by_id(db, task_id, str(current_user.id))
    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description="Update task title and/or description",
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a task's details.

    - **task_id**: Task ID
    - **title**: New title (optional)
    - **description**: New description (optional)

    At least one field must be provided.
    US6: Data isolation - only allows updating tasks owned by current user.
    """
    # Verify task exists and belongs to user
    task = await task_crud.get_task_by_id(db, task_id, str(current_user.id))
    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")

    # Validate at least one field is provided
    if task_data.title is None and task_data.description is None:
        raise ValidationException(detail="At least one field (title or description) must be provided")

    # Update task
    updated_task = await task_crud.update_task(db, task, task_data)

    # Log event to database
    task_dict = _task_to_dict(updated_task)
    await _log_event(db, updated_task.id, "updated", task_dict)

    # Publish event (fire and forget)
    background_tasks.add_task(_publish_event_later, "updated", task_dict)

    return updated_task


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Toggle task completion status",
    description="Mark task as complete or incomplete",
)
async def toggle_task_completion(
    task_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Toggle task completion status.

    - **task_id**: Task ID

    If completed=False, sets to True. If completed=True, sets to False.
    US6: Data isolation - only allows toggling tasks owned by current user.
    """
    # Verify task exists and belongs to user
    task = await task_crud.get_task_by_id(db, task_id, str(current_user.id))
    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")

    # Toggle completion
    updated_task = await task_crud.toggle_task_completion(db, task)

    # Only log and publish if task was completed (not un-completed)
    if updated_task.completed:
        # Log event to database
        task_dict = _task_to_dict(updated_task)
        await _log_event(db, updated_task.id, "completed", task_dict)

        # Publish event (fire and forget)
        background_tasks.add_task(_publish_event_later, "completed", task_dict)

    return updated_task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently delete a task",
)
async def delete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a task permanently.

    - **task_id**: Task ID

    Returns 204 No Content on success.
    US6: Data isolation - only allows deleting tasks owned by current user.
    """
    # Verify task exists and belongs to user
    task = await task_crud.get_task_by_id(db, task_id, str(current_user.id))
    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")

    # Capture task data before deletion
    task_dict = _task_to_dict(task)

    # Delete task
    await task_crud.delete_task(db, task)

    # Log event to database (after task is deleted from tasks table but event log remains)
    await _log_event(db, task_id, "deleted", task_dict)

    # Publish event (fire and forget)
    background_tasks.add_task(_publish_event_later, "deleted", task_dict)


@router.post(
    "/breakdown",
    response_model=List[SubtaskResponse],
    status_code=status.HTTP_200_OK,
    summary="AI Task Breakdown",
    description="Use AI to break down a large task into smaller actionable subtasks",
)
async def breakdown_task(
    request: TaskBreakdownRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Use AI to break down a large task into smaller actionable subtasks.

    - **task_title**: The title of the task to break down (min 10 characters)

    Returns a list of 3-7 subtasks, each with:
    - title: Specific subtask title
    - description: Brief description (optional)

    The AI generates subtasks that are:
    - Specific and concrete
    - Can be completed in 1-2 hours
    - Ordered logically

    Uses Groq API for fast AI-powered task breakdown.
    """
    task_title = request.task_title

    # Create prompt for AI
    prompt = f"""Break down the following task into 3-7 smaller, actionable subtasks.
Each subtask should be:
- Specific and concrete
- Something that can be completed in 1-2 hours
- Ordered logically (what needs to be done first)

Task: {task_title}

Respond ONLY with a JSON array of objects, each with:
- title: subtask title
- description: brief description (optional)

Example format:
[
  {{"title": "Research topic", "description": "Gather information"}},
  {{"title": "Create outline", "description": "Structure content"}}
]

Return ONLY valid JSON, no other text, no markdown code blocks."""

    try:
        # Import Groq client
        from groq import Groq
        from app.config import settings

        # Use Groq API directly for faster response
        client = Groq(api_key=settings.groq_api_key)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a task breakdown assistant. Always respond with valid JSON arrays only. Never include markdown code blocks or explanatory text."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content.strip()

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
                result = result.strip()

            parsed = json.loads(result)

            # Handle if AI returns a dict with 'subtasks' or similar key
            if isinstance(parsed, dict):
                # Try to find the list in common keys
                for key in ["subtasks", "tasks", "items", "breakdown"]:
                    if key in parsed and isinstance(parsed[key], list):
                        parsed = parsed[key]
                        break
                else:
                    # If no list key found, treat the dict values as potential subtasks
                    parsed = [{"title": k, "description": str(v)} for k, v in parsed.items() if k != ""]

            # Validate we have a list
            if not isinstance(parsed, list):
                raise ValueError("Response is not a list")

            subtasks = []
            for item in parsed:
                if isinstance(item, dict):
                    title = item.get("title", "")
                    description = item.get("description")
                    if title:
                        subtasks.append(SubtaskResponse(title=title, description=description))
                elif isinstance(item, str):
                    # Handle simple string items
                    subtasks.append(SubtaskResponse(title=item, description=None))

            # Ensure we have at least some subtasks
            if not subtasks:
                raise ValueError("No valid subtasks generated")

            return subtasks

        except (json.JSONDecodeError, ValueError) as parse_error:
            print(f"Parse error: {parse_error}, result was: {result[:200]}")
            # Fallback: create simple breakdown
            return _create_fallback_breakdown(task_title)

    except Exception as e:
        # Log error for debugging
        print(f"AI breakdown error: {type(e).__name__}: {str(e)}")
        # Fallback to simple breakdown
        return _create_fallback_breakdown(task_title)


def _create_fallback_breakdown(task_title: str) -> List[SubtaskResponse]:
    """
    Create a simple fallback breakdown when AI is unavailable.
    """
    return [
        SubtaskResponse(title=f"Plan: {task_title[:50]}...", description="Create a detailed plan and gather requirements"),
        SubtaskResponse(title=f"Execute: {task_title[:50]}...", description="Complete the main work according to the plan"),
        SubtaskResponse(title=f"Review: {task_title[:50]}...", description="Check results and refine as needed"),
    ]


@router.post(
    "/quick-add",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Quick add a task using natural language",
    description="Parse natural language input to create a task with title, priority, due date, and recurrence",
)
async def quick_add_task(
    request: QuickAddRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick add a task by parsing natural language.

    Parses natural language input to extract:
    - **Title**: The main task description
    - **Priority**: urgent/important (high), low (low), default medium
    - **Due date**: today, tomorrow, Monday, next Friday, in 3 days, in 2 weeks
    - **Recurrence**: daily, weekly, monthly, yearly

    Examples:
    - "Call mom tomorrow urgent" -> High priority, due tomorrow
    - "Submit report by Friday important" -> High priority, due Friday
    - "Weekly team meeting every Monday" -> Recurring weekly task

    Returns the created task.
    """
    from app.services.natural_language import NaturalLanguageParser

    # Parse the natural language input
    parsed = NaturalLanguageParser.parse(request.text)

    # Create task from parsed data
    task_data = TaskCreate(**parsed)
    task = await task_crud.create_task(db, task_data, str(current_user.id))

    return task
