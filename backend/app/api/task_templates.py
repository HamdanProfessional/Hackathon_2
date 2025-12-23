"""TaskTemplate API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User
from app.schemas.task_template import (
    TaskTemplateCreate,
    TaskTemplateUpdate,
    TaskTemplateResponse,
    TaskFromTemplateRequest
)
from app.schemas.task import TaskResponse
from app.crud import task_template as task_template_crud
from app.crud import task as task_crud
from app.api.deps import get_current_user
from app.utils.exceptions import NotFoundException, ForbiddenException, ValidationException


router = APIRouter()


@router.post(
    "",
    response_model=TaskTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task template",
    description="Create a new task template for the authenticated user",
)
async def create_template(
    template_data: TaskTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new task template.

    - **title**: Template title (required, max 500 chars)
    - **description**: Default description (optional, max 2000 chars)
    - **priority_id**: Default priority ID (1=Low, 2=Medium, 3=High)
    - **is_recurring**: Whether tasks from this template should be recurring
    - **recurrence_pattern**: Recurrence pattern (required if is_recurring=True)
    - **tags**: List of tags associated with the template
    - **subtasks**: List of subtask templates

    Returns the created template.
    """
    new_template = await task_template_crud.create_template(
        db, template_data, str(current_user.id)
    )
    return new_template


@router.get(
    "",
    response_model=List[TaskTemplateResponse],
    summary="Get all task templates for current user",
    description="Retrieve all task templates belonging to the authenticated user",
)
async def get_templates(
    sort_by: Optional[str] = Query("created_at", description="Field to sort by: 'created_at', 'updated_at', or 'title'"),
    sort_order: Optional[str] = Query("desc", description="Sort order: 'asc' or 'desc'"),
    limit: Optional[int] = Query(100, ge=1, le=100, description="Number of templates to return (max 100)"),
    offset: Optional[int] = Query(0, ge=0, description="Number of templates to skip (for pagination)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all task templates for the current user.

    - **sort_by**: Field to sort templates by (default: created_at)
    - **sort_order**: Sort direction (default: desc for newest first)
    - **limit**: Number of templates to return (max 100)
    - **offset**: Number of templates to skip for pagination

    Returns only templates owned by the current user.
    """
    templates = await task_template_crud.get_templates_by_user(
        db=db,
        user_id=str(current_user.id),
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )
    return templates


@router.get(
    "/{template_id}",
    response_model=TaskTemplateResponse,
    summary="Get a specific task template",
    description="Retrieve a single task template by ID (must belong to current user)",
)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific task template by ID.

    - **template_id**: Template ID

    Returns template only if owned by current user.
    Returns 404 if template doesn't exist or doesn't belong to user.
    """
    template = await task_template_crud.get_template_by_id(
        db, template_id, str(current_user.id)
    )
    if not template:
        raise NotFoundException(detail=f"Task template {template_id} not found")
    return template


@router.put(
    "/{template_id}",
    response_model=TaskTemplateResponse,
    summary="Update a task template",
    description="Update task template title, description, priority, recurrence settings, tags, or subtasks",
)
async def update_template(
    template_id: int,
    template_data: TaskTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a task template's details.

    - **template_id**: Template ID
    - **title**: New title (optional)
    - **description**: New description (optional)
    - **priority_id**: New priority ID (optional)
    - **is_recurring**: New recurring status (optional)
    - **recurrence_pattern**: New recurrence pattern (optional)
    - **tags**: New list of tags (optional)
    - **subtasks**: New list of subtask templates (optional)

    At least one field must be provided.
    Only allows updating templates owned by current user.
    """
    # Verify template exists and belongs to user
    template = await task_template_crud.get_template_by_id(
        db, template_id, str(current_user.id)
    )
    if not template:
        raise NotFoundException(detail=f"Task template {template_id} not found")

    # Validate at least one field is provided
    if all([
        template_data.title is None,
        template_data.description is None,
        template_data.priority_id is None,
        template_data.is_recurring is None,
        template_data.recurrence_pattern is None,
        template_data.tags is None,
        template_data.subtasks is None
    ]):
        raise ValidationException(detail="At least one field must be provided")

    # Update template
    updated_template = await task_template_crud.update_template(db, template, template_data)
    return updated_template


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task template",
    description="Permanently delete a task template",
)
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a task template permanently.

    - **template_id**: Template ID

    Returns 204 No Content on success.
    Only allows deleting templates owned by current user.
    """
    # Verify template exists and belongs to user
    template = await task_template_crud.get_template_by_id(
        db, template_id, str(current_user.id)
    )
    if not template:
        raise NotFoundException(detail=f"Task template {template_id} not found")

    # Delete template
    await task_template_crud.delete_template(db, template)


@router.post(
    "/{template_id}/use",
    response_model=TaskResponse,
    summary="Create a task from a template",
    description="Create a new task based on a template with optional overrides",
)
async def use_template(
    template_id: int,
    overrides: Optional[TaskFromTemplateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a task from a template with optional overrides.

    - **template_id**: Template ID to use
    - **title**: Optional title override
    - **description**: Optional description override
    - **due_date**: Optional due date (YYYY-MM-DD format)

    Creates a new task using the template's defaults,
    with any provided overrides applied.

    Only works with templates owned by current user.
    """
    # Verify template exists and belongs to user
    template = await task_template_crud.get_template_by_id(
        db, template_id, str(current_user.id)
    )
    if not template:
        raise NotFoundException(detail=f"Task template {template_id} not found")

    # Get task data from template with overrides
    overrides_data = overrides.dict() if overrides else {}
    task_data_dict = await task_template_crud.create_task_from_template(
        db=db,
        template=template,
        user_id=str(current_user.id),
        title_override=overrides_data.get("title"),
        description_override=overrides_data.get("description"),
        due_date=overrides_data.get("due_date"),
    )

    # Convert to TaskCreate schema
    from app.schemas.task import TaskCreate
    task_create = TaskCreate(**task_data_dict)

    # Create the task
    new_task = await task_crud.create_task(db, task_create, str(current_user.id))

    return new_task


class SaveTaskAsTemplateRequest(BaseModel):
    """Schema for saving an existing task as a template."""

    template_title: str = Field(..., min_length=1, max_length=500, description="Title for the template")
    include_description: bool = Field(default=True, description="Include task description in template")
    include_priority: bool = Field(default=True, description="Include task priority in template")
    include_recurrence: bool = Field(default=True, description="Include task recurrence settings in template")


@router.post(
    "/from-task/{task_id}",
    response_model=TaskTemplateResponse,
    summary="Save an existing task as a template",
    description="Create a template from an existing task",
)
async def save_task_as_template(
    task_id: int,
    request: SaveTaskAsTemplateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Save an existing task as a template.

    - **task_id**: Task ID to save as template
    - **template_title**: Title for the new template
    - **include_description**: Whether to include task description
    - **include_priority**: Whether to include task priority
    - **include_recurrence**: Whether to include task recurrence settings

    Creates a new template from the specified task.
    Only works with tasks owned by current user.
    """
    # Get the task to verify ownership
    task = await task_crud.get_task_by_id(db, task_id, str(current_user.id))
    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")

    # Create template data from task
    template_data = TaskTemplateCreate(
        title=request.template_title,
        description=task.description if request.include_description else None,
        priority_id=task.priority_id if request.include_priority else 2,
        is_recurring=task.is_recurring if request.include_recurrence else False,
        recurrence_pattern=task.recurrence_pattern if request.include_recurrence else None,
        tags=None,  # Tags not currently supported on tasks
        subtasks=None,  # Subtasks not currently supported on tasks
    )

    # Create the template
    new_template = await task_template_crud.create_template(
        db, template_data, str(current_user.id)
    )

    return new_template
