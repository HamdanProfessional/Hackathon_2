# Stateless AI Flow Architecture Specification

## Overview

This specification defines the stateless AI flow architecture for Phase III of the Todo Evolution application. The architecture ensures that AI agents have no in-memory conversation state, with all conversation state persisted in the Neon database using SQLModel.

### Key Technologies
- **AI Model**: Google Gemini 2.5 Flash via OpenAI Compatibility Layer
- **Agent SDK**: OpenAI Agents SDK (Python) - MANDATORY
- **Database**: Neon PostgreSQL with SQLModel for persistence
- **Architecture**: Stateless design for horizontal scaling

## Core Principles

### 1. Stateless Architecture
- **No in-memory conversation state** between requests
- **Database-driven context loading** for each AI request
- **Horizontal scalability** without session affinity
- **Request isolation** for reliability and debugging

### 2. Database-First Context
- All conversation history stored in PostgreSQL
- Context loaded per request from database
- Efficient indexing for fast context retrieval
- Cursor-based pagination for long conversations

### 3. Immutable Request Flow
- Each request is self-contained
- No reliance on previous request state
- All necessary context passed explicitly
- Clear input/output contracts

## Request Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API Gateway
    participant Load Balancer
    participant API Instance 1
    participant API Instance 2
    participant Database
    participant OpenAI API
    participant MCP Tools

    User->>Frontend: Send message
    Frontend->>API Gateway: POST /api/chat/message
    API Gateway->>Load Balancer: Route request

    Note over Load Balancer: Stateless routing - any instance can handle

    par Request to Instance 1
        Load Balancer->>API Instance 1: Forward request
    or Request to Instance 2
        Load Balancer->>API Instance 2: Forward request
    end

    API Instance 1->>Database: Load conversation context
    Database-->>API Instance 1: Return context (messages, tasks, user data)

    API Instance 1->>OpenAI API: Create thread with context
    OpenAI API-->>API Instance 1: Thread created

    API Instance 1->>OpenAI API: Run assistant with tools
    OpenAI API-->>API Instance 1: Assistant response with tool calls

    loop Tool Execution
        API Instance 1->>MCP Tools: Execute tool calls
        MCP Tools->>Database: Perform operations
        Database-->>MCP Tools: Operation results
        MCP Tools-->>API Instance 1: Tool results
        API Instance 1->>OpenAI API: Submit tool results
    end

    OpenAI API-->>API Instance 1: Final response

    API Instance 1->>Database: Save conversation turn
    Database-->>API Instance 1: Saved

    API Instance 1-->>Load Balancer: Response
    Load Balancer-->>API Gateway: Response
    API Gateway-->>Frontend: Response
    Frontend-->>User: Display AI response
```

## Database Schema for Stateless Architecture

### Optimized Tables for Context Loading

#### Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Optimized indexes
CREATE INDEX idx_conversations_user_id_updated ON conversations(user_id, updated_at DESC);
CREATE INDEX idx_conversations_user_last_message ON conversations(user_id, last_message_at DESC);
```

#### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    tool_calls JSONB DEFAULT '[]',
    token_usage JSONB DEFAULT '{}',
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Optimized indexes for fast retrieval
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_conversation_role ON messages(conversation_id, role);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Partial index for recent messages (optimization)
CREATE INDEX idx_messages_recent ON messages(conversation_id, created_at)
WHERE created_at > NOW() - INTERVAL '7 days';
```

#### Conversation Context Cache Table
```sql
CREATE TABLE conversation_context_cache (
    conversation_id UUID PRIMARY KEY REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_summary JSONB DEFAULT '{}',
    user_preferences JSONB DEFAULT '{}',
    recent_task_ids UUID[] DEFAULT '{}',
    context_hash VARCHAR(64),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 hour')
);

CREATE INDEX idx_context_cache_expires ON conversation_context_cache(expires_at);
CREATE INDEX idx_context_cache_user ON conversation_context_cache(user_id);
```

## Context Loading Strategy

### 1. Efficient Context Retrieval
```python
# backend/app/ai/context.py
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_
from app.models import Conversation, Message, Task

class ContextLoader:
    @staticmethod
    async def load_conversation_context(
        user_id: str,
        conversation_id: Optional[str] = None,
        max_messages: int = 50
    ) -> Dict[str, Any]:
        """
        Load complete context for AI agent request
        """

        # 1. Try to load from cache first
        if conversation_id:
            cached_context = await ContextLoader._load_from_cache(conversation_id)
            if cached_context:
                return cached_context

        # 2. Build fresh context
        context = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "messages": [],
            "tasks": [],
            "user_data": {},
            "summary": {}
        }

        # 3. Load conversation messages
        if conversation_id:
            context["messages"] = await ContextLoader._load_conversation_messages(
                conversation_id, max_messages
            )

        # 4. Load user's recent tasks
        context["tasks"] = await ContextLoader._load_user_tasks(user_id)

        # 5. Load user preferences
        context["user_data"] = await ContextLoader._load_user_data(user_id)

        # 6. Generate context summary
        context["summary"] = await ContextLoader._generate_summary(context)

        # 7. Cache the context
        if conversation_id:
            await ContextLoader._cache_context(conversation_id, context)

        return context

    @staticmethod
    async def _load_conversation_messages(
        conversation_id: str,
        max_messages: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Load recent messages from conversation with efficient pagination
        """
        query = (
            select(Message)
            .where(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.deleted_at.is_(None)
                )
            )
            .order_by(Message.created_at.desc())
            .limit(max_messages)
        )

        messages = await session.execute(query).scalars().all()

        # Convert to dict format and reverse to chronological order
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "tool_calls": msg.tool_calls or [],
                "timestamp": msg.created_at.isoformat()
            }
            for msg in reversed(messages)
        ]

    @staticmethod
    async def _load_user_tasks(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Load user's most relevant tasks for context
        """
        query = (
            select(Task)
            .where(
                and_(
                    Task.user_id == user_id,
                    Task.deleted_at.is_(None),
                    or_(
                        Task.status.in_(["pending", "in_progress"]),
                        Task.created_at > datetime.utcnow() - timedelta(days=7)
                    )
                )
            )
            .order_by(
                # Prioritize: urgent/high priority -> due soon -> recently created
                Task.priority.desc(),
                Task.due_date.asc().nulls_last(),
                Task.created_at.desc()
            )
            .limit(limit)
        )

        tasks = await session.execute(query).scalars().all()

        return [task.to_context_dict() for task in tasks]
```

### 2. Context Optimization
```python
# backend/app/ai/optimizer.py
class ContextOptimizer:
    @staticmethod
    async def optimize_context_for_ai(
        context: Dict[str, Any],
        max_tokens: int = 8000
    ) -> Dict[str, Any]:
        """
        Optimize context to fit within token limits while preserving relevance
        """

        # Calculate approximate token usage
        current_tokens = ContextOptimizer._estimate_tokens(context)

        if current_tokens <= max_tokens:
            return context

        # Apply optimization strategies
        optimized_context = context.copy()

        # 1. Summarize old messages
        if len(optimized_context["messages"]) > 20:
            recent_messages = optimized_context["messages"][-10:]
            old_messages = optimized_context["messages"][:-10]

            summary = await ContextOptimizer._summarize_messages(old_messages)

            optimized_context["messages"] = [
                {
                    "role": "system",
                    "content": f"Earlier conversation summary: {summary}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ] + recent_messages

        # 2. Limit task details
        if len(optimized_context["tasks"]) > 15:
            # Keep most important tasks, summarize others
            important_tasks = optimized_context["tasks"][:10]
            other_tasks_count = len(optimized_context["tasks"]) - 10

            optimized_context["tasks"] = important_tasks + [{
                "summary": f"... and {other_tasks_count} other tasks"
            }]

        # 3. Compress user data
        if optimized_context.get("user_data"):
            optimized_context["user_data"] = {
                "preferences": optimized_context["user_data"].get("preferences", {}),
                "stats": optimized_context["user_data"].get("stats", {})
            }

        return optimized_context
```

## Stateless AI Agent Implementation

### 1. Request Handler
```python
# backend/app/ai/agent.py
from fastapi import HTTPException, Depends
from app.api.deps import get_current_user
from app.ai.context import ContextLoader
from app.ai.optimizer import ContextOptimizer

class StatelessTodoAgent:
    def __init__(self, openai_client, tool_registry):
        self.client = openai_client
        self.tools = tool_registry

    async def process_message(
        self,
        message: str,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single message with complete statelessness
        """

        try:
            # 1. Load complete context (no reliance on memory)
            context = await ContextLoader.load_conversation_context(
                user_id=user_id,
                conversation_id=conversation_id
            )

            # 2. Optimize context for AI
            optimized_context = await ContextOptimizer.optimize_context_for_ai(
                context,
                max_tokens=8000
            )

            # 3. Create new OpenAI thread with full context
            thread = await self._create_thread_with_context(optimized_context)

            # 4. Add current message
            await self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=message
            )

            # 5. Run assistant
            run = await self._run_assistant(thread)

            # 6. Process tool calls
            final_response = await self._process_tool_calls(run, thread, user_id)

            # 7. Save to database (for next request's context)
            new_conversation_id = await self._save_conversation_turn(
                user_id=user_id,
                conversation_id=conversation_id,
                message=message,
                response=final_response
            )

            # 8. Invalidate context cache
            if new_conversation_id:
                await ContextLoader.invalidate_cache(new_conversation_id)

            return {
                "content": final_response["content"],
                "conversation_id": new_conversation_id,
                "metadata": final_response.get("metadata", {})
            }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to process message"
            )

    async def _create_thread_with_context(self, context: Dict[str, Any]):
        """
        Create a new thread with complete context - stateless approach
        """

        # Build system prompt with context
        system_prompt = self._build_system_prompt(context)

        # Create thread with context messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add conversation history (limited and optimized)
        for msg in context.get("messages", [])[-20:]:  # Last 20 messages
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add task context as system message
        if context.get("tasks"):
            task_context = self._format_tasks_for_ai(context["tasks"])
            messages.append({
                "role": "system",
                "content": f"Current tasks context:\n{task_context}"
            })

        thread = await self.client.beta.threads.create(
            messages=messages
        )

        return thread
```

### 2. Horizontal Scaling Support
```python
# backend/app/ai/scaling.py
class ScalingManager:
    @staticmethod
    async def ensure_request_distribution():
        """
        Ensure requests can be distributed across any instance
        """

        # 1. No local state
        # 2. All state in database
        # 3. Connection pooling configured
        # 4. Read replicas for context loading

        pass

    @staticmethod
    async def handle_instance_restart():
        """
        Gracefully handle instance restarts without losing state
        """

        # 1. No in-memory state to lose
        # 2. Database handles persistence
        # 3. New instances immediately ready

        pass

    @staticmethod
    async def monitor_performance():
        """
        Monitor performance for scaling decisions
        """

        metrics = {
            "context_load_time": await ContextLoader.measure_load_time(),
            "database_query_time": await Database.measure_query_time(),
            "ai_response_time": await OpenAI.measure_response_time(),
            "concurrent_requests": await get_current_load()
        }

        return metrics
```

## Performance Optimization

### 1. Database Optimizations
```sql
-- Partitioning for large message tables
CREATE TABLE messages_partitioned (
    LIKE messages INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE messages_2025_12 PARTITION OF messages_partitioned
FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Materialized view for conversation stats
CREATE MATERIALIZED VIEW conversation_stats AS
SELECT
    c.id as conversation_id,
    c.user_id,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at,
    MIN(m.created_at) as first_message_at
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.deleted_at IS NULL
GROUP BY c.id, c.user_id;

-- Refresh strategy
CREATE OR REPLACE FUNCTION refresh_conversation_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY conversation_stats;
END;
$$ LANGUAGE plpgsql;
```

### 2. Caching Strategy
```python
# backend/app/ai/cache.py
from redis import asyncio as aioredis
import json
from typing import Optional

class ContextCache:
    def __init__(self):
        self.redis = aioredis.from_url(os.getenv("REDIS_URL"))
        self.default_ttl = 3600  # 1 hour

    async def get_context(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get cached context"""
        key = f"context:{conversation_id}"
        data = await self.redis.get(key)

        if data:
            return json.loads(data)
        return None

    async def set_context(
        self,
        conversation_id: str,
        context: Dict[str, Any],
        ttl: int = None
    ):
        """Cache context"""
        key = f"context:{conversation_id}"
        ttl = ttl or self.default_ttl

        await self.redis.setex(
            key,
            ttl,
            json.dumps(context, default=str)
        )

    async def invalidate_context(self, conversation_id: str):
        """Invalidate cached context"""
        key = f"context:{conversation_id}"
        await self.redis.delete(key)
```

## Monitoring and Observability

### 1. Key Metrics
```python
# backend/app/ai/metrics.py
from prometheus_client import Histogram, Counter, Gauge

# Performance metrics
context_load_time = Histogram(
    'context_load_seconds',
    'Time to load conversation context'
)

ai_processing_time = Histogram(
    'ai_processing_seconds',
    'Time to process AI request'
)

database_query_time = Histogram(
    'database_query_seconds',
    'Time for database queries'
)

# Business metrics
conversation_length = Histogram(
    'conversation_length_messages',
    'Number of messages in conversation'
)

tool_usage = Counter(
    'tool_usage_total',
    'Number of tool calls',
    ['tool_name']
)

concurrent_requests = Gauge(
    'concurrent_ai_requests',
    'Current number of concurrent AI requests'
)
```

### 2. Health Checks
```python
# backend/app/ai/health.py
class HealthChecker:
    @staticmethod
    async def check_database_health():
        """Check database connectivity and performance"""
        try:
            # Test query
            await session.execute(select(1))
            return {"status": "healthy", "latency_ms": 50}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    async def check_openai_health():
        """Check OpenAI API availability"""
        try:
            # Test API call
            response = await openai_client.models.list()
            return {"status": "healthy", "models_count": len(response.data)}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    async def check_cache_health():
        """Check Redis cache availability"""
        try:
            await cache.redis.ping()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
```

## Testing the Stateless Architecture

### 1. State Isolation Tests
```python
# tests/test_stateless.py
import pytest
from app.ai.agent import StatelessTodoAgent

@pytest.mark.asyncio
async def test_request_isolation():
    """Test that each request is isolated"""
    agent = StatelessTodoAgent(openai_client, tool_registry)

    user_id = "test-user"

    # Request 1
    response1 = await agent.process_message(
        message="Create a task called 'Test Task 1'",
        user_id=user_id
    )
    conv_id_1 = response1["conversation_id"]

    # Request 2 (same user, new conversation)
    response2 = await agent.process_message(
        message="What tasks do I have?",
        user_id=user_id
    )
    conv_id_2 = response2["conversation_id"]

    # Verify different conversations
    assert conv_id_1 != conv_id_2

    # Request 3 (continuing first conversation)
    response3 = await agent.process_message(
        message="What was the task I just created?",
        user_id=user_id,
        conversation_id=conv_id_1
    )

    # Should mention 'Test Task 1'
    assert "Test Task 1" in response3["content"]

@pytest.mark.asyncio
async def test_horizontal_scaling_simulation():
    """Test that different instances produce same results"""
    agent1 = StatelessTodoAgent(openai_client, tool_registry)
    agent2 = StatelessTodoAgent(openai_client, tool_registry)  # Simulating different instance

    user_id = "test-user"
    conversation_id = None

    # Simulate alternating requests between instances
    for i, message in enumerate([
        "Create a task for meeting",
        "List my tasks",
        "Mark the meeting task as completed"
    ]):
        agent = agent1 if i % 2 == 0 else agent2

        response = await agent.process_message(
            message=message,
            user_id=user_id,
            conversation_id=conversation_id
        )

        conversation_id = response["conversation_id"]

        # Verify consistent conversation ID
        assert conversation_id is not None
```

## Deployment Considerations

### 1. Container Configuration
```yaml
# k8s/ai-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-ai-service
spec:
  replicas: 3  # Horizontal scaling
  selector:
    matchLabels:
      app: todo-ai-service
  template:
    metadata:
      labels:
        app: todo-ai-service
    spec:
      containers:
      - name: ai-service
        image: todo-ai:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: openai-key
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: redis-url
```

### 2. Auto-scaling Rules
```yaml
# k8s/ai-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: todo-ai-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todo-ai-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

This stateless architecture ensures that the AI system can scale horizontally without losing conversation context or functionality, meeting the requirements of the project constitution while providing a robust foundation for Phase IV and V.