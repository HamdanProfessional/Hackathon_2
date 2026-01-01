# MCP Integration Best Practices

## Tool Design Principles

### 1. Descriptive Docstrings

The AI reads your docstrings to understand when and how to use tools.

**Good:**
```python
async def get_tasks(user_token: str, status: str = None) -> Dict:
    """
    Get all tasks for the current user.

    Use this when the user asks to see their tasks, wants a task summary,
    or needs to know what tasks they have. Supports optional filtering
    by status (pending, in_progress, completed).

    Args:
        user_token: JWT authentication token
        status: Optional filter by task status

    Returns:
        List of tasks with id, title, description, status, and priority
    """
```

**Bad:**
```python
async def get_tasks(user_token: str, status: str = None) -> Dict:
    """Get tasks."""  # Too vague - AI won't know when to use it
```

### 2. Strong Type Hints

```python
from typing import Dict, List, Optional, Literal

# Good: Specific types
async def create_task(
    user_token: str,
    title: str,
    priority: Literal["low", "normal", "high"] = "normal",
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    pass

# Bad: Generic types
async def create_task(token, data) -> dict:
    pass
```

### 3. Structured Error Handling

Always return consistent structure:

```python
# Good: Structured response
return {
    "success": True,
    "data": result
}

# Good: Structured error
return {
    "success": False,
    "error": "Descriptive error message",
    "error_code": "VALIDATION_ERROR"
}

# Bad: Inconsistent responses
if error:
    return {"error": str(e)}
else:
    return result  # Different structure!
```

### 4. Input Validation

```python
async def create_task(user_token: str, title: str, **kwargs) -> Dict:
    # Validate required fields
    if not title or len(title.strip()) == 0:
        return {
            "success": False,
            "error": "Title cannot be empty"
        }

    if len(title) > 255:
        return {
            "success": False,
            "error": "Title too long (max 255 characters)"
        }

    # Validate enums
    valid_priorities = ["low", "normal", "high"]
    priority = kwargs.get("priority", "normal")
    if priority not in valid_priorities:
        return {
            "success": False,
            "error": f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
        }

    # Proceed with creation
    ...
```

## Authentication

### Always Verify Tokens

```python
from app.auth import verify_token

@register_tool("sensitive_operation")
async def sensitive_operation(user_token: str, ...) -> Dict:
    try:
        user_id = verify_token(user_token)
        # All operations scoped to user_id
    except jwt.InvalidTokenError:
        return {"success": False, "error": "Invalid or expired token"}
```

### User Isolation

```python
# Good: User-scoped query
tasks = db.exec(
    select(Task)
    .where(Task.user_id == user_id)  # Enforce boundaries
).all()

# Bad: No user filtering (security issue!)
tasks = db.exec(select(Task)).all()
```

## Tool Naming Conventions

| Pattern | Usage | Example |
|---------|-------|---------|
| `get_<resource>` | Fetch items | `get_tasks`, `get_conversations` |
| `create_<resource>` | Create new item | `create_task`, `create_user` |
| `update_<resource>` | Modify existing | `update_task`, `update_settings` |
| `delete_<resource>` | Remove item | `delete_task`, `delete_message` |
| `search_<resource>` | Find by query | `search_tasks`, `search_messages` |
| `complete_<action>` | Perform action | `complete_task`, `archive_conversation` |

## Performance Optimization

### Batch Operations

```python
# Bad: Multiple calls
for task_id in task_ids:
    await get_task(user_token, task_id)

# Good: Batch support
@register_tool("get_tasks_by_ids")
async def get_tasks_by_ids(user_token: str, task_ids: List[int]) -> Dict:
    """Fetch multiple tasks in one call."""
    tasks = task_service.get_tasks_by_ids(user_id, task_ids)
    return {"success": True, "tasks": tasks}
```

### Pagination

```python
@register_tool("get_tasks")
async def get_tasks(
    user_token: str,
    limit: int = 50,
    offset: int = 0
) -> Dict:
    """
    Get tasks with pagination.

    Args:
        limit: Maximum items to return (default: 50, max: 100)
        offset: Number of items to skip (for pagination)

    Returns:
        Tasks list with pagination metadata
    """
    limit = min(limit, 100)  # Enforce max limit
    tasks = task_service.get_tasks(user_id, limit=limit, offset=offset)

    return {
        "success": True,
        "tasks": tasks,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "has_more": len(tasks) == limit
        }
    }
```

## Testing Tools

### Unit Test Template

```python
import pytest
from app.ai.task_tools import create_task, get_tasks

def test_create_task_success(db_session, test_user):
    """Test successful task creation."""
    from app.auth import create_access_token

    token = create_access_token(test_user.id)
    result = await create_task(
        user_token=token,
        title="Test Task",
        priority="high"
    )

    assert result["success"] is True
    assert result["task"]["title"] == "Test Task"
    assert result["task"]["priority"] == "high"

def test_create_task_empty_title(db_session, test_user):
    """Test validation rejects empty title."""
    token = create_access_token(test_user.id)
    result = await create_task(user_token=token, title="")

    assert result["success"] is False
    assert "empty" in result["error"].lower()
```

## Security Checklist

- [ ] All tools verify JWT tokens
- [ ] User cannot access another user's data
- [ ] Input validation on all parameters
- [ ] SQL queries use parameterized statements
- [ ] No hardcoded secrets
- [ ] Rate limiting on expensive operations
- [ ] Sensitive data filtered from responses
- [ ] Error messages don't leak information
