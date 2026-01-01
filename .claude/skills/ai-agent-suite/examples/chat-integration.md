# Chat Integration Example

Complete AI agent integration with MCP tools and database-backed conversation history.

## Agent Service with Tools

```python
# backend/app/ai/agent_service.py
from openai import AsyncOpenAI
from typing import Optional
from sqlmodel import Session, select
from app.models import Conversation, Message
from app.ai.tools import get_tools

class AgentService:
    """Stateless AI agent with MCP tools and conversation persistence."""

    def __init__(self, user_id: str, db: Session):
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        self.model = settings.AI_MODEL
        self.user_id = user_id
        self.db = db
        self.tools = get_tools()

    async def process_message(
        self,
        message: str,
        conversation_id: Optional[int] = None
    ) -> dict:
        """Process user message with AI and tools."""
        # 1. Load conversation history from database
        history = self._load_history(conversation_id)

        # 2. Create conversation if needed
        if not conversation_id:
            conversation = Conversation(user_id=self.user_id, title="New Chat")
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            conversation_id = conversation.id

        # 3. Save user message
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=message
        )
        self.db.add(user_msg)
        self.db.commit()

        # 4. Call AI with tools
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({"role": "user", "content": message})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools
        )

        # 5. Handle tool calls if present
        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            results = await self._execute_tools(assistant_message.tool_calls)

            # Send results back to AI
            messages.append({
                "role": "assistant",
                "content": "",
                "tool_calls": assistant_message.tool_calls
            })
            messages.append({
                "role": "tool",
                "content": str(results)
            })

            final_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            assistant_message = final_response.choices[0].message

        # 6. Save assistant response
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_message.content
        )
        self.db.add(assistant_msg)
        self.db.commit()

        return {
            "response": assistant_message.content,
            "conversation_id": conversation_id,
            "message_id": assistant_msg.id
        }

    def _load_history(self, conversation_id: Optional[int]) -> list[Message]:
        """Load conversation history from database."""
        if not conversation_id:
            return []

        messages = self.db.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(50)
        ).all()

        return messages

    async def _execute_tools(self, tool_calls) -> dict:
        """Execute MCP tools called by AI."""
        results = {}

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Import and execute the tool function
            from app.ai.tools import TOOL_REGISTRY
            if tool_name in TOOL_REGISTRY:
                result = await TOOL_REGISTRY[tool_name](**tool_args)
                results[tool_call.id] = result

        return results
```

## MCP Tools Registry

```python
# backend/app/ai/tools.py
from typing import Dict, Any
from app.auth import verify_token
from app.services import task_service

TOOL_REGISTRY = {}

def register_tool(name: str):
    """Decorator to register MCP tools."""
    def decorator(func):
        TOOL_REGISTRY[name] = func
        return func
    return decorator

def get_tools() -> list[dict]:
    """Get tools schema for OpenAI."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_tasks",
                "description": "Get all tasks for the current user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed"],
                            "description": "Filter by task status"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a new task",
                "parameters": {
                    "type": "object",
                    "required": ["title"],
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "priority": {
                            "type": "string",
                            "enum": ["low", "normal", "high"]
                        }
                    }
                }
            }
        }
    ]

@register_tool("get_tasks")
async def get_tasks(user_token: str, status: str = None) -> Dict[str, Any]:
    """Get tasks for authenticated user."""
    user_id = verify_token(user_token)
    tasks = task_service.get_user_tasks(user_id, status=status)
    return {"tasks": [t.dict() for t in tasks]}

@register_tool("create_task")
async def create_task(user_token: str, title: str, description: str = None, priority: str = "normal") -> Dict[str, Any]:
    """Create a task for authenticated user."""
    user_id = verify_token(user_token)
    task = task_service.create_task(user_id, title, description, priority)
    return task.dict()
```
