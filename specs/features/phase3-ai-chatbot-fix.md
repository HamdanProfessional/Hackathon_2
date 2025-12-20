# Feature: AI Chatbot - Corrected Architecture for Phase III

## Overview
Fix the Phase 3 AI chatbot implementation to properly use Python-based OpenAI SDKs with MCP integration, removing incorrect React ChatKit dependencies and establishing proper agent orchestration with Gemini 2.5 Flash.

## Problem Analysis
Current Phase 3 incorrectly attempts to use React ChatKit for conversational AI. The correct architecture should be:
- Backend: Python with OpenAI Agents SDK + OpenAI ChatKit SDK for conversation storage
- Frontend: Simple React client communicating with backend API
- Agent: Uses openai_agents_sdk with Gemini 2.5 Flash via AsyncOpenAI
- Tools: MCP SDK for task management operations

## User Stories
- **US-1**: As a user, I want to chat with an AI assistant that understands my natural language task management requests, so that I can manage todos without using forms
- **US-2**: As a user, I want the AI to remember our conversation history, so that I can refer to previous tasks naturally
- **US-3**: As a user, I want the AI to create, update, complete, and delete tasks on my behalf, so that task management is conversational and efficient

## Acceptance Criteria
- [ ] **AC-1**: System uses openai_agents_sdk in Python (NOT React) for agent orchestration
- [ ] **AC-2**: System uses openai_chatkit_sdk in Python backend for conversation persistence (NOT React)
- [ ] **AC-3**: Frontend is a simple React client that sends messages to `/api/chat` endpoint
- [ ] **AC-4**: Agent connects to Gemini 2.5 Flash using AsyncOpenAI with proper base_url
- [ ] **AC-5**: MCP tools are properly registered and executed by the agent
- [ ] **AC-6**: All conversation history is stored/retrieved via ChatKit Python SDK
- [ ] **AC-7**: No React ChatKit dependencies remain in frontend code

## Technical Architecture

### Backend Components (Python)
1. **Agent Service** (`backend/app/ai/agent.py`)
   - Uses `openai_agents_sdk` for orchestration
   - Connects to Gemini 2.5 Flash via `AsyncOpenAI`
   - Manages tool execution loop

2. **Conversation Service** (NEW: `backend/app/ai/conversation_manager.py`)
   - Uses `openai_chatkit_sdk` for persistence
   - Stores/retrieves conversation history
   - Manages conversation state

3. **MCP Tools** (`backend/app/ai/mcp_tools.py`)
   - Already implemented correctly
   - Exposes task CRUD operations to agent

### Frontend Components (React - Simplified)
1. **Chat Interface** (`frontend/components/chat/simple-chat.tsx`)
   - Replaces ChatKit React component
   - Simple message display and input
   - Communicates with `/api/chat` endpoint

2. **API Client** (`frontend/lib/chat-api.ts`)
   - Wrapper around axios for chat endpoints
   - Handles conversation ID management

## Data Flow
```
User (React) → /api/chat → Agent Service → Gemini API → Tool Execution → Response → ChatKit Storage → User
```

## Implementation Tasks

### 1. Remove Incorrect ChatKit React Implementation
- Delete: `frontend/components/chat/chatkit-chat.tsx`
- Delete: `frontend/components/chat/chatkit-provider.tsx`
- Remove `@openai/chatkit-react` from package.json

### 2. Create Python Conversation Manager
```python
# backend/app/ai/conversation_manager.py
from openai_chatkit import ChatKit
import os

class ConversationManager:
    def __init__(self):
        # Initialize ChatKit for conversation persistence
        self.chatkit = ChatKit(
            api_key=os.getenv("OPENAI_API_KEY"),
            # Configure for your storage backend
        )

    async def get_history(self, conversation_id: str) -> List[dict]:
        """Retrieve conversation history"""
        pass

    async def save_message(self, conversation_id: str, role: str, content: str):
        """Save message to conversation"""
        pass
```

### 3. Update Agent Service
```python
# backend/app/ai/agent.py
from openai import AsyncOpenAI
from openai_agents_sdk import Agent, Runner
from .conversation_manager import ConversationManager

class AgentService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.conversation_manager = ConversationManager()

    async def run_agent(self, user_id: int, message: str, conversation_id: str = None):
        """Process user message with agent"""
        # Load history from ChatKit
        history = await self.conversation_manager.get_history(conversation_id)

        # Create agent with tools
        agent = Agent(
            name="Todo Assistant",
            instructions="Help users manage their tasks",
            model="gemini-2.5-flash",
            tools=mcp_tools.list_tools()
        )

        # Run agent
        result = await Runner.run(agent, input=message, context=history)

        # Save to ChatKit
        await self.conversation_manager.save_message(
            conversation_id, "user", message
        )
        await self.conversation_manager.save_message(
            conversation_id, "assistant", result.response
        )

        return result
```

### 4. Create Simple React Chat Component
```typescript
// frontend/components/chat/simple-chat.tsx
"use client";

import { useState } from "react";
import { chatApi } from "@/lib/chat-api";

export default function SimpleChat() {
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    setIsLoading(true);
    try {
      const response = await chatApi.sendMessage({
        message: input,
        conversation_id: conversationId
      });

      setMessages(prev => [
        ...prev,
        { role: "user", content: input },
        { role: "assistant", content: response.response }
      ]);

      setConversationId(response.conversation_id);
      setInput("");
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, i) => (
          <div key={i} className={`mb-4 ${msg.role === "user" ? "text-right" : "text-left"}`}>
            <div className={`inline-block p-3 rounded-lg ${msg.role === "user" ? "bg-blue-500 text-white" : "bg-gray-200"}`}>
              {msg.content}
            </div>
          </div>
        ))}
      </div>
      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && sendMessage()}
            className="flex-1 border rounded px-3 py-2"
            placeholder="Ask me about your tasks..."
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
          >
            {isLoading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
```

## Dependencies & Integration
- **Remove**: `@openai/chatkit-react` from frontend
- **Add Backend**: `openai-agents-sdk`, `openai-chatkit-sdk`
- **Keep**: Existing MCP tools implementation
- **Update**: Agent service to use proper SDKs

## Migration Steps
1. Backup current chat implementation
2. Remove React ChatKit components
3. Implement Python conversation manager with ChatKit SDK
4. Update agent service to use openai_agents_sdk
5. Create simple React chat component
6. Update chat API endpoint to use new architecture
7. Test end-to-end flow

## Verification Tests
1. Agent connects to Gemini 2.5 Flash successfully
2. Conversations are stored/retrieved via ChatKit Python SDK
3. MCP tools execute properly through agent
4. Frontend displays conversation correctly
5. No React ChatKit dependencies remain

## Out of Scope
- Voice input/output
- Multi-user conversations
- Advanced AI personality configuration
- Real-time collaborative features

## References
- OpenAI Agents SDK Documentation
- OpenAI ChatKit SDK Documentation
- Gemini 2.5 Flash API Documentation
- MCP SDK Documentation