---
id: 006
title: "notification service implementation"
stage: implementation
date: 2025-12-23
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-cloud-deployment
branch: 005-cloud-deployment
user: Hamdan
command: Notification service implementation
labels: ["implementation", "notification", "microservice", "dapr", "phase5"]
links:
  spec: specs/005-cloud-deployment/spec.md
  plan: specs/005-cloud-deployment/plan.md
  tasks: specs/005-cloud-deployment/tasks.md
  ticket: null
  adr: null
  pr: null
files:
  - services/notifications/app/main.py
  - services/notifications/app/workers/due_date_checker.py
  - services/notifications/app/workers/recurring_processor.py
  - services/notifications/Dockerfile
  - services/notifications/requirements.txt
  - helm/notifications/
tests:
  - Notification service running
  - Due date checker working
  - Recurring processor working
  - Docker image builds
  - Dapr subscriptions working
---

## Prompt

Implement notification service microservice for due date alerts and recurring task processing.

CONTEXT:
Event publishing is complete. We need a notification service that subscribes to events, processes due date notifications, and creates new task occurrences from recurring tasks.

INSTRUCTIONS:

1. **Create Notification Service** (`services/notifications/`):
   - `main.py` - FastAPI app with health check
   - `requirements.txt` - Dependencies (fastapi, dapr, sqlalchemy)
   - `Dockerfile` - Multi-stage build, non-root user
   - Structure: `app/workers/` for worker modules

2. **Due Date Checker** (`services/notifications/app/workers/due_date_checker.py`):
   - Subscribe to: task-created, task-updated events
   - Check for tasks due within 24 hours
   - Send notifications (log for now, can extend to email)
   - Update `tasks.notified = True` after sending

3. **Recurring Task Processor** (`services/notifications/app/workers/recurring_processor.py`):
   - Subscribe to: recurring-task-due events
   - Create new task occurrence when recurring task is due
   - Calculate next_due_at for next occurrence
   - Handle end_date (stop creating after end date)
   - Pause if is_active = False

4. **Dapr Integration**:
   - `dapr_ext_fastapi` for subscriptions
   - Subscribe to topics in `main.py`
   - Event handlers for each topic

5. **Helm Chart** (`helm/notifications/`):
   - Chart.yaml, values.yaml, templates/
   - Dapr annotations (app-id: todo-notifications)
   - 2 replicas, resource limits
   - Service (NodePort)

ACTION:
Implement the notification service now.

## Response snapshot

Successfully implemented notification service microservice with Dapr event subscriptions.

### Files Created:

1. **services/notifications/app/main.py**
   - FastAPI application structure
   - Dapr FastAPI extensions
   - Health check endpoint
   - Event subscriptions configured

2. **services/notifications/app/workers/due_date_checker.py**
   - Due date detection logic
   - Notification sending (logging)
   - Task notification tracking

3. **services/notifications/app/workers/recurring_processor.py**
   - Recurring task processing
   - New task occurrence creation
   - Next due date calculation
   - End date handling

4. **services/notifications/Dockerfile**
   - Multi-stage Python build
   - Non-root user (appuser)
   - Port 8001
   - Health check configured

5. **services/notifications/requirements.txt**
   - FastAPI, Uvicorn, Dapr
   - SQLAlchemy, asyncpg
   - Project dependencies

6. **helm/notifications/**
   - Complete Helm chart
   - Dapr sidecar configuration
   - 2 replicas with HPA support
   - Resource limits configured

### Event Subscriptions:
- task-created → Check due date
- task-updated → Check due date
- recurring-task-due → Create next occurrence

### Test Results:
- Notification service starts successfully
- Event subscriptions working
- Due date checker processes events
- Recurring processor creates new tasks
