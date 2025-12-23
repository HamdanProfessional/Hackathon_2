"""Subtask API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.subtask import Subtask
from app.schemas.subtask import SubtaskCreate, SubtaskResponse
from app.api.deps import get_current_user
from app.utils.exceptions import NotFoundException, ForbiddenException

router = APIRouter()


class SubtaskUpdateRequest(BaseModel):
    """Schema for subtask update request (simple completion toggle)."""
    completed: bool


@router.get(
    "/tasks/{task_id}/subtasks",
    response_model=List[SubtaskResponse],
    summary="Get all subtasks for a task",
    description="Retrieve all subtasks belonging to a specific task (must belong to current user)",
)
async def get_subtasks(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all subtasks for a specific task.

    - **task_id**: Task ID
    - Returns subtasks ordered by sort_order

    Data isolation - only returns subtasks for tasks owned by current user.
    Returns 404 if task doesn't exist or doesn't belong to user.
    """
    # Verify task exists and belongs to user
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")

    # Get subtasks ordered by sort_order
    result = await db.execute(
        select(Subtask)
        .where(Subtask.task_id == task_id)
        .order_by(Subtask.sort_order, Subtask.id)
    )
    subtasks = result.scalars().all()
    return subtasks


@router.post(
    "/tasks/{task_id}/subtasks",
    response_model=SubtaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new subtask",
    description="Create a new subtask for a specific task",
)
async def create_subtask(
    task_id: int,
    subtask_data: SubtaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new subtask.

    - **task_id**: Task ID to add the subtask to
    - **title**: Subtask title (required, max 500 chars)
    - **description**: Subtask description (optional, max 2000 chars)

    Data isolation - only allows creating subtasks for tasks owned by current user.
    """
    # Verify task exists and belongs to user
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")

    # Get max sort_order for this task
    result = await db.execute(
        select(Subtask.sort_order)
        .where(Subtask.task_id == task_id)
        .order_by(Subtask.sort_order.desc())
        .limit(1)
    )
    max_order = result.scalar_one_or_none()

    # Create new subtask
    new_subtask = Subtask(
        task_id=task_id,
        title=subtask_data.title,
        description=subtask_data.description,
        sort_order=(max_order + 1 if max_order is not None else 0)
    )

    db.add(new_subtask)
    await db.commit()
    await db.refresh(new_subtask)

    return new_subtask


@router.patch(
    "/subtasks/{subtask_id}",
    response_model=SubtaskResponse,
    summary="Update a subtask",
    description="Update subtask completion status or other fields",
)
async def update_subtask(
    subtask_id: int,
    completed: bool = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a subtask (typically completion status).

    - **subtask_id**: Subtask ID
    - **completed**: New completion status

    Data isolation - only allows updating subtasks for tasks owned by current user.
    """
    # Get subtask
    result = await db.execute(
        select(Subtask).where(Subtask.id == subtask_id)
    )
    subtask = result.scalar_one_or_none()

    if not subtask:
        raise NotFoundException(detail=f"Subtask {subtask_id} not found")

    # Verify task belongs to user
    result = await db.execute(
        select(Task).where(Task.id == subtask.task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise ForbiddenException(detail="You do not have permission to update this subtask")

    # Update subtask
    subtask.completed = completed
    await db.commit()
    await db.refresh(subtask)

    return subtask


@router.delete(
    "/subtasks/{subtask_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a subtask",
    description="Permanently delete a subtask",
)
async def delete_subtask(
    subtask_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a subtask permanently.

    - **subtask_id**: Subtask ID

    Returns 204 No Content on success.
    Data isolation - only allows deleting subtasks for tasks owned by current user.
    """
    # Get subtask
    result = await db.execute(
        select(Subtask).where(Subtask.id == subtask_id)
    )
    subtask = result.scalar_one_or_none()

    if not subtask:
        raise NotFoundException(detail=f"Subtask {subtask_id} not found")

    # Verify task belongs to user
    result = await db.execute(
        select(Task).where(Task.id == subtask.task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise ForbiddenException(detail="You do not have permission to delete this subtask")

    # Delete subtask
    await db.delete(subtask)
    await db.commit()
