# Advanced MCP Tools Example

Complete MCP tool suite with comprehensive task management capabilities.

## Tool Registry Pattern

```python
# backend/app/ai/tools.py
from typing import Dict, Any, Callable
from functools import wraps

# Global tool registry
TOOL_REGISTRY: Dict[str, Callable] = {}

def register_tool(name: str):
    """Decorator to register MCP tools."""
    def decorator(func: Callable) -> Callable:
        TOOL_REGISTRY[name] = func
        func.__tool_name__ = name
        return func
    return decorator

def get_all_tools() -> list[Dict]:
    """Get all registered tool schemas."""
    return [
        {
            "type": "function",
            "function": {
                "name": func.__tool_name__,
                "description": func.__doc__,
                "parameters": _extract_params(func)
            }
        }
        for func in TOOL_REGISTRY.values()
    ]
```

## Complete Task Tools

```python
# backend/app/ai/task_tools.py
from typing import Optional, Literal
from pydantic import BaseModel, Field
from app.auth import verify_token
from app.services import task_service

# Request/Response models for validation
class TaskCreate(BaseModel):
    """Task creation input."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Literal["low", "normal", "high"] = "normal"
    due_date: Optional[str] = None

class TaskUpdate(BaseModel):
    """Task update input."""
    task_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal["pending", "in_progress", "completed"]] = None
    priority: Optional[Literal["low", "normal", "high"]] = None

@register_tool("get_tasks")
async def get_tasks(
    user_token: str,
    status: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get all tasks for the current user.

    Use this when the user asks to see their tasks, wants a task summary,
    or needs to know what tasks they have.

    Args:
        user_token: JWT authentication token
        status: Filter by status (pending, in_progress, completed)
        limit: Maximum number of tasks to return (default: 50)

    Returns:
        List of tasks with id, title, description, status, priority, and due_date
    """
    try:
        user_id = verify_token(user_token)
        tasks = task_service.get_user_tasks(
            user_id,
            status=status,
            limit=limit
        )
        return {
            "success": True,
            "tasks": [t.dict() for t in tasks],
            "count": len(tasks)
        }
    except ValueError as e:
        return {"success": False, "error": f"Invalid input: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to retrieve tasks: {e}"}

@register_tool("create_task")
async def create_task(
    user_token: str,
    title: str,
    description: Optional[str] = None,
    priority: str = "normal",
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task for the user.

    Use this when the user wants to add a new task, create a reminder,
    or track something they need to do.

    Args:
        user_token: JWT authentication token
        title: Task title (required, 1-255 characters)
        description: Optional detailed description
        priority: Task priority - low, normal (default), or high
        due_date: Optional due date in ISO format (YYYY-MM-DD)

    Returns:
        Created task with all fields including the assigned task ID
    """
    try:
        user_id = verify_token(user_token)

        # Validate input
        if not title or len(title.strip()) == 0:
            return {"success": False, "error": "Title cannot be empty"}

        task = task_service.create_task(
            user_id=user_id,
            title=title.strip(),
            description=description,
            priority=priority,
            due_date=due_date
        )

        return {
            "success": True,
            "task": task.dict(),
            "message": f"Task '{title}' created successfully"
        }
    except ValueError as e:
        return {"success": False, "error": f"Validation error: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to create task: {e}"}

@register_tool("update_task")
async def update_task(
    user_token: str,
    task_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing task's status or priority.

    Use this when the user wants to mark a task as complete,
    change task priority, or update task status.

    Args:
        user_token: JWT authentication token
        task_id: ID of the task to update
        status: New status (pending, in_progress, completed)
        priority: New priority (low, normal, high)

    Returns:
        Updated task details or error if task not found
    """
    try:
        user_id = verify_token(user_token)

        task = task_service.get_task(task_id)
        if not task or task.user_id != user_id:
            return {"success": False, "error": f"Task {task_id} not found"}

        updated = task_service.update_task(
            task_id=task_id,
            status=status,
            priority=priority
        )

        return {
            "success": True,
            "task": updated.dict(),
            "message": f"Task '{updated.title}' updated"
        }
    except ValueError as e:
        return {"success": False, "error": f"Validation error: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to update task: {e}"}

@register_tool("delete_task")
async def delete_task(user_token: str, task_id: int) -> Dict[str, Any]:
    """
    Delete a task permanently.

    Use this when the user explicitly asks to delete or remove a task.
    Ask for confirmation before deleting unless the user is certain.

    Args:
        user_token: JWT authentication token
        task_id: ID of the task to delete

    Returns:
        Confirmation message or error if task not found
    """
    try:
        user_id = verify_token(user_token)

        task = task_service.get_task(task_id)
        if not task or task.user_id != user_id:
            return {"success": False, "error": f"Task {task_id} not found"}

        task_service.delete_task(task_id)

        return {
            "success": True,
            "message": f"Task '{task.title}' deleted successfully"
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to delete task: {e}"}

@register_tool("search_tasks")
async def search_tasks(
    user_token: str,
    query: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search tasks by title or description.

    Use this when the user wants to find tasks matching
    specific keywords or phrases.

    Args:
        user_token: JWT authentication token
        query: Search query (matches title or description)
        limit: Maximum results to return (default: 20)

    Returns:
        List of matching tasks
    """
    try:
        user_id = verify_token(user_token)
        tasks = task_service.search_tasks(user_id, query, limit=limit)

        return {
            "success": True,
            "tasks": [t.dict() for t in tasks],
            "count": len(tasks),
            "query": query
        }
    except Exception as e:
        return {"success": False, "error": f"Search failed: {e}"}
```

## Tool Execution Handler

```python
# backend/app/ai/tool_executor.py
import json
import logging
from typing import Dict, Any
from app.ai.tools import TOOL_REGISTRY

logger = logging.getLogger(__name__)

async def execute_tool_calls(tool_calls: list, user_id: str, user_token: str) -> Dict[str, Any]:
    """
    Execute multiple tool calls and return results.

    Args:
        tool_calls: List of tool call objects from AI response
        user_id: Current user ID
        user_token: JWT token for authentication

    Returns:
        Dictionary mapping tool_call IDs to results
    """
    results = {}

    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_id = tool_call.id

        try:
            # Parse arguments
            arguments = json.loads(tool_call.function.arguments)

            # Add user token to arguments
            arguments["user_token"] = user_token

            # Execute tool
            if tool_name in TOOL_REGISTRY:
                result = await TOOL_REGISTRY[tool_name](**arguments)
                results[tool_id] = result
            else:
                results[tool_id] = {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
                logger.warning(f"Unknown tool requested: {tool_name}")

        except json.JSONDecodeError as e:
            results[tool_id] = {
                "success": False,
                "error": f"Invalid tool arguments: {e}"
            }
            logger.error(f"JSON decode error for tool {tool_name}: {e}")

        except Exception as e:
            results[tool_id] = {
                "success": False,
                "error": f"Tool execution failed: {e}"
            }
            logger.error(f"Tool {tool_name} execution error: {e}")

    return results
```
