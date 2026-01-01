# Implementation Plan: Email Notification System

**Branch**: `006-fix-email` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-fix-email/spec.md`

## Summary

Implement direct email notifications for Todo task CRUD operations using a custom email API, bypassing complex Dapr pub/sub infrastructure. The system sends HTML-formatted emails asynchronously when users create, complete, update, or delete tasks. Email sending is non-blocking and failure-tolerant to ensure task operations are never impacted by email service availability.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: FastAPI, httpx, SQLModel
**Storage**: PostgreSQL (Neon) for user data, existing TaskEventLog for audit
**Testing**: pytest (integration tests), manual testing in production
**Target Platform**: Kubernetes (DigitalOcean DOKS), local Minikube
**Project Type**: Web application (backend + frontend)
**Performance Goals**: Email sending <5 seconds, support 100 task ops/minute
**Constraints**: Non-blocking email sends, failure-tolerant, HTTP timeout 10 seconds
**Scale/Scope**: ~100 users, 4 event types (created/updated/completed/deleted)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Stateless Architecture: Email sending uses external API, no in-memory queue state
- ✅ Error Handling: All email failures logged, non-blocking to task operations
- ✅ Security: API key stored as Kubernetes secret, Bearer token authentication
- ✅ Logging: Comprehensive print() and logging for debugging
- ✅ Database: Uses existing User model for email lookup, no new tables required

## Project Structure

### Documentation (this feature)

```text
specs/006-fix-email/
├── spec.md              # Feature specification
├── plan.md              # This file
├── tasks.md             # Implementation tasks
├── research.md          # Technical research (Phase 0)
├── data-model.md        # Data structures (Phase 1)
├── quickstart.md        # Testing guide (Phase 1)
└── contracts/           # API contracts (Phase 1)
    └── email-api.yaml   # Email API specification
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── tasks.py                    # Modified: Add email notifications
│   ├── utils/
│   │   └── email_notifier.py           # New: Direct email sending utility
│   ├── models/
│   │   └── user.py                     # Existing: User.email for recipients
│   └── services/
│       └── event_publisher.py          # Modified: Kept for Dapr (unused for email)
├── tests/
│   └── test_email_notifications.py    # New: Email notification tests
└── Dockerfile                          # Existing: Backend container

k8s/
└── backend/
    ├── deployment.yaml                  # Existing: Backend with env vars
    └── secrets.yaml                     # Existing: EMAIL_API_KEY secret
```

**Structure Decision**: Web application with backend (FastAPI) + frontend (Next.js). Email notification logic lives entirely in backend as direct API calls from task endpoints using FastAPI BackgroundTasks.

## Complexity Tracking

> No constitution violations requiring justification

## Phase 0: Research & Decisions

### 0.1 Email Service Options

**Question**: Which email service to use given Gmail API OAuth2 complexity and SMTP blocking?

**Decision**: Custom email API at `https://email.testservers.online/api/send`

**Rationale**:
- User rejected third-party API keys (SendGrid, Resend)
- Gmail OAuth2 failed due to redirect_uri_mismatch and testing restrictions
- SMTP blocked by DigitalOcean (ports 25, 465, 587)
- Custom API provides simple Bearer token authentication
- Already whitelisted and working in production

**Alternatives Considered**:
- Gmail API with OAuth2: Too complex, redirect URI issues
- SendGrid/Resend: User rejected (no API keys)
- SMTP: Blocked by cloud provider
- Dapr pub/sub with Kafka: DNS resolution issues, complex infrastructure

### 0.2 Async Email Sending Pattern

**Question**: How to send emails asynchronously without blocking task operations?

**Decision**: FastAPI BackgroundTasks with direct HTTP calls

**Rationale**:
- FastAPI BackgroundTasks provides built-in async task execution
- No external queue infrastructure needed
- Simple to implement: `background_tasks.add_task(send_email, ...)`
- Tasks run in same process but after response is sent
- Exception handling: failures logged but don't affect response

**Alternatives Considered**:
- Dapr pub/sub with email worker subscriber: DNS issues, namespace complexity
- Celery with Redis: Additional infrastructure complexity
- asyncio.create_task(): Less controlled, could impact event loop

### 0.3 Email Template Strategy

**Question**: How to format HTML emails for task notifications?

**Decision**: Inline HTML with embedded CSS

**Rationale**:
- Simple string formatting in Python
- No template engine dependency (Jinja2 adds complexity)
- Inline CSS ensures email client compatibility
- Responsive design with CSS media queries
- Status badges with color coding

**Alternatives Considered**:
- Jinja2 templates: Adds dependency, overkill for simple templates
- External template service: External dependency, latency
- Plain text emails: Poor user experience

### 0.4 Error Handling Strategy

**Question**: How to handle email sending failures?

**Decision**: Log and continue (non-blocking)

**Rationale**:
- Task operations are primary feature, email is secondary notification
- Users see task CRUD success in UI immediately
- Email delivery failures don't impact core functionality
- Comprehensive logging for debugging
- httpx timeout set to 10 seconds prevents hanging

**Alternatives Considered**:
- Retry logic: Adds complexity, could cause duplicate emails
- Queue for retry: Additional infrastructure
- Fail task operations: Poor UX, email not critical path

## Phase 1: Design & Contracts

### 1.1 Data Model

#### Email Notification Event

```python
{
    "event_type": "created" | "updated" | "completed" | "deleted",
    "user_email": str,
    "task_data": {
        "task_id": int,
        "title": str,
        "description": Optional[str],
        "priority_id": Optional[int],
        "due_date": Optional[str],
        "completed": bool,
        "created_at": str,
        "updated_at": str
    }
}
```

#### Email Template Structure

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Responsive styles, status badges */
    </style>
</head>
<body>
    <div class="container">
        <div class="header">Todo Task Notification</div>
        <div class="content">
            <h3 class="task-title">{title}</h3>
            <span class="task-status status-{event_type}">{status}</span>
            <p>{description}</p>
            <a href="{app_url}">View your tasks</a>
        </div>
    </div>
</body>
</html>
```

### 1.2 API Contract

#### Email API Endpoint

**POST** `https://email.testservers.online/api/send`

**Request Headers**:
```
Authorization: Bearer {EMAIL_API_KEY}
Content-Type: application/json
```

**Request Body**:
```json
{
    "to": "recipient@example.com",
    "is_html": true,
    "subject": "Task Created: Buy groceries",
    "body": "<html>...</html>"
}
```

**Response**:
- `200 OK`: Email sent successfully
- `401 Unauthorized`: Invalid API key
- `4xx/5xx`: Email delivery failure

### 1.3 Internal API Contract

#### Backend Email Sending Function

```python
async def send_task_email(
    email: str,
    subject: str,
    task_title: str,
    task_description: Optional[str] = None,
    task_status: str = "created"
) -> bool
```

**Returns**: `True` if email sent successfully, `False` otherwise

**Raises**: No exceptions (all errors caught and logged)

### 1.4 Quickstart Testing Guide

```bash
# 1. Get JWT token
TOKEN=$(curl -X POST "https://api.testservers.online/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"n00bi2761@gmail.com","password":"test1234"}' | \
  jq -r '.access_token')

# 2. Create task (triggers email)
curl -X POST "https://api.testservers.online/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Email Notification","description":"Testing direct email"}'

# 3. Check backend logs
kubectl logs -n default deployment/todo-backend --tail=30 | grep EMAIL

# 4. Verify email arrived at n00bi2761@gmail.com
```

## Phase 2: Implementation Overview

### 2.1 Component: Email Notification Utility

**File**: `backend/app/utils/email_notifier.py`

**Responsibilities**:
- Send task notification emails via custom API
- Build HTML email templates with status badges
- Handle HTTP errors with logging

**Key Functions**:
```python
async def send_task_email(email, subject, task_title, task_description, task_status) -> bool
async def send_task_created_email(email, task_data) -> bool
async def send_task_updated_email(email, task_data) -> bool
async def send_task_completed_email(email, task_data) -> bool
async def send_task_deleted_email(email, task_data) -> bool
```

### 2.2 Component: Task Endpoint Modifications

**File**: `backend/app/api/tasks.py`

**Changes**:
1. Import `BackgroundTasks` from FastAPI
2. Add `background_tasks: BackgroundTasks` parameter to endpoints
3. Import `_send_email_notification` helper function
4. Replace `_publish_event_later()` calls with `_send_email_notification()`
5. Pass `current_user.email` to email function

**Modified Endpoints**:
- `POST /api/tasks` - Task created
- `PUT /api/tasks/{task_id}` - Task updated
- `PATCH /api/tasks/{task_id}/complete` - Task completed
- `DELETE /api/tasks/{task_id}` - Task deleted

### 2.3 Component: Helper Function

**File**: `backend/app/api/tasks.py` (internal)

**Function**:
```python
async def _send_email_notification(event_type: str, task_data: Dict, user_email: str):
    """Send email notification in background without blocking response."""
    print(f"[EMAIL] Sending {event_type} email to {user_email} for task {task_data.get('task_id')}")
    try:
        if event_type == "created":
            result = await send_task_created_email(user_email, task_data)
        elif event_type == "updated":
            result = await send_task_updated_email(user_email, task_data)
        elif event_type == "completed":
            result = await send_task_completed_email(user_email, task_data)
        elif event_type == "deleted":
            result = await send_task_deleted_email(user_email, task_data)

        if result:
            print(f"[EMAIL] Successfully sent {event_type} email to {user_email}")
        else:
            print(f"[EMAIL] Failed to send {event_type} email to {user_email}")
    except Exception as e:
        print(f"[EMAIL] Email sending failed for {event_type}: {e}")
        traceback.print_exc()
```

### 2.4 Environment Configuration

**Kubernetes Secret**: `k8s/backend/secrets.yaml`
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-backend-secrets
type: Opaque
stringData:
  email-api-key: "emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d"
```

**Environment Variables** (in deployment):
```yaml
env:
  - name: EMAIL_API_URL
    value: "https://email.testservers.online/api/send"
  - name: EMAIL_API_KEY
    valueFrom:
      secretKeyRef:
        name: todo-backend-secrets
        key: email-api-key
```

## Testing Strategy

### Unit Tests
- Mock httpx.AsyncClient to test email API calls
- Test error handling (HTTP 401, 500, timeout)
- Test HTML template generation

### Integration Tests
- Create task → Verify email function called
- Complete task → Verify completion email sent
- Update task → Verify update email sent
- Delete task → Verify deletion email sent

### Manual Tests
- Test with real email API (production)
- Verify email rendering in Gmail/Outlook
- Test email delivery to n00bi2761@gmail.com

## Deployment Plan

1. Build Docker image with unique tag: `direct-email-v1`
2. Push to DigitalOcean registry
3. Update Kubernetes deployment: `kubectl set image deployment/todo-backend`
4. Verify rollout: `kubectl rollout status deployment/todo-backend`
5. Check logs: `kubectl logs -f deployment/todo-backend | grep EMAIL`
6. Test email creation in production

## Monitoring & Observability

### Logging
- `[EMAIL] Sending {event_type} email to {email} for task {task_id}`
- `[EMAIL] Successfully sent {event_type} email to {email}`
- `[EMAIL] Failed to send {event_type} email to {email}`
- `[EMAIL] Email sending failed for {event_type}: {exception}`

### Metrics
- Email send success rate (should be >95%)
- Email send duration (should be <5 seconds p95)
- Email failure count (alert if >10% failure rate)

## Success Verification

- ✅ Task creation triggers email to user's registered address
- ✅ Task completion triggers congratulatory email
- ✅ Task update triggers notification email
- ✅ Task deletion triggers confirmation email
- ✅ Email sending failures don't block task operations
- ✅ HTML emails render correctly in Gmail/Outlook
- ✅ Backend logs show email sending attempts
- ✅ Production deployment successful at https://api.testservers.online
