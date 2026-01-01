# Data Model: Email Notification System

**Feature**: 006-fix-email
**Date**: 2025-12-27
**Purpose**: Define data structures for email notification system

## Overview

The email notification system uses existing data models from the Todo application and introduces new data structures for email events and templates. No new database tables are required - all email data is derived from existing Task and User models.

## Existing Models Used

### User Model

**Location**: `backend/app/models/user.py`

```python
class User(Base):
    __tablename__ = "users"

    id: UUID  # Primary key
    email: str  # Email address for notifications
    name: str  # User display name
    hashed_password: str  # Authentication
    created_at: datetime
```

**Usage**: User.email is the recipient address for all task notifications.

### Task Model

**Location**: `backend/app/models/task.py`

```python
class Task(Base):
    __tablename__ = "tasks"

    id: int  # Primary key
    user_id: UUID  # Foreign key to users
    title: str  # Task title
    description: Optional[str]  # Task description
    priority_id: Optional[int]  # Priority level
    due_date: Optional[datetime]  # Due date
    completed: bool  # Completion status
    is_recurring: bool  # Recurring task flag
    recurrence_pattern: Optional[str]  # Recurrence pattern
    created_at: datetime  # Creation timestamp
    updated_at: datetime  # Last update timestamp
```

**Usage**: Task data is included in email notifications for context.

## New Data Structures

### Email Notification Event

**Type**: Dictionary (in-memory, not persisted)

```python
EmailNotificationEvent = {
    "event_type": "created" | "updated" | "completed" | "deleted",
    "user_email": str,
    "task_data": {
        "task_id": int,
        "user_id": str,  # UUID as string
        "title": str,
        "description": Optional[str],
        "priority_id": Optional[int],
        "due_date": Optional[str],  # ISO format
        "completed": bool,
        "is_recurring": bool,
        "recurrence_pattern": Optional[str],
        "created_at": Optional[str],  # ISO format
        "updated_at": Optional[str]  # ISO format
    }
}
```

**Purpose**: Data structure passed to email sending functions.

**Creation**: Converted from Task model via `_task_to_dict()` function:

```python
def _task_to_dict(task) -> Dict[str, Any]:
    return {
        "task_id": task.id,
        "user_id": str(task.user_id),
        "title": task.title,
        "description": task.description,
        "priority_id": task.priority_id,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "completed": task.completed,
        "is_recurring": task.is_recurring,
        "recurrence_pattern": task.recurrence_pattern,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }
```

### Email API Request

**Type**: Dictionary for HTTP POST to email API

```python
EmailApiRequest = {
    "to": str,  # Recipient email address
    "is_html": bool,  # True for HTML email
    "subject": str,  # Email subject line
    "body": str  # HTML email content
}
```

**Usage**: Sent to `https://email.testservers.online/api/send`

**Example**:
```python
{
    "to": "n00bi2761@gmail.com",
    "is_html": True,
    "subject": "Task Created: Buy groceries",
    "body": "<!DOCTYPE html>..."
}
```

### Email Template Context

**Type**: Dictionary for template string formatting

```python
EmailTemplateContext = {
    "task_title": str,
    "task_description": str,
    "task_status": str,  # "created" | "updated" | "completed" | "deleted"
    "app_url": str  # "https://hackathon2.testservers.online"
}
```

**Usage**: Variables injected into HTML email template.

### HTML Email Template Structure

**Type**: Multi-line Python string with f-string formatting

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        /* CSS for email client compatibility */
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
        .task-title {{ font-size: 24px; font-weight: bold; margin: 0 0 10px 0; }}
        .task-status {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 14px; font-weight: bold; }}
        .status-created {{ background: #d4edda; color: #155724; }}
        .status-updated {{ background: #fff3cd; color: #856404; }}
        .status-completed {{ background: #d3f8d7; color: #155724; }}
        .status-deleted {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Todo Task Notification</h2>
        </div>
        <div class="content">
            <h3 class="task-title">{task_title}</h3>
            <p><span class="task-status status-{task_status}">Status: {task_status.upper()}</span></p>
            {task_description}
            <p><strong>View your tasks:</strong> <a href="{app_url}">{app_url}</a></p>
        </div>
    </div>
</body>
</html>
```

## Data Flow

### 1. Task Created Event

```
Task Model (DB)
    ↓
_task_to_dict(task)
    ↓
EmailNotificationEvent
    ↓
send_task_created_email(user_email, event_data)
    ↓
EmailApiRequest
    ↓
Email API (HTTP POST)
    ↓
User Inbox (n00bi2761@gmail.com)
```

### 2. Task Completed Event

```
Task Model (DB)
    ↓
toggle_task_completion()
    ↓
_task_to_dict(updated_task)
    ↓
EmailNotificationEvent (event_type: "completed")
    ↓
send_task_completed_email(user_email, event_data)
    ↓
EmailApiRequest (subject: "Task Completed: ...")
    ↓
Email API (HTTP POST)
    ↓
User Inbox (congratulatory email)
```

## State Transitions

### Task Completion Email Condition

```python
if updated_task.completed:
    # Send completion email
    background_tasks.add_task(_send_email_notification, "completed", task_dict, current_user.email)
```

**Logic**: Only send completion email when task transitions to completed state. No email when un-completing.

### Event Type Mapping

| Task Operation | Event Type | Email Subject |
|----------------|------------|---------------|
| POST /api/tasks | `created` | "Task Created: {title}" |
| PUT /api/tasks/{id} | `updated` | "Task Updated: {title}" |
| PATCH /api/tasks/{id}/complete | `completed` | "Task Completed: {title}" |
| DELETE /api/tasks/{id} | `deleted` | "Task Deleted: {title}" |

## Validation Rules

### Email Validation
- User.email must be present (required during registration)
- Email format validated by SQLAlchemy schema
- No additional validation required (email API handles invalid emails)

### Task Data Validation
- Task title: Required, max 500 characters
- Task description: Optional, max 10000 characters
- All datetime fields converted to ISO format strings
- UUID converted to string for JSON serialization

## Error States

### Email Sending Failure

**State**: Email API returns non-200 status

**Handling**:
- Log error message
- Log HTTP status code
- Log response body
- DO NOT raise exception
- Task operation succeeds regardless

**Example**:
```python
if response.status_code == 200:
    logger.info(f"Email sent successfully to {email}")
else:
    logger.error(f"Failed to send email: {response.status_code} - {response.text}")
```

## Performance Considerations

### Memory Usage
- Email event dict: ~1KB per task
- HTML template: ~2KB per email
- No persistence - garbage collected after send

### Network I/O
- HTTP POST to email API: ~10ms (local), ~500ms (remote)
- Timeout: 10 seconds
- Async execution: doesn't block response

### Concurrency
- BackgroundTasks executes in same process
- No thread safety issues (separate task per email)
- No connection pooling needed (httpx handles this)

## Security Considerations

### API Key Storage
- Stored as Kubernetes secret
- Environment variable: `EMAIL_API_KEY`
- Never logged or exposed in error messages

### Email Content
- No sensitive data in emails
- No password reset links
- Task titles/descriptions only (user-controlled content)
- Sanitized by email API

## Future Extensions

### Potential Additional Fields
```python
EmailNotificationEvent = {
    # Current fields
    "event_type": str,
    "user_email": str,
    "task_data": Dict,

    # Potential future fields
    "priority": str,  # "High" | "Medium" | "Low"
    "due_date": str,  # Formatted due date
    "tags": List[str],  # Task tags
    "recurrence_info": str,  # Recurrence pattern description
}
```

### Potential Email Enhancements
- Task priority badges
- Due date warnings
- Recurrence information
- Task tags/categories
- Direct task action links

## References

- User Model: `backend/app/models/user.py`
- Task Model: `backend/app/models/task.py`
- Email Utility: `backend/app/utils/email_notifier.py`
- Task API: `backend/app/api/tasks.py`
