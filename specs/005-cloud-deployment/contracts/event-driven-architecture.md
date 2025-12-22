# API Contract: Event-Driven Architecture

**Feature**: 005-cloud-deployment

This document defines the event contracts, Dapr integration, and API specifications for Phase V.

---

## Event Schemas

### Task Created Event

**Topic**: `task-created`
**Publisher**: Backend Service
**Subscribers**: Notification Service

```json
{
    "event_id": "uuid",
    "event_type": "task-created",
    "timestamp": "2025-01-01T00:00:00Z",
    "data": {
        "task_id": "uuid",
        "user_id": "uuid",
        "title": "Complete report",
        "description": "Finish Q4 analysis report",
        "priority": 2,
        "due_date": "2025-01-15T17:00:00Z",
        "recurring_task_id": null,
        "created_at": "2025-01-01T00:00:00Z"
    }
}
```

---

### Task Updated Event

**Topic**: `task-updated`
**Publisher**: Backend Service
**Subscribers**: Notification Service, Analytics Service

```json
{
    "event_id": "uuid",
    "event_type": "task-updated",
    "timestamp": "2025-01-01T01:00:00Z",
    "data": {
        "task_id": "uuid",
        "user_id": "uuid",
        "changes": {
            "title": {
                "old": "Complete report",
                "new": "Complete Q4 report"
            }
        },
        "updated_at": "2025-01-01T01:00:00Z"
    }
}
```

---

### Task Completed Event

**Topic**: `task-completed`
**Publisher**: Backend Service
**Subscribers**: Notification Service, Analytics Service

```json
{
    "event_id": "uuid",
    "event_type": "task-completed",
    "timestamp": "2025-01-15T18:00:00Z",
    "data": {
        "task_id": "uuid",
        "user_id": "uuid",
        "title": "Complete report",
        "completed_at": "2025-01-15T18:00:00Z",
        "was_overdue": false
    }
}
```

---

### Task Due Soon Event

**Topic**: `task-due-soon`
**Publisher**: Notification Service (Worker)
**Subscribers**: Notification Service

```json
{
    "event_id": "uuid",
    "event_type": "task-due-soon",
    "timestamp": "2025-01-15T05:00:00Z",
    "data": {
        "task_id": "uuid",
        "user_id": "uuid",
        "title": "Complete report",
        "due_date": "2025-01-15T17:00:00Z",
        "hours_until_due": 12,
        "priority": 2
    }
}
```

---

### Recurring Task Due Event

**Topic**: `recurring-task-due`
**Publisher**: Notification Service (Worker)
**Subscribers**: Notification Service

```json
{
    "event_id": "uuid",
    "event_type": "recurring-task-due",
    "timestamp": "2025-01-08T00:00:00Z",
    "data": {
        "recurring_task_id": "uuid",
        "user_id": "uuid",
        "title": "Weekly Team Meeting",
        "recurrence_type": "weekly",
        "recurrence_interval": 1,
        "occurrence_date": "2025-01-08T09:00:00Z",
        "next_due_at": "2025-01-15T09:00:00Z"
    }
}
```

---

## API Endpoints

### Recurring Tasks

#### POST /api/recurring-tasks

Create a new recurring task configuration.

**Request**:
```http
POST /api/recurring-tasks HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
    "title": "Weekly Team Meeting",
    "description": "Weekly standup with the team",
    "priority": 2,
    "recurrence_type": "weekly",
    "recurrence_interval": 1,
    "start_date": "2025-01-01T09:00:00Z",
    "end_date": "2025-12-31T09:00:00Z"
}
```

**Response** (201 Created):
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "123e4567-e89b-12d3-a456-426614174001",
    "title": "Weekly Team Meeting",
    "description": "Weekly standup with the team",
    "priority": 2,
    "recurrence_type": "weekly",
    "recurrence_interval": 1,
    "start_date": "2025-01-01T09:00:00Z",
    "end_date": "2025-12-31T09:00:00Z",
    "last_created_at": null,
    "next_due_at": "2025-01-08T09:00:00Z",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
}
```

**Errors**:
- `400`: Invalid recurrence_type or interval
- `401`: Unauthorized
- `400`: end_date before start_date

---

#### GET /api/recurring-tasks

List all recurring tasks for the authenticated user.

**Request**:
```http
GET /api/recurring-tasks?page=1&page_size=20 HTTP/1.1
Authorization: Bearer <token>
```

**Response** (200 OK):
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "items": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Weekly Team Meeting",
            "recurrence_type": "weekly",
            "next_due_at": "2025-01-08T09:00:00Z",
            "is_active": true
        }
    ],
    "total": 5,
    "page": 1,
    "page_size": 20,
    "pages": 1
}
```

---

#### GET /api/recurring-tasks/{id}

Get a specific recurring task.

**Request**:
```http
GET /api/recurring-tasks/{id} HTTP/1.1
Authorization: Bearer <token>
```

**Response** (200 OK):
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "123e4567-e89b-12d3-a456-426614174001",
    "title": "Weekly Team Meeting",
    "description": "Weekly standup with the team",
    "priority": 2,
    "recurrence_type": "weekly",
    "recurrence_interval": 1,
    "start_date": "2025-01-01T09:00:00Z",
    "end_date": "2025-12-31T09:00:00Z",
    "last_created_at": "2025-01-01T09:00:00Z",
    "next_due_at": "2025-01-08T09:00:00Z",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
}
```

**Errors**:
- `404`: Recurring task not found
- `403`: Recurring task belongs to different user

---

#### PUT /api/recurring-tasks/{id}

Update a recurring task.

**Request**:
```http
PUT /api/recurring-tasks/{id} HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
    "title": "Updated Title",
    "is_active": false
}
```

**Response** (200 OK):
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Updated Title",
    "is_active": false,
    "updated_at": "2025-01-02T00:00:00Z"
}
```

---

#### DELETE /api/recurring-tasks/{id}

Delete a recurring task.

**Request**:
```http
DELETE /api/recurring-tasks/{id} HTTP/1.1
Authorization: Bearer <token>
```

**Response** (204 No Content):
```http
HTTP/1.1 204 No Content
```

---

### Updated Task Endpoints

#### POST /api/tasks

Supports optional `due_date` field.

**Request**:
```http
POST /api/tasks HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
    "title": "Complete report",
    "description": "Finish Q4 analysis",
    "priority": 1,
    "due_date": "2025-01-15T17:00:00Z"
}
```

**Response** (201 Created):
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": "uuid",
    "title": "Complete report",
    "description": "Finish Q4 analysis",
    "priority": 1,
    "completed": false,
    "due_date": "2025-01-15T17:00:00Z",
    "notified": false,
    "recurring_task_id": null,
    "created_at": "2025-01-01T00:00:00Z"
}
```

---

#### GET /api/tasks

Supports filtering by due date.

**Request**:
```http
GET /api/tasks?due_before=2025-01-31T23:59:59Z HTTP/1.1
Authorization: Bearer <token>
```

**Response**: Returns tasks due before the specified date.

---

## Dapr Service Invocation

### Notification Service → Backend

Subscribe to task events.

```python
from dapr.ext.fastapi import DaprApp

dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="todo-pubsub", topic="task-created")
async def handle_task_created(event_data: dict):
    task_id = event_data["data"]["task_id"]
    due_date = event_data["data"].get("due_date")

    if due_date:
        await schedule_notification(task_id, due_date)
```

---

## Redpanda Topics

### Topic Configuration

| Topic | Partitions | Replication | Retention | Purpose |
|-------|-----------|-------------|-----------|---------|
| task-created | 3 | 3 | 7 days | New tasks |
| task-updated | 3 | 3 | 7 days | Task modifications |
| task-completed | 3 | 3 | 7 days | Task completions |
| task-due-soon | 3 | 3 | 1 day | Due notifications |
| recurring-task-due | 3 | 3 | 7 days | Recurring tasks |

### Topic Creation

```bash
# Via Redpanda pod
kubectl exec -it redpanda-0 -- rpk topic create task-created -p 3 -r 3
kubectl exec -it redpanda-0 -- rpk topic create task-updated -p 3 -r 3
kubectl exec -it redpanda-0 -- rpk topic create task-completed -p 3 -r 3
kubectl exec -it redpanda-0 -- rpk topic create task-due-soon -p 3 -r 3 --retention 86400000
kubectl exec -it redpanda-0 -- rpk topic create recurring-task-due -p 3 -r 3
```

---

## Dapr Components

### Pub/Sub Component

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
  namespace: default
spec:
  type: pubsub.redpanda
  version: v1
  metadata:
  - name: brokers
    value: "redpanda-0.redpanda.default.svc.cluster.local:9092"
  - name: authRequired
    value: "false"
  - name: allowedTopics
    value: "task-created,task-updated,task-completed,task-due-soon,recurring-task-due"
  - name: consumerID
    value: "todo-consumer-group"
```

### State Store Component (Optional - Redis)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-state
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis-secrets
      key: password
```

---

## Notification Service Contract

### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
    "status": "healthy",
    "workers": {
        "due_date_checker": "running",
        "recurring_processor": "running"
    },
    "dapr": {
        "sidecar_status": "healthy",
        "subscribed_topics": [
            "task-created",
            "task-updated",
            "task-completed",
            "task-due-soon",
            "recurring-task-due"
        ]
    }
}
```

### Worker Status

**Endpoint**: `GET /workers/status`

**Response**:
```json
{
    "due_date_checker": {
        "status": "running",
        "last_run": "2025-01-01T12:00:00Z",
        "tasks_checked": 150,
        "notifications_sent": 5
    },
    "recurring_processor": {
        "status": "running",
        "last_run": "2025-01-01T12:00:00Z",
        "recurring_tasks_processed": 10,
        "new_tasks_created": 10
    }
}
```

---

## Error Handling

### Event Processing Errors

All events must be processed with at-least-once semantics:

1. **Retry Strategy**: Exponential backoff (1s, 2s, 4s, 8s, 16s, 32s)
2. **Dead Letter Queue**: Failed events move to DLT after max retries
3. **Logging**: All errors logged with event context

### Error Event Schema

```json
{
    "event_id": "uuid",
    "original_event_id": "uuid",
    "event_type": "processing-failed",
    "timestamp": "2025-01-01T00:00:00Z",
    "data": {
        "original_topic": "task-created",
        "error": "Database connection timeout",
        "retry_count": 5,
        "will_retry": false
    }
}
```
