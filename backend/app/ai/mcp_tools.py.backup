"""
MCP Server Implementation for Todo App Tools

This module implements the Model Context Protocol server for the Todo application,
providing tool definitions that can be used by AI agents.
"""

from typing import Dict, Any, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from mcp.server.fastmcp import FastMCP
from app.crud import task as task_crud
from app.schemas.task import TaskCreate
from app.models.task import Priority

# Initialize MCP server
mcp = FastMCP("TodoAgent")

# Global context for tool execution (set by the agent service)
_db_session: Optional[AsyncSession] = None
_user_id: Optional[int] = None

def set_mcp_context(db: AsyncSession, user_id: int):
    """Set the database session and user_id for MCP tool execution."""
    global _db_session, _user_id
    _db_session = db
    _user_id = user_id

def clear_mcp_context():
    """Clear the MCP tool context."""
    global _db_session, _user_id
    _db_session = None
    _user_id = None

@mcp.tool()
async def add_task(
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task for the user.

    Use this when the user wants to add a todo item or create a new task.

    Args:
        title: The title of the task (required, 1-500 characters)
        description: Optional description with additional details about the task
        priority: Priority level (low, medium, high) - default: medium
        due_date: Optional due date in YYYY-MM-DD format

    Returns:
        Dictionary with task creation result including task details
    """
    if not _db_session or not _user_id:
        raise ValueError("MCP context not set - ensure set_mcp_context() was called")

    # Convert priority string to priority_id
    priority_mapping = {
        "low": 1,
        "medium": 2,
        "high": 3
    }
    task_priority_id = priority_mapping.get(priority, 2)  # Default to Medium (ID=2)

    # Convert due_date string to date object
    due_date_obj = None
    if due_date:
        try:
            due_date_obj = date.fromisoformat(due_date)
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid date format: {due_date}. Use YYYY-MM-DD format."
            }

    # Create task data
    task_data = TaskCreate(
        title=title,
        description=description or "",
        priority_id=task_priority_id,
        due_date=due_date_obj
    )

    try:
        # Create task using CRUD
        task = await task_crud.create_task(_db_session, task_data, str(_user_id))

        return {
            "success": True,
            "message": f"Task '{title}' created successfully!",
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority_obj.name if task.priority_obj else "Medium",
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }

@mcp.tool()
async def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    date_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    List tasks for the user with optional filtering.

    Use this when the user wants to see their tasks, todo list, or check what's due.

    Args:
        status: Filter by status (pending, completed, all) - default: all
        priority: Filter by priority (low, medium, high)
        date_filter: Filter by date (today, tomorrow, overdue, this_week)

    Returns:
        Dictionary with list of tasks and filtering info
    """
    if not _db_session or not _user_id:
        raise ValueError("MCP context not set - ensure set_mcp_context() was called")

    try:
        # Get tasks using CRUD
        tasks = await task_crud.get_tasks_by_user(_db_session, _user_id)

        # Apply filters
        filtered_tasks = []
        for task in tasks:
            # Status filter
            if status and status != "all":
                if status == "completed" and not task.completed:
                    continue
                if status == "pending" and task.completed:
                    continue

            # Priority filter
            if priority:
                if not task.priority_obj:
                    continue
                if priority == "high" and task.priority_obj.name.lower() != "high":
                    continue
                if priority == "medium" and task.priority_obj.name.lower() != "medium":
                    continue
                if priority == "low" and task.priority_obj.name.lower() != "low":
                    continue

            # Date filter
            if date_filter:
                today = date.today()
                if date_filter == "today":
                    if not task.due_date or task.due_date != today:
                        continue
                elif date_filter == "tomorrow":
                    tomorrow = today.replace(day=today.day + 1)
                    if not task.due_date or task.due_date != tomorrow:
                        continue
                elif date_filter == "overdue":
                    if not task.due_date or task.due_date >= today:
                        continue
                elif date_filter == "this_week":
                    # Simple check: same week (within 7 days)
                    if not task.due_date:
                        continue
                    days_diff = (task.due_date - today).days
                    if days_diff < 0 or days_diff > 7:
                        continue

            filtered_tasks.append(task)

        return {
            "success": True,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority_obj.name if task.priority_obj else "Medium",
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                }
                for task in filtered_tasks
            ],
            "total": len(filtered_tasks),
            "filters_applied": {
                "status": status,
                "priority": priority,
                "date_filter": date_filter
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list tasks: {str(e)}"
        }

@mcp.tool()
async def complete_task(task_id: int) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Use this when the user says they finished, completed, or done with a specific task.

    Args:
        task_id: The ID of the task to mark as complete

    Returns:
        Dictionary with task completion result
    """
    if not _db_session or not _user_id:
        raise ValueError("MCP context not set - ensure set_mcp_context() was called")

    try:
        # Get task first to verify ownership
        task = await task_crud.get_task_by_id(_db_session, task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task with ID {task_id} not found"
            }

        # Verify user owns this task
        if str(task.user_id) != str(_user_id):
            return {
                "success": False,
                "error": "You do not have permission to modify this task"
            }

        # Mark task as complete
        updated_task = await task_crud.update_task(
            _db_session,
            task_id,
            {"completed": True},
            _user_id
        )

        return {
            "success": True,
            "message": f"Task '{updated_task.title}' marked as complete!",
            "task": {
                "id": updated_task.id,
                "title": updated_task.title,
                "completed": updated_task.completed
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to complete task: {str(e)}"
        }

@mcp.tool()
async def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update an existing task with new values.

    Use this when the user wants to modify, rename, or change details of a task.

    Args:
        task_id: The ID of the task to update
        title: New title for the task (optional)
        description: New description for the task (optional)
        priority: New priority level (low, medium, high) (optional)
        due_date: New due date in YYYY-MM-DD format (optional)
        completed: New completion status (True/False) (optional)

    Returns:
        Dictionary with task update result showing what changed
    """
    if not _db_session or not _user_id:
        raise ValueError("MCP context not set - ensure set_mcp_context() was called")

    try:
        # Get task first to verify ownership
        task = await task_crud.get_task_by_id(_db_session, task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task with ID {task_id} not found"
            }

        # Verify user owns this task
        if str(task.user_id) != str(_user_id):
            return {
                "success": False,
                "error": "You do not have permission to modify this task"
            }

        # Prepare update data
        update_data = {}

        if title is not None:
            update_data["title"] = title

        if description is not None:
            update_data["description"] = description

        if priority is not None:
            priority_mapping = {
                "low": 1,
                "medium": 2,
                "high": 3
            }
            update_data["priority_id"] = priority_mapping.get(priority.lower(), 2)

        if due_date is not None:
            try:
                update_data["due_date"] = date.fromisoformat(due_date)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid date format: {due_date}. Use YYYY-MM-DD format."
                }

        if completed is not None:
            update_data["completed"] = completed

        # Apply updates
        updated_task = await task_crud.update_task(
            _db_session,
            task_id,
            update_data,
            _user_id
        )

        # Track what changed
        changes = []
        if title and title != task.title:
            changes.append(f"title: '{task.title}' → '{title}'")
        if description is not None and description != task.description:
            changes.append(f"description updated")
        if priority is not None:
            old_priority = task.priority_obj.name if task.priority_obj else "Medium"
            changes.append(f"priority: '{old_priority}' → '{priority}'")
        if due_date is not None:
            old_due = task.due_date.isoformat() if task.due_date else "None"
            changes.append(f"due date: {old_due} → {due_date}")
        if completed is not None and completed != task.completed:
            changes.append(f"status: {'completed' if completed else 'pending'}")

        changes_str = ", ".join(changes) if changes else "no changes"

        return {
            "success": True,
            "message": f"Task '{updated_task.title}' updated! Changed: {changes_str}",
            "task": {
                "id": updated_task.id,
                "title": updated_task.title,
                "description": updated_task.description,
                "priority": updated_task.priority_obj.name if updated_task.priority_obj else "Medium",
                "due_date": updated_task.due_date.isoformat() if updated_task.due_date else None,
                "completed": updated_task.completed
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update task: {str(e)}"
        }

@mcp.tool()
async def delete_task(task_id: int) -> Dict[str, Any]:
    """
    Delete a task permanently.

    Use this when the user explicitly requests to remove or delete a task.
    This action cannot be undone.

    Args:
        task_id: The ID of the task to delete

    Returns:
        Dictionary with task deletion result
    """
    if not _db_session or not _user_id:
        raise ValueError("MCP context not set - ensure set_mcp_context() was called")

    try:
        # Get task first to verify ownership and return details
        task = await task_crud.get_task_by_id(_db_session, task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task with ID {task_id} not found"
            }

        # Verify user owns this task
        if str(task.user_id) != str(_user_id):
            return {
                "success": False,
                "error": "You do not have permission to delete this task"
            }

        # Delete the task
        deleted = await task_crud.delete_task(_db_session, task_id, _user_id)

        if deleted:
            return {
                "success": True,
                "message": f"Task '{task.title}' has been permanently deleted",
                "deleted_task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description
                }
            }
        else:
            return {
                "success": False,
                "error": "Failed to delete task - please try again"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to delete task: {str(e)}"
        }

# Export MCP server instance
__all__ = ["mcp", "set_mcp_context", "clear_mcp_context"]