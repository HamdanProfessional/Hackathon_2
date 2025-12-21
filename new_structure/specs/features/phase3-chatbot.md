# Phase III: AI Chatbot Interface Specification

## Overview
Phase III transforms the Todo application by adding an intelligent conversational interface. This phase integrates OpenAI ChatKit for the UI, Google Gemini 2.5 Flash via OpenAI Agents SDK compatibility layer for AI capabilities, and MCP tools for backend integration, following a strict stateless architecture.

## User Stories

### Story 1: Conversational Task Management
**As a** user
**I want to** manage my tasks through natural conversation
**So that** I can interact with my todo list more intuitively

**Acceptance Criteria**:
- Natural language input for creating, updating, and querying tasks
- AI understands context and maintains conversation flow
- Supports complex commands like "Show me all urgent work tasks due this week"
- Conversational feedback for confirmation and clarification
- Ability to correct AI misunderstandings

### Story 2: Intelligent Task Assistance
**As a** user
**I want to** receive AI-powered suggestions and insights
**So that** I can manage my tasks more effectively

**Acceptance Criteria**:
- AI suggests task prioritization based on due dates and importance
- Identifies potential scheduling conflicts
- Provides productivity tips and task management advice
- Learns from user patterns and preferences
- Offers proactive reminders and follow-ups

### Story 3: Multi-Modal Interaction
**As a** user
**I want to** interact with the chatbot using different input methods
**So that** I can choose the most convenient way to communicate

**Acceptance Criteria**:
- Text chat with rich formatting and emoji support
- Voice input-to-text capability
- Quick action buttons for common commands
- File/image upload for task attachments (Phase IV)
- Keyboard shortcuts for power users

### Story 4: Contextual Awareness
**As a** user
**I want to** the AI to understand the current context
**So that** conversations are more relevant and efficient

**Acceptance Criteria**:
- AI remembers conversation history within the session
- Understands references to previous tasks and discussions
- Provides context-aware suggestions
- Maintains topic continuity across message exchanges
- Handles context switching gracefully

### Story 5: Personalized Experience
**As a** user
**I want to** the AI to adapt to my preferences and work style
**So that** the interaction feels personalized and efficient

**Acceptance Criteria**:
- AI learns user's task categorization preferences
- Adapts communication style based on user interactions
- Remembers user's preferred time formats, date formats
- Customizes response length and detail level
- Provides personalized productivity insights

## Technical Requirements

### Frontend Stack
- **Chatbot UI**: OpenAI ChatKit - **MANDATORY**
  - *UI Integration*: The `Frontend-UX-Designer-Core` must implement the ChatKit `<Chat />` interface connecting to the Phase II backend
  - *Reference*: https://platform.openai.com/docs/guides/chatkit
  - *Constraint*: Do NOT build custom chat UI from scratch (e.g., standard React forms). Use ChatKit components
- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript (strict mode)
- **State Management**: React hooks with context
- **Real-time**: WebSocket or HTTP polling for updates

### Backend Stack
- **AI Model:** Google Gemini 2.5 Flash - **MANDATORY**
  - *Provider*: Google Gemini via OpenAI Compatibility Layer
  - *Base URL*: `https://generativelanguage.googleapis.com/v1beta/openai/`
  - *API Key*: Environment variable `GOOGLE_API_KEY`
- **AI Agent Runtime:** OpenAI Agents SDK (Python) - **MANDATORY**
  - *Library Requirement*: Backend must install `openai-agents-python` package
  - *Agent Pattern*: Must implement the `Agent` and `Runner` patterns with `OpenAIChatCompletionsModel`
  - *Reference*: https://openai.github.io/openai-agents-python/
  - *Constraint*: Do NOT use LangChain, CrewAI, or vanilla OpenAI API calls
  - *SDK Pattern*: `AsyncOpenAI` + `OpenAIChatCompletionsModel` + `set_default_openai_client()`
- **Backend Adapter**: Custom ChatKit backend adapter
- **Tools Integration**: MCP (Model Context Protocol) tools - **MANDATORY**
  - *Constraint*: All AI tools must be implemented as MCP tools following the Official MCP SDK specification
- **Architecture**: Stateless (no in-memory conversation state)
  - *State Management*: Agents SDK must be configured to persist state to Neon DB via SQLModel, not in-memory

### MCP Tools
```python
# MCP Tool Definitions
tools = [
    {
        "name": "create_task",
        "description": "Create a new task",
        "parameters": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string"},
            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
            "due_date": {"type": "string", "format": "date-time"}
        }
    },
    {
        "name": "list_tasks",
        "description": "List tasks with filters",
        "parameters": {
            "status": {"type": "string", "enum": ["pending", "completed", "all"]},
            "priority": {"type": "string"},
            "category": {"type": "string"},
            "limit": {"type": "integer", "default": 20}
        }
    },
    {
        "name": "update_task",
        "description": "Update an existing task",
        "parameters": {
            "task_id": {"type": "string", "required": True},
            "updates": {"type": "object"}
        }
    },
    {
        "name": "delete_task",
        "description": "Delete a task",
        "parameters": {
            "task_id": {"type": "string", "required": True}
        }
    },
    {
        "name": "get_task_statistics",
        "description": "Get user's task statistics",
        "parameters": {}
    }
]
```

### Project Structure
```
backend/
├── app/
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── agents.py           # OpenAI Agents SDK integration
│   │   ├── tools/              # MCP tools implementation
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py        # Task-related MCP tools
│   │   │   └── user.py         # User-related MCP tools
│   │   ├── chatkit/            # Custom ChatKit backend adapter
│   │   │   ├── __init__.py
│   │   │   ├── adapter.py      # Main adapter implementation
│   │   │   ├── handlers.py     # Message handlers
│   │   │   └── auth.py         # Authentication for chat
│   │   └── conversation.py     # Conversation context management
│   ├── api/
│   │   ├── chat.py             # Chat API endpoints
│   │   └── conversations.py    # Conversation management endpoints
│   └── models/
│       ├── conversation.py     # Conversation data model
│       └── message.py          # Message data model

frontend/
├── app/
│   ├── chat/
│   │   ├── page.tsx            # Main chat interface
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   ├── QuickActions.tsx
│   │   │   └── TypingIndicator.tsx
│   │   └── hooks/
│   │       ├── useChat.ts      # Chat state management
│   │       └── useConversation.ts # Conversation context
│   └── lib/
│       ├── chatkit.ts          # ChatKit client configuration
│       └── conversation.ts     # Conversation utilities
```

### Database Schema (Additions)

#### Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
```

#### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    tool_calls JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
```

### AI Implementation Strategy

#### Gemini 2.5 Flash Integration via OpenAI Agents SDK

**CRITICAL:** The AI implementation MUST follow this exact pattern. Do NOT deviate from this code structure.

```python
# CODE PATTERN: GEMINI 2.5 WITH OPENAI AGENTS SDK
from agents import Agent, Runner, set_default_openai_client, AsyncOpenAI, OpenAIChatCompletionsModel
import os

# 1. Configure the Custom Client for Gemini
# Note: Use AsyncOpenAI, not OpenAIAsyncIO
gemini_client = AsyncOpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 2. Register as Global Default
set_default_openai_client(gemini_client)

# 3. Define the Model Adapter
# Critical: Must use OpenAIChatCompletionsModel for non-OpenAI native models
gemini_model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=gemini_client
)

# 4. Define Agent
todo_agent = Agent(
    name="TodoAssistant",
    model=gemini_model,  # Explicitly pass the Gemini adapter
    instructions="You are a helpful Todo assistant...",
    tools=[add_task, list_tasks] # List your MCP tools here
)

# backend/app/ai/agents.py
from agents import Agent, Runner, set_default_openai_client, AsyncOpenAI, OpenAIChatCompletionsModel
from app.ai.tools import create_tool_registry
from app.ai.conversation import load_conversation_context
import os

class TodoAgent:
    def __init__(self):
        # Initialize Gemini client with OpenAI compatibility
        self.client = AsyncOpenAI(
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        # Set as global default for OpenAI Agents SDK
        set_default_openai_client(self.client)

        # Configure the model adapter
        self.model = OpenAIChatCompletionsModel(
            model="gemini-2.5-flash",  # EXACT model string required
            openai_client=self.client
        )

        # Load MCP tools
        self.tool_registry = create_tool_registry()

        # Create the agent
        self.agent = Agent(
            name="TodoAssistant",
            model=self.model,
            instructions=self._build_system_prompt(),
            tools=self.tool_registry.get_tools()
        )

    async def process_message(self, user_id: str, message: str, conversation_id: str = None):
        # Load conversation context from database (stateless!)
        context = await load_conversation_context(user_id, conversation_id)

        # Create runner with context
        runner = Runner(
            self.agent,
            context=self._build_context(context)
        )

        # Process message
        result = await runner.run(message)

        # Save conversation to database
        await self._save_conversation(user_id, conversation_id, message, result)

        return result

    def _build_system_prompt(self) -> str:
        return """
        You are a helpful task management assistant for the Todo application.

        Guidelines:
        1. Be conversational and friendly
        2. Ask for clarification when needed
        3. Confirm actions before executing them
        4. Provide helpful suggestions
        5. Use the available tools to manage tasks
        6. Always reference task IDs when discussing tasks
        7. Format dates consistently (YYYY-MM-DD)
        """

    def _build_context(self, context: dict) -> str:
        return f"""
        Current Context:
        - User ID: {context.get('user_id')}
        - Total tasks: {context.get('total_tasks', 0)}
        - Pending tasks: {context.get('pending_tasks', 0)}
        - Categories: {', '.join(context.get('categories', []))}
        - Recent tasks: {context.get('recent_tasks_summary', [])}
        """
```

#### Important Implementation Notes
- **DO NOT use `OpenAIAsyncIO`** - The correct class is `openai.AsyncOpenAI`
- **Model string must be exactly `gemini-2.5-flash`** - Do not use `gemini-1.5` or `gemini-2.0`
- **Always use `OpenAIChatCompletionsModel`** for non-OpenAI models
- **Set global default client** before creating agents
- **Statelessness must be maintained** - All context loaded from database on every request

### Custom ChatKit Backend Adapter
```python
# backend/app/ai/chatkit/adapter.py
from fastapi import HTTPException, Depends
from app.api.deps import get_current_user
from app.ai.agents import TodoAgent

class ChatKitBackendAdapter:
    def __init__(self, agent: TodoAgent):
        self.agent = agent

    async def handle_message(self, message: str, conversation_id: str = None):
        try:
            # Process message through AI agent
            response = await self.agent.process_message(
                user_id=current_user.id,
                message=message,
                conversation_id=conversation_id
            )

            return {
                "id": str(uuid4()),
                "role": "assistant",
                "content": response.content,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": response.metadata
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_conversations(self):
        # Retrieve user's conversations from database
        pass

    async def get_messages(self, conversation_id: str):
        # Retrieve messages for a conversation
        pass
```

### Frontend Chat Interface
```typescript
// frontend/app/chat/components/ChatInterface.tsx
'use client'

import { useState, useEffect, useRef } from 'react'
import { ChatKitProvider, MessageList, MessageInput } from '@openai/chatkit-react'
import { useChat } from '../hooks/useChat'
import { Message } from '@openai/chatkit'

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { sendMessage, getConversations } = useChat()

  const handleSendMessage = async (content: string) => {
    // Add user message immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      createdAt: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setIsTyping(true)

    try {
      // Send to backend
      const response = await sendMessage(content)

      // Add AI response
      const aiMessage: Message = {
        id: response.id,
        role: 'assistant',
        content: response.content,
        createdAt: new Date(response.created_at)
      }
      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      // Add error message
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        createdAt: new Date()
      }])
    } finally {
      setIsTyping(false)
    }
  }

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList
          messages={messages}
          isTyping={isTyping}
          ref={messagesEndRef}
        />
      </div>

      <div className="border-t p-4">
        <MessageInput
          onSend={handleSendMessage}
          disabled={isTyping}
          placeholder="Ask me about your tasks..."
        />
      </div>
    </div>
  )
}
```

### Stateless Architecture Implementation
```python
# backend/app/ai/conversation.py
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.models import Conversation, Message, Task
from app.crud import get_user_tasks, create_conversation, save_message

class ConversationManager:
    @staticmethod
    async def load_conversation_context(user_id: str, conversation_id: Optional[str] = None) -> Dict:
        """
        Load conversation context from database. NO in-memory state!
        """
        # Get recent tasks for context
        recent_tasks = await get_user_tasks(
            user_id=user_id,
            limit=20,
            filters={"status": ["pending", "in_progress"]}
        )

        # Get conversation history if conversation_id provided
        conversation_history = []
        if conversation_id:
            conversation_history = await Message.get_conversation_history(
                conversation_id=conversation_id,
                limit=50  # Last 50 messages
            )

        # Build context object
        return {
            "user_id": user_id,
            "total_tasks": await Task.count_user_tasks(user_id),
            "pending_tasks": len([t for t in recent_tasks if t.status == "pending"]),
            "recent_tasks": [task.to_dict() for task in recent_tasks],
            "categories": await Task.get_user_categories(user_id),
            "conversation_history": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in conversation_history
            ],
            "current_time": datetime.utcnow().isoformat()
        }

    @staticmethod
    async def save_interaction(
        user_id: str,
        conversation_id: Optional[str],
        user_message: str,
        ai_response: Dict,
        tool_calls: List[Dict] = None
    ) -> str:
        """
        Save conversation interaction to database
        """
        # Create or get conversation
        if not conversation_id:
            conversation_id = await create_conversation(
                user_id=user_id,
                title=user_message[:100] + ("..." if len(user_message) > 100 else "")
            )

        # Save user message
        await save_message(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )

        # Save AI response
        await save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response["content"],
            metadata=ai_response.get("metadata", {}),
            tool_calls=tool_calls or []
        )

        return conversation_id
```

### MCP Tools Implementation
```python
# backend/app/ai/tools/tasks.py
from typing import Dict, Any, List
from app.crud import create_task, get_tasks, update_task, delete_task
from app.schemas import TaskCreate, TaskUpdate

async def create_task_handler(parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    MCP Tool: Create a new task
    """
    task_data = TaskCreate(
        title=parameters["title"],
        description=parameters.get("description"),
        priority=parameters.get("priority", "medium"),
        due_date=parameters.get("due_date")
    )

    task = await create_task(task_data=task_data, user_id=user_id)

    return {
        "success": True,
        "task_id": str(task.id),
        "message": f"Task '{task.title}' created successfully"
    }

async def list_tasks_handler(parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    MCP Tool: List tasks with filters
    """
    filters = {
        "status": parameters.get("status"),
        "priority": parameters.get("priority"),
        "category": parameters.get("category")
    }
    filters = {k: v for k, v in filters.items() if v is not None}

    tasks = await get_tasks(
        user_id=user_id,
        limit=parameters.get("limit", 20),
        filters=filters
    )

    return {
        "success": True,
        "tasks": [task.to_dict() for task in tasks],
        "count": len(tasks)
    }

# Tool registry
TOOL_HANDLERS = {
    "create_task": create_task_handler,
    "list_tasks": list_tasks_handler,
    "update_task": update_task_handler,
    "delete_task": delete_task_handler,
    "get_task_statistics": get_task_statistics_handler
}
```

## Performance Requirements

### AI Response Time
- Initial response: < 3 seconds
- Tool execution: < 2 seconds per tool call
- Conversation loading: < 500ms
- Message sending: < 1 second

### Scaling Requirements
- Concurrent conversations: 1000+ per user
- Messages per minute: 60 per user
- Tool calls per minute: 120 per user
- Database queries: < 50ms average

### Resource Limits
- OpenAI API rate limits: Respect all limits
- Memory usage: < 100MB per conversation
- Database connections: Pool management
- Response size: < 10KB per message

## Security Requirements

### AI Security
- Input sanitization for all user inputs
- SQL injection prevention in MCP tools
- Prompt injection protection
- Rate limiting per user
- Content filtering for harmful requests

### Data Privacy
- Conversation data encrypted at rest
- Access control: users only see their data
- Audit logging for all AI interactions
- Data retention policies
- Right to deletion (GDPR)

### Authentication
- JWT token validation for all chat endpoints
- Session management for conversations
- CSRF protection
- Secure WebSocket connections

## Definition of Done

### Functional Requirements
- [ ] OpenAI ChatKit integration complete
- [ ] Custom ChatKit backend adapter implemented
- [ ] MCP tools for all CRUD operations
- [ ] OpenAI Agents SDK integration
- [ ] Stateless architecture enforced
- [ ] Conversation persistence in database

### Technical Requirements
- [ ] All AI responses under 3 seconds
- [ ] Database queries optimized (< 50ms)
- [ ] No in-memory conversation state
- [ ] Comprehensive error handling
- [ ] WebSocket fallback to HTTP polling
- [ ] Responsive design on all devices

### Quality Requirements
- [ ] 99.9% uptime for AI features
- [ ] Security audit passed
- [ ] Performance benchmarks met
- [ ] Accessibility compliance
- [ ] Comprehensive test coverage
- [ ] Documentation complete

## Success Metrics
- Task completion via chat: > 80% success rate
- User satisfaction with AI: > 4.5/5 rating
- Average conversation length: 5-15 messages
- Tool execution accuracy: > 95%
- Response time compliance: > 98% under 3 seconds

## Out of Scope
- Voice output (text-to-speech)
- Advanced AI features (sentiment analysis, etc.)
- Multi-user collaborative conversations
- Custom AI model training
- Integration with external AI services beyond OpenAI

## Notes for Phase IV Transition
- AI components containerized for Kubernetes deployment
- Database schema ready for horizontal scaling
- MCP tools designed for microservice architecture
- Performance monitoring and observability ready
- A/B testing framework for AI responses