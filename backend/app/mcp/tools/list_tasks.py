"""MCP tool: list_tasks - Retrieve tasks via natural language."""
from typing import Dict, Any, List, Literal
from fastapi import HTTPException

from app.database import AsyncSessionLocal
from app.crud.task import get_tasks_by_user


async def list_tasks(
    user_id: int,
    status: Literal["all", "pending", "completed"] = "all"
) -> Dict[str, Any]:
    """
    Retrieve tasks for the authenticated user with optional status filtering.

    This MCP tool wraps the get_tasks_by_user CRUD function,
    providing task retrieval capability to the AI agent.

    Args:
        user_id: ID of the user retrieving tasks (auto-injected by agent)
        status: Filter by status - "all", "pending", or "completed" (default: "all")

    Returns:
        Dict with tasks array and count

    Raises:
        HTTPException: 401 if user_id is invalid

    Examples:
        >>> await list_tasks(user_id=1, status="all")
        {"tasks": [...], "count": 5}

        >>> await list_tasks(user_id=1, status="pending")
        {"tasks": [...], "count": 3}
    """
    # Validation: user_id required
    if not user_id or user_id <= 0:
        raise HTTPException(status_code=401, detail="User ID validation failed")

    # Validation: status must be valid enum value
    if status not in ["all", "pending", "completed"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be 'all', 'pending', or 'completed'"
        )

    # Retrieve tasks using existing CRUD
    async with AsyncSessionLocal() as db:
        try:
            all_tasks = await get_tasks_by_user(db, user_id)

            # Filter by status if not "all"
            if status == "pending":
                filtered_tasks = [t for t in all_tasks if not t.completed]
            elif status == "completed":
                filtered_tasks = [t for t in all_tasks if t.completed]
            else:  # status == "all"
                filtered_tasks = all_tasks

            # Format response
            tasks_data = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                }
                for task in filtered_tasks
            ]

            return {
                "tasks": tasks_data,
                "count": len(tasks_data),
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve tasks: {str(e)}"
            )
