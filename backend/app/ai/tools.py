"""
AI Agent Tools for Task Management using MCP SDK

This module defines the tools available to the AI Agent using the Model Context Protocol.
Each tool integrates with existing CRUD operations while enforcing security
by requiring user_id injection.

Security: user_id is injected at runtime from JWT authentication, ensuring
the agent can only access/modify the authenticated user's data.
"""

from typing import Dict, Any, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import task as task_crud
from app.schemas.task import TaskCreate
from app.models.task import Priority

# Store database session and user_id for tool execution
_db_session: Optional[AsyncSession] = None
_user_id: Optional[str] = None

def set_tool_context(db: AsyncSession, user_id: str):
    """Set the database session and user_id for tool execution."""
    global _db_session, _user_id
    _db_session = db
    _user_id = user_id

def clear_tool_context():
    """Clear the tool context."""
    global _db_session, _user_id
    _db_session = None
    _user_id = None

# Export all tools for agent
__all__ = ["add_task", "list_tasks", "complete_task", "update_task", "delete_task", "set_tool_context", "clear_tool_context"]


# OpenAI Function Calling Tool Schema
ADD_TASK_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "add_task",
        "description": "Create a new task for the user. Use this when the user wants to add a todo item.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the task (required, 1-500 characters)"
                },
                "description": {
                    "type": "string",
                    "description": "Optional description with additional details about the task"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Priority level of the task (default: medium)"
                },
                "due_date": {
                    "type": "string",
                    "description": "Optional due date in YYYY-MM-DD format"
                }
            },
            "required": ["title"]
        }
    }
}


async def add_task(
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    user_id: Optional[str] = None,  # This will be injected by the agent service (UUID string)
    db: Optional[AsyncSession] = None  # Optional for direct calls from agent
) -> Dict[str, Any]:
    """
    Create a new task for the user.

    Use this when the user wants to add a todo item or create a new task.

    Args:
        title: The title of the task (required, 1-500 characters)
        description: Optional description with additional details about the task
        priority: Priority level (low, medium, high) - default: medium
        due_date: Optional due date in YYYY-MM-DD format
        user_id: Internal user ID (automatically injected)
        db: Database session (provided by agent)

    Returns:
        Dictionary with task creation result including task details

    Example:
        result = await add_task(
            title="Buy groceries",
            description="Milk, eggs, bread",
            priority="high"
        )
    """
    # Use global context if parameters not provided (for MCP compatibility)
    global _db_session, _user_id
    if db is None:
        db = _db_session
    if user_id is None:
        user_id = _user_id

    if not db or not user_id:
        return {
            "status": "error",
            "message": "Database session and user_id are required"
        }

    try:
        # user_id is already a UUID string from the JWT token
        user_uuid = user_id

        # Parse priority
        # Map priority string to priority_id
        priority_mapping = {
            "low": 1,
            "medium": 2,
            "high": 3
        }
        # Default to Medium (ID=2) if priority is None or invalid
        priority_id = 2
        if priority and priority.lower() in priority_mapping:
            priority_id = priority_mapping[priority.lower()]

        # Parse due date
        due_date_obj = None
        if due_date:
            try:
                # Expected format: YYYY-MM-DD
                year, month, day = due_date.split("-")
                due_date_obj = date(int(year), int(month), int(day))
            except (ValueError, AttributeError):
                # Invalid date format, ignore
                pass

        # Create task using existing CRUD
        task_data = TaskCreate(
            title=title,
            description=description or "",
            priority_id=priority_id,
            due_date=due_date_obj
        )

        task = await task_crud.create_task(
            db=db,
            task_data=task_data,
            user_id=user_uuid
        )

        # Get priority name from priority_obj
        priority_name = "medium"
        if hasattr(task, 'priority_obj') and task.priority_obj:
            priority_name = task.priority_obj.name

        # Return success response for agent
        return {
            "status": "success",
            "task_id": task.id,
            "title": task.title,
            "priority": priority_name,
            "message": f"Task '{task.title}' created successfully!"
        }

    except Exception as e:
        # Return error response for agent
        return {
            "status": "error",
            "message": f"Failed to create task: {str(e)}"
        }


# OpenAI Function Calling Tool Schema for list_tasks
LIST_TASKS_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_tasks",
        "description": "Retrieve and filter the user's tasks. Use this when the user asks to see their tasks, todo list, or wants to know what tasks they have.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter by task status. Use 'pending' for active/incomplete tasks, 'completed' for finished tasks, or 'all' for everything (default: all)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Filter by priority level"
                },
                "date_filter": {
                    "type": "string",
                    "enum": ["today", "tomorrow", "overdue", "this_week"],
                    "description": "Filter by due date. 'today' = due today, 'tomorrow' = due tomorrow, 'overdue' = past due date, 'this_week' = due within 7 days"
                }
            },
            "required": []
        }
    }
}


async def list_tasks(
    db: Optional[AsyncSession] = None,
    user_id: Optional[str] = None,  # Changed from int to str (UUID)
    status: Optional[str] = None,
    priority: Optional[str] = None,
    date_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tool function: List and filter user's tasks.

    SECURITY: This function MUST receive user_id from the authenticated session.
    The agent cannot specify user_id - it's injected by the endpoint.

    Args:
        db: Database session (provided by agent)
        user_id: Authenticated user ID (injected, not from agent)
        status: Filter by status - "all", "pending", "completed"
        priority: Filter by priority - "low", "medium", "high"
        date_filter: Filter by due date - "today", "tomorrow", "overdue", "this_week"

    Returns:
        Dictionary with task list result

    Example:
        result = await list_tasks(
            db=session,
            user_id=current_user.id,
            status="pending",
            priority="high",
            date_filter="today"
        )
    """
    # Use global context if parameters not provided (for MCP compatibility)
    global _db_session, _user_id
    if db is None:
        db = _db_session
    if user_id is None:
        user_id = _user_id

    if not db or not user_id:
        return {
            "status": "error",
            "message": "Database session and user_id are required",
            "count": 0,
            "tasks": []
        }

    try:
        from datetime import date, datetime, timedelta

        # Build parameters for CRUD query
        query_params: Dict[str, Any] = {}

        # Status filter
        if status and status != "all":
            query_params["status"] = status

        # Priority filter - convert string to priority_id
        if priority:
            priority_mapping = {
                "low": 1,
                "medium": 2,
                "high": 3
            }
            priority_id = priority_mapping.get(priority.lower())
            if priority_id:
                query_params["priority"] = priority_id

        # Date filter logic
        if date_filter:
            today = date.today()

            if date_filter == "today":
                # Tasks due today
                query_params["due_date_start"] = today
                query_params["due_date_end"] = today
            elif date_filter == "tomorrow":
                # Tasks due tomorrow
                tomorrow = today + timedelta(days=1)
                query_params["due_date_start"] = tomorrow
                query_params["due_date_end"] = tomorrow
            elif date_filter == "overdue":
                # Tasks past due date (and not completed)
                query_params["due_date_end"] = today - timedelta(days=1)
                query_params["status"] = "pending"  # Only show incomplete overdue tasks
            elif date_filter == "this_week":
                # Tasks due within next 7 days
                week_end = today + timedelta(days=7)
                query_params["due_date_start"] = today
                query_params["due_date_end"] = week_end

        # Remove date range params from query_params (not supported by CRUD)
        date_range_start = query_params.pop("due_date_start", None)
        date_range_end = query_params.pop("due_date_end", None)

        # Fetch tasks from database - try without relationship loading first
        try:
            tasks = await task_crud.get_tasks_by_user(
                db=db,
                user_id=user_id,  # Already a UUID string
                limit=100,  # Get more tasks for filtering
                **query_params
            )
        except Exception as e:
            # If the above fails, try a simpler query without any filters
            print(f"Error fetching tasks with filters: {e}")
            try:
                from sqlalchemy import select
                simple_query = select(Task).where(Task.user_id == user_id).limit(100)
                result = await db.execute(simple_query)
                tasks = result.scalars().all()
            except Exception as e2:
                print(f"Error with simple query too: {e2}")
                raise e2

        # Apply date filtering if needed (post-fetch)
        if date_filter:
            filtered_tasks = []
            for task in tasks:
                if task.due_date:
                    if date_range_start and date_range_end:
                        # Check if due date is within range
                        if date_range_start <= task.due_date <= date_range_end:
                            filtered_tasks.append(task)
                    elif date_range_end:
                        # For overdue (only end date)
                        if task.due_date <= date_range_end:
                            filtered_tasks.append(task)
                elif date_filter == "overdue":
                    # Task with no due date can't be overdue
                    continue
            tasks = filtered_tasks

        # Format tasks for agent
        task_list = []
        for task in tasks:
            try:
                # Get priority name from priority_obj relationship with safe access
                priority_name = "medium"  # Default fallback

                # Try to access priority safely
                if hasattr(task, 'priority_id') and task.priority_id:
                    # Use direct priority_id mapping (most reliable)
                    priority_mapping = {1: "low", 2: "medium", 3: "high"}
                    priority_name = priority_mapping.get(task.priority_id, "medium")

                # Handle task creation date safely
                created_at_str = None
                if hasattr(task, 'created_at') and task.created_at:
                    try:
                        created_at_str = task.created_at.isoformat()
                    except Exception:
                        pass

                # Handle due date safely
                due_date_str = None
                if hasattr(task, 'due_date') and task.due_date:
                    try:
                        due_date_str = task.due_date.isoformat()
                    except Exception:
                        pass

                task_info = {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": priority_name,
                    "completed": task.completed,
                    "due_date": due_date_str,
                    "created_at": created_at_str
                }
                task_list.append(task_info)

            except Exception as task_error:
                # If individual task fails, log it and continue with next task
                print(f"Error formatting task {task.id if hasattr(task, 'id') else 'unknown'}: {task_error}")
                continue

        # Return formatted response
        return {
            "status": "success",
            "count": len(task_list),
            "tasks": task_list,
            "filters_applied": {
                "status": status or "all",
                "priority": priority or "any",
                "date_filter": date_filter or "none"
            }
        }

    except Exception as e:
        # Return error response for agent
        return {
            "status": "error",
            "message": f"Failed to retrieve tasks: {str(e)}",
            "count": 0,
            "tasks": []
        }


# OpenAI Function Calling Tool Schema for complete_task
COMPLETE_TASK_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "complete_task",
        "description": "Mark a task as complete. Use this when the user says they finished, completed, or are done with a task. You MUST provide the task_id - if the user refers to a task by name, first use list_tasks to find the task_id.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to mark as complete (required). If user mentions task by name, first call list_tasks to find the ID."
                }
            },
            "required": ["task_id"]
        }
    }
}


async def complete_task(
    task_id: int,
    db: Optional[AsyncSession] = None,
    user_id: Optional[str] = None  # UUID string
) -> Dict[str, Any]:
    """
    Tool function: Mark a task as complete.

    SECURITY: This function MUST receive user_id from the authenticated session.
    The agent cannot specify user_id - it's injected by the endpoint.

    Args:
        task_id: ID of the task to complete (from agent)
        db: Database session (provided by agent)
        user_id: Authenticated user ID (injected, not from agent)

    Returns:
        Dictionary with completion result

    Example:
        result = await complete_task(
            task_id=42,
            db=session,
            user_id=current_user.id  # Injected from JWT
        )
    """
    # Use global context if parameters not provided (for MCP compatibility)
    global _db_session, _user_id
    if db is None:
        db = _db_session
    if user_id is None:
        user_id = _user_id

    if not db or not user_id:
        return {
            "status": "error",
            "message": "Database session and user_id are required"
        }

    try:
        # Verify task exists and belongs to user
        task = await task_crud.get_task_by_id(
            db=db,
            task_id=task_id,
            user_id=user_id
        )

        if not task:
            return {
                "status": "error",
                "message": f"Task with ID {task_id} not found or you don't have permission to access it."
            }

        # Check if already completed
        if task.completed:
            return {
                "status": "info",
                "task_id": task.id,
                "title": task.title,
                "message": f"Task '{task.title}' is already marked as complete!"
            }

        # Mark task as complete
        from app.schemas.task import TaskUpdate
        updated_task = await task_crud.update_task(
            db=db,
            task=task,
            task_data=TaskUpdate(completed=True)
        )

        # Return success response for agent
        return {
            "status": "success",
            "task_id": updated_task.id,
            "title": updated_task.title,
            "message": f"Great job! I've marked '{updated_task.title}' as complete."
        }

    except Exception as e:
        # Return error response for agent
        return {
            "status": "error",
            "message": f"Failed to complete task: {str(e)}"
        }


# OpenAI Function Calling Tool Schema for update_task
UPDATE_TASK_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "update_task",
        "description": "Update task details (title, description, priority, or due date). Use this when user wants to modify, change, rename, or reschedule a task. Only provide fields that need to change - omit fields that should stay the same. If user refers to task by name, first use list_tasks to find the task_id.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to update (required). If user mentions task by name, first call list_tasks to find the ID."
                },
                "title": {
                    "type": "string",
                    "description": "New title for the task (optional, only if user wants to rename it)"
                },
                "description": {
                    "type": "string",
                    "description": "New description for the task (optional, only if user wants to change it)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "New priority level (optional, only if user wants to change priority)"
                },
                "due_date": {
                    "type": "string",
                    "description": "New due date in YYYY-MM-DD format (optional, only if user wants to reschedule). Calculate the date if user says 'tomorrow', 'next week', etc."
                }
            },
            "required": ["task_id"]
        }
    }
}


async def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    db: Optional[AsyncSession] = None,
    user_id: Optional[str] = None  # UUID string
) -> Dict[str, Any]:
    """
    Tool function: Update task details.

    SECURITY: This function MUST receive user_id from the authenticated session.
    The agent cannot specify user_id - it's injected by the endpoint.

    Args:
        task_id: ID of the task to update (from agent)
        title: New title (optional, from agent)
        description: New description (optional, from agent)
        priority: New priority level (optional, from agent)
        due_date: New due date string (optional, from agent)
        db: Database session (provided by agent)
        user_id: Authenticated user ID (injected, not from agent)

    Returns:
        Dictionary with update result

    Example:
        result = await update_task(
            task_id=42,
            title="Buy Groceries",
            due_date="2025-12-20",
            db=session,
            user_id=current_user.id  # Injected from JWT
        )
    """
    # Use global context if parameters not provided (for MCP compatibility)
    global _db_session, _user_id
    if db is None:
        db = _db_session
    if user_id is None:
        user_id = _user_id

    if not db or not user_id:
        return {
            "status": "error",
            "message": "Database session and user_id are required"
        }

    try:
        # Verify task exists and belongs to user
        task = await task_crud.get_task_by_id(
            db=db,
            task_id=task_id,
            user_id=user_id
        )

        if not task:
            return {
                "status": "error",
                "message": f"Task with ID {task_id} not found or you don't have permission to access it."
            }

        # Store original values for comparison
        original_title = task.title
        original_description = task.description
        original_priority_id = task.priority_id
        original_due_date = task.due_date.isoformat() if task.due_date else None

        # Parse priority if provided
        priority_id = None
        if priority:
            priority_mapping = {
                "low": 1,
                "medium": 2,
                "high": 3
            }
            priority_id = priority_mapping.get(priority.lower())
            if priority_id is None:
                return {
                    "status": "error",
                    "message": f"Invalid priority '{priority}'. Must be low, medium, or high."
                }

        # Parse due date if provided
        due_date_obj = None
        if due_date:
            try:
                from datetime import date as date_type
                # Expected format: YYYY-MM-DD
                year, month, day = due_date.split("-")
                due_date_obj = date_type(int(year), int(month), int(day))
            except (ValueError, AttributeError):
                return {
                    "status": "error",
                    "message": f"Invalid date format '{due_date}'. Please use YYYY-MM-DD format."
                }

        # Build update data - only include fields that were provided
        from app.schemas.task import TaskUpdate
        update_data = TaskUpdate(
            title=title,
            description=description,
            priority_id=priority_id,
            due_date=due_date_obj
        )

        # Update task
        updated_task = await task_crud.update_task(
            db=db,
            task=task,
            task_data=update_data
        )

        # Build list of what changed for confirmation message
        changes = []
        if title and title != original_title:
            changes.append(f"title to '{title}'")
        if description is not None and description != original_description:
            changes.append(f"description")
        if priority_id and priority_id != original_priority_id:
            # Convert priority_id back to name for display
            priority_names = {1: "low", 2: "medium", 3: "high"}
            changes.append(f"priority to {priority_names.get(priority_id, 'unknown')}")
        if due_date_obj and (original_due_date is None or due_date_obj.isoformat() != original_due_date):
            changes.append(f"due date to {due_date_obj.isoformat()}")

        # Build confirmation message
        if changes:
            changes_text = ", ".join(changes)
            message = f"I've updated the {changes_text} for '{updated_task.title}'."
        else:
            message = f"No changes were made to '{updated_task.title}' (all values were the same)."

        # Return success response for agent
        return {
            "status": "success",
            "task_id": updated_task.id,
            "title": updated_task.title,
            "changes": changes,
            "message": message
        }

    except Exception as e:
        # Return error response for agent
        return {
            "status": "error",
            "message": f"Failed to update task: {str(e)}"
        }


# OpenAI Function Calling Tool Schema for delete_task
DELETE_TASK_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "delete_task",
        "description": "PERMANENTLY delete a task. Use this when user explicitly requests deletion (e.g., 'delete the task', 'remove the meeting'). IMPORTANT: This is destructive - ensure you have the correct task_id. If user refers to task by name, first use list_tasks to find the task_id. Ask for confirmation if ambiguous.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to delete (required). If user mentions task by name, first call list_tasks to find the ID. If multiple tasks match, ask user to clarify which one to delete."
                }
            },
            "required": ["task_id"]
        }
    }
}


async def delete_task(
    task_id: int,
    db: Optional[AsyncSession] = None,
    user_id: Optional[str] = None  # UUID string
) -> Dict[str, Any]:
    """
    Tool function: Delete a task permanently.

    SECURITY: This function MUST receive user_id from the authenticated session.
    The agent cannot specify user_id - it's injected by the endpoint.

    SAFETY: This is a destructive operation. The agent should verify the task
    before calling this function.

    Args:
        task_id: ID of the task to delete (from agent)
        db: Database session (provided by agent)
        user_id: Authenticated user ID (injected, not from agent)

    Returns:
        Dictionary with deletion result

    Example:
        result = await delete_task(
            task_id=42,
            db=session,
            user_id=current_user.id  # Injected from JWT
        )
    """
    # Use global context if parameters not provided (for MCP compatibility)
    global _db_session, _user_id
    if db is None:
        db = _db_session
    if user_id is None:
        user_id = _user_id

    if not db or not user_id:
        return {
            "status": "error",
            "message": "Database session and user_id are required"
        }

    try:
        # Verify task exists and belongs to user
        task = await task_crud.get_task_by_id(
            db=db,
            task_id=task_id,
            user_id=user_id
        )

        if not task:
            return {
                "status": "error",
                "message": f"Task with ID {task_id} not found or you don't have permission to access it."
            }

        # Store task title for confirmation message before deletion
        task_title = task.title

        # Delete task
        await task_crud.delete_task(db=db, task=task)

        # Return success response for agent
        return {
            "status": "success",
            "task_id": task_id,
            "title": task_title,
            "message": f"I have removed '{task_title}' from your list."
        }

    except Exception as e:
        # Return error response for agent
        return {
            "status": "error",
            "message": f"Failed to delete task: {str(e)}"
        }


# Tool registry for easy access
AVAILABLE_TOOLS = {
    "add_task": {
        "schema": ADD_TASK_TOOL_SCHEMA,
        "function": add_task
    },
    "list_tasks": {
        "schema": LIST_TASKS_TOOL_SCHEMA,
        "function": list_tasks
    },
    "complete_task": {
        "schema": COMPLETE_TASK_TOOL_SCHEMA,
        "function": complete_task
    },
    "update_task": {
        "schema": UPDATE_TASK_TOOL_SCHEMA,
        "function": update_task
    },
    "delete_task": {
        "schema": DELETE_TASK_TOOL_SCHEMA,
        "function": delete_task
    }
}
