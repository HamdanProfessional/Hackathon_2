---
name: mcp-integration
description: MCP (Model Context Protocol) integration including tool maker (expose backend functionality to AI agents), stateless agent enforcement (validate NO in-memory state architecture), and slash command to MCP server conversion. Essential for AI agent integration and constitutional compliance.
version: 2.0.0
category: ai-integration
tags: [mcp, agents, tools, stateless, architecture, validation]
dependencies: [mcp-sdk, fastapi, sqlmodel]
---

# MCP Integration Skill

Comprehensive MCP (Model Context Protocol) integration for AI agents.

## Quick Reference

| Feature | Location | Description |
|---------|----------|-------------|
| Examples | `examples/` | Basic MCP tool, advanced tools, best practices |
| Scripts | `scripts/` | `validate_stateless.py` - stateless architecture validator |
| Templates | `references/templates.md` | Reusable code templates |
| Links | `references/links.md` | External documentation |

## When to Use This Skill

Use this skill when:
- User asks to "expose this function to AI" or "make this AI-accessible"
- Creating MCP tools to expose backend functionality to AI agents
- Validating stateless agent architecture compliance
- Converting slash commands to MCP server format
- Ensuring constitutional compliance with "NO in-memory conversation state"

## Common Issues & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| AI not calling tools | Poor tool descriptions | Improve docstrings, add usage examples |
| Stateful violations detected | In-memory conversation state | Run `validate_stateless.py`, refactor to DB queries |
| Tool execution fails | Missing JWT validation | Add `verify_token()` to all tools |
| Schema generation errors | Missing type hints | Add proper type hints to all parameters |

---

## Part 1: MCP Tool Maker

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
