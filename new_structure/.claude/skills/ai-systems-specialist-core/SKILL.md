---
name: ai-systems-specialist-core
description: Comprehensive AI systems integration for OpenAI Agents SDK and MCP server implementation. Manages stateless agent architecture, MCP tool creation, conversation management, and chatbot integration. Handles the complete AI evolution from basic task automation to intelligent conversational interfaces across all phases.
---

# AI Systems Specialist Core

## Quick Start

```python
# Initialize AI system with mandatory Gemini 2.5 Flash
from ai_systems_specialist_core import AISystem
import os
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_default_openai_client

# ⚠️ MANDATORY: Always use Google Gemini 2.5 Flash via OpenAI compatibility layer
ai_system = AISystem(
    # Google Gemini 2.5 Flash configuration (MANDATORY)
    openai_api_key=os.getenv("GOOGLE_API_KEY"),  # NOT OpenAI key
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model="gemini-2.0-flash-exp",
    mcp_tools=["tasks", "conversations", "reminders"],
    architecture="stateless"  # ⚠️ MANDATORY: Always stateless
)

# Configure stateless agent
agent = ai_system.create_agent(
    instructions="You are a helpful task assistant...",
    tools=mcp_tools
)
```

## Core Capabilities

### 1. Google Gemini 2.5 Flash Integration (MANDATORY)
```python
# ⚠️ EXACT TEMPLATE: Always use this pattern for Gemini 2.5 Flash integration
import os
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_default_openai_client

class GeminiConfig:
    """Mandatory configuration for Google Gemini 2.5 Flash integration."""

    def __init__(self):
        # ⚠️ MANDATORY: Google API Key, NOT OpenAI key
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        # ⚠️ MANDATORY: Google Gemini OpenAI compatibility layer URL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

        # ⚠️ MANDATORY: Use Gemini 2.0 Flash model
        self.model = "gemini-2.0-flash-exp"

    def get_openai_client(self) -> AsyncOpenAI:
        """Get configured AsyncOpenAI client for Gemini."""
        return AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def get_model(self) -> OpenAIChatCompletionsModel:
        """Get configured model for Agents SDK."""
        client = self.get_openai_client()
        set_default_openai_client(client)  # ⚠️ MANDATORY: Set as global default

        return OpenAIChatCompletionsModel(
            model=self.model,
            openai_client=client
        )

# Usage Example (MANDATORY PATTERN)
def create_task_agent():
    """Create task management agent with mandatory Gemini configuration."""

    # ⚠️ MANDATORY: Initialize Gemini configuration
    gemini_config = GeminiConfig()

    # ⚠️ MANDATORY: Set global OpenAI client for Agents SDK
    client = gemini_config.get_openai_client()
    set_default_openai_client(client)

    # ⚠️ MANDATORY: Create stateless agent with no memory argument
    from agents import Agent

    task_agent = Agent(
        name="task-assistant",
        instructions=(
            "You are a helpful todo assistant for the Todo Evolution application. "
            "You can help users manage their tasks using natural language. "
            "Always use the provided tools to interact with tasks. "
            "Never store conversation state in memory."
        ),
        tools=[add_task_tool, list_tasks_tool, complete_task_tool, delete_task_tool]
        # ⚠️ IMPORTANT: NO memory parameter - agents must be stateless
    )

    return task_agent
```

### 2. Stateless Architecture Enforcement
```python
import ast
import os
from typing import List, Dict, Any

class StatelessArchitectureValidator:
    """Validates that AI agents follow stateless architecture patterns."""

    def __init__(self):
        self.violations = []
        self.warnings = []

    def validate_agent_file(self, file_path: str) -> Dict[str, Any]:
        """Validate that an agent file follows stateless architecture."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            tree = ast.parse(content)

            # Check for stateless violations
            self._check_memory_parameter(tree, file_path)
            self._check_conversation_storage(tree, file_path)
            self._check_state_dependencies(tree, file_path)
            self._check_gemini_configuration(tree, file_path)

            return {
                "file": file_path,
                "violations": self.violations,
                "warnings": self.warnings,
                "compliant": len(self.violations) == 0
            }

        except Exception as e:
            return {
                "file": file_path,
                "error": str(e),
                "compliant": False
            }

    def _check_memory_parameter(self, tree: ast.AST, file_path: str):
        """Check for forbidden memory parameter in Agent constructor."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Name) and node.func.id == "Agent") or \
                   (isinstance(node.func, ast.Attribute) and node.func.attr == "Agent"):

                    # Check for memory parameter
                    for keyword in node.keywords:
                        if keyword.arg == "memory":
                            self.violations.append(
                                f"{file_path}:line {node.lineno} - "
                                f"Agent has 'memory' parameter (violates stateless architecture)"
                            )

    def _check_conversation_storage(self, tree: ast.AST, file_path: str):
        """Check for in-memory conversation storage."""
        dangerous_patterns = [
            "self.conversation", "self.messages", "self.context",
            "conversation_history", "chat_history", "session_memory"
        ]

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        attr_name = target.attr.lower()
                        if any(pattern in attr_name for pattern in dangerous_patterns):
                            self.violations.append(
                                f"{file_path}:line {node.lineno} - "
                                f"Potential state storage: {target.attr}"
                            )

    def _check_state_dependencies(self, tree: ast.AST, file_path: str):
        """Check for dependencies on stateful patterns."""
        # Check for Redis, memory cache, or other stateful storage
        stateful_imports = ["redis", "memcache", "memory_cache"]

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(stateful in alias.name.lower() for stateful in stateful_imports):
                        self.warnings.append(
                            f"{file_path}:line {node.lineno} - "
                            f"Potentially stateful import: {alias.name}"
                        )

    def _check_gemini_configuration(self, tree: ast.AST, file_path: str):
        """Check for proper Gemini 2.5 Flash configuration."""
        has_gemini_config = False
        uses_openai_directly = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Str):
                if "generativelanguage.googleapis.com" in node.s:
                    has_gemini_config = True
                elif "api.openai.com" in node.s:
                    uses_openai_directly = True

        if not has_gemini_config:
            self.violations.append(
                f"{file_path} - Missing Google Gemini 2.5 Flash configuration"
            )

        if uses_openai_directly:
            self.violations.append(
                f"{file_path} - Using OpenAI API directly instead of Gemini"
            )

# Usage
validator = StatelessArchitectureValidator()
result = validator.validate_agent_file("backend/app/ai/agent.py")
if not result["compliant"]:
    print("❌ Stateless architecture violations found:")
    for violation in result["violations"]:
        print(f"  - {violation}")
```

### 3. MCP Tool Integration Pattern
```python
# ⚠️ MANDATORY MCP Tool Pattern for Gemini 2.5 Flash
from agents.mcp import MCPServerSse
import json

class TodoMCPServer:
    """MCP Server for Todo operations with Gemini integration."""

    def __init__(self):
        # ⚠️ MANDATORY: Initialize with Gemini configuration
        self.gemini_config = GeminiConfig()
        self.server = MCPServerSse(
            name="todo-mcp-server",
            description="MCP server for task management operations",
        )

        # Register all MCP tools
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools for task operations."""

        @self.server.call_tool()
        async def create_task(arguments: dict):
            """Create a new task (MCP Tool)."""
            # Implementation must be stateless - load from database
            return await self._execute_create_task(arguments)

        @self.server.call_tool()
        async def list_tasks(arguments: dict):
            """List user tasks (MCP Tool)."""
            return await self._execute_list_tasks(arguments)

        # Add more tools as needed
        # - update_task
        # - delete_task
        # - complete_task

    async def _execute_create_task(self, arguments: dict):
        """Execute task creation with database persistence."""
        # ⚠️ MANDATORY: Always load from database, never use in-memory state
        user_id = arguments.get("user_id")
        title = arguments.get("title")

        # Database operation here (implementation depends on your ORM)
        # This is just a template
        task = {
            "id": "generated-id",
            "title": title,
            "user_id": user_id,
            "created_at": "2024-01-01T00:00:00Z"
        }

        return {
            "success": True,
            "task": task,
            "message": f"Task '{title}' created successfully"
        }

# Integration with Agents SDK
def create_stateless_agent_with_mcp():
    """Create a stateless agent with MCP tools."""

    # ⚠️ MANDATORY: Initialize Gemini
    gemini_config = GeminiConfig()
    client = gemini_config.get_openai_client()
    set_default_openai_client(client)

    # ⚠️ MANDATORY: Initialize MCP server
    mcp_server = TodoMCPServer()

    # ⚠️ MANDATORY: Create agent with MCP tools
    from agents import Agent

    agent = Agent(
        name="todo-assistant",
        instructions=(
            "You are a helpful todo assistant. Use the available tools to "
            "manage tasks. Always load task data from the database for each request."
        ),
        tools=mcp_server.tools
        # ⚠️ IMPORTANT: No memory parameter
    )

    return agent, mcp_server
```
```

### 2. MCP Server Implementation
```python
from mcp.server import Server

app = Server("todo-mcp-server")

@app.list_tools()
async def list_tools():
    """List all available MCP tools."""
    return [
        {
            "name": "add_task",
            "description": "Create a new task",
            "inputSchema": ADD_TASK_SCHEMA
        },
        {
            "name": "list_tasks",
            "description": "Retrieve user's tasks",
            "inputSchema": LIST_TASKS_SCHEMA
        }
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Route tool calls to handlers."""
    if name == "add_task":
        return await add_task_handler(**arguments)
    elif name == "list_tasks":
        return await list_tasks_handler(**arguments)
```

### 3. Stateless Architecture Enforcement
```python
class StatelessConversationManager:
    """Ensures server holds no conversation state."""

    async def handle_message(self, user_id: str, message: str, conv_id: int = None):
        # 1. Load conversation from database
        messages = await self.load_conversation(conv_id)

        # 2. Add current message
        messages.append({"role": "user", "content": message})

        # 3. Store user message immediately
        user_msg = await self.store_message(user_id, conv_id, "user", message)

        # 4. Run agent (no in-memory state)
        response = await runner.run(messages)

        # 5. Store assistant response
        await self.store_message(
            user_msg.conversation_id,
            "assistant",
            response.messages[-1].content,
            response.tool_calls
        )

        return {
            "conversation_id": user_msg.conversation_id,
            "response": response.messages[-1].content,
            "tool_calls": response.tool_calls
        }
```

## MCP Tool Development

### Task Management Tools
```python
# Add task MCP tool
ADD_TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "user_id": {"type": "string"},
        "title": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "description": {
            "type": "string",
            "maxLength": 1000
        },
        "priority": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "default": "medium"
        }
    },
    "required": ["user_id", "title"]
}

async def add_task_handler(user_id: str, title: str, description: str = None, priority: str = "medium"):
    """Handle add_task tool call."""
    try:
        task = await TaskService.create_task(
            user_id=user_id,
            title=title,
            description=description or "",
            priority=priority
        )

        return {
            "success": True,
            "task_id": task.id,
            "title": task.title,
            "status": "created"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### List Tasks Tool
```python
LIST_TASKS_SCHEMA = {
    "type": "object",
    "properties": {
        "user_id": {"type": "string"},
        "status": {
            "type": "string",
            "enum": ["all", "pending", "completed", "overdue"],
            "default": "all"
        },
        "limit": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "default": 50
        }
    },
    "required": ["user_id"]
}

async def list_tasks_handler(user_id: str, status: str = "all", limit: int = 50):
    """Handle list_tasks tool call."""
    tasks = await TaskService.get_user_tasks(
        user_id=user_id,
        filter_status=status,
        limit=limit
    )

    return {
        "success": True,
        "tasks": [task.to_dict() for task in tasks],
        "count": len(tasks)
    }
```

## Conversation Management

### Database Models
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from datetime import datetime

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id")
    role: str = Field()  # 'user' or 'assistant'
    content: str
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")
```

### Context Loading
```python
class ConversationContextLoader:
    """Loads conversation context from database."""

    async def load_context(self, conversation_id: int, limit: int = 50) -> List[dict]:
        """Load conversation history with pagination."""
        messages = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
        ).scalars().all()

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "tool_calls": msg.tool_calls
            }
            for msg in messages
        ]

    async def store_message(
        self,
        user_id: str,
        conversation_id: Optional[int],
        role: str,
        content: str,
        tool_calls: Optional[dict] = None
    ) -> Message:
        """Store message and return with conversation ID."""
        if conversation_id is None:
            # Create new conversation
            conv = Conversation(user_id=user_id)
            session.add(conv)
            session.commit()
            session.refresh(conv)
            conversation_id = conv.id

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        session.add(message)
        session.commit()
        session.refresh(message)

        return message
```

## Agent Orchestration

### Multi-Agent Coordination
```python
class AgentOrchestrator:
    """Coordinates multiple specialized agents."""

    def __init__(self):
        self.task_agent = TaskAgent()
        self.reminder_agent = ReminderAgent()
        self.search_agent = SearchAgent()

    async def route_request(self, user_id: str, message: str):
        """Route request to appropriate agent."""
        # Intent classification
        intent = await self.classify_intent(message)

        if intent == "task_management":
            return await self.task_agent.handle(user_id, message)
        elif intent == "reminder":
            return await self.reminder_agent.handle(user_id, message)
        elif intent == "search":
            return await self.search_agent.handle(user_id, message)
        else:
            return await self.task_agent.handle(user_id, message)  # Default
```

### Tool Composition
```python
class ComposableAgent:
    """Agent that can chain multiple tools."""

    async def handle_complex_request(self, user_id: str, message: str):
        """Handle requests requiring multiple tool calls."""
        # Example: "Complete the shopping task and create a new task for next week"

        # Parse request
        actions = await self.parse_actions(message)

        results = []
        for action in actions:
            if action["type"] == "complete_task":
                result = await complete_task_handler(
                    user_id=user_id,
                    task_id=action["task_id"]
                )
            elif action["type"] == "add_task":
                result = await add_task_handler(
                    user_id=user_id,
                    title=action["title"],
                    description=action.get("description")
                )

            results.append(result)

        return results
```

## ChatKit Integration

### Frontend Chat Interface
```typescript
// ChatKit provider setup
import { ChatKitProvider, ChatView } from '@openai/chatkit-react';

export function TodoChat({ userToken }: { userToken: string }) {
  return (
    <ChatKitProvider
      apiUrl="/api/chat"
      authToken={userToken}
      theme="todo-theme"
    >
      <ChatView
        welcomeMessage="Hi! I can help you manage your tasks. What would you like to do?"
        placeholder="Ask me to add, complete, or list your tasks..."
        customComponents={{
          ToolCall: ToolCallDisplay,
          SystemMessage: SystemMessageDisplay
        }}
      />
    </ChatKitProvider>
  );
}
```

### Tool Call Visualization
```typescript
// Display MCP tool calls
const ToolCallDisplay = ({ toolCall }: { toolCall: ToolCall }) => {
  const getIcon = (toolName: string) => {
    switch (toolName) {
      case 'add_task': return '➕';
      case 'complete_task': return '✅';
      case 'delete_task': return '🗑️';
      default: return '🔧';
    }
  };

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 my-2">
      <div className="flex items-center gap-2">
        <span className="text-lg">{getIcon(toolCall.name)}</span>
        <span className="font-medium capitalize">{toolCall.name.replace('_', ' ')}</span>
      </div>
      <div className="text-sm text-gray-600 mt-1">
        {toolCall.result?.message || 'Processing...'}
      </div>
    </div>
  );
};
```

## Natural Language Processing

### Intent Recognition
```python
class IntentClassifier:
    """Classifies user intents for tool selection."""

    INTENT_PATTERNS = {
        "add_task": ["add", "create", "new", "remember", "need to"],
        "list_tasks": ["show", "list", "what", "see all", "display"],
        "complete_task": ["done", "complete", "finished", "check", "mark"],
        "delete_task": ["delete", "remove", "cancel", "get rid of"],
        "update_task": ["change", "update", "modify", "rename", "edit"]
    }

    def classify(self, message: str) -> str:
        """Classify intent from message."""
        message_lower = message.lower()

        for intent, keywords in self.INTENT_PATTERNS.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return "unknown"
```

### Entity Extraction
```python
class EntityExtractor:
    """Extracts entities from natural language."""

    def extract_task_id(self, message: str) -> Optional[int]:
        """Extract task ID from message."""
        # Look for "task 3", "item #3", "3rd task", etc.
        patterns = [
            r'task\s+(\d+)',
            r'item\s*#?(\d+)',
            r'(\d+)(?:st|nd|rd|th)\s+task',
            r'#(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return int(match.group(1))

        return None

    def extract_title(self, message: str) -> str:
        """Extract task title from message."""
        # Remove intent words and extract remaining as title
        intent_words = ["add", "create", "new", "task", "item"]
        cleaned = message.lower()

        for word in intent_words:
            cleaned = cleaned.replace(word, "")

        return cleaned.strip().capitalize()
```

## Error Handling

### Agent Error Recovery
```python
class AgentErrorHandler:
    """Handles errors in agent execution."""

    async def handle_tool_error(self, tool_name: str, error: Exception):
        """Handle MCP tool execution errors."""
        error_messages = {
            "ValidationError": "I need more information to do that. Could you please provide specific details?",
            "TaskNotFound": "I couldn't find that task. Would you like me to list your tasks?",
            "PermissionError": "I don't have permission to do that.",
            "RateLimitError": "I'm receiving too many requests. Please try again in a moment."
        }

        error_type = type(error).__name__
        friendly_message = error_messages.get(error_type, "Something went wrong. Please try again.")

        return {
            "success": False,
            "error": friendly_message,
            "retry_suggested": error_type in ["ValidationError", "RateLimitError"]
        }
```

### Fallback Responses
```python
class FallbackHandler:
    """Provides fallback responses when tools fail."""

    async def handle_unknown_intent(self, message: str):
        """Handle messages with unclear intent."""
        return {
            "response": "I'm not sure I understand. I can help you to:\n"
                     "• Add tasks (e.g., 'Add a task to buy groceries')\n"
                     "• List tasks (e.g., 'Show me all my tasks')\n"
                     "• Complete tasks (e.g., 'Mark task 3 as done')\n"
                     "• Delete tasks (e.g., 'Delete task 2')",
            "suggestions": [
                "Add a task to...",
                "Show my tasks",
                "Mark task as complete",
                "Delete a task"
            ]
        }
```

## Performance Optimization

### Tool Caching
```python
from functools import lru_cache
import asyncio

class CachedMCPHandler:
    """Caches frequently used tool results."""

    @lru_cache(maxsize=100)
    async def cached_list_tasks(user_id: str, status: str = "all"):
        """Cache task lists for 1 minute."""
        return await list_tasks_handler(user_id, status)

    def invalidate_cache(self, user_id: str):
        """Invalidate cache when tasks change."""
        self.cached_list_tasks.cache_clear()
```

### Concurrent Tool Execution
```python
async def execute_tools_parallel(tools: List[dict]):
    """Execute multiple tools concurrently."""
    tasks = []
    for tool in tools:
        if tool["name"] == "add_task":
            tasks.append(add_task_handler(**tool["arguments"]))
        elif tool["name"] == "complete_task":
            tasks.append(complete_task_handler(**tool["arguments"]))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results
```

## Testing

### Agent Testing
```python
import pytest

async def test_add_task_tool():
    """Test add_task MCP tool."""
    result = await add_task_handler(
        user_id="test_user",
        title="Test Task",
        description="Test description"
    )

    assert result["success"] is True
    assert result["title"] == "Test Task"
    assert "task_id" in result

async def test_conversation_persistence():
    """Test conversation state persistence."""
    manager = StatelessConversationManager()

    # Send first message
    response1 = await manager.handle_message("user1", "Add a task")
    conv_id = response1["conversation_id"]

    # Send second message in same conversation
    response2 = await manager.handle_message(
        "user1",
        "Show my tasks",
        conv_id
    )

    assert response2["conversation_id"] == conv_id
    assert len(await manager.load_conversation(conv_id)) == 2
```

## Security

### Tool Authorization
```python
class ToolAuthorizer:
    """Ensures tools only access user's data."""

    async def authorize_tool_call(self, tool_name: str, arguments: dict, user_id: str):
        """Verify user can perform this tool call."""
        # Extract user_id from arguments for verification
        if "user_id" in arguments:
            if arguments["user_id"] != user_id:
                raise PermissionError("Cannot access other users' data")

        # Additional authorization logic
        if tool_name == "delete_task":
            task_id = arguments.get("task_id")
            if not await self.owns_task(user_id, task_id):
                raise PermissionError("Task not found or access denied")
```

### Input Sanitization
```python
def sanitize_mcp_input(data: dict, schema: dict) -> dict:
    """Sanitize input against MCP schema."""
    sanitized = {}
    properties = schema.get("properties", {})

    for key, value in data.items():
        if key in properties:
            prop_schema = properties[key]

            # Apply type conversion and limits
            if prop_schema.get("type") == "string":
                sanitized[key] = str(value)
                max_length = prop_schema.get("maxLength")
                if max_length:
                    sanitized[key] = sanitized[key][:max_length]
            elif prop_schema.get("type") == "integer":
                sanitized[key] = int(value)

    return sanitized
```

## Integration Points

### With Backend
- MCP tools use existing TaskService
- Shared database models for conversations
- Consistent error handling patterns

### With Frontend
- Real-time chat updates
- Tool call visualization
- Conversation history display

### With Other Agents
- Tool composition capabilities
- Intent classification for routing
- Error handling coordination

## Best Practices

### Stateless Architecture
1. **No in-memory state** - Everything stored in database
2. **Context per request** - Load full context each time
3. **Idempotent operations** - Safe to retry
4. **Scalable design** - Multiple instances can handle requests

### MCP Tool Design
1. **Clear schemas** - Well-defined input/output
2. **Error handling** - Graceful failures with messages
3. **Atomic operations** - Single responsibility per tool
4. **Documentation** - Clear tool descriptions

### Agent Behavior
1. **Helpful responses** - Confirm actions taken
2. **Error recovery** - Suggest fixes for failures
3. **Transparency** - Show tool calls made
4. **Safety first** - Never execute without confirmation