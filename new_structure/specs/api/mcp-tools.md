# MCP (Model Context Protocol) Tools Specification

## Overview

This specification defines the MCP (Model Context Protocol) tools that enable AI agents to interact with the Todo Evolution application. MCP tools provide a standardized way for AI models to perform CRUD operations and advanced task management through the OpenAI Agents SDK.

### Phase III AI Integration
These MCP tools are essential for Phase III of the Todo Evolution project, where:
- **OpenAI Agents SDK** uses these tools to enable AI agents to manage tasks
- **Google Gemini 2.5 Flash** processes user requests and decides which tools to invoke
- **Stateless Architecture** ensures all operations go through these database-backed tools
- **Real-time Context** loads conversation history and user data for each interaction

## MCP Tool Architecture

### Tool Registration
```python
# backend/app/ai/tools/registry.py
from typing import Dict, List, Any
from pydantic import BaseModel, Field

class MCPTool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: callable

class MCPToolRegistry:
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._register_core_tools()

    def _register_core_tools(self):
        # Register all core MCP tools
        self.register_tool(create_task_tool)
        self.register_tool(list_tasks_tool)
        self.register_tool(update_task_tool)
        self.register_tool(delete_task_tool)
        self.register_tool(get_task_tool)
        self.register_tool(search_tasks_tool)
        self.register_tool(get_task_statistics_tool)
        self.register_tool(get_user_profile_tool)
        self.register_tool(update_user_preferences_tool)
```

## Core MCP Tools

### 1. create_task
Creates a new task for the user.

**Tool Definition**:
```json
{
  "name": "create_task",
  "description": "Create a new task with title, description, priority, and due date",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Task title (required, 1-255 characters)",
        "minLength": 1,
        "maxLength": 255
      },
      "description": {
        "type": "string",
        "description": "Detailed task description (optional)",
        "maxLength": 2000
      },
      "priority": {
        "type": "string",
        "description": "Task priority level",
        "enum": ["low", "medium", "high", "urgent"],
        "default": "medium"
      },
      "category": {
        "type": "string",
        "description": "Task category for organization",
        "maxLength": 100
      },
      "due_date": {
        "type": "string",
        "description": "Due date in ISO 8601 format (optional)",
        "format": "date-time"
      },
      "tags": {
        "type": "array",
        "description": "Array of tags for the task",
        "items": {
          "type": "string",
          "maxLength": 50
        },
        "maxItems": 10
      }
    },
    "required": ["title"]
  }
}
```

**Implementation**:
```python
# backend/app/ai/tools/tasks.py
from typing import Dict, Any
from datetime import datetime
from app.crud import create_task
from app.schemas import TaskCreate
from app.models import User

async def create_task_handler(parameters: Dict[str, Any], user: User) -> Dict[str, Any]:
    try:
        # Parse due_date if provided
        due_date = None
        if parameters.get("due_date"):
            due_date = datetime.fromisoformat(parameters["due_date"])

        # Create task data
        task_data = TaskCreate(
            title=parameters["title"],
            description=parameters.get("description"),
            priority=parameters.get("priority", "medium"),
            category=parameters.get("category"),
            due_date=due_date,
            tags=parameters.get("tags", [])
        )

        # Create task in database
        task = await create_task(task_data=task_data, user_id=user.id)

        return {
            "success": True,
            "task": task.to_dict(),
            "message": f"Task '{task.title}' created successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create task"
        }

# Tool registration
create_task_tool = MCPTool(
    name="create_task",
    description="Create a new task",
    parameters={
        "type": "object",
        "properties": {
            "title": {"type": "string", "minLength": 1, "maxLength": 255},
            "description": {"type": "string", "maxLength": 2000},
            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
            "category": {"type": "string", "maxLength": 100},
            "due_date": {"type": "string", "format": "date-time"},
            "tags": {"type": "array", "items": {"type": "string"}, "maxItems": 10}
        },
        "required": ["title"]
    },
    handler=create_task_handler
)
```

### 2. list_tasks
Lists tasks with optional filtering and pagination.

**Tool Definition**:
```json
{
  "name": "list_tasks",
  "description": "List user's tasks with optional filters and sorting",
  "parameters": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "description": "Filter by task status",
        "enum": ["pending", "completed", "cancelled", "all"],
        "default": "all"
      },
      "priority": {
        "type": "string",
        "description": "Filter by priority level",
        "enum": ["low", "medium", "high", "urgent"]
      },
      "category": {
        "type": "string",
        "description": "Filter by category"
      },
      "limit": {
        "type": "integer",
        "description": "Maximum number of tasks to return",
        "default": 20,
        "minimum": 1,
        "maximum": 100
      },
      "offset": {
        "type": "integer",
        "description": "Number of tasks to skip",
        "default": 0,
        "minimum": 0
      },
      "sort": {
        "type": "string",
        "description": "Sort field",
        "enum": ["created_at", "updated_at", "due_date", "priority", "title"],
        "default": "created_at"
      },
      "order": {
        "type": "string",
        "description": "Sort order",
        "enum": ["asc", "desc"],
        "default": "desc"
      }
    }
  }
}
```

**Implementation**:
```python
async def list_tasks_handler(parameters: Dict[str, Any], user: User) -> Dict[str, Any]:
    try:
        # Build filters
        filters = {}
        if parameters.get("status") and parameters["status"] != "all":
            filters["status"] = parameters["status"]
        if parameters.get("priority"):
            filters["priority"] = parameters["priority"]
        if parameters.get("category"):
            filters["category"] = parameters["category"]

        # Get tasks
        tasks = await get_tasks(
            user_id=user.id,
            limit=parameters.get("limit", 20),
            offset=parameters.get("offset", 0),
            filters=filters,
            sort=parameters.get("sort", "created_at"),
            order=parameters.get("order", "desc")
        )

        # Get total count for pagination
        total_count = await count_tasks(user_id=user.id, filters=filters)

        return {
            "success": True,
            "tasks": [task.to_dict() for task in tasks],
            "total": total_count,
            "limit": parameters.get("limit", 20),
            "offset": parameters.get("offset", 0),
            "message": f"Found {total_count} tasks"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to list tasks"
        }
```

### 3. update_task
Updates an existing task.

**Tool Definition**:
```json
{
  "name": "update_task",
  "description": "Update an existing task",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "UUID of the task to update",
        "format": "uuid"
      },
      "updates": {
        "type": "object",
        "description": "Fields to update",
        "properties": {
          "title": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
          },
          "description": {
            "type": "string",
            "maxLength": 2000
          },
          "status": {
            "type": "string",
            "enum": ["pending", "completed", "cancelled", "in_progress"]
          },
          "priority": {
            "type": "string",
            "enum": ["low", "medium", "high", "urgent"]
          },
          "category": {
            "type": "string",
            "maxLength": 100
          },
          "due_date": {
            "type": "string",
            "format": "date-time"
          },
          "tags": {
            "type": "array",
            "items": {
              "type": "string",
              "maxLength": 50
            },
            "maxItems": 10
          }
        }
      }
    },
    "required": ["task_id", "updates"]
  }
}
```

### 4. delete_task
Deletes a task.

**Tool Definition**:
```json
{
  "name": "delete_task",
  "description": "Delete a task permanently",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "UUID of the task to delete",
        "format": "uuid"
      }
    },
    "required": ["task_id"]
  }
}
```

### 5. get_task
Get a single task by ID.

**Tool Definition**:
```json
{
  "name": "get_task",
  "description": "Get detailed information about a specific task",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "UUID of the task",
        "format": "uuid"
      }
    },
    "required": ["task_id"]
  }
}
```

### 6. search_tasks
Search tasks by content.

**Tool Definition**:
```json
{
  "name": "search_tasks",
  "description": "Search tasks by title, description, or tags",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query",
        "minLength": 1,
        "maxLength": 100
      },
      "limit": {
        "type": "integer",
        "description": "Maximum results to return",
        "default": 20,
        "minimum": 1,
        "maximum": 100
      }
    },
    "required": ["query"]
  }
}
```

### 7. get_task_statistics
Get user's task statistics.

**Tool Definition**:
```json
{
  "name": "get_task_statistics",
  "description": "Get comprehensive task statistics for the user",
  "parameters": {
    "type": "object",
    "properties": {
      "period": {
        "type": "string",
        "description": "Time period for statistics",
        "enum": ["today", "week", "month", "year", "all"],
        "default": "all"
      }
    }
  }
}
```

**Implementation**:
```python
async def get_task_statistics_handler(parameters: Dict[str, Any], user: User) -> Dict[str, Any]:
    try:
        period = parameters.get("period", "all")

        # Get statistics based on period
        stats = await calculate_task_statistics(
            user_id=user.id,
            period=period
        )

        return {
            "success": True,
            "statistics": stats,
            "period": period,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get statistics"
        }

async def calculate_task_statistics(user_id: str, period: str) -> Dict[str, Any]:
    """Calculate comprehensive task statistics"""
    # Get date range based on period
    end_date = datetime.utcnow()
    if period == "today":
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = end_date - timedelta(days=7)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "year":
        start_date = end_date - timedelta(days=365)
    else:  # all
        start_date = None

    # Query database for statistics
    total_tasks = await count_tasks(user_id=user_id, start_date=start_date)
    pending_tasks = await count_tasks(user_id=user_id, status="pending", start_date=start_date)
    completed_tasks = await count_tasks(user_id=user_id, status="completed", start_date=start_date)

    # Get priority breakdown
    priority_stats = await get_task_count_by_priority(user_id=user_id, start_date=start_date)

    # Get category breakdown
    category_stats = await get_task_count_by_category(user_id=user_id, start_date=start_date)

    # Calculate completion rate
    completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0

    # Get overdue tasks
    overdue_tasks = await count_overdue_tasks(user_id=user_id)

    # Get productivity trend (tasks completed per day)
    productivity_trend = await get_productivity_trend(user_id=user_id, days=30)

    return {
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": round(completion_rate, 2),
        "productivity_score": calculate_productivity_score(completion_tasks, pending_tasks),
        "breakdown": {
            "by_priority": priority_stats,
            "by_category": category_stats
        },
        "trends": {
            "daily_completion": productivity_trend
        }
    }
```

### 8. get_user_profile
Get user profile information.

**Tool Definition**:
```json
{
  "name": "get_user_profile",
  "description": "Get user's profile information and preferences",
  "parameters": {
    "type": "object",
    "properties": {}
  }
}
```

### 9. update_user_preferences
Update user preferences.

**Tool Definition**:
```json
{
  "name": "update_user_preferences",
  "description": "Update user preferences for AI interactions",
  "parameters": {
    "type": "object",
    "properties": {
      "preferences": {
        "type": "object",
        "description": "User preferences to update",
        "properties": {
          "ai_response_style": {
            "type": "string",
            "enum": ["concise", "detailed", "friendly", "professional"]
          },
          "default_priority": {
            "type": "string",
            "enum": ["low", "medium", "high", "urgent"]
          },
          "timezone": {
            "type": "string",
            "description": "User's timezone (IANA format)"
          },
          "notifications": {
            "type": "object",
            "properties": {
              "task_reminders": {"type": "boolean"},
              "daily_summary": {"type": "boolean"},
              "ai_suggestions": {"type": "boolean"}
            }
          }
        }
      }
    },
    "required": ["preferences"]
  }
}
```

## MCP Tool Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    // Tool-specific data
  },
  "message": "Operation completed successfully",
  "timestamp": "2025-12-21T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "task_id",
      "issue": "Invalid UUID format"
    }
  },
  "timestamp": "2025-12-21T10:30:00Z"
}
```

## Tool Security and Validation

### Input Validation
- All parameters validated against schemas
- SQL injection prevention through ORMs
- XSS prevention in text fields
- File path traversal prevention
- Resource limits enforced

### Authorization
- All operations require valid user context
- Row-level security (users only access their data)
- Rate limiting per user
- Audit logging for all tool calls

### Error Handling
```python
# backend/app/ai/tools/base.py
from functools import wraps
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)

def mcp_tool_handler(func: Callable) -> Callable:
    """Decorator for MCP tool handlers with error handling"""
    @wraps(func)
    async def wrapper(parameters: Dict[str, Any], user: User) -> Dict[str, Any]:
        try:
            # Validate user
            if not user or not user.is_active:
                return {
                    "success": False,
                    "error": {
                        "code": "AUTHENTICATION_ERROR",
                        "message": "User not authenticated or inactive"
                    }
                }

            # Execute tool
            result = await func(parameters, user)

            # Log successful tool call
            logger.info(f"Tool {func.__name__} executed successfully for user {user.id}")

            return result

        except ValidationError as e:
            logger.warning(f"Validation error in tool {func.__name__}: {str(e)}")
            return {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input data",
                    "details": str(e)
                }
            }

        except PermissionError as e:
            logger.warning(f"Permission error in tool {func.__name__}: {str(e)}")
            return {
                "success": False,
                "error": {
                    "code": "PERMISSION_ERROR",
                    "message": "Insufficient permissions"
                }
            }

        except Exception as e:
            logger.error(f"Unexpected error in tool {func.__name__}: {str(e)}")
            return {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal error occurred"
                }
            }

    return wrapper
```

## Tool Testing

### Unit Testing
```python
# tests/test_mcp_tools.py
import pytest
from app.ai.tools.tasks import create_task_handler, list_tasks_handler
from app.models import User

@pytest.mark.asyncio
async def test_create_task_handler():
    # Create test user
    user = User(id="test-uuid", email="test@example.com")

    # Test parameters
    parameters = {
        "title": "Test Task",
        "description": "Test description",
        "priority": "high"
    }

    # Call handler
    result = await create_task_handler(parameters, user)

    # Assertions
    assert result["success"] is True
    assert "task" in result
    assert result["task"]["title"] == "Test Task"
    assert result["task"]["priority"] == "high"

@pytest.mark.asyncio
async def test_create_task_validation():
    user = User(id="test-uuid", email="test@example.com")

    # Test missing required title
    parameters = {
        "description": "Test description"
    }

    result = await create_task_handler(parameters, user)

    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"
```

### Integration Testing
```python
# tests/test_mcp_integration.py
import pytest
from app.ai.tools.registry import MCPToolRegistry

@pytest.mark.asyncio
async def test_mcp_tool_execution():
    registry = MCPToolRegistry()

    # Test creating a task
    result = await registry.execute_tool(
        tool_name="create_task",
        parameters={
            "title": "Integration Test Task"
        },
        user=test_user
    )

    assert result["success"] is True

    # Test listing tasks
    result = await registry.execute_tool(
        tool_name="list_tasks",
        parameters={},
        user=test_user
    )

    assert result["success"] is True
    assert len(result["tasks"]) > 0
```

## Performance Monitoring

### Metrics Collection
- Tool execution time
- Tool success/failure rates
- Most used tools per user
- Error rates by tool type
- Resource usage per tool call

### Monitoring Implementation
```python
# backend/app/ai/tools/monitoring.py
import time
from prometheus_client import Histogram, Counter

# Metrics
tool_execution_time = Histogram(
    'mcp_tool_execution_seconds',
    'Time spent executing MCP tools',
    ['tool_name']
)

tool_calls_total = Counter(
    'mcp_tool_calls_total',
    'Total number of MCP tool calls',
    ['tool_name', 'status']
)

def monitor_tool_execution(tool_name: str):
    """Decorator to monitor tool execution"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                tool_calls_total.labels(tool_name=tool_name, status='success').inc()
                return result
            except Exception as e:
                tool_calls_total.labels(tool_name=tool_name, status='error').inc()
                raise
            finally:
                execution_time = time.time() - start_time
                tool_execution_time.labels(tool_name=tool_name).observe(execution_time)
        return wrapper
    return decorator
```