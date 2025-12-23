"""TaskTemplate CRUD operations."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, desc
from sqlalchemy.orm import selectinload

from app.models.task_template import TaskTemplate
from app.schemas.task_template import TaskTemplateCreate, TaskTemplateUpdate


async def create_template(
    db: AsyncSession,
    template_data: TaskTemplateCreate,
    user_id: str
) -> TaskTemplate:
    """
    Create a new task template for a user.

    Args:
        db: Database session
        template_data: Template creation data
        user_id: Owner user ID (UUID string)

    Returns:
        Created template instance
    """
    db_template = TaskTemplate(
        user_id=user_id,
        title=template_data.title,
        description=template_data.description,
        priority_id=template_data.priority_id,
        is_recurring=template_data.is_recurring,
        recurrence_pattern=template_data.recurrence_pattern,
        tags=template_data.tags,
        subtasks_template=template_data.subtasks,
    )

    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)

    # Re-fetch with eager loading
    stmt = (
        select(TaskTemplate)
        .where(TaskTemplate.id == db_template.id)
        .options(selectinload(TaskTemplate.owner))
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_templates_by_user(
    db: AsyncSession,
    user_id: str,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 100,
    offset: int = 0
) -> List[TaskTemplate]:
    """
    Get all task templates for a specific user.

    Args:
        db: Database session
        user_id: User ID (UUID string) to filter by
        sort_by: Field to sort by (created_at, updated_at, title)
        sort_order: Sort order ("asc" or "desc")
        limit: Maximum number of templates to return
        offset: Number of templates to skip

    Returns:
        List of user's templates
    """
    # Start with base query with relationship loading
    query = (
        select(TaskTemplate)
        .options(selectinload(TaskTemplate.owner))
        .where(TaskTemplate.user_id == user_id)
    )

    # Apply sorting
    if sort_by == "title":
        if sort_order == "asc":
            query = query.order_by(asc(TaskTemplate.title))
        else:
            query = query.order_by(desc(TaskTemplate.title))
    elif sort_by == "updated_at":
        if sort_order == "asc":
            query = query.order_by(asc(TaskTemplate.updated_at))
        else:
            query = query.order_by(desc(TaskTemplate.updated_at))
    else:
        # Default: Sort by created_at
        if sort_order == "asc":
            query = query.order_by(asc(TaskTemplate.created_at))
        else:
            query = query.order_by(desc(TaskTemplate.created_at))

    # Apply pagination
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()


async def get_template_by_id(
    db: AsyncSession,
    template_id: int,
    user_id: str
) -> Optional[TaskTemplate]:
    """
    Get a specific template by ID, ensuring it belongs to the user.

    Args:
        db: Database session
        template_id: Template ID
        user_id: User ID (UUID string) to verify ownership

    Returns:
        Template instance if found and owned by user, None otherwise
    """
    result = await db.execute(
        select(TaskTemplate)
        .options(selectinload(TaskTemplate.owner))
        .where(TaskTemplate.id == template_id, TaskTemplate.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_template(
    db: AsyncSession,
    template: TaskTemplate,
    template_data: TaskTemplateUpdate
) -> TaskTemplate:
    """
    Update a template's details.

    Args:
        db: Database session
        template: Template instance to update
        template_data: Updated template data

    Returns:
        Updated template instance
    """
    if template_data.title is not None:
        template.title = template_data.title
    if template_data.description is not None:
        template.description = template_data.description
    if template_data.priority_id is not None:
        template.priority_id = template_data.priority_id
    if template_data.is_recurring is not None:
        template.is_recurring = template_data.is_recurring
    if template_data.recurrence_pattern is not None:
        template.recurrence_pattern = template_data.recurrence_pattern
    if template_data.tags is not None:
        template.tags = template_data.tags
    if template_data.subtasks is not None:
        template.subtasks_template = template_data.subtasks

    await db.commit()
    await db.refresh(template)

    # Re-fetch with eager loading
    stmt = (
        select(TaskTemplate)
        .where(TaskTemplate.id == template.id)
        .options(selectinload(TaskTemplate.owner))
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def delete_template(db: AsyncSession, template: TaskTemplate) -> None:
    """
    Delete a template.

    Args:
        db: Database session
        template: Template instance to delete
    """
    await db.delete(template)
    await db.commit()


async def create_task_from_template(
    db: AsyncSession,
    template: TaskTemplate,
    user_id: str,
    title_override: Optional[str] = None,
    description_override: Optional[str] = None,
    due_date: Optional[str] = None
) -> dict:
    """
    Create a task from a template with optional overrides.

    Args:
        db: Database session
        template: Template to create task from
        user_id: Owner user ID (UUID string)
        title_override: Optional title override
        description_override: Optional description override
        due_date: Optional due date (YYYY-MM-DD format)

    Returns:
        Dictionary containing task data ready for creation
    """
    from datetime import datetime

    task_data = {
        "title": title_override or template.title,
        "description": description_override or template.description or "",
        "priority_id": template.priority_id,
        "is_recurring": template.is_recurring,
        "recurrence_pattern": template.recurrence_pattern,
    }

    # Add due_date if provided
    if due_date:
        try:
            task_data["due_date"] = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            pass  # Invalid date format, skip

    return task_data
