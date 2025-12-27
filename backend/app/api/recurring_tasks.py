"""RecurringTask API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.recurring_task import (
    RecurringTaskCreate,
    RecurringTaskUpdate,
    RecurringTaskResponse,
    RecurringTaskListResponse,
    RecurringTaskPauseResponse,
)
from app.crud import recurring_task as recurring_task_crud
from app.api.deps import get_current_user
from app.utils.exceptions import NotFoundException, ValidationException

router = APIRouter()


@router.post(
    "",
    response_model=RecurringTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new recurring task",
    description="Create a new recurring task for the authenticated user",
)
async def create_recurring_task(
    task_data: RecurringTaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new recurring task.

    - **title**: Recurring task title (required, max 500 chars)
    - **description**: Recurring task description (optional, max 5000 chars)
    - **recurrence_pattern**: Pattern for recurrence (daily, weekly, monthly, yearly)
    - **start_date**: When to start creating tasks from this recurring task
    - **end_date**: Optional end date for the recurrence
    - **task_priority_id**: Priority ID (1=Low, 2=Medium, 3=High)

    Returns the created recurring task with is_active=True by default.
    """
    new_task = await recurring_task_crud.create_recurring_task(
        db, task_data, str(current_user.id)
    )
    return new_task


@router.get(
    "",
    response_model=List[RecurringTaskResponse],
    summary="Get all recurring tasks for current user",
    description="Retrieve all recurring tasks belonging to the authenticated user with optional filtering and sorting",
)
async def get_recurring_tasks(
    active_only: Optional[bool] = Query(
        False,
        description="If true, only return active recurring tasks"
    ),
    sort_by: Optional[str] = Query(
        "created_at",
        description="Field to sort by: 'created_at', 'next_due_at', or 'title'"
    ),
    sort_order: Optional[str] = Query(
        "desc",
        description="Sort order: 'asc' or 'desc'"
    ),
    limit: Optional[int] = Query(
        20,
        ge=1,
        le=100,
        description="Number of recurring tasks to return (max 100)"
    ),
    offset: Optional[int] = Query(
        0,
        ge=0,
        description="Number of recurring tasks to skip (for pagination)"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all recurring tasks for the current user with optional filtering and sorting.

    - **active_only**: Filter to only show active recurring tasks
    - **sort_by**: Field to sort recurring tasks by (default: created_at)
    - **sort_order**: Sort direction (default: desc for newest first)
    - **limit**: Maximum number of results to return
    - **offset**: Number of results to skip for pagination

    Data isolation - only returns recurring tasks owned by current user.
    """
    tasks = await recurring_task_crud.get_recurring_tasks_by_user(
        db=db,
        user_id=str(current_user.id),
        active_only=active_only,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )
    return tasks


@router.get(
    "/{recurring_task_id}",
    response_model=RecurringTaskResponse,
    summary="Get a specific recurring task",
    description="Retrieve a single recurring task by ID (must belong to current user)",
)
async def get_recurring_task(
    recurring_task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific recurring task by ID.

    - **recurring_task_id**: Recurring task ID

    Data isolation - only returns recurring task if owned by current user.
    Returns 404 if recurring task doesn't exist or doesn't belong to user.
    """
    task = await recurring_task_crud.get_recurring_task_by_id(
        db, recurring_task_id, str(current_user.id)
    )
    if not task:
        raise NotFoundException(
            detail=f"Recurring task {recurring_task_id} not found"
        )
    return task


@router.put(
    "/{recurring_task_id}",
    response_model=RecurringTaskResponse,
    summary="Update a recurring task",
    description="Update recurring task details",
)
async def update_recurring_task(
    recurring_task_id: int,
    task_data: RecurringTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a recurring task's details.

    - **recurring_task_id**: Recurring task ID
    - **title**: New title (optional)
    - **description**: New description (optional)
    - **recurrence_pattern**: New recurrence pattern (optional)
    - **start_date**: New start date (optional)
    - **end_date**: New end date (optional)
    - **is_active**: Pause or resume the recurring task
    - **task_priority_id**: New priority ID (optional)

    At least one field must be provided.
    Data isolation - only allows updating recurring tasks owned by current user.
    """
    # Verify recurring task exists and belongs to user
    task = await recurring_task_crud.get_recurring_task_by_id(
        db, recurring_task_id, str(current_user.id)
    )
    if not task:
        raise NotFoundException(
            detail=f"Recurring task {recurring_task_id} not found"
        )

    # Validate at least one field is being updated
    update_data = task_data.model_dump(exclude_unset=True)
    if not update_data:
        raise ValidationException(
            detail="At least one field must be provided for update"
        )

    # Validate end_date is after start_date if both are provided
    if task_data.end_date is not None and task_data.start_date is not None:
        if task_data.end_date <= task_data.start_date:
            raise ValidationException(
                detail="end_date must be after start_date"
            )

    # Update recurring task
    updated_task = await recurring_task_crud.update_recurring_task(
        db, task, task_data
    )
    return updated_task


@router.delete(
    "/{recurring_task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recurring task",
    description="Permanently delete a recurring task",
)
async def delete_recurring_task(
    recurring_task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a recurring task permanently.

    - **recurring_task_id**: Recurring task ID

    Returns 204 No Content on success.
    Note: This will NOT delete any tasks that were already created from this recurring task.
    Data isolation - only allows deleting recurring tasks owned by current user.
    """
    # Verify recurring task exists and belongs to user
    task = await recurring_task_crud.get_recurring_task_by_id(
        db, recurring_task_id, str(current_user.id)
    )
    if not task:
        raise NotFoundException(
            detail=f"Recurring task {recurring_task_id} not found"
        )

    # Delete recurring task
    await recurring_task_crud.delete_recurring_task(db, task)


@router.post(
    "/{recurring_task_id}/pause",
    response_model=RecurringTaskPauseResponse,
    summary="Pause a recurring task",
    description="Pause a recurring task (sets is_active to False)",
)
async def pause_recurring_task(
    recurring_task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Pause a recurring task.

    - **recurring_task_id**: Recurring task ID

    Sets is_active to False, preventing new tasks from being generated.
    Data isolation - only allows pausing recurring tasks owned by current user.
    """
    # Verify recurring task exists and belongs to user
    task = await recurring_task_crud.get_recurring_task_by_id(
        db, recurring_task_id, str(current_user.id)
    )
    if not task:
        raise NotFoundException(
            detail=f"Recurring task {recurring_task_id} not found"
        )

    # Check if already paused
    if not task.is_active:
        return RecurringTaskPauseResponse(
            id=task.id,
            is_active=task.is_active,
            next_due_at=task.next_due_at,
            message="Recurring task is already paused"
        )

    # Pause recurring task
    updated_task = await recurring_task_crud.pause_recurring_task(db, task)

    return RecurringTaskPauseResponse(
        id=updated_task.id,
        is_active=updated_task.is_active,
        next_due_at=updated_task.next_due_at,
        message="Recurring task paused successfully"
    )


@router.post(
    "/{recurring_task_id}/resume",
    response_model=RecurringTaskPauseResponse,
    summary="Resume a paused recurring task",
    description="Resume a paused recurring task (sets is_active to True and recalculates next_due_at if needed)",
)
async def resume_recurring_task(
    recurring_task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Resume a paused recurring task.

    - **recurring_task_id**: Recurring task ID

    Sets is_active to True and recalculates next_due_at if it was in the past.
    Data isolation - only allows resuming recurring tasks owned by current user.
    """
    # Verify recurring task exists and belongs to user
    task = await recurring_task_crud.get_recurring_task_by_id(
        db, recurring_task_id, str(current_user.id)
    )
    if not task:
        raise NotFoundException(
            detail=f"Recurring task {recurring_task_id} not found"
        )

    # Check if already active
    if task.is_active:
        return RecurringTaskPauseResponse(
            id=task.id,
            is_active=task.is_active,
            next_due_at=task.next_due_at,
            message="Recurring task is already active"
        )

    # Resume recurring task
    updated_task = await recurring_task_crud.resume_recurring_task(db, task)

    return RecurringTaskPauseResponse(
        id=updated_task.id,
        is_active=updated_task.is_active,
        next_due_at=updated_task.next_due_at,
        message="Recurring task resumed successfully"
    )


@router.get(
    "/stats/count",
    response_model=dict,
    summary="Get recurring task count",
    description="Get the count of recurring tasks for the current user",
)
async def get_recurring_task_count(
    active_only: Optional[bool] = Query(
        False,
        description="If true, only count active recurring tasks"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the count of recurring tasks for the current user.

    - **active_only**: If true, only count active recurring tasks

    Returns a JSON object with the count.
    """
    count = await recurring_task_crud.count_recurring_tasks_by_user(
        db, str(current_user.id), active_only
    )
    return {"count": count}
