"""MCP tool: update_task - Modify task details via natural language."""
from typing import Dict, Any, Optional
from fastapi import HTTPException

from app.database import AsyncSessionLocal
from app.crud.task import get_task_by_id, update_task as update_task_crud
from app.schemas.task import TaskUpdate


async def update_task(
    user_id: int,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update task title and/or description.

    This MCP tool wraps the update_task CRUD function,
    providing task editing capability to the AI agent.

    Args:
        user_id: ID of the user (auto-injected by agent)
        task_id: ID of the task to update
        title: New title (optional, 1-500 chars)
        description: New description (optional, max 10000 chars)

    Returns:
        Dict with task_id, status="updated", and new title

    Raises:
        HTTPException: 401 if unauthorized, 404 if not found, 400 if validation fails

    Examples:
        >>> await update_task(user_id=1, task_id=42, title="Buy organic groceries")
        {"task_id": 42, "status": "updated", "title": "Buy organic groceries"}
    """
    # Validation: user_id required
    if not user_id or user_id <= 0:
        raise HTTPException(status_code=401, detail="User ID validation failed")

    # Validation: task_id required
    if not task_id or task_id <= 0:
        raise HTTPException(status_code=400, detail="Task ID is required")

    # Validation: at least one field must be provided
    if title is None and description is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field (title or description) must be provided"
        )

    # Validation: title constraints
    if title is not None:
        if not title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        if len(title) > 500:
            raise HTTPException(status_code=400, detail="Title must not exceed 500 characters")

    # Validation: description constraints
    if description is not None and len(description) > 10000:
        raise HTTPException(status_code=400, detail="Description must not exceed 10000 characters")

    # Update task
    async with AsyncSessionLocal() as db:
        try:
            # Get task with ownership validation
            task = await get_task_by_id(db, task_id, user_id)

            if not task:
                raise HTTPException(
                    status_code=404,
                    detail=f"Task {task_id} not found or does not belong to user"
                )

            # Prepare update data
            update_data = TaskUpdate(
                title=title.strip() if title else None,
                description=description.strip() if description else None
            )

            # Update task
            updated_task = await update_task_crud(db, task, update_data)

            return {
                "task_id": updated_task.id,
                "status": "updated",
                "title": updated_task.title,
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update task: {str(e)}"
            )
