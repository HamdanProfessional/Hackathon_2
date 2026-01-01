# Basic MCP Tool Example

A minimal MCP tool that exposes backend functionality to AI agents.

## Implementation

```python
# backend/app/ai/tools.py
from typing import Dict, Any
from app.auth import verify_token
from app.services import task_service

def get_task_tool_schema() -> Dict:
    """Get tool schema for AI."""
    return {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "Retrieve all tasks for the authenticated user. Supports optional filtering by status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Filter tasks by status (optional)"
                    }
                }
            }
        }
    }

async def get_tasks(user_token: str, status: str = None) -> Dict[str, Any]:
    """
    Retrieve all tasks for the authenticated user.

    Args:
        user_token: JWT authentication token
        status: Optional status filter (pending, in_progress, completed)

    Returns:
        Dictionary with success status and list of tasks or error message
    """
    try:
        user_id = verify_token(user_token)
        tasks = task_service.get_user_tasks(user_id, status=status)
        return {
            "success": True,
            "tasks": [t.dict() for t in tasks]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

## Usage in AI Agent

```python
# backend/app/ai/agent.py
from openai import AsyncOpenAI
from app.ai.tools import get_task_tool_schema, get_tasks

class AgentService:
    def __init__(self, user_id: str, db: Session):
        self.client = AsyncOpenAI(api_key=settings.AI_API_KEY)
        self.tools = [get_task_tool_schema()]
        self.tool_registry = {"get_tasks": get_tasks}

    async def process_message(self, message: str):
        response = await self.client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[{"role": "user", "content": message}],
            tools=self.tools
        )

        # Handle tool calls
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                func = self.tool_registry[tool_call.function.name]
                result = await func(**json.loads(tool_call.function.arguments))

        return result
```

## Key Points

- **Descriptive docstrings**: AI reads these to understand when to use the tool
- **Strong type hints**: Enable automatic schema generation
- **Error handling**: Always return structured responses with success/error
- **JWT authentication**: All tools verify user tokens
