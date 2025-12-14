"""MCP tool: add_task - Create tasks via natural language."""
from typing import Dict, Any
from fastapi import HTTPException

from app.database import AsyncSessionLocal
from app.crud.task import create_task
from app.schemas.task import TaskCreate


async def add_task(user_id: int, title: str, description: str = "") -> Dict[str, Any]:
    """
    Create a new task for the authenticated user.

    This MCP tool wraps the existing create_task CRUD function,
    providing task creation capability to the AI agent.

    Args:
        user_id: ID of the user creating the task (auto-injected by agent)
        title: Task title extracted from user's natural language input (1-500 chars)
        description: Optional detailed description (max 10000 chars)

    Returns:
        Dict with task_id, status="created", and title

    Raises:
        HTTPException: 401 if user_id is invalid, 400 if validation fails

    Examples:
        >>> await add_task(user_id=1, title="Buy groceries")
        {"task_id": 42, "status": "created", "title": "Buy groceries"}

        >>> await add_task(user_id=1, title="Finish Q4 report", description="Complete financial analysis")
        {"task_id": 43, "status": "created", "title": "Finish Q4 report"}
    """
    # Validation: user_id required
    if not user_id or user_id <= 0:
        raise HTTPException(status_code=401, detail="User ID validation failed")

    # Validation: title required and length constraints
    if not title or not title.strip():
        raise HTTPException(status_code=400, detail="Title is required and must not be empty")

    if len(title) > 500:
        raise HTTPException(status_code=400, detail="Title must not exceed 500 characters")

    # Validation: description length constraint
    if description and len(description) > 10000:
        raise HTTPException(status_code=400, detail="Description must not exceed 10000 characters")

    # Create task using existing CRUD
    async with AsyncSessionLocal() as db:
        try:
            task_data = TaskCreate(title=title.strip(), description=description.strip() if description else "")
            task = await create_task(db, task_data, user_id)

            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title,
            }
        except Exception as e:
            # Log error and re-raise
            raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")
