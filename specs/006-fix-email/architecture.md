# Email Notification Architecture

## Overview

The email notification system uses an event-driven architecture with Dapr pub/sub pattern. The backend publishes task lifecycle events, and the email worker subscribes to these events to send notifications.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Kubernetes Cluster                             │
│                                                                         │
│  ┌─────────────┐                  ┌──────────────────────────────┐    │
│  │   Frontend  │                  │         Dapr Sidecar         │    │
│  │   (Next.js) │                  │      (todo-pubsub)           │    │
│  └──────┬──────┘                  └──────────────┬───────────────┘    │
│         │                                        │                     │
│         │ HTTP                                   │ Pub/Sub              │
│         ▼                                        ▼                     │
│  ┌─────────────┐   Publish Events   ┌──────────────────────────────┐  │
│  │   Backend   │ ──────────────────▶│      Dapr Sidecar            │  │
│  │  (FastAPI)  │                    │      (todo-pubsub)           │  │
│  └─────────────┘                    └──────────────┬───────────────┘  │
│                                              │                         │
│                                              │ Subscribe               │
│                                              ▼                         │
│                                    ┌──────────────────────────────┐  │
│                                    │      Email Worker            │  │
│                                    │      (FastAPI + Dapr)        │  │
│                                    │                              │  │
│                                    │  ┌────────────────────────┐  │  │
│                                    │  │  Event Subscribers     │  │  │
│                                    │  │  - task-created        │  │  │
│                                    │  │  - task-updated        │  │  │
│                                    │  │  - task-completed      │  │  │
│                                    │  │  - task-deleted        │  │  │
│                                    │  │  - task-due-soon       │  │  │
│                                    │  │  - recurring-task-due  │  │  │
│                                    │  └───────────┬────────────┘  │  │
│                                    │              │               │  │
│                                    │              ▼               │  │
│                                    │  ┌────────────────────────┐  │  │
│                                    │  │  Email Service         │  │  │
│                                    │  │  - Template Renderer   │  │  │
│                                    │  │  - HTTP Client (httpx) │  │  │
│                                    │  └───────────┬────────────┘  │  │
│                                    └──────────────┼───────────────┘  │
│                                                   │                   │
│                                                   │ HTTPS             │
│                                                   ▼                   │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    PostgreSQL Database                         │  │
│  │  - User email addresses for recipient lookup                  │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘

                          │
                          │ HTTPS (Bearer Token)
                          ▼

┌─────────────────────────────────────────────────────────────────────┐
│                    External Email API                               │
│               email.testservers.online                              │
│                                                                     │
│  POST /api/send                                                    │
│  Headers: Authorization: Bearer <EMAIL_KEY>                        │
│  Body: {to, subject, body}                                         │
└─────────────────────────────────────────────────────────────────────┘

                          │
                          │ SMTP
                          ▼

┌─────────────────────────────────────────────────────────────────────┐
│                     User Email Inbox                                │
│                  n00bi2761@gmail.com                                │
└─────────────────────────────────────────────────────────────────────┘
```

## Event Flow

### Task Creation Flow

```
1. User creates task via Frontend
   └─▶ POST /api/tasks

2. Backend creates task in database
   └─▶ INSERT INTO tasks ...

3. Backend publishes event
   └─▶ DaprClient.publish_event(
         pubsub_name="todo-pubsub",
         topic_name="task-created",
         data={
           "task_id": "uuid",
           "user_id": "uuid",
           "title": "Task title",
           "description": "...",
           "priority": "high",
           "due_date": "2025-12-27T10:00:00Z"
         }
       )

4. Dapr delivers event to Email Worker
   └─▶ POST /task-created
       └─▶ handle_task_created_event(event_data)

5. Email Worker queries database for user email
   └─▶ SELECT email FROM users WHERE id = $user_id

6. Email Worker renders template
   └─▶ task-crud.html with context={title, action="created", ...}

7. Email Worker sends email via API
   └─▶ POST https://email.testservers.online/api/send
       Headers: Authorization: Bearer <EMAIL_KEY>
       Body: {to: user.email, subject: "Task Created: ...", body: "<html>..."}

8. User receives email notification
```

## Component Details

### Backend Event Publisher

**File**: `backend/app/api/tasks.py`

```python
from dapr.clients import DaprClient

def _publish_event_later(task_data: dict, event_name: str):
    def publish():
        with DaprClient() as dapr:
            dapr.publish_event(
                pubsub_name=settings.DAPR_PUBSUB_NAME,
                topic_name=event_name,
                data=task_data
            )

    threading.Thread(target=publish, daemon=True).start()

# Called after task CRUD operations
_publish_event_later(task_data, "task-created")
_publish_event_later(task_data, "task-updated")
_publish_event_later(task_data, "task-completed")
_publish_event_later(task_data, "task-deleted")
```

### Email Worker Subscribers

**File**: `services/email-worker/app/subscribers.py`

```python
from dapr.ext.fastapi import DaprApp

@dapr_app.subscribe(pubsub="todo-pubsub", topic="task-created")
async def task_created_subscriber(event_data: Dict[str, Any]):
    await handle_task_created_event(event_data)
    return {"status": "processed"}
```

### Email Service

**File**: `services/email-worker/app/email_service.py`

```python
class EmailService:
    async def send_template_email(
        self,
        template_name: str,
        subject: str,
        email: List[str],
        context: Dict[str, Any]
    ) -> bool:
        html_body = self.render_template(template_name, context)
        return await self.send_email(subject, email, html_body, html=True)
```

## Data Flow Diagram

```
┌─────────┐     ┌─────────┐     ┌──────────────┐     ┌─────────┐
│  User   │ ──▶ │Frontend │ ──▶ │   Backend    │ ──▶ │   DB    │
└─────────┘     └─────────┘     └──────┬───────┘     └────┬────┘
                                      │                   │
                                      │ Event             │ User Email
                                      ▼                   ▼
                             ┌──────────────┐     ┌──────────┐
                             │ Dapr Pub/Sub │     │  Users   │
                             └──────┬───────┘     └──────────┘
                                    │
                                    │ Subscribe
                                    ▼
                             ┌──────────────┐
                             │ Email Worker │
                             └──────┬───────┘
                                    │
                                    │ Render Template
                                    ▼
                             ┌──────────────┐
                             │   HTML Body  │
                             └──────┬───────┘
                                    │
                                    │ HTTP POST
                                    ▼
                             ┌──────────────┐
                             │ Email API    │
                             └──────┬───────┘
                                    │
                                    │ SMTP
                                    ▼
                             ┌──────────────┐
                             │ User Inbox   │
                             └──────────────┘
```

## Security

### API Key Management
- Stored as Kubernetes Secret
- Mounted as environment variable in email-worker pod
- Never logged or exposed in error messages

### IP Whitelisting
- Email API requires IP whitelisting
- Current whitelisted IP: 167.71.45.19 (DigitalOcean cluster)

### Dapr Security
- Service-to-service communication via Dapr sidecar
- Topic-level access control
- No direct HTTP access to subscribers

## Scalability

### Horizontal Scaling
- Email worker can scale to multiple pods
- Dapr distributes events across all subscribers
- Each pod processes events independently

### Resource Limits
```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### Throughput
- Single pod: ~10 emails/second
- Scaled to 3 pods: ~30 emails/second
- Sufficient for current workload (<100 tasks/day)

## Monitoring

### Health Checks
- `/health/live`: Liveness probe
- `/health/ready`: Readiness probe (includes DB connection check)

### Logging
- Event received: `Processing task-created event for task {task_id}`
- Email sent: `Task created email sent to {user.email}`
- Email failed: `Failed to send task created email to {user.email}`

### Metrics (Future)
- Emails sent per topic
- Email success/failure rate
- Average processing time per event
