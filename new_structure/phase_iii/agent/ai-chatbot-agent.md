# Phase III: AI Chatbot Agent

## Agent Identity
**Name**: ai-chatbot-developer
**Domain**: AI-Powered Application Development
**Primary Responsibilities**: Building conversational interfaces using OpenAI ChatKit, Agents SDK, and Official MCP SDK for todo management

## Agent Description
The ai-chatbot-developer agent specializes in creating AI-powered chatbot interfaces that can manage todos through natural language. This agent implements a conversational layer on top of the Phase II application, using OpenAI's technologies to enable users to interact with their tasks via chat.

## Core Capabilities

### 1. Chat Interface Development
- **OpenAI ChatKit**: Build modern chat UI components
- **Real-time Messaging**: Bidirectional communication
- **Message History**: Persistent conversation storage
- **Multi-turn Dialogues**: Context-aware conversations

### 2. AI Agent Implementation
- **OpenAI Agents SDK**: Create intelligent task agents
- **Natural Language Understanding**: Parse user intents
- **Tool Calling**: Execute task operations via MCP
- **Stateless Architecture**: Scalable, production-ready design

### 3. MCP (Model Context Protocol)
- **MCP Server Development**: Expose task operations as tools
- **Tool Integration**: Connect AI agent to todo CRUD operations
- **Protocol Implementation**: Official MCP SDK compliance
- **Schema Definition**: Clear tool interfaces

### 4. Conversation Management
- **Stateless Server**: Database-backed conversation state
- **Context Loading**: Retrieve conversation history
- **Session Management**: Handle multiple conversations
- **Message Persistence**: Store chat history securely

## Available Skills

### AI Integration Skills
1. **chatkit-integrator**: Integrate OpenAI ChatKit with Next.js
2. **openai-agent-builder**: Create AI agents with OpenAI SDK
3. **mcp-tool-maker**: Develop MCP tools for task operations
4. **conversation-manager**: Handle conversation state and history

### Backend Skills
1. **stateless-agent**: Ensure server remains stateless
2. **agent-orchestrator**: Coordinate AI agent with MCP tools
3. **context-loader**: Load conversation context from database
4. **message-processor**: Process and store chat messages

### Frontend Skills
1. **chat-interface-builder**: Create chat UI components
2. **real-time-updater**: Implement real-time message updates
3. **message-formatter**: Display messages with proper formatting
4. **typing-indicator**: Show when AI is responding

### Integration Skills
1. **api-schema-sync**: Sync frontend/backend schemas
2. **cors-fixer**: Resolve CORS issues for chat endpoints
3. **error-handler**: Handle AI service errors gracefully

## Agent Workflow

### 1. Setup Architecture
```python
1. Initialize MCP server with task tools
2. Create OpenAI agent with tool access
3. Set up ChatKit UI in frontend
4. Configure chat endpoint in backend
5. Implement conversation state management
```

### 2. Tool Development Loop
```python
for operation in task_operations:
    1. Define MCP tool schema
    2. Implement tool logic with SQLModel
    3. Register tool with MCP server
    4. Test with AI agent
    5. Validate error handling
```

### 3. Conversation Flow
```python
1. Receive user message
2. Load conversation history from database
3. Build message array for agent
4. Store user message
5. Run AI agent with MCP tools
6. Store AI response
7. Return to client (stateless)
```

## Chat API Architecture

### Chat Endpoint Design
```python
POST /api/{user_id}/chat

Request:
{
  "message": "string",           # User's natural language input
  "conversation_id": "number"    # Optional existing conversation
}

Response:
{
  "conversation_id": "number",   # Conversation identifier
  "response": "string",          # AI's natural language response
  "tool_calls": [                # List of MCP tools executed
    {
      "tool": "string",          # Tool name
      "input": {},               # Tool input
      "output": {}               # Tool result
    }
  ],
  "message_id": "number"         # Message identifier
}
```

### Stateless Request Cycle
```
┌─────────┐      ┌──────────────────┐      ┌─────────────┐
│ Client  │────▶│  Load History    │────▶│   Database  │
│         │      │  from DB         │      │             │
└─────────┘      └──────────────────┘      └─────────────┘
      │                   │
      ▼                   ▼
┌─────────┐      ┌──────────────────┐
│ Store   │────▶│  Run Agent       │
│ Message │      │  with MCP Tools  │
└─────────┘      └──────────────────┘
      │                   │
      ▼                   ▼
┌─────────┐      ┌──────────────────┐
│ Store   │◀─────│  Get AI Response │
│ Response │      │                  │
└─────────┘      └──────────────────┘
```

## MCP Tools Implementation

### Tool: add_task
```python
{
  "name": "add_task",
  "description": "Create a new task",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {"type": "string", "description": "User identifier"},
      "title": {"type": "string", "description": "Task title"},
      "description": {"type": "string", "description": "Optional description"}
    },
    "required": ["user_id", "title"]
  }
}

# Implementation
def add_task(user_id: str, title: str, description: str = None) -> dict:
    task = TaskService.create_task(user_id, title, description)
    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }
```

### Tool: list_tasks
```python
{
  "name": "list_tasks",
  "description": "Retrieve user's tasks",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {"type": "string"},
      "status": {"type": "string", "enum": ["all", "pending", "completed"]}
    },
    "required": ["user_id"]
  }
}
```

### Tool: complete_task
```python
{
  "name": "complete_task",
  "description": "Mark task as complete",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {"type": "string"},
      "task_id": {"type": "integer"}
    },
    "required": ["user_id", "task_id"]
  }
}
```

## AI Agent Configuration

### Agent Setup
```python
from openai import OpenAI
from agents import Agent, AgentRunner

client = OpenAI(api_key="your-key")

# Create agent with task management capabilities
task_agent = Agent(
    instructions=(
        "You are a helpful todo assistant. "
        "You can help users manage their tasks by adding, "
        "listing, completing, and deleting tasks. "
        "Always confirm actions with the user."
    ),
    tools=[
        add_task_tool,
        list_tasks_tool,
        complete_task_tool,
        delete_task_tool,
        update_task_tool
    ]
)

runner = AgentRunner(task_agent)
```

### Conversation Handling
```python
async def handle_message(user_id: str, message: str, conversation_id: int = None):
    # Load conversation history
    messages = await load_conversation(conversation_id) if conversation_id else []

    # Add current message
    messages.append({"role": "user", "content": message})

    # Store user message
    user_msg = await store_message(user_id, conversation_id, "user", message)

    # Run agent
    response = await runner.run(messages)

    # Store AI response
    ai_msg = await store_message(
        user_id,
        user_msg.conversation_id,
        "assistant",
        response.messages[-1].content,
        response.tool_calls
    )

    return {
        "conversation_id": user_msg.conversation_id,
        "response": ai_msg.content,
        "tool_calls": ai_msg.tool_calls
    }
```

## Frontend Chat Integration

### ChatKit Setup
```typescript
// components/ChatInterface.tsx
import { ChatKitProvider, ChatView } from '@openai/chatkit-react';

export function TodoChatInterface({ userToken }: { userToken: string }) {
  return (
    <ChatKitProvider
      apiUrl="/api/chat"
      authToken={userToken}
      theme="todo-theme"
    >
      <ChatView
        welcomeMessage="Hi! I can help you manage your tasks. What would you like to do?"
        placeholder="Ask me to add, complete, or list your tasks..."
      />
    </ChatKitProvider>
  );
}
```

### Custom Backend Adapter
```typescript
// lib/chatkit-adapter.ts
export class TodoChatAdapter implements ChatBackendAdapter {
  async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId
      })
    });

    return response.json();
  }
}
```

## Database Schema Extensions

### Conversations Table
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    tool_calls JSONB, -- Store tool calls made by AI
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);
```

### SQLModel Models
```python
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id")
    role: str = Field()  # 'user' or 'assistant'
    content: str
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    conversation: Conversation = Relationship(back_populates="messages")
```

## Natural Language Processing

### Intent Recognition
The AI agent automatically understands these patterns:

| User Intent | Example Phrases | Action |
|-------------|----------------|--------|
| Create Task | "Add task to buy groceries", "I need to remember to...", "Create a task for..." | `add_task` |
| List Tasks | "Show me my tasks", "What do I need to do?", "List all tasks" | `list_tasks` |
| Complete Task | "Mark task 3 as done", "I finished calling mom", "Complete the meeting task" | `complete_task` |
| Delete Task | "Delete task 2", "Remove the old task", "Cancel the appointment" | `delete_task` |
| Update Task | "Change task 1 title", "Update task description", "Rename task to..." | `update_task` |

### Entity Extraction
```python
# Example entity extraction in responses
User: "Mark task 3 as complete"
AI extracts:
- task_id: 3
- action: complete
- confirms: "I'll mark task 3 'Buy groceries' as complete. Is that correct?"

User: "Add a task to call mom tomorrow at 5pm"
AI extracts:
- title: "Call mom"
- details: "tomorrow at 5pm"
- confirms: "I'll add a task 'Call mom' with note 'tomorrow at 5pm'. OK?"
```

## Error Handling

### AI Service Errors
```python
class AIServiceError(Exception):
    """Base class for AI service errors"""
    pass

class ToolExecutionError(AIServiceError):
    """Error when MCP tool fails"""
    def __init__(self, tool_name: str, error: str):
        self.tool_name = tool_name
        self.error = error
        super().__init__(f"Tool '{tool_name}' failed: {error}")

async def handle_ai_error(error: Exception) -> str:
    """Convert AI errors to user-friendly messages"""
    if isinstance(error, ToolExecutionError):
        return f"Sorry, I couldn't {error.tool_name.replace('_', ' ')}: {error.error}"
    elif "rate limit" in str(error).lower():
        return "I'm receiving too many requests. Please try again in a moment."
    else:
        return "Something went wrong. Please try again."
```

### Frontend Error Display
```typescript
// Error component for chat
function ErrorMessage({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="flex items-center gap-2 text-red-600">
      <AlertCircle className="w-4 h-4" />
      <span>{error}</span>
      <button
        onClick={onRetry}
        className="text-sm underline hover:text-red-700"
      >
        Retry
      </button>
    </div>
  );
}
```

## Testing Strategy

### Unit Tests for MCP Tools
```python
def test_add_task_tool():
    """Test MCP add_task tool"""
    result = add_task("user1", "Test task", "Test description")
    assert result["status"] == "created"
    assert result["title"] == "Test task"
    assert "task_id" in result
```

### Integration Tests for Agent
```python
async def test_agent_conversation():
    """Test full conversation flow"""
    response = await handle_message("user1", "Add a task to buy groceries")
    assert "task" in response["response"].lower()
    assert len(response["tool_calls"]) > 0
```

### E2E Tests for Chat Interface
```typescript
// Playwright test
test('user can add task via chat', async ({ page }) => {
  await page.goto('/chat');
  await page.fill('[data-testid="chat-input"]', 'Add task to buy groceries');
  await page.click('[data-testid="send-button"]');

  await expect(page.locator('[data-testid="message"]')).toContainText('task created');
});
```

## Performance Optimization

### Conversation Pagination
```python
async def load_conversation(
    conversation_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[Message]:
    """Load conversation with pagination"""
    query = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).offset(offset).limit(limit)

    return session.exec(query).all()
```

### Tool Call Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_task_list(user_id: str, status: str) -> List[Task]:
    """Cache task lists for 1 minute"""
    return TaskService.get_user_tasks(user_id, status)
```

## Success Criteria

### Functional Requirements
- Users can manage tasks via natural language
- AI correctly interprets user intents
- All task operations available through chat
- Conversation history persists across sessions
- Stateless server architecture

### Technical Requirements
- MCP tools properly implemented
- ChatKit UI integrated seamlessly
- Error handling covers all edge cases
- Performance meets conversation latency < 2s
- Secure handling of user data

## Migration Path

### To Phase IV (Kubernetes)
- Containerize chat service
- Scale stateless chat endpoints
- Deploy MCP server as separate service
- Configure service discovery

### To Phase V (Advanced Features)
- Add voice input capabilities
- Implement proactive notifications
- Support multiple languages (Urdu)
- Add emotion detection in conversations