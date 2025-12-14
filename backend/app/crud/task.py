"""Task CRUD operations."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, task_data: TaskCreate, user_id: int) -> Task:
    """
    Create a new task for a user.

    Args:
        db: Database session
        task_data: Task creation data
        user_id: Owner user ID

    Returns:
        Created task instance
    """
    db_task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description or "",
    )

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    return db_task


async def get_tasks_by_user(db: AsyncSession, user_id: int) -> List[Task]:
    """
    Get all tasks for a specific user.

    Args:
        db: Database session
        user_id: User ID to filter by

    Returns:
        List of user's tasks
    """
    result = await db.execute(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
    )
    return result.scalars().all()


async def get_task_by_id(db: AsyncSession, task_id: int, user_id: int) -> Optional[Task]:
    """
    Get a specific task by ID, ensuring it belongs to the user.

    Args:
        db: Database session
        task_id: Task ID
        user_id: User ID to verify ownership

    Returns:
        Task instance if found and owned by user, None otherwise
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_task(
    db: AsyncSession, task: Task, task_data: TaskUpdate
) -> Task:
    """
    Update a task's details.

    Args:
        db: Database session
        task: Task instance to update
        task_data: Updated task data

    Returns:
        Updated task instance
    """
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description

    await db.commit()
    await db.refresh(task)

    return task


async def toggle_task_completion(db: AsyncSession, task: Task) -> Task:
    """
    Toggle task completion status.

    Args:
        db: Database session
        task: Task instance to toggle

    Returns:
        Updated task instance
    """
    task.completed = not task.completed

    await db.commit()
    await db.refresh(task)

    return task


async def delete_task(db: AsyncSession, task: Task) -> None:
    """
    Delete a task.

    Args:
        db: Database session
        task: Task instance to delete
    """
    await db.delete(task)
    await db.commit()
