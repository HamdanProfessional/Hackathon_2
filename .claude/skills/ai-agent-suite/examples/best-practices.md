# AI Agent Best Practices

## Core Principles

### 1. Stateless Architecture

**Always Required**: Load conversation context from database on every request.

```python
# CORRECT: Stateless - DB fetch every request
async def process_message(conversation_id: str, message: str, db: Session):
    history = load_conversation_context(conversation_id, db)
    # ... process with AI
```

```python
# WRONG: Stateful - Stores in memory
class Agent:
    def __init__(self):
        self.conversations = {}  # VIOLATION
```

### 2. Tenant Isolation

Always enforce user_id boundaries to prevent data leakage.

```python
# CORRECT: User-scoped queries
messages = db.exec(
    select(Message)
    .join(Conversation)
    .where(Conversation.user_id == current_user.id)
).all()

# WRONG: No user filtering
messages = db.exec(select(Message)).all()  # SECURITY ISSUE
```

### 3. Tool Execution Safety

Validate and handle all tool execution errors.

```python
async def execute_tool(tool_name: str, args: dict) -> dict:
    try:
        result = await TOOL_REGISTRY[tool_name](**args)
        return {"success": True, "data": result}
    except ValidationError as e:
        return {"success": False, "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"Tool {tool_name} failed: {e}")
        return {"success": False, "error": "Tool execution failed"}
```

## Performance Optimization

### Connection Pooling

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_ai_client():
    """Shared AI client for all requests."""
    return AsyncOpenAI(api_key=settings.AI_API_KEY)
```

### Database Query Optimization

```python
# Use indexes for conversation queries
class Message(SQLModel, table=True):
    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )

# Limit history size
history = db.exec(
    select(Message)
    .where(Message.conversation_id == conv_id)
    .order_by(Message.created_at.desc())
    .limit(50)
).all()
```

### Caching Strategy

Cache non-user-specific data only:

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def get_system_prompt(template_name: str):
    """Cache system prompts - no user data."""
    return load_prompt_template(template_name)

# DON'T cache user data
@lru_cache(maxsize=None)  # VIOLATION
def get_user_tasks(user_id: str):  # NO
```

## Error Handling

### Graceful Degradation

```python
async def process_with_tools(message: str, tools: list):
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            tools=tools
        )
        return response
    except RateLimitError:
        # Fallback to no tools
        return await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}]
        )
    except Exception as e:
        logger.error(f"AI request failed: {e}")
        return {"error": "AI service temporarily unavailable"}
```

## Monitoring

### Track Agent Metrics

```python
from prometheus_client import Counter, Histogram

ai_requests = Counter('ai_requests_total', 'Total AI requests')
ai_latency = Histogram('ai_latency_seconds', 'AI request latency')
tool_executions = Counter('tool_executions_total', 'Tool executions', ['tool_name'])

@ai_latency.time()
async def call_ai(messages: list):
    ai_requests.inc()
    # ... AI call
```

## Security Checklist

- [ ] All MCP tools verify JWT tokens
- [ ] No user can access another user's conversations
- [ ] API keys stored in environment variables
- [ ] SQL queries use parameterized statements
- [ ] Tool inputs validated before execution
- [ ] Rate limiting on AI endpoints
- [ ] Sensitive data not logged
- [ ] Tool responses filtered for sensitive info
