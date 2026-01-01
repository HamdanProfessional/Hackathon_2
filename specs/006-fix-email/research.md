# Research: Email Notification System

**Feature**: 006-fix-email
**Date**: 2025-12-27
**Purpose**: Document technical decisions and research for email notification implementation

## Decision 1: Email Service Provider

**Question**: Which email service to use for sending task notifications?

### Options Evaluated

| Option | Pros | Cons | Verdict |
|--------|-------|-------|---------|
| Gmail API with OAuth2 | Free, reliable | Complex OAuth flow, redirect_uri_mismatch, testing mode restrictions | ❌ Rejected |
| SMTP (Gmail/O365) | Standard protocol | Port blocking by DigitalOcean (25, 465, 587), requires app passwords | ❌ Rejected |
| SendGrid | Industry standard, free tier | User rejected - no API keys allowed | ❌ Rejected |
| Resend | Modern API, generous free tier | User rejected - no API keys allowed | ❌ Rejected |
| Custom Email API | Simple Bearer auth, already whitelisted | Custom dependency | ✅ **Selected** |

### Decision: Use Custom Email API

**Rationale**:
- User explicitly rejected third-party API keys
- Gmail OAuth2 proved too complex (redirect URI issues)
- SMTP blocked by cloud provider infrastructure
- Custom API already deployed and working in production
- Simple Bearer token authentication
- HTML email support

**URL**: `https://email.testservers.online/api/send`
**Auth**: `Authorization: Bearer <EMAIL_API_KEY>`

## Decision 2: Async Email Sending Pattern

**Question**: How to send emails asynchronously without blocking task operations?

### Options Evaluated

| Option | Pros | Cons | Verdict |
|--------|-------|-------|---------|
| FastAPI BackgroundTasks | Built-in, simple, async | In-process only | ✅ **Selected** |
| Dapr Pub/Sub + Worker | Scalable, decoupled | DNS issues, namespace complexity, overkill | ❌ Rejected |
| Celery + Redis | Production-grade, reliable | Additional infrastructure, complex | ❌ Rejected |
| asyncio.create_task() | Native asyncio | Less controlled, can impact event loop | ❌ Rejected |
| Queue + Worker Service | Scalable, retry logic | Additional service to manage | ❌ Rejected |

### Decision: FastAPI BackgroundTasks

**Rationale**:
- Built into FastAPI framework
- Simple API: `background_tasks.add_task(function, *args)`
- Executes after HTTP response sent
- Exception handling: failures logged but don't affect response
- No additional infrastructure
- Sufficient for current scale (~100 users)

**Implementation**:
```python
from fastapi import BackgroundTasks

@router.post("/api/tasks")
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    task = await task_crud.create_task(db, task_data, current_user.id)

    # Schedule email sending in background
    background_tasks.add_task(send_task_created_email, current_user.email, task_data)

    return task
```

## Decision 3: Email Template Strategy

**Question**: How to format HTML emails for task notifications?

### Options Evaluated

| Option | Pros | Cons | Verdict |
|--------|-------|-------|---------|
| Jinja2 Templates | Professional, reusable | Adds dependency, more files | ❌ Rejected |
| Inline HTML with f-strings | Simple, Python-native | Longer strings, harder to maintain | ✅ **Selected** |
| External Template Service | Managed, scalable | External dependency, latency | ❌ Rejected |
| Plain Text Emails | Simplest | Poor UX, no formatting | ❌ Rejected |

### Decision: Inline HTML with f-strings

**Rationale**:
- No additional dependencies
- Simple string formatting in Python
- Inline CSS for email client compatibility
- Status badges with color coding
- Responsive design with CSS media queries
- Easy to modify and test

**Template Structure**:
```python
html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .task-status {{ padding: 5px 15px; border-radius: 20px; }}
        .status-created {{ background: #d4edda; color: #155724; }}
        .status-completed {{ background: #d3f8d7; color: #155724; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Todo Task Notification</h2>
        </div>
        <div class="content">
            <h3>{task_title}</h3>
            <span class="task-status status-{task_status}">{task_status.upper()}</span>
            <p>{task_description or 'No description'}</p>
        </div>
    </div>
</body>
</html>
"""
```

## Decision 4: Error Handling Strategy

**Question**: How to handle email sending failures?

### Options Evaluated

| Option | Pros | Cons | Verdict |
|--------|-------|-------|---------|
| Log and Continue | Non-blocking, simple | Email may not be sent | ✅ **Selected** |
| Retry with Exponential Backoff | Higher delivery rate | Complex, duplicate emails risk | ❌ Rejected |
| Queue for Retry | Guaranteed delivery | Additional infrastructure | ❌ Rejected |
| Fail Task Operation | Ensures email sent | Poor UX, email not critical | ❌ Rejected |

### Decision: Log and Continue

**Rationale**:
- Email notifications are secondary, not critical
- Task operations are primary value
- Users see task CRUD success in UI immediately
- Email serves as confirmation/audit trail
- Comprehensive logging for debugging
- httpx timeout (10s) prevents hanging

**Error Handling Flow**:
```python
try:
    result = await send_email(...)
    if result:
        logger.info(f"Email sent successfully to {email}")
    else:
        logger.error(f"Failed to send email to {email}")
except Exception as e:
    logger.error(f"Email sending failed: {e}")
    traceback.print_exc()
# Never raise - always continue
```

## Decision 5: HTTP Client Choice

**Question**: Which HTTP client library for calling email API?

### Options Evaluated

| Option | Pros | Cons | Verdict |
|--------|-------|-------|---------|
| httpx | Async-first, modern, HTTP/2 | Additional dependency | ✅ **Selected** |
| requests | Popular, synchronous | Blocking, no native async | ❌ Rejected |
| aiohttp | Mature async | Lower-level API | ❌ Rejected |
| urllib (stdlib) | No dependency | Synchronous, clunky API | ❌ Rejected |

### Decision: httpx

**Rationale**:
- Async/await support matches FastAPI
- Modern, type-safe API
- HTTP/2 support
- Built-in timeout handling
- Automatic connection pooling
- Already commonly used with FastAPI

**Configuration**:
```python
import httpx

async with httpx.AsyncClient(timeout=10.0) as client:
    response = await client.post(
        EMAIL_API_URL,
        json=payload,
        headers=headers
    )
    return response.status_code == 200
```

## Decision 6: Task Event Types

**Question**: Which task events should trigger email notifications?

### Options Evaluated

| Event | Send Email? | Rationale |
|-------|-------------|-----------|
| Task Created | ✅ Yes | Confirmation, primary use case |
| Task Completed | ✅ Yes | Positive reinforcement, closure |
| Task Updated | ✅ Yes | Audit trail, change notification |
| Task Deleted | ✅ Yes | Confirmation, audit trail |
| Task Un-completed | ❌ No | Too noisy, less valuable |
| Task Viewed | ❌ No | Too frequent, low value |

### Decision: Four Event Types

**Events**:
1. `created` - New task created
2. `completed` - Task marked as complete
3. `updated` - Task title/description changed
4. `deleted` - Task removed from database

**Rationale**:
- Covers all CRUD operations
- Provides complete audit trail
- Un-completion excluded (too noisy)
- View excluded (too frequent)

## Technical Constraints

### Email API Limits
- Unknown rate limits (assume reasonable)
- 10-second timeout to prevent hanging
- No retry logic (avoid duplicates)

### Performance Targets
- Email sending: <5 seconds (95th percentile)
- Non-blocking to task operations
- Support 100 task ops/minute

### Scalability Considerations
- Current scale: ~100 users
- BackgroundTasks: In-process only
- Future: Consider queue if scale increases

## Security Considerations

### API Key Storage
- Kubernetes secret (not in code)
- Environment variable in deployment
- Bearer token authentication

### Email Content
- No sensitive data in emails
- Task titles/descriptions only (user-controlled)
- No password reset links (not requested)

## Best Practices Applied

1. **Async/Await**: Match FastAPI patterns
2. **Dependency Injection**: BackgroundTasks from FastAPI
3. **Error Handling**: Comprehensive logging, never raise
4. **Timeouts**: httpx timeout prevents hanging
5. **Logging**: Print statements for Kubernetes visibility
6. **Separation of Concerns**: Utility function for email logic
7. **Testability**: Mock httpx for unit tests

## Alternatives Not Pursued

1. **Dapr Pub/Sub with Kafka**: DNS resolution issues, too complex
2. **Email Worker Service**: Additional service to manage, namespace issues
3. **Jinja2 Templates**: Overkill for simple formatting
4. **Retry Logic**: Risk of duplicate emails
5. **Queue System**: Additional infrastructure

## References

- FastAPI BackgroundTasks: https://fastapi.tiangolo.com/tutorial/background-tasks/
- httpx Documentation: https://www.python-httpx.org/
- Email API: https://email.testservers.online/api/send
- HTML Email Best Practices: https://www.campaignmonitor.com/blog/email-design/
