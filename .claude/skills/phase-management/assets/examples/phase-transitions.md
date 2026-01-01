# Phase Management - Evolution of TODO Edition

This guide documents the actual phase transitions and architectural decisions made during the Evolution of TODO project.

## Project Phases

| Phase | Status | Description | Key Technologies |
|-------|--------|-------------|------------------|
| Phase I | ✅ Complete | Console App CLI | Python, Click, File storage |
| Phase II | ✅ Complete | Web Application | FastAPI, Next.js, PostgreSQL, JWT |
| Phase III | ✅ Complete | AI Chatbot | Groq/Gemini, MCP tools, Conversation persistence |
| Phase IV | ✅ Complete | Kubernetes | Docker, Helm, Minikube |
| Phase V | ✅ Complete | Event-Driven Cloud | Dapr, Kubernetes, Cloud deployment |

## Phase I: Console App

### Architecture
- Single `main.py` file with all logic
- File-based storage (JSON)
- CLI interface with Click/Typer

### Key Decisions
- Simplicity over structure
- No database (files are enough)
- No authentication (local only)

## Phase II: Web Application

### Architecture
```
┌─────────┐      ┌─────────┐      ┌────────────┐
│ Frontend│ ───> │ Backend │ ───> │ PostgreSQL │
│ Next.js │      │ FastAPI │      │   Neon     │
└─────────┘      └─────────┘      └────────────┘
```

### Key Decisions (ADR: Phase I to Phase II Migration)
- **Backend**: FastAPI for async support
- **Frontend**: Next.js 14 App Router for React + SSR
- **Database**: PostgreSQL (Neon for cloud)
- **Auth**: JWT tokens (Better Auth integration)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)

### Migration Steps
1. Created FastAPI backend with CRUD endpoints
2. Created Next.js frontend with shadcn/ui
3. Set up PostgreSQL database with Alembic migrations
4. Implemented JWT authentication
5. Deployed to Vercel (frontend) and Railway/backend

## Phase III: AI Chatbot

### Architecture
```
┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│ Frontend│ ───> │ Backend │ ───> │   AI    │ ───> │   DB    │
│ ChatKit │      │  Agent  │      │ Groq    │      │ Conversations│
└─────────┘      └─────────┘      └─────────┘      └─────────┘
```

### Key Decisions (ADR: Phase II to Phase III AI Chatbot)
- **AI Provider**: Groq (primary) with Gemini/OpenAI fallback
- **Chat UI**: OpenAI ChatKit (not used in final implementation)
- **Conversation Storage**: Database-backed (stateless agent)
- **MCP Tools**: 5 tools for task management (add, list, complete, update, delete)
- **Language Support**: Bilingual (English/Urdu) with language detection

### Stateful vs Stateless Decision

**Initial Approach (Stateful)**:
```python
# BAD: In-memory state
class Agent:
    def __init__(self):
        self.conversation_history = []  # ❌ Lost on restart
```

**Final Approach (Stateless)**:
```python
# GOOD: Database-backed state
class AgentService:
    async def process_message(self, db, user_id, message, conversation_id):
        # Load history from database
        history = await conversation_manager.get_history(conversation_id)

        # Process with AI
        result = await self.run_agent(db, user_id, message, history)

        # Save to database
        await conversation_manager.save_message(conversation_id, "user", message)
        await conversation_manager.save_message(conversation_id, "assistant", result["response"])

        return result
```

### MCP Tools Defined
```python
AVAILABLE_TOOLS = {
    "add_task": {
        "schema": {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                        "due_date": {"type": "string"}
                    },
                    "required": ["title"]
                }
            }
        }
    },
    "list_tasks": {...},
    "complete_task": {...},
    "update_task": {...},
    "delete_task": {...}
}
```

### Bilingual Support
```python
def _detect_language(self, text: str) -> str:
    """Detect Urdu vs English from input."""
    import re
    urdu_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    total_chars = len(re.sub(r'\s', '', text))

    if total_chars > 0 and (urdu_chars / total_chars) > 0.3:
        return 'ur'
    return 'en'
```

## Phase IV: Kubernetes

### Architecture
```
┌──────────────────────────────────────────────┐
│            Kubernetes Cluster                │
│  ┌────────────┐  ┌────────────┐  ┌────────┐ │
│  │ Frontend   │  │ Backend    │  │  Postgres│
│  │ Deployment │  │ Deployment │  │  StatefulSet│
│  └────────────┘  └────────────┘  └────────┘ │
└──────────────────────────────────────────────┘
```

### Key Decisions (ADR: Phase III to Phase IV Kubernetes)
- **Container Runtime**: Docker
- **Orchestration**: Kubernetes (Minikube for local, DOKS for prod)
- **Package Manager**: Helm
- **Ingress**: Nginx with cert-manager for SSL
- **Registry**: DigitalOcean Container Registry

### Helm Chart Structure
```
helm/todo-app/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── backend/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── configmap.yaml
    │   └── secrets.yaml
    ├── frontend/
    │   ├── deployment.yaml
    │   └── service.yaml
    └── ingress.yaml
```

## Phase V: Event-Driven Cloud

### Architecture
```
┌──────────┐       ┌──────────┐       ┌─────────────┐
│ Frontend │ ───> │ Backend  │ ───> │ Email Worker│
│          │       │ (Dapr)   │       │ (Subscriber)│
└──────────┘       └──────────┘       └─────────────┘
                         │
                         v
                    ┌─────────┐
                    │  PubSub │
                    │ (Redis) │
                    └─────────┘
```

### Key Decisions (ADR: Phase IV to Phase V Cloud Deployment)
- **Event Bus**: Dapr pub/sub (Redis)
- **Email Service**: Direct API calls (no Dapr in final implementation)
- **Background Tasks**: FastAPI BackgroundTasks
- **Cloud Provider**: DigitalOcean (DOKS)
- **Monitoring**: Health checks and logging

### Event Publishing Pattern
```python
# CRUD operations publish events
async def create_task(db, task_data, user_id):
    task = Task(**task_data.dict(), user_id=user_id)
    db.add(task)
    await db.commit()

    # Publish event (fire and forget)
    try:
        event_data = {"task_id": task.id, "user_id": user_id}
        await dapr_event_publisher.publish_task_created(event_data)
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")

    return task
```

### Email Notification Pattern
```python
# Background task for email
@router.post("")
async def create_task(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await task_crud.create_task(db, task_data, str(current_user.id))

    # Fire and forget email
    background_tasks.add_task(
        _send_email_notification,
        "created",
        _task_to_dict(task),
        current_user.email
    )

    return task
```

## Phase Transition Checklist

### Before Migrating to Next Phase
- [ ] All features from current phase implemented
- [ ] Tests passing (70%+ coverage)
- [ ] Documentation updated
- [ ] No critical bugs
- [ ] Performance acceptable
- [ ] Security review completed
- [ ] ADR created for architectural decisions
- [ ] Migration plan documented

### Migration Process
1. **Plan**: Create ADR documenting the changes
2. **Implement**: Build new architecture in parallel
3. **Test**: Comprehensive testing of new phase
4. **Deploy**: Gradual rollout with rollback plan
5. **Monitor**: Watch for issues post-deployment
6. **Document**: Update README and CLAUDE.md

## Production URLs

| Service | URL |
|---------|-----|
| Frontend | https://hackathon2.testservers.online |
| Backend | https://api.testservers.online |
| API Docs | https://api.testservers.online/docs |

## Key Learnings

1. **Stateless Architecture**: Always design for statelessness from the start
2. **Event-Driven**: Fire-and-forget pattern prevents cascading failures
3. **Database Backed**: Use database for all persistent state
4. **Multi-Provider**: Have fallback providers for critical services (AI)
5. **Tenant Isolation**: Always filter by user_id in queries
6. **Background Tasks**: Use async operations for slow tasks (email, webhooks)
7. **Health Checks**: Implement /health endpoints for all services
8. **Documentation**: Keep ADRs for all major decisions
