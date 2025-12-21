---
name: mcp-tool-maker
description: Creates MCP (Model Context Protocol) tools that expose backend functionality to AI agents. Generates tool schemas, implementations, and server setup. Use when building Phase III AI chatbots or any application needing to connect AI agents with existing backend operations.
---

# MCP Tool Maker

## Quick Start

```python
from mcp_tool_maker import MCPTool, MCPServer

# Create a simple MCP tool
add_task_tool = MCPTool(
    name="add_task",
    description="Create a new task",
    handler=add_task_handler,
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Task title"},
            "description": {"type": "string", "description": "Optional description"}
        },
        "required": ["title"]
    }
)

# Create and start MCP server
server = MCPServer(
    name="todo-tools",
    version="1.0.0",
    tools=[add_task_tool, list_tasks_tool, complete_task_tool]
)
server.run()
```

## MCP Tool Structure

### Core Components

1. **Tool Definition**: Schema and metadata
2. **Handler Function**: Implementation logic
3. **Server Registration**: Tools grouped in server
4. **Protocol Compliance**: MCP SDK integration

### Generated File Structure
```
mcp_server/
├── tools/
│   ├── __init__.py
│   ├── base_tool.py      # Base MCP tool class
│   ├── task_tools.py     # Task management tools
│   └── user_tools.py     # User management tools
├── server.py             # MCP server setup
├── handlers/
│   ├── task_handlers.py  # Tool implementation
│   └── auth_handlers.py  # Authentication handlers
└── schemas/
    └── tool_schemas.py   # JSON schemas for tools
```

## Tool Generation Templates

### CRUD Tool Generator
```python
# Generate complete CRUD tools for a model
generate_mcp_crud(
    model_name="Task",
    operations=["create", "read", "update", "delete", "list"],
    user_field="user_id",  # Multi-tenant support
    soft_delete=True       # Add soft delete operations
)

# Output:
# - create_task tool
# - get_task tool
# - update_task tool
# - delete_task tool
# - list_tasks tool
# - restore_task tool (if soft_delete)
```

### Custom Tool Definition
```python
# Define custom tool with business logic
@MCPTool(
    name="complete_task",
    description="Mark a task as complete",
    requires_auth=True,
    rate_limit=10  # Max 10 calls per minute
)
async def complete_task_handler(task_id: int, user_id: str):
    """Mark task as complete with side effects."""
    # Get task
    task = TaskService.get_task(user_id, task_id)
    if not task:
        raise ToolError(f"Task {task_id} not found")

    # Check dependencies
    if has_dependencies(task):
        return {
            "success": False,
            "message": "Task has uncompleted dependencies",
            "dependencies": get_dependencies(task)
        }

    # Complete task
    task.completed = True
    task.completed_at = datetime.utcnow()
    TaskService.update(task)

    # Trigger completion event
    await EventService.task_completed(task)

    return {
        "success": True,
        "task_id": task_id,
        "title": task.title,
        "message": f"Task '{task.title}' marked as complete"
    }
```

## Complete Todo MCP Tools

### 1. Add Task Tool
```python
# tools/task_tools.py
{
    "name": "add_task",
    "description": "Create a new task in the user's todo list",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Unique identifier for the user"
            },
            "title": {
                "type": "string",
                "description": "Brief task title (1-200 characters)",
                "minLength": 1,
                "maxLength": 200
            },
            "description": {
                "type": "string",
                "description": "Optional detailed description",
                "maxLength": 1000
            },
            "priority": {
                "type": "string",
                "description": "Task priority level",
                "enum": ["low", "medium", "high"],
                "default": "medium"
            },
            "due_date": {
                "type": "string",
                "description": "Due date in ISO 8601 format",
                "format": "date-time"
            }
        },
        "required": ["user_id", "title"]
    }
}

# Handler
async def add_task_handler(
    user_id: str,
    title: str,
    description: str = None,
    priority: str = "medium",
    due_date: str = None
) -> dict:
    """Create a new task with validation and business rules."""
    try:
        # Validate title uniqueness for today
        if TaskService.exists_today(user_id, title):
            return {
                "success": False,
                "error": "Task with this title already exists today"
            }

        # Parse due date if provided
        due_datetime = None
        if due_date:
            due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))

        # Create task
        task = TaskService.create_task(
            user_id=user_id,
            title=title,
            description=description or "",
            priority=priority,
            due_date=due_datetime
        )

        # Log creation
        logger.info(f"Task created: {task.id} for user {user_id}")

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "status": "pending"
            },
            "message": f"Task '{task.title}' created successfully"
        }

    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return {
            "success": False,
            "error": "Failed to create task"
        }
```

### 2. List Tasks Tool
```python
{
    "name": "list_tasks",
    "description": "Retrieve and filter tasks from the user's todo list",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "status": {
                "type": "string",
                "enum": ["all", "pending", "completed", "overdue"],
                "default": "all",
                "description": "Filter tasks by status"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Filter by priority level"
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 50,
                "description": "Maximum number of tasks to return"
            },
            "sort_by": {
                "type": "string",
                "enum": ["created", "due_date", "priority", "title"],
                "default": "created",
                "description": "Sort tasks by field"
            }
        },
        "required": ["user_id"]
    }
}

# Handler
async def list_tasks_handler(
    user_id: str,
    status: str = "all",
    priority: str = None,
    limit: int = 50,
    sort_by: str = "created"
) -> dict:
    """List tasks with filtering and sorting."""
    tasks = TaskService.get_user_tasks(
        user_id=user_id,
        status=status,
        priority=priority,
        limit=limit,
        sort_by=sort_by
    )

    # Add computed fields
    task_list = []
    for task in tasks:
        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "overdue": False
        }

        # Check if overdue
        if task.due_date and not task.completed:
            task_data["overdue"] = task.due_date < datetime.utcnow()

        task_list.append(task_data)

    # Get statistics
    stats = TaskService.get_task_stats(user_id)

    return {
        "success": True,
        "tasks": task_list,
        "stats": stats,
        "count": len(task_list)
    }
```

### 3. Complete Task Tool
```python
{
    "name": "complete_task",
    "description": "Mark a task as complete or incomplete",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "task_id": {"type": "integer"},
            "completed": {
                "type": "boolean",
                "default": True,
                "description": "True to mark complete, False to mark incomplete"
            }
        },
        "required": ["user_id", "task_id"]
    }
}

# Handler
async def complete_task_handler(
    user_id: str,
    task_id: int,
    completed: bool = True
) -> dict:
    """Toggle task completion status."""
    task = TaskService.get_task(user_id, task_id)
    if not task:
        return {
            "success": False,
            "error": f"Task {task_id} not found"
        }

    # Check if already in desired state
    if task.completed == completed:
        status = "already complete" if completed else "not completed"
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task is {status}",
            "status": "unchanged"
        }

    # Update status
    old_status = task.completed
    task.completed = completed
    if completed:
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None

    TaskService.update(task)

    # Log completion
    action = "completed" if completed else "reopened"
    logger.info(f"Task {task_id} {action} by user {user_id}")

    return {
        "success": True,
        "task_id": task_id,
        "title": task.title,
        "completed": task.completed,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "message": f"Task '{task.title}' marked as {action}"
    }
```

## MCP Server Setup

### Server Configuration
```python
# server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

app = Server("todo-mcp-server")

# Register all tools
@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="add_task",
            description="Create a new task",
            inputSchema=add_task_schema
        ),
        Tool(
            name="list_tasks",
            description="List user's tasks",
            inputSchema=list_tasks_schema
        ),
        Tool(
            name="complete_task",
            description="Mark task as complete",
            inputSchema=complete_task_schema
        ),
        Tool(
            name="update_task",
            description="Update task details",
            inputSchema=update_task_schema
        ),
        Tool(
            name="delete_task",
            description="Delete a task",
            inputSchema=delete_task_schema
        )
    ]

# Tool call handler
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> dict:
    """Route tool calls to appropriate handlers."""
    try:
        if name == "add_task":
            return await add_task_handler(**arguments)
        elif name == "list_tasks":
            return await list_tasks_handler(**arguments)
        elif name == "complete_task":
            return await complete_task_handler(**arguments)
        elif name == "update_task":
            return await update_task_handler(**arguments)
        elif name == "delete_task":
            return await delete_task_handler(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool {name} error: {e}")
        return {
            "success": False,
            "error": f"Tool execution failed: {str(e)}"
        }

# Run server
async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Error Handling

### Custom Tool Errors
```python
# handlers/errors.py
class ToolError(Exception):
    """Base class for tool errors."""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(message)

class ValidationError(ToolError):
    """Input validation failed."""
    pass

class AuthenticationError(ToolError):
    """User authentication failed."""
    pass

class PermissionError(ToolError):
    """User doesn't have permission."""
    pass

class ResourceNotFoundError(ToolError):
    """Requested resource not found."""
    pass

# Error response format
def format_error(error: Exception) -> dict:
    """Format errors for MCP response."""
    if isinstance(error, ToolError):
        return {
            "success": False,
            "error": error.message,
            "code": error.code or type(error).__name__
        }
    else:
        return {
            "success": False,
            "error": "An unexpected error occurred",
            "code": "INTERNAL_ERROR"
        }
```

## Testing MCP Tools

### Unit Tests
```python
# tests/test_tools.py
import pytest
from mcp_tool_maker import MCPTool

@pytest.mark.asyncio
async def test_add_task_tool():
    """Test add_task tool functionality."""
    result = await add_task_handler(
        user_id="test_user",
        title="Test Task",
        description="Test description"
    )

    assert result["success"] is True
    assert "task_id" in result["task"]
    assert result["task"]["title"] == "Test Task"

@pytest.mark.asyncio
async def test_add_task_validation():
    """Test add_task validation."""
    # Empty title
    result = await add_task_handler(user_id="test_user", title="")
    assert result["success"] is False
    assert "title" in result["error"].lower()

    # Title too long
    long_title = "x" * 201
    result = await add_task_handler(user_id="test_user", title=long_title)
    assert result["success"] is False
```

### Integration Tests
```python
# tests/test_server.py
async def test_mcp_server_tool_call():
    """Test full MCP server tool call."""
    # Mock MCP call
    response = await call_tool(
        name="add_task",
        arguments={
            "user_id": "test_user",
            "title": "Integration Test Task"
        }
    )

    assert response["success"] is True
    assert "task" in response
```

## Security Considerations

### Input Sanitization
```python
def sanitize_input(data: dict, schema: dict) -> dict:
    """Sanitize input based on schema."""
    sanitized = {}
    properties = schema.get("properties", {})

    for key, value in data.items():
        if key in properties:
            prop_schema = properties[key]

            # Type validation
            if prop_schema.get("type") == "string":
                sanitized[key] = str(value)
            elif prop_schema.get("type") == "integer":
                sanitized[key] = int(value)
            elif prop_schema.get("type") == "boolean":
                sanitized[key] = bool(value)

            # Length validation
            if "maxLength" in prop_schema:
                sanitized[key] = sanitized[key][:prop_schema["maxLength"]]

    return sanitized
```

### Rate Limiting
```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_calls: int, period: timedelta):
        self.max_calls = max_calls
        self.period = period
        self.calls = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        now = datetime.utcnow()
        user_calls = self.calls[user_id]

        # Remove old calls
        self.calls[user_id] = [
            call_time for call_time in user_calls
            if now - call_time < self.period
        ]

        # Check limit
        if len(self.calls[user_id]) >= self.max_calls:
            return False

        # Add new call
        self.calls[user_id].append(now)
        return True

# Apply to tools
rate_limiter = RateLimiter(max_calls=10, period=timedelta(minutes=1))

@MCPTool(name="add_task", rate_limit=True)
async def add_task_with_rate_limit(**kwargs):
    if not rate_limiter.is_allowed(kwargs["user_id"]):
        raise ToolError("Rate limit exceeded", "RATE_LIMIT_EXCEEDED")
    return await add_task_handler(**kwargs)
```

## Best Practices

1. **Always validate inputs** against schema
2. **Return consistent response format** with success/error
3. **Log all tool calls** for debugging
4. **Use transactions** for multi-table operations
5. **Implement proper error handling** with meaningful messages
6. **Add rate limiting** to prevent abuse
7. **Sanitize all inputs** to prevent injection
8. **Document tools** with clear descriptions
9. **Use async/await** for I/O operations
10. **Test all tools** with edge cases

## Integration Checklist

- [ ] All CRUD operations implemented
- [ ] Input validation complete
- [ ] Error handling implemented
- [ ] Rate limiting configured
- [ ] Logging added
- [ ] Tests written
- [ ] Documentation complete
- [ ] Security review done
- [ ] Performance tested
- [ ] Deployment ready