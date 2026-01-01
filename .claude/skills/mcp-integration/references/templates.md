# MCP Integration - Reusable Templates

## Tool Registration Template

```python
# backend/app/ai/tools.py
from typing import Dict, Callable, Any
import json

TOOL_REGISTRY: Dict[str, Callable] = {}

def register_tool(name: str):
    """Decorator to register MCP tools."""
    def decorator(func: Callable) -> Callable:
        TOOL_REGISTRY[name] = func
        func.__tool_name__ = name
        return func
    return decorator

def get_all_tool_schemas() -> list[dict]:
    """Get schemas for all registered tools."""
    schemas = []
    for func in TOOL_REGISTRY.values():
        schema = {
            "type": "function",
            "function": {
                "name": func.__tool_name__,
                "description": func.__doc__ or "",
                "parameters": extract_parameters(func)
            }
        }
        schemas.append(schema)
    return schemas

def extract_parameters(func: Callable) -> dict:
    """Extract parameters from function signature."""
    import inspect
    sig = inspect.signature(func)

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        # Skip user_token (added automatically)
        if name == "user_token":
            continue

        param_type = param.annotation
        if param_type == inspect.Parameter.empty:
            param_type = "string"

        # Handle Optional types
        if hasattr(param_type, "__origin__") and param_type.__origin__ is Union:
            types = [t.__name__ if hasattr(t, "__name__") else str(t)
                    for t in param_type.__args__ if t is not type(None)]
            param_type = types[0] if types else "string"
        elif hasattr(param_type, "__name__"):
            param_type = param_type.__name__
        else:
            param_type = str(param_type)

        properties[name] = {
            "type": param_type.lower(),
            "description": f"Parameter {name}"
        }

        # Handle default values
        if param.default == inspect.Parameter.empty:
            required.append(name)
        elif hasattr(param.default, "__name__") and param.default.__name__ == "Literal":
            # Handle Literal types for enums
            values = list(param.default.__args__)
            properties[name]["enum"] = values

    return {
        "type": "object",
        "properties": properties,
        "required": required
    }
```

## Tool Template

```python
# backend/app/ai/task_tools.py
from typing import Dict, Any, Optional, Literal
from app.auth import verify_token
from app.services import task_service

@register_tool("tool_name")
async def tool_name(
    user_token: str,
    required_param: str,
    optional_param: str = None,
    enum_param: Literal["option1", "option2", "option3"] = "option1"
) -> Dict[str, Any]:
    """
    Brief description of what this tool does.

    More detailed explanation of when to use this tool and what it does.
    Include examples of when the AI should invoke this function.

    Args:
        user_token: JWT authentication token
        required_param: Description of required parameter
        optional_param: Description of optional parameter
        enum_param: One of option1, option2, or option3

    Returns:
        Description of what is returned

    Raises:
        Description of errors (mapped to error responses)
    """
    try:
        # Validate authentication
        user_id = verify_token(user_token)

        # Validate input
        if not required_param:
            return {
                "success": False,
                "error": "required_param cannot be empty"
            }

        # Execute business logic
        result = await perform_operation(
            user_id=user_id,
            required_param=required_param,
            optional_param=optional_param,
            enum_param=enum_param
        )

        return {
            "success": True,
            "data": result
        }

    except ValueError as e:
        return {
            "success": False,
            "error": f"Validation error: {str(e)}",
            "error_code": "VALIDATION_ERROR"
        }
    except PermissionError:
        return {
            "success": False,
            "error": "Permission denied",
            "error_code": "PERMISSION_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Operation failed: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }
```

## Tool Executor Template

```python
# backend/app/ai/tool_executor.py
import json
import logging
from typing import Dict, Any, List
from app.ai.tools import TOOL_REGISTRY

logger = logging.getLogger(__name__)

async def execute_tools(
    tool_calls: List[Dict],
    user_token: str,
    user_id: str
) -> Dict[str, Any]:
    """
    Execute multiple tool calls and return results.

    Args:
        tool_calls: Tool call objects from AI response
        user_token: JWT authentication token
        user_id: Current user ID

    Returns:
        Dictionary mapping tool_call IDs to results
    """
    results = {}

    for tool_call in tool_calls:
        tool_id = tool_call.id
        tool_name = tool_call.function.name

        try:
            # Parse arguments
            arguments = json.loads(tool_call.function.arguments)

            # Add authentication
            arguments["user_token"] = user_token

            # Execute tool
            if tool_name not in TOOL_REGISTRY:
                results[tool_id] = {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
                logger.warning(f"Unknown tool: {tool_name}")
                continue

            result = await TOOL_REGISTRY[tool_name](**arguments)
            results[tool_id] = result

            # Log execution
            if result.get("success"):
                logger.info(f"Tool {tool_name} executed successfully")
            else:
                logger.warning(f"Tool {tool_name} failed: {result.get('error')}")

        except json.JSONDecodeError as e:
            results[tool_id] = {
                "success": False,
                "error": f"Invalid arguments: {e}"
            }
            logger.error(f"JSON error in {tool_name}: {e}")

        except Exception as e:
            results[tool_id] = {
                "success": False,
                "error": f"Execution failed: {e}"
            }
            logger.error(f"Tool {tool_name} error: {e}", exc_info=True)

    return results
```

## Agent Integration Template

```python
# backend/app/ai/agent.py
from openai import AsyncOpenAI
from sqlmodel import Session
from app.ai.tools import get_all_tool_schemas
from app.ai.tool_executor import execute_tools
from app.config import settings

class AgentService:
    """Stateless AI agent with MCP tools."""

    def __init__(self, user_id: str, db: Session):
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        self.model = settings.AI_MODEL
        self.user_id = user_id
        self.db = db
        self.tools = get_all_tool_schemas()

    async def process_message(
        self,
        message: str,
        conversation_id: int = None
    ) -> Dict[str, Any]:
        """Process message with AI and tools."""
        # Load conversation history
        history = self._load_history(conversation_id)

        # Build messages
        messages = [
            {"role": m.role, "content": m.content}
            for m in history
        ]
        messages.append({"role": "user", "content": message})

        # Call AI with tools
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools
        )

        assistant_msg = response.choices[0].message

        # Execute tools if called
        if assistant_msg.tool_calls:
            user_token = self._get_user_token()

            tool_results = await execute_tools(
                tool_calls=assistant_msg.tool_calls,
                user_token=user_token,
                user_id=self.user_id
            )

            # Send results back to AI
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": assistant_msg.tool_calls
            })

            for tool_id, result in tool_results.items():
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": json.dumps(result)
                })

            # Get final response
            final_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            assistant_msg = final_response.choices[0].message

        # Save to database
        # ... save messages

        return {
            "response": assistant_msg.content,
            "conversation_id": conversation_id
        }

    def _load_history(self, conversation_id: int):
        """Load conversation history from database."""
        if not conversation_id:
            return []

        return self.db.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(50)
        ).all()
```

## Test Template

```python
# tests/test_mcp_tools.py
import pytest
from app.ai.task_tools import create_task, get_tasks
from app.auth import create_access_token

class TestMCPTools:
    """Test MCP tool implementations."""

    @pytest.fixture
    def user_token(self, test_user):
        """Get valid JWT token for test user."""
        return create_access_token(test_user.id)

    def test_create_task_success(self, db_session, user_token):
        """Test successful task creation."""
        result = await create_task(
            user_token=user_token,
            title="Test Task",
            priority="high"
        )

        assert result["success"] is True
        assert result["task"]["title"] == "Test Task"
        assert result["task"]["priority"] == "high"

    def test_create_task_empty_title(self, db_session, user_token):
        """Test validation rejects empty title."""
        result = await create_task(
            user_token=user_token,
            title=""
        )

        assert result["success"] is False
        assert "empty" in result["error"].lower()

    def test_get_tasks_user_isolation(self, db_session, user_token, test_user):
        """Test user cannot access other users' tasks."""
        # Create task for different user
        other_user = create_test_user()
        other_task = task_service.create_task(
            user_id=other_user.id,
            title="Other User Task"
        )

        # Try to access with original user token
        result = await get_tasks(user_token=user_token)

        assert result["success"] is True
        assert other_task.id not in [t["id"] for t in result["tasks"]]
```
