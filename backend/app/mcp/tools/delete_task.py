"""MCP tool: delete_task - Remove tasks via natural language with confirmation."""
from typing import Dict, Any
from fastapi import HTTPException

from app.database import AsyncSessionLocal
from app.crud.task import get_task_by_id, delete_task as delete_task_crud


async def delete_task(user_id: int, task_id: int) -> Dict[str, Any]:
    """
    Delete a task permanently.

    IMPORTANT: Agent must ALWAYS ask user confirmation before calling this tool.

    This MCP tool wraps the delete_task CRUD function,
    providing task deletion capability to the AI agent.

    Args:
        user_id: ID of the user (auto-injected by agent)
        task_id: ID of the task to delete

    Returns:
        Dict with task_id, status="deleted", and title of deleted task

    Raises:
        HTTPException: 401 if unauthorized, 404 if task not found

    Examples:
        >>> await delete_task(user_id=1, task_id=42)
        {"task_id": 42, "status": "deleted", "title": "Buy groceries"}
    """
    # Validation: user_id required
    if not user_id or user_id <= 0:
        raise HTTPException(status_code=401, detail="User ID validation failed")

    # Validation: task_id required
    if not task_id or task_id <= 0:
        raise HTTPException(status_code=400, detail="Task ID is required")

    # Delete task
    async with AsyncSessionLocal() as db:
        try:
            # Get task with ownership validation
            task = await get_task_by_id(db, task_id, user_id)

            if not task:
                raise HTTPException(
                    status_code=404,
                    detail=f"Task {task_id} not found or does not belong to user"
                )

            # Store title before deletion
            task_title = task.title

            # Delete task
            await delete_task_crud(db, task)

            return {
                "task_id": task_id,
                "status": "deleted",
                "title": task_title,
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete task: {str(e)}"
            )
