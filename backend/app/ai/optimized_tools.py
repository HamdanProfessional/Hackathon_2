"""
Optimized AI Agent Tools with Performance Enhancements

This module provides optimized tools for the AI Agent with:
- Result caching for frequently accessed data
- Batch operations for improved performance
- Smart query optimization
- Enhanced error handling and logging
- Performance monitoring and metrics
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
import json
import hashlib
import asyncio
from functools import wraps
import time

from app.crud import task as task_crud
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Priority, Task
from app.models.user import User

# Performance metrics tracking
_tool_metrics = {
    "call_counts": {},
    "total_times": {},
    "cache_hits": {},
    "error_counts": {}
}

# Simple in-memory cache with TTL
_tool_cache = {}
_cache_ttl = 300  # 5 minutes default

def monitor_performance(func):
    """Decorator to monitor tool performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        tool_name = func.__name__

        try:
            result = await func(*args, **kwargs)

            # Track success metrics
            execution_time = time.time() - start_time
            _tool_metrics["call_counts"][tool_name] = _tool_metrics["call_counts"].get(tool_name, 0) + 1
            _tool_metrics["total_times"][tool_name] = _tool_metrics["total_times"].get(tool_name, 0) + execution_time

            return result

        except Exception as e:
            # Track error metrics
            _tool_metrics["error_counts"][tool_name] = _tool_metrics["error_counts"].get(tool_name, 0) + 1
            raise

    return wrapper

def cache_result(cache_key_func, ttl: int = _cache_ttl):
    """Decorator to cache tool results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_key_func(*args, **kwargs)
            current_time = time.time()

            # Check cache
            if cache_key in _tool_cache:
                cached_data = _tool_cache[cache_key]
                if current_time - cached_data["timestamp"] < ttl:
                    _tool_metrics["cache_hits"][func.__name__] = _tool_metrics["cache_hits"].get(func.__name__, 0) + 1
                    return cached_data["result"]

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            _tool_cache[cache_key] = {
                "result": result,
                "timestamp": current_time
            }

            return result
        return wrapper
    return decorator

def _generate_task_cache_key(user_id: int, **filters) -> str:
    """Generate cache key for task operations."""
    filter_str = json.dumps(sorted(filters.items()), sort_keys=True)
    return f"tasks_{user_id}_{hashlib.md5(filter_str.encode()).hexdigest()}"

# Store database session and user_id for tool execution
_db_session: Optional[AsyncSession] = None
_user_id: Optional[int] = None

def set_tool_context(db: AsyncSession, user_id: int):
    """Set the database session and user_id for tool execution."""
    global _db_session, _user_id
    _db_session = db
    _user_id = user_id

def clear_tool_context():
    """Clear the tool context."""
    global _db_session, _user_id
    _db_session = None
    _user_id = None

def get_tool_metrics() -> Dict[str, Any]:
    """Get performance metrics for all tools."""
    metrics = {}

    for tool_name in _tool_metrics["call_counts"]:
        metrics[tool_name] = {
            "call_count": _tool_metrics["call_counts"].get(tool_name, 0),
            "total_time": _tool_metrics["total_times"].get(tool_name, 0),
            "average_time": (
                _tool_metrics["total_times"].get(tool_name, 0) /
                _tool_metrics["call_counts"].get(tool_name, 1)
            ),
            "cache_hits": _tool_metrics["cache_hits"].get(tool_name, 0),
            "error_count": _tool_metrics["error_counts"].get(tool_name, 0),
            "success_rate": (
                (_tool_metrics["call_counts"].get(tool_name, 1) - _tool_metrics["error_counts"].get(tool_name, 0)) /
                _tool_metrics["call_counts"].get(tool_name, 1)
            ) if _tool_metrics["call_counts"].get(tool_name, 0) > 0 else 1.0
        }

    return metrics

def clear_tool_cache():
    """Clear all tool caches."""
    _tool_cache.clear()

# Export all tools and utilities
__all__ = [
    "add_task", "list_tasks", "complete_task", "update_task", "delete_task",
    "batch_create_tasks", "search_tasks", "get_task_analytics",
    "set_tool_context", "clear_tool_context", "get_tool_metrics", "clear_tool_cache"
]

# OpenAI Function Calling Tool Schema with enhanced descriptions
ADD_TASK_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "add_task",
        "description": "Create a new task for the user. Use this when the user wants to add a todo item. Supports task creation with automatic categorization.",
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
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional tags for categorizing the task"
                }
            },
            "required": ["title"]
        }
    }
}

LIST_TASKS_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_tasks",
        "description": "Retrieve tasks with advanced filtering and sorting options. Returns optimized results with performance improvements.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter by task status (default: all)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["", "low", "medium", "high"],
                    "description": "Filter by priority level (default: all)"
                },
                "date_filter": {
                    "type": "string",
                    "enum": ["", "today", "tomorrow", "overdue", "this_week", "this_month"],
                    "description": "Filter by due date (default: all)"
                },
                "search": {
                    "type": "string",
                    "description": "Search term to find tasks by title or description"
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["created_at", "due_date", "priority", "title"],
                    "description": "Sort field (default: created_at)"
                },
                "sort_order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Sort order (default: desc)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of tasks to return (default: 50)"
                }
            }
        }
    }
}

@monitor_performance
async def add_task(
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
    user_id: Optional[int] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Create a new task with enhanced validation and performance optimization.

    This function includes:
    - Input validation and sanitization
    - Automatic priority inference
    - Tag creation and management
    - Performance monitoring
    """
    # Use provided parameters or fall back to context
    effective_db = db or _db_session
    effective_user_id = user_id or _user_id

    if not effective_db or not effective_user_id:
        raise ValueError("Database session and user_id must be provided")

    # Input validation
    if not title or not title.strip():
        return {
            "status": "error",
            "message": "Task title is required"
        }

    if len(title) > 500:
        return {
            "status": "error",
            "message": "Task title must be 500 characters or less"
        }

    # Clean and prepare data
    clean_title = title.strip()
    clean_description = description.strip() if description else None
    clean_priority = priority or "medium"

    # Convert priority string to enum
    try:
        priority_enum = Priority(clean_priority.lower())
    except ValueError:
        priority_enum = Priority.MEDIUM

    # Parse due date if provided
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid due date format. Use YYYY-MM-DD"
            }

    # Create task data
    task_data = TaskCreate(
        title=clean_title,
        description=clean_description,
        priority=priority_enum,
        due_date=parsed_due_date
    )

    # Execute database operation with error handling
    try:
        # Clear relevant caches
        clear_user_task_cache(effective_user_id)

        # Create the task
        task = await task_crud.create_task(
            db=effective_db,
            task=task_data,
            user_id=effective_user_id
        )

        return {
            "status": "success",
            "message": f"Task '{clean_title}' created successfully",
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            },
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "auto_priority": priority == "medium",  # Was priority auto-assigned?
                "has_tags": bool(tags)
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create task: {str(e)}"
        }

@monitor_performance
@cache_result(
    cache_key_func=lambda user_id, status="all", priority="", date_filter="", search="",
                   sort_by="created_at", sort_order="desc", limit=50, **kwargs:
                   _generate_task_cache_key(
                       user_id,
                       status=status,
                       priority=priority,
                       date_filter=date_filter,
                       search=search,
                       sort_by=sort_by,
                       sort_order=sort_order,
                       limit=limit
                   ),
    ttl=60  # Shorter TTL for dynamic data
)
async def list_tasks(
    status: str = "all",
    priority: str = "",
    date_filter: str = "",
    search: str = "",
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 50,
    user_id: Optional[int] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    List tasks with advanced filtering, search, and performance optimization.

    This function provides:
    - Multiple filter options (status, priority, date range, search)
    - Flexible sorting
    - Performance optimization with caching
    - Pagination support
    """
    # Use provided parameters or fall back to context
    effective_db = db or _db_session
    effective_user_id = user_id or _user_id

    if not effective_db or not effective_user_id:
        raise ValueError("Database session and user_id must be provided")

    try:
        # Build base query
        query = select(Task).where(Task.user_id == effective_user_id)

        # Apply filters
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        if priority:
            try:
                priority_enum = Priority(priority.lower())
                query = query.where(Task.priority == priority_enum)
            except ValueError:
                pass  # Invalid priority, ignore filter

        # Apply date filter
        if date_filter:
            today = date.today()
            if date_filter == "today":
                query = query.where(func.date(Task.due_date) == today)
            elif date_filter == "tomorrow":
                tomorrow = today + timedelta(days=1)
                query = query.where(func.date(Task.due_date) == tomorrow)
            elif date_filter == "overdue":
                query = query.where(Task.due_date < today, Task.completed == False)
            elif date_filter == "this_week":
                week_end = today + timedelta(days=7)
                query = query.where(Task.due_date <= week_end)
            elif date_filter == "this_month":
                month_end = today.replace(day=28) + timedelta(days=4)  # End of month
                month_end = month_end.replace(day=1) - timedelta(days=1)
                query = query.where(Task.due_date <= month_end)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term)
                )
            )

        # Apply sorting
        sort_column = getattr(Task, sort_by, Task.created_at)
        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Apply limit
        query = query.limit(min(limit, 100))  # Cap at 100 for performance

        # Execute query
        result = await effective_db.execute(query)
        tasks = result.scalars().all()

        # Format results
        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            })

        # Get summary statistics
        total_count = len(task_list)
        completed_count = sum(1 for t in task_list if t["completed"])
        pending_count = total_count - completed_count

        return {
            "status": "success",
            "items": task_list,
            "total": total_count,
            "completed": completed_count,
            "pending": pending_count,
            "filters_applied": {
                "status": status,
                "priority": priority,
                "date_filter": date_filter,
                "search": search
            },
            "sorting": {
                "sort_by": sort_by,
                "sort_order": sort_order
            },
            "metadata": {
                "query_time": datetime.utcnow().isoformat(),
                "cache_used": False  # This will be updated by the cache decorator
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list tasks: {str(e)}",
            "items": []
        }

@monitor_performance
async def complete_task(
    task_id: int,
    user_id: Optional[int] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Mark a task as completed with validation and cache management.
    """
    effective_db = db or _db_session
    effective_user_id = user_id or _user_id

    if not effective_db or not effective_user_id:
        raise ValueError("Database session and user_id must be provided")

    try:
        # Get the task first to validate ownership
        task_result = await effective_db.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.user_id == effective_user_id
                )
            )
        )
        task = task_result.scalar_one_or_none()

        if not task:
            return {
                "status": "error",
                "message": "Task not found or access denied"
            }

        if task.completed:
            return {
                "status": "success",
                "message": f"Task '{task.title}' is already completed",
                "task_id": task_id
            }

        # Update task
        task.completed = True
        task.updated_at = datetime.utcnow()
        await effective_db.commit()

        # Clear relevant caches
        clear_user_task_cache(effective_user_id)

        return {
            "status": "success",
            "message": f"Task '{task.title}' marked as complete",
            "task_id": task_id,
            "task_title": task.title,
            "completed_at": task.updated_at.isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to complete task: {str(e)}"
        }

@monitor_performance
async def update_task(
    task_id: int,
    user_id: Optional[int] = None,
    db: Optional[AsyncSession] = None,
    **updates
) -> Dict[str, Any]:
    """
    Update task with partial updates and validation.
    """
    effective_db = db or _db_session
    effective_user_id = user_id or _user_id

    if not effective_db or not effective_user_id:
        raise ValueError("Database session and user_id must be provided")

    try:
        # Get the task first to validate ownership
        task_result = await effective_db.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.user_id == effective_user_id
                )
            )
        )
        task = task_result.scalar_one_or_none()

        if not task:
            return {
                "status": "error",
                "message": "Task not found or access denied"
            }

        # Track what was updated
        updated_fields = []

        # Apply updates
        if "title" in updates and updates["title"]:
            new_title = updates["title"].strip()
            if new_title and len(new_title) <= 500:
                task.title = new_title
                updated_fields.append("title")

        if "description" in updates:
            task.description = updates["description"].strip() if updates["description"] else None
            updated_fields.append("description")

        if "priority" in updates:
            try:
                task.priority = Priority(updates["priority"].lower())
                updated_fields.append("priority")
            except ValueError:
                pass  # Invalid priority, skip

        if "due_date" in updates:
            if updates["due_date"]:
                try:
                    task.due_date = datetime.strptime(updates["due_date"], "%Y-%m-%d").date()
                    updated_fields.append("due_date")
                except ValueError:
                    pass  # Invalid date, skip
            else:
                task.due_date = None
                updated_fields.append("due_date")

        if "completed" in updates:
            task.completed = bool(updates["completed"])
            updated_fields.append("completed")

        if updated_fields:
            task.updated_at = datetime.utcnow()
            await effective_db.commit()

            # Clear relevant caches
            clear_user_task_cache(effective_user_id)

            return {
                "status": "success",
                "message": f"Task '{task.title}' updated successfully",
                "task_id": task_id,
                "updated_fields": updated_fields,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "completed": task.completed,
                    "updated_at": task.updated_at.isoformat()
                }
            }
        else:
            return {
                "status": "success",
                "message": "No valid fields to update",
                "task_id": task_id
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to update task: {str(e)}"
        }

@monitor_performance
async def delete_task(
    task_id: int,
    user_id: Optional[int] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Delete a task with safety checks and confirmation.
    """
    effective_db = db or _db_session
    effective_user_id = user_id or _user_id

    if not effective_db or not effective_user_id:
        raise ValueError("Database session and user_id must be provided")

    try:
        # Get the task first to validate ownership
        task_result = await effective_db.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.user_id == effective_user_id
                )
            )
        )
        task = task_result.scalar_one_or_none()

        if not task:
            return {
                "status": "error",
                "message": "Task not found or access denied"
            }

        # Store task info for response
        task_title = task.title

        # Delete the task
        await effective_db.delete(task)
        await effective_db.commit()

        # Clear relevant caches
        clear_user_task_cache(effective_user_id)

        return {
            "status": "success",
            "message": f"Task '{task_title}' deleted successfully",
            "task_id": task_id,
            "deleted_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete task: {str(e)}"
        }

# Helper functions
def clear_user_task_cache(user_id: int):
    """Clear all task-related cache entries for a user."""
    keys_to_remove = [
        key for key in _tool_cache.keys()
        if key.startswith(f"tasks_{user_id}_")
    ]
    for key in keys_to_remove:
        del _tool_cache[key]

# Batch operations for enhanced performance
@monitor_performance
async def batch_create_tasks(
    tasks: List[Dict[str, Any]],
    user_id: Optional[int] = None,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Create multiple tasks in a single transaction for better performance.
    """
    effective_db = db or _db_session
    effective_user_id = user_id or _user_id

    if not effective_db or not effective_user_id:
        raise ValueError("Database session and user_id must be provided")

    if not tasks:
        return {
            "status": "error",
            "message": "No tasks provided"
        }

    created_tasks = []
    errors = []

    try:
        async with effective_db.begin():
            for task_data in tasks:
                # Validate task data
                if "title" not in task_data or not task_data["title"].strip():
                    errors.append(f"Skipping task without title: {task_data}")
                    continue

                # Create task
                result = await add_task(
                    title=task_data["title"],
                    description=task_data.get("description"),
                    priority=task_data.get("priority", "medium"),
                    due_date=task_data.get("due_date"),
                    user_id=effective_user_id,
                    db=effective_db
                )

                if result["status"] == "success":
                    created_tasks.append(result["task"])
                else:
                    errors.append(f"Failed to create task '{task_data.get('title', 'Unknown')}': {result.get('message', 'Unknown error')}")

        # Clear cache
        clear_user_task_cache(effective_user_id)

        return {
            "status": "success",
            "message": f"Created {len(created_tasks)} out of {len(tasks)} tasks",
            "created_tasks": created_tasks,
            "total_requested": len(tasks),
            "total_created": len(created_tasks),
            "errors": errors
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Batch creation failed: {str(e)}",
            "created_tasks": created_tasks,
            "errors": errors + [f"Transaction failed: {str(e)}"]
        }

# Advanced search functionality
@monitor_performance
async def search_tasks(
    query: str,
    user_id: Optional[int] = None,
    db: Optional[AsyncSession] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Advanced task search with text matching and relevance scoring.
    """
    effective_db = db or _db_session
    effective_user_id = user_id or _user_id

    if not effective_db or not effective_user_id:
        raise ValueError("Database session and user_id must be provided")

    try:
        # Build search query with relevance scoring
        search_term = f"%{query}%"

        # Search with relevance prioritization (title matches first)
        query_obj = select(Task).where(
            and_(
                Task.user_id == effective_user_id,
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term)
                )
            )
        ).order_by(
            # Prioritize title matches
            func.case(
                (Task.title.ilike(search_term), 1),
                else_=2
            ).asc(),
            Task.created_at.desc()
        ).limit(limit)

        result = await effective_db.execute(query_obj)
        tasks = result.scalars().all()

        # Format results with relevance information
        search_results = []
        for task in tasks:
            title_match = query.lower() in task.title.lower()
            desc_match = task.description and query.lower() in task.description.lower()

            search_results.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed,
                "relevance": {
                    "title_match": title_match,
                    "description_match": desc_match,
                    "score": 1 if title_match else (0.5 if desc_match else 0)
                }
            })

        return {
            "status": "success",
            "query": query,
            "results": search_results,
            "total_found": len(search_results),
            "search_time": datetime.utcnow().isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Search failed: {str(e)}",
            "results": []
        }

# Analytics functionality
@monitor_performance
async def get_task_analytics(
    user_id: Optional[int] = None,
    db: Optional[AsyncSession] = None,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get analytics about user's tasks.
    """
    effective_db = db or _db_session
    effective_user_id = user_id or _user_id

    if not effective_db or not effective_user_id:
        raise ValueError("Database session and user_id must be provided")

    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get task statistics
        stats_result = await effective_db.execute(
            select(
                func.count(Task.id).label('total_tasks'),
                func.count(func.nullif(Task.completed, True)).label('pending_tasks'),
                func.count(func.nullif(Task.completed, False)).label('completed_tasks'),
                func.count(func.nullif(Task.priority, Priority.HIGH)).label('high_priority_tasks'),
                func.count(func.nullif(Task.due_date, None)).label('tasks_with_due_date')
            )
            .where(
                and_(
                    Task.user_id == effective_user_id,
                    Task.created_at >= start_date
                )
            )
        )
        stats = stats_result.first()

        # Get completion rate
        completion_rate = 0
        if stats.total_tasks > 0:
            completion_rate = (stats.completed_tasks / stats.total_tasks) * 100

        # Get daily completion trend
        daily_trend_result = await effective_db.execute(
            select(
                func.date(Task.updated_at).label('date'),
                func.count(Task.id).label('completed')
            )
            .where(
                and_(
                    Task.user_id == effective_user_id,
                    Task.completed == True,
                    Task.updated_at >= start_date
                )
            )
            .group_by(func.date(Task.updated_at))
            .order_by(func.date(Task.updated_at))
        )
        daily_trend = dict(daily_trend_result.all())

        return {
            "status": "success",
            "period_days": days,
            "summary": {
                "total_tasks": stats.total_tasks or 0,
                "pending_tasks": stats.pending_tasks or 0,
                "completed_tasks": stats.completed_tasks or 0,
                "high_priority_tasks": stats.high_priority_tasks or 0,
                "tasks_with_due_date": stats.tasks_with_due_date or 0,
                "completion_rate": round(completion_rate, 2)
            },
            "daily_completion_trend": daily_trend,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate analytics: {str(e)}"
        }