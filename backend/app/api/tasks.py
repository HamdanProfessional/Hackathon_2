"""Task API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.crud import task as task_crud
from app.api.deps import get_current_user
from app.utils.exceptions import NotFoundException, ForbiddenException, ValidationException

router = APIRouter()


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the authenticated user",
)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new task.

    - **title**: Task title (required, max 500 chars)
    - **description**: Task description (optional, max 10000 chars)

    Returns the created task with completed=False by default.
    """
    new_task = await task_crud.create_task(db, task_data, current_user.id)
    return new_task


@router.get(
    "",
    response_model=List[TaskResponse],
    summary="Get all tasks for current user",
    description="Retrieve all tasks belonging to the authenticated user",
)
async def get_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all tasks for the current user.

    Returns tasks ordered by creation date (newest first).
    US6: Data isolation - only returns tasks owned by current user.
    """
    tasks = await task_crud.get_tasks_by_user(db, current_user.id)
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
    task = await task_crud.get_task_by_id(db, task_id, current_user.id)
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
    task = await task_crud.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")

    # Validate at least one field is provided
    if task_data.title is None and task_data.description is None:
        raise ValidationException(detail="At least one field (title or description) must be provided")

    # Update task
    updated_task = await task_crud.update_task(db, task, task_data)
    return updated_task


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Toggle task completion status",
    description="Mark task as complete or incomplete",
)
async def toggle_task_completion(
    task_id: int,
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
    task = await task_crud.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")

    # Toggle completion
    updated_task = await task_crud.toggle_task_completion(db, task)
    return updated_task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently delete a task",
)
async def delete_task(
    task_id: int,
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
    task = await task_crud.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")

    # Delete task
    await task_crud.delete_task(db, task)
