# Implementation Plan: Phase 3 AI Chatbot Architecture Fix

**Spec**: @specs/features/phase3-ai-chatbot-fix.md
**Phase**: III (Agent-Augmented)
**Estimated Complexity**: Complex
**Timeline**: 3-4 days

---

## Overview

Fix the incorrect Phase 3 implementation that incorrectly uses React ChatKit by implementing the proper Python-based architecture with OpenAI Agents SDK, OpenAI ChatKit SDK for conversation persistence, and MCP tools for task management.

**Success Criteria**:
- [ ] React ChatKit dependencies completely removed
- [ ] Python backend uses openai_agents_sdk for agent orchestration
- [ ] Python backend uses openai_chatkit_sdk for conversation storage
- [ ] Agent connects to Gemini 2.5 Flash successfully
- [ ] Simple React frontend communicates via `/api/chat` endpoint
- [ ] MCP tools properly integrated and functional

---

## Architecture

### Component Diagram

```
┌─────────────────┐
│   Frontend      │
│  (Simple React) │
│  - Chat UI      │
│  - API Client   │
└────────┬────────┘
         │ HTTP/WebSocket
         ↓
┌─────────────────┐
│   Backend API   │
│   (FastAPI)     │
│  - /api/chat    │
│  - Agent Service│
│  - Conv Manager │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ↓         ↓
┌─────────┐ ┌──────────┐
│ Gemini  │ │ ChatKit  │
│ 2.5 Flash│ │Storage   │
└─────────┘ └──────────┘
    │         │
    └────┬────┘
         ↓
┌─────────────────┐
│   MCP Tools     │
│ (Task CRUD)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Database      │
│  (PostgreSQL)   │
└─────────────────┘
```

### Component Responsibilities

**1. Frontend**:
- Location: `frontend/components/chat/`
- Responsibility: Simple chat interface, message display, user input
- Dependencies: Backend `/api/chat` endpoint
- Key Files:
  - `simple-chat.tsx` - Main chat component (replaces ChatKit)
  - `message-list.tsx` - Message display component
  - `chat-input.tsx` - Input component

**2. Backend API**:
- Location: `backend/app/api/chat.py` (existing, needs updates)
- Responsibility: HTTP endpoint for chat, auth, rate limiting
- Dependencies: Agent Service, Conversation Manager
- Key Files:
  - `chat.py` - API endpoint (already exists)
  - Need minimal changes

**3. Agent Service**:
- Location: `backend/app/ai/agent.py` (needs refactoring)
- Responsibility: Agent orchestration using openai_agents_sdk
- Dependencies: Gemini API, MCP Tools, Conversation Manager
- Key Changes:
  - Remove manual tool execution
  - Use openai_agents_sdk Runner
  - Connect to Gemini 2.5 Flash

**4. Conversation Manager** (NEW):
- Location: `backend/app/ai/conversation_manager.py`
- Responsibility: Conversation persistence using openai_chatkit_sdk
- Dependencies: ChatKit Python SDK
- Key Files:
  - `conversation_manager.py` - New file for conversation storage

**5. MCP Tools**:
- Location: `backend/app/ai/mcp_tools.py` (already correct)
- Responsibility: Task management operations
- Dependencies: None (already working)
- Key Files:
  - `mcp_tools.py` - No changes needed

---

## Data Flow

### Corrected Flow
```
1. User types message in React UI
2. Frontend sends POST /api/chat with message and conversation_id
3. Backend API validates JWT, checks rate limit
4. Conversation Manager loads history from ChatKit
5. Agent Service creates Agent with MCP tools
6. Runner executes agent with user message + history
7. Agent calls Gemini API with tools
8. Tools execute task operations
9. Agent returns response
10. Conversation Manager saves new messages to ChatKit
11. Backend API returns response to frontend
12. Frontend displays new message
```

---

## Implementation Tasks

### Task 1: Remove Incorrect React ChatKit Implementation
**Complexity**: Simple
**Dependencies**: None

**Acceptance Criteria**:
- [ ] Delete `frontend/components/chat/chatkit-chat.tsx`
- [ ] Delete `frontend/components/chat/chatkit-provider.tsx`
- [ ] Remove `@openai/chatkit-react` from package.json
- [ ] Update imports in `frontend/app/chat/page.tsx`
- [ ] Update imports in `frontend/components/providers/ClientProviders.tsx`
- [ ] Run `npm install` to clean up dependencies

**Files to Modify/Delete**:
- `frontend/components/chat/chatkit-chat.tsx` (DELETE)
- `frontend/components/chat/chatkit-provider.tsx` (DELETE)
- `frontend/package.json` (remove dependency)
- `frontend/app/chat/page.tsx` (update imports)
- `frontend/components/providers/ClientProviders.tsx` (update imports)

---

### Task 2: Install Python Dependencies
**Complexity**: Simple
**Dependencies**: Task 1

**Acceptance Criteria**:
- [ ] Add `openai-agents-sdk` to backend requirements
- [ ] Add `openai-chatkit-sdk` to backend requirements
- [ ] Run `pip install -r requirements.txt`
- [ ] Verify imports work in Python

**Files to Modify**:
- `backend/requirements.txt` (add new dependencies)
- Test import in Python shell

---

### Task 3: Create Conversation Manager
**Complexity**: Moderate
**Dependencies**: Task 2

**Acceptance Criteria**:
- [ ] Create `backend/app/ai/conversation_manager.py`
- [ ] Initialize ChatKit client with proper configuration
- [ ] Implement `get_history(conversation_id)` method
- [ ] Implement `save_message(conversation_id, role, content)` method
- [ ] Implement `create_conversation(user_id)` method
- [ ] Add error handling for ChatKit operations
- [ ] Write unit tests for conversation manager

**Files to Create**:
```python
# backend/app/ai/conversation_manager.py
from typing import List, Optional
from openai_chatkit import ChatKit
from app.config import settings

class ConversationManager:
    def __init__(self):
        """Initialize ChatKit client for conversation persistence."""
        self.chatkit = ChatKit(
            api_key=settings.OPENAI_API_KEY,
            # Configure storage backend (PostgreSQL, etc.)
        )

    async def create_conversation(self, user_id: int) -> str:
        """Create new conversation and return conversation ID."""
        pass

    async def get_history(self, conversation_id: str, limit: int = 30) -> List[dict]:
        """Retrieve conversation history as list of messages."""
        pass

    async def save_message(self, conversation_id: str, role: str, content: str) -> None:
        """Save a message to the conversation."""
        pass

    async def get_user_conversations(self, user_id: int) -> List[dict]:
        """Get all conversations for a user."""
        pass
```

---

### Task 4: Refactor Agent Service
**Complexity**: Complex
**Dependencies**: Task 2, Task 3

**Acceptance Criteria**:
- [ ] Import openai_agents_sdk in agent.py
- [ ] Create Agent instance with proper instructions
- [ ] Register MCP tools with the agent
- [ ] Use Runner for agent execution (not manual loop)
- [ ] Configure for Gemini 2.5 Flash
- [ ] Remove manual tool execution code
- [ ] Keep conversation loading/saving to ConversationManager
- [ ] Test agent with simple message

**Files to Modify**:
```python
# backend/app/ai/agent.py (partial rewrite needed)
from openai import AsyncOpenAI
from openai_agents_sdk import Agent, Runner
from .conversation_manager import ConversationManager
from .mcp_tools import mcp

class AgentService:
    def __init__(self):
        """Initialize agent service with OpenAI client and conversation manager."""
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        self.conversation_manager = ConversationManager()
        self.model = settings.AI_MODEL

    def _create_agent(self, user_id: int) -> Agent:
        """Create agent instance with tools."""
        return Agent(
            name="Todo Assistant",
            instructions=self._build_system_prompt(user_id),
            model=self.model,
            tools=mcp.list_tools(),  # Get tools from MCP
            client=self.client
        )

    async def run_agent(
        self,
        db: AsyncSession,
        user_id: int,
        user_message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run agent with user message and return response."""
        # Create or get conversation
        if not conversation_id:
            conversation_id = await self.conversation_manager.create_conversation(user_id)

        # Load history
        history = await self.conversation_manager.get_history(conversation_id)

        # Create agent
        agent = self._create_agent(user_id)

        # Run agent using Runner
        result = await Runner.run(
            agent=agent,
            input=user_message,
            context=history
        )

        # Save messages
        await self.conversation_manager.save_message(
            conversation_id, "user", user_message
        )
        await self.conversation_manager.save_message(
            conversation_id, "assistant", result.response
        )

        return {
            "response": result.response,
            "conversation_id": conversation_id,
            "tool_calls": result.tool_calls or []
        }
```

---

### Task 5: Create Simple React Chat Component
**Complexity**: Moderate
**Dependencies**: Task 1

**Acceptance Criteria**:
- [ ] Create `frontend/components/chat/simple-chat.tsx`
- [ ] Implement message list display
- [ ] Implement chat input with send button
- [ ] Add loading state while processing
- [ ] Handle errors gracefully
- [ ] Style with Tailwind CSS
- [ ] Support auto-scroll to latest message
- [ ] Handle Enter key to send

**Files to Create**:
```typescript
// frontend/components/chat/simple-chat.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import { chatApi } from "@/lib/chat-api";
import { Loader2 } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function SimpleChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: input,
        conversation_id: conversationId
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setConversationId(response.conversation_id);
    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[70%] p-3 rounded-lg ${
                message.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-3 rounded-lg">
              <Loader2 className="w-4 h-4 animate-spin" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            placeholder="Ask me about your tasks..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

### Task 6: Update Chat Page Integration
**Complexity**: Simple
**Dependencies**: Task 5

**Acceptance Criteria**:
- [ ] Update `frontend/app/chat/page.tsx` to use SimpleChat
- [ ] Remove ChatKit provider wrapper
- [ ] Ensure proper layout and styling
- [ ] Test page loads correctly

**Files to Modify**:
```typescript
// frontend/app/chat/page.tsx
import SimpleChat from "@/components/chat/simple-chat";

export default function ChatPage() {
  return (
    <div className="container mx-auto h-screen py-8">
      <div className="h-full max-w-4xl mx-auto border rounded-lg overflow-hidden">
        <SimpleChat />
      </div>
    </div>
  );
}
```

---

### Task 7: Update Chat API Client
**Complexity**: Simple
**Dependencies**: None

**Acceptance Criteria**:
- [ ] Create `frontend/lib/chat-api.ts`
- [ ] Implement `sendMessage` function
- [ ] Include JWT token in headers
- [ ] Handle error responses
- [ ] TypeScript interfaces for request/response

**Files to Create**:
```typescript
// frontend/lib/chat-api.ts
import { apiClient } from "./api";

interface ChatRequest {
  message: string;
  conversation_id?: string;
}

interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: any[];
}

export const chatApi = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post("/chat", request);
    return response.data;
  }
};
```

---

### Task 8: Update Backend Chat Endpoint
**Complexity**: Simple
**Dependencies**: Task 3, Task 4

**Acceptance Criteria**:
- [ ] Update `backend/app/api/chat.py` to use new AgentService
- [ ] Remove old conversation/message CRUD if using ChatKit
- [ ] Ensure proper error handling
- [ ] Test endpoint with curl/Postman

**Files to Modify**:
- `backend/app/api/chat.py` (update send_chat_message function)

---

### Task 9: Environment Configuration
**Complexity**: Simple
**Dependencies**: Task 2

**Acceptance Criteria**:
- [ ] Add OPENAI_API_KEY to .env for ChatKit
- [ ] Ensure GEMINI_API_KEY is set
- [ ] Update backend config to load new keys
- [ ] Document environment variables

**Files to Modify**:
- `.env` (add OPENAI_API_KEY)
- `backend/app/config.py` (add new config options)

---

### Task 10: Integration Testing
**Complexity**: Moderate
**Dependencies**: All previous tasks

**Acceptance Criteria**:
- [ ] Test complete chat flow end-to-end
- [ ] Verify agent creates tasks via MCP tools
- [ ] Verify conversation history persists
- [ ] Test error scenarios (API failures)
- [ ] Test with multiple users (data isolation)
- [ ] Performance test (response time < 3 seconds)

**Test Cases**:
1. User says "Create a task to buy groceries"
2. Verify task created in database
3. User says "What are my tasks?"
4. Verify response includes created task
5. Refresh page, verify conversation history loaded
6. User says "Mark the groceries task as complete"
7. Verify task marked complete

---

## Testing Strategy

### Unit Tests
**Backend**:
- Test ConversationManager methods
- Test AgentService with mocked Gemini
- Test MCP tools (already exist)

**Frontend**:
- Test SimpleChat component rendering
- Test message sending and display
- Test error handling

### Integration Tests
- Test chat endpoint with real agent
- Test ChatKit conversation storage
- Test MCP tool execution through agent

### End-to-End Tests
- Complete user workflow using Cypress/Playwright
- Test conversation persistence across refreshes
- Test task creation/completion via chat

---

## Risks & Mitigations

### Risk 1: ChatKit Python SDK Configuration
**Probability**: High
**Impact**: Medium
**Mitigation**:
- Start with basic configuration
- Have fallback to manual conversation storage if ChatKit fails
- Document configuration steps clearly

### Risk 2: openai_agents_sdk Compatibility with Gemini
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Test with simple agent first
- Verify AsyncOpenAI client works with Gemini base URL
- Have manual implementation as fallback

### Risk 3: MCP Tool Integration
**Probability**: Low
**Impact**: Medium
**Mitigation**:
- MCP tools already working
- Just need to register with agent properly
- Test each tool individually

---

## Dependencies

**External**:
- Gemini 2.5 Flash API
- OpenAI ChatKit Service

**Internal**:
- Existing task CRUD operations
- JWT authentication system
- Database schema

**Blocking**:
- None identified

---

## Success Metrics

**Functional**:
- [ ] All React ChatKit references removed
- [ ] Chat functionality works with new architecture
- [ ] All user stories from spec implemented
- [ ] No data loss during migration

**Non-Functional**:
- [ ] Chat response time < 3 seconds
- [ ] Conversation loads in < 2 seconds
- [ ] 100% conversation persistence
- [ ] Zero security issues

---

## Rollback Plan

If implementation fails:
1. **Frontend**: Revert to Git commit before changes
2. **Backend**: Keep existing implementation as fallback
3. **Database**: No schema changes needed
4. **Configuration**: Can revert environment variables

**Safe Rollback Window**: 48 hours after deployment

---

## Post-Implementation

After completing all tasks:
1. **Deploy to Staging**: Test with staging database
2. **Load Testing**: Test with concurrent users
3. **User Testing**: Get feedback on chat experience
4. **Documentation**: Update README with new architecture
5. **Create PHR**: Document the fix implementation
6. **Monitor**: Watch for errors in production

---

## Additional Notes

**Migration Strategy**:
- Implement alongside existing code
- Use feature flag if needed
- Test thoroughly before switching

**Security Considerations**:
- Ensure all API calls have proper JWT validation
- Sanitize AI responses before display
- Rate limit chat endpoints

**Performance Optimizations**:
- Cache conversation history
- Implement conversation pagination
- Consider WebSocket for real-time updates

---

## Quality Checklist

Before completing:
- [ ] All React ChatKit dependencies removed
- [ ] Python SDKs properly installed and configured
- [ ] Agent creates and executes tools correctly
- [ ] Conversations persist across refreshes
- [ ] Error handling implemented throughout
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Security review completed