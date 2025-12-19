"""MCP tool: complete_task - Toggle task completion via natural language."""
from typing import Dict, Any
from fastapi import HTTPException

from app.database import AsyncSessionLocal
from app.crud.task import get_task_by_id, toggle_task_completion


async def complete_task(user_id: int, task_id: int) -> Dict[str, Any]:
    """
    Toggle task completion status (complete ⟷ incomplete).

    This MCP tool wraps the toggle_task_completion CRUD function,
    providing task completion capability to the AI agent.

    Args:
        user_id: ID of the user (auto-injected by agent)
        task_id: ID of the task to toggle

    Returns:
        Dict with task_id, status ("completed" or "incomplete"), and title

    Raises:
        HTTPException: 401 if unauthorized, 404 if task not found

    Examples:
        >>> await complete_task(user_id=1, task_id=42)
        {"task_id": 42, "status": "completed", "title": "Buy groceries"}
    """
    # Validation: user_id required
    if not user_id or user_id <= 0:
        raise HTTPException(status_code=401, detail="User ID validation failed")

    # Validation: task_id required
    if not task_id or task_id <= 0:
        raise HTTPException(status_code=400, detail="Task ID is required")

    # Get and toggle task
    async with AsyncSessionLocal() as db:
        try:
            # Get task with ownership validation
            task = await get_task_by_id(db, task_id, user_id)

            if not task:
                raise HTTPException(
                    status_code=404,
                    detail=f"Task {task_id} not found or does not belong to user"
                )

            # Toggle completion status
            updated_task = await toggle_task_completion(db, task)

            return {
                "task_id": updated_task.id,
                "status": "completed" if updated_task.completed else "incomplete",
                "title": updated_task.title,
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to toggle task completion: {str(e)}"
            )
