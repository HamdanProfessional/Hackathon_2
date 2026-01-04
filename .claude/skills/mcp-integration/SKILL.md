---
name: mcp-integration
description: Expose FastAPI endpoints as MCP tools by defining tool schemas with name/description/parameters in backend/app/ai/tools.py, validate stateless architecture by checking conversation history loads from PostgreSQL via load_conversation_context() on every request (not stored in self.history), and convert slash commands like /create-task to MCP tool format. Use when AI agents need to invoke CRUD functions like create_task({title, priority}), get_tasks({status}), or ensuring tools are called with JWT user_id from Authorization headers.
---

# MCP Integration Skill

Expose backend APIs as MCP tools, validate stateless architecture, and convert commands to MCP servers.

## File Structure

```
backend/app/ai/
├── tools.py              # MCP tool registry and implementations
├── agent.py              # Agent service using tools
└── conversation_manager.py  # Stateless context loading

scripts/
└── validate_stateless.py  # Architecture validator
```

## Common Scenarios

### Scenario 1: Expose Task CRUD as MCP Tools
**User Request**: "Make the AI agent able to create and list tasks"

**Commands**:
```bash
# Create tools directory
mkdir -p backend/app/ai

# Create tools file
touch backend/app/ai/tools.py

# Test tool invocation
python backend/test_agent.py
```

**File: `backend/app/ai/tools.py`**
```python
"""
MCP Tool Registry for AI agent integration.
"""
from typing import Dict, Optional, Literal

TOOL_REGISTRY: Dict[str, any] = {}

def register_tool(name: str, description: str, parameters: dict):
    """Register a tool for AI agent use."""
    TOOL_REGISTRY[name] = {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters
        }
    }
    return lambda f: f  # decorator that returns function unchanged

# Register get_tasks tool
get_tasks_tool = {
    "type": "function",
    "function": {
        "name": "get_tasks",
        "description": "Retrieve tasks for the authenticated user from database. Use this when user asks: 'Show my tasks', 'What do I need to do?', 'List my todo items'. Supports optional filtering by status.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_token": {
                    "type": "string",
                    "description": "JWT authentication token"
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed", "in_progress"],
                    "description": "Optional filter by task status"
                }
            },
            "required": ["user_token"]
        }
    }
}

# Register create_task tool
create_task_tool = {
    "type": "function",
    "function": {
        "name": "create_task",
        "description": "Create a new task for the authenticated user. Use this when user says: 'Add a task', 'Create todo', 'New reminder'.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title (max 255 chars)"
                },
                "description": {
                    "type": "string",
                    "description": "Optional detailed description"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high"],
                    "description": "Task priority level"
                },
                "user_token": {
                    "type": "string",
                    "description": "JWT authentication token"
                }
            },
            "required": ["title", "user_token"]
        }
    }
}

TOOL_REGISTRY["get_tasks"] = get_tasks_tool
TOOL_REGISTRY["create_task"] = create_task_tool
```

### Scenario 2: Fix AI Not Calling Tools
**Error**: AI responds with text but `tool_calls` array is empty

**Root Causes & Fixes**:

| Issue | Fix |
|-------|-----|
| Tool description too vague | Add "Use this when user asks..." to description |
| Missing parameter types | Add `type: "string"` for all parameters |
| Wrong enum values | Verify enum matches backend expectations |
| Tool not in registry | Check `TOOL_REGISTRY[name] = tool` called |

**Fix Example**:
```python
# BEFORE - Too vague
{
    "name": "get_tasks",
    "description": "Get tasks"
}

# AFTER - Clear and actionable
{
    "name": "get_tasks",
    "description": "Retrieve tasks from database. Use this when user asks: 'Show my tasks', 'What do I need to do?', 'List todo items'. Supports filtering by status (pending/completed).",
    "parameters": {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["pending", "completed"]}
        },
        "required": ["user_token"]
    }
}
```

### Scenario 3: Validate Stateless Agent Architecture
**User Request**: "Check if agent is stateless"

**Actions**:
1. **Run validator** - `python scripts/validate_stateless.py backend/app/ai/`
2. **Check for violations**:
   - Instance variables storing conversation state (❌)
   - Global dictionaries caching messages (❌)
   - Direct database queries on every request (✅)
3. **Fix violations**:
```python
# ❌ WRONG - In-memory state
class Agent:
    def __init__(self):
        self.conversation_cache = {}  # Violation

# ✅ CORRECT - Stateless pattern
async def run_agent(conversation_id: str, db: Session):
    messages = db.exec(select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(50)
    ).all()
```

### Scenario 4: Add JWT Authentication to MCP Tools
**User Request**: "Secure tools with user authentication"

**Actions**:
1. **Create verify_token function** in `backend/app/auth/jwt.py`:
```python
def verify_token(token: str) -> UUID:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return UUID(payload["user_id"])
    except JWTError:
        raise HTTPException(401, "Invalid token")
```
2. **Add to all tools**:
```python
@register_tool("create_task")
async def create_task(title: str, user_token: str) -> Dict:
    user_id = verify_token(user_token)  # Validate first
    task = Task(user_id=user_id, title=title)
    # ... rest of implementation
```

---

## Quick Templates

### MCP Tool Registration Pattern
```python
from typing import Dict, Callable

TOOL_REGISTRY: Dict[str, Callable] = {}

def register_tool(name: str):
    def decorator(func: Callable) -> Callable:
        TOOL_REGISTRY[name] = func
        return func
    return decorator

@register_tool("get_tasks")
async def get_tasks(user_token: str, status: str = None) -> Dict:
    """
    Retrieve tasks for the authenticated user.

    Use this when user asks: "Show me my tasks", "What do I need to do?",
    "List my pending items"
    """
    user_id = verify_token(user_token)
    # ... database query ...
    return {"success": True, "data": tasks}
```

### Stateless Agent Pattern
```python
async def run_agent(conversation_id: str, user_message: str, db: Session):
    # ✅ Load from database every time (stateless)
    history = load_conversation_context(conversation_id, db)
    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": user_message})

    # Call AI with full context
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=messages,
        tools=list(TOOL_REGISTRY.values())
    )

    # Persist response to database
    save_message(conversation_id, "assistant", response.choices[0].message)

    return response
```

### Tool Schema Best Practices
```python
# ✅ GOOD - Descriptive, type-annotated
async def create_task(
    title: str,
    description: str | None = None,
    priority: Literal["low", "normal", "high"] = "normal",
    user_token: str
) -> Dict[str, any]:
    """
    Create a new task for the authenticated user.

    Use this when user says: "Add a task", "Create todo", "New reminder"

    Args:
        title: Task title (required, max 255 chars)
        description: Optional detailed description
        priority: Task priority level
        user_token: JWT authentication token

    Returns:
        Dict with created task data or error message
    """
```

---

### Quick Start

See `examples/basic-mcp-tool.md` for simple tool creation and `examples/advanced-mcp-tools.md` for comprehensive tool suite.

### Tool Registration Pattern

```python
from typing import Dict, Callable

TOOL_REGISTRY: Dict[str, Callable] = {}

def register_tool(name: str):
    """Decorator to register MCP tools."""
    def decorator(func: Callable) -> Callable:
        TOOL_REGISTRY[name] = func
        return func
    return decorator

@register_tool("get_tasks")
async def get_tasks(user_token: str, status: str = None) -> Dict:
    """Tool implementation."""
    pass
```

### Tool Schema Best Practices

1. **Descriptive Docstrings**:
```python
async def tool_name(arg: str) -> Dict:
    """
    First line: Brief description (AI reads this first)

    Detailed explanation of what the tool does, when to use it,
    and what results to expect.

    Args:
        arg: Detailed parameter description with examples

    Returns:
        Detailed return value description
    """
```

2. **Strong Type Hints**:
```python
from typing import Dict, List, Optional, Literal

async def typed_tool(
    required_str: str,
    optional_int: Optional[int] = None,
    priority: Literal["low", "normal", "high"] = "normal"
) -> Dict[str, any]:
    """Type hints enable automatic schema generation."""
```

3. **Error Handling**:
```python
async def safe_tool(arg: str) -> Dict:
    """Always return structured responses."""
    try:
        # Tool logic
        return {"success": True, "data": result}
    except ValueError as e:
        return {"success": False, "error": f"Invalid input: {str(e)}"}
```

4. **Authentication**:
```python
async def authenticated_tool(user_token: str, data: str) -> Dict:
    """All tools should verify JWT tokens."""
    try:
        user_id = verify_token(user_token)
        # Proceed with authorized operation
    except:
        return {"error": "Unauthorized", "success": False}
```

---

## Part 2: Stateless Agent Enforcer

### Constitutional Requirement

**From CLAUDE.md**:
> All conversation history must be fetched from database on every request. Agent runtime MUST NOT store conversation state in memory.

**Why this matters**:
- **Horizontal Scaling**: Multiple agent instances can serve the same user
- **Load Balancing**: Requests can route to any instance without sticky sessions
- **Crash Recovery**: No state lost when instance restarts
- **Compliance**: Constitutional guarantee for data persistence and auditability

### Validation Tool

Run the validator:
```bash
python .claude/skills/mcp-integration/scripts/validate_stateless.py backend/app
```

### Common Anti-Patterns

**Anti-Pattern 1: Instance Variables for Conversation State**
```python
class Agent:
    def __init__(self):
        self.message_cache = {}  # VIOLATION
```

**Solution**:
```python
async def run_agent(conversation_id: str, db: Session):
    messages = load_conversation_context(conversation_id, db)  # CORRECT
```

**Anti-Pattern 2: Global State Dictionaries**
```python
CONVERSATION_STATE = {}  # VIOLATION
```

**Solution**:
```python
# CORRECT: No global state, database query
async def run_agent(conversation_id: str, db: Session):
    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(50)
    ).all()
```

**Anti-Pattern 3: Unbounded LRU Cache**
```python
from functools import lru_cache

@lru_cache(maxsize=None)  # VIOLATION: Grows indefinitely
def get_conversation_title(conversation_id: str):
    ...
```

**Solution**:
```python
# CORRECT: Direct database query with proper indexes
def get_conversation_title(conversation_id: str, db: Session):
    conversation = db.get(Conversation, conversation_id)
    return conversation.title if conversation else None
```

---

## Part 3: MCP Builder (Commands to Server)

### Quick Start

Convert slash commands to MCP server:

```bash
/skill mcp-builder
```

### Generated Structure

```
mcp-server/
├── server.py          # MCP server implementation
├── pyproject.toml      # Package configuration
└── README.md          # Usage documentation
.mcp.json              # MCP client configuration
```

---

## Quality Checklist

Before finalizing:
- [ ] MCP tools have descriptive docstrings
- [ ] Strong type hints for all parameters
- [ ] Error handling with user-friendly messages
- [ ] JWT authentication integrated
- [ ] Agent uses stateless pattern (DB fetch on every request)
- [ ] No instance variables storing conversation state
- [ ] No global dictionaries caching messages
- [ ] Database session parameter in all agent functions
- [ ] Conversation history loaded from DB on every request
- [ ] Caches (if any) have TTL and invalidation
- [ ] Run `scripts/validate_stateless.py` - all checks pass
- [ ] Compliance tests pass
