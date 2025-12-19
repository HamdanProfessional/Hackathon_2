"""Task CRUD operations."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, asc, desc
from sqlalchemy.orm import selectinload

from app.models.task import Task, Priority
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, task_data: TaskCreate, user_id: str) -> Task:
    """
    Create a new task for a user.

    Args:
        db: Database session
        task_data: Task creation data
        user_id: Owner user ID (UUID string)

    Returns:
        Created task instance
    """
    db_task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description or "",
        priority_id=task_data.priority_id,
        due_date=task_data.due_date,
        completed=False,
        is_recurring=False,
    )

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    # Re-fetch with eager loading to prevent DetachedInstanceError
    stmt = select(Task).where(Task.id == db_task.id).options(selectinload(Task.priority_obj))
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_tasks_by_user(
    db: AsyncSession,
    user_id: str,
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    limit: Optional[int] = 20,
    offset: Optional[int] = 0
) -> List[Task]:
    """
    Get all tasks for a specific user with optional filtering and sorting.

    Args:
        db: Database session
        user_id: User ID (UUID string) to filter by
        search: Optional search term to filter by title or description
        status: Optional status filter ("completed" or "pending")
        priority: Optional priority filter (1=Low, 2=Medium, 3=High)
        sort_by: Field to sort by (created_at, due_date, priority_id, title)
        sort_order: Sort order ("asc" or "desc")

    Returns:
        List of user's tasks matching the criteria
    """
    # Start with base query with relationship loading
    query = select(Task).options(selectinload(Task.priority_obj)).where(Task.user_id == user_id)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term)
            )
        )

    # Apply status filter
    if status == "completed":
        query = query.where(Task.completed == True)
    elif status == "pending":
        query = query.where(Task.completed == False)

    # Apply priority filter
    if priority and priority in [1, 2, 3]:
        query = query.where(Task.priority_id == priority)

    # Apply sorting with proper field handling and null management
    if sort_by == "due_date":
        # Sort by due_date, putting tasks with NO due date at the bottom
        if sort_order == "asc":
            query = query.order_by(asc(Task.due_date).nulls_last())
        else:
            query = query.order_by(desc(Task.due_date).nulls_last())
    elif sort_by == "priority":
        # Sort by priority level (join with priorities table to get level)
        query = query.order_by(desc(Task.priority_id) if sort_order == "desc" else asc(Task.priority_id))
    elif sort_by == "title":
        # Sort by title
        if sort_order == "asc":
            query = query.order_by(asc(Task.title))
        else:
            query = query.order_by(desc(Task.title))
    else:
        # Default: Sort by created_at
        if sort_order == "asc":
            query = query.order_by(asc(Task.created_at))
        else:
            query = query.order_by(desc(Task.created_at))

    # Apply pagination
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()


async def get_task_by_id(db: AsyncSession, task_id: int, user_id: str) -> Optional[Task]:
    """
    Get a specific task by ID, ensuring it belongs to the user.

    Args:
        db: Database session
        task_id: Task ID
        user_id: User ID (UUID string) to verify ownership

    Returns:
        Task instance if found and owned by user, None otherwise
    """
    result = await db.execute(
        select(Task).options(selectinload(Task.priority_obj)).where(Task.id == task_id, Task.user_id == user_id)
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
    if task_data.priority_id is not None:
        task.priority_id = task_data.priority_id
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    if task_data.completed is not None:
        task.completed = task_data.completed

    await db.commit()
    await db.refresh(task)

    # Re-fetch with eager loading to prevent DetachedInstanceError
    stmt = select(Task).where(Task.id == task.id).options(selectinload(Task.priority_obj))
    result = await db.execute(stmt)
    return result.scalar_one()


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

    # Re-fetch with eager loading to prevent DetachedInstanceError
    stmt = select(Task).where(Task.id == task.id).options(selectinload(Task.priority_obj))
    result = await db.execute(stmt)
    return result.scalar_one()


async def delete_task(db: AsyncSession, task: Task) -> None:
    """
    Delete a task.

    Args:
        db: Database session
        task: Task instance to delete
    """
    await db.delete(task)
    await db.commit()
