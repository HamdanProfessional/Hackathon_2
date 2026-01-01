# Email Notification Testing Guide

## Overview

This guide covers testing strategies for the email notification system, including unit tests, integration tests, and end-to-end testing.

## Test Environment Setup

### Prerequisites

1. **Email Service**
   - Valid EMAIL_KEY
   - IP whitelisted for email API

2. **Database**
   - Test database with sample users
   - User email: `test@example.com`

3. **Dapr**
   - Dapr sidecar running
   - Pub/sub component configured

### Test Configuration

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def test_user(db):
    return {
        "id": "test-user-uuid",
        "email": "test@example.com",
        "name": "Test User"
    }

@pytest.fixture
def test_task():
    return {
        "id": "test-task-uuid",
        "user_id": "test-user-uuid",
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high",
        "due_date": "2025-12-27T10:00:00Z"
    }
```

## Unit Tests

### Email Service Tests

```python
# tests/test_email_service.py
import pytest
from app.email_service import EmailService

class TestEmailService:
    @pytest.fixture
    def email_service(self):
        return EmailService()

    @pytest.mark.asyncio
    async def test_send_email_success(self, email_service, mocker):
        """Test successful email sending."""
        # Mock HTTP client
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mocker.patch("httpx.AsyncClient.post", return_value=mock_response)

        result = await email_service.send_email(
            subject="Test Subject",
            email=["test@example.com"],
            body="Test Body"
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_email_failure(self, email_service, mocker):
        """Test email sending failure."""
        mock_response = mocker.Mock()
        mock_response.status_code = 500
        mocker.patch("httpx.AsyncClient.post", return_value=mock_response)

        result = await email_service.send_email(
            subject="Test Subject",
            email=["test@example.com"],
            body="Test Body"
        )

        assert result is False

    def test_render_template(self, email_service):
        """Test template rendering."""
        html = email_service.render_template(
            "task-crud.html",
            {"title": "Test Task", "action": "created"}
        )

        assert "Test Task" in html
        assert "created" in html
        assert "<html>" in html
```

### Subscriber Handler Tests

```python
# tests/test_subscribers.py
import pytest
from app.subscribers import handle_task_created_event

@pytest.mark.asyncio
async def test_task_created_handler(mocker, test_task, test_user):
    """Test task created event handler."""
    # Mock database
    mock_db = mocker.AsyncMock()
    mock_get_user = mocker.patch("app.subscribers.get_user_by_id")
    mock_get_user.return_value = test_user

    # Mock email service
    mock_send_email = mocker.patch("app.subscribers.email_service.send_template_email")
    mock_send_email.return_value = True

    # Execute handler
    await handle_task_created_event(test_task)

    # Verify email was sent
    mock_send_email.assert_called_once()
    call_args = mock_send_email.call_args
    assert call_args[1]["email"] == [test_user["email"]]
    assert "Task Created:" in call_args[1]["subject"]

@pytest.mark.asyncio
async def test_task_created_handler_user_not_found(mocker, test_task):
    """Test handler when user not found."""
    mock_get_user = mocker.patch("app.subscribers.get_user_by_id")
    mock_get_user.return_value = None

    mock_send_email = mocker.patch("app.subscribers.email_service.send_template_email")

    # Execute handler
    await handle_task_created_event(test_task)

    # Verify email was NOT sent
    mock_send_email.assert_not_called()
```

### Template Tests

```python
# tests/test_templates.py
import pytest
from app.email_service import EmailService

class TestEmailTemplates:
    @pytest.fixture
    def email_service(self):
        return EmailService()

    def test_task_created_template(self, email_service):
        """Test task created email template."""
        html = email_service.render_template(
            "task-crud.html",
            {
                "title": "Complete Project",
                "description": "Finish the implementation",
                "priority": "High",
                "due_date": "December 27, 2025",
                "app_url": "https://hackathon2.testservers.online",
                "action": "created"
            }
        )

        # Verify content
        assert "Complete Project" in html
        assert "Finish the implementation" in html
        assert "High" in html
        assert "December 27, 2025" in html
        assert "Task Created" in html

        # Verify styling
        assert "action-created" in html
        assert "gradient" in html.lower()

    def test_task_completed_template(self, email_service):
        """Test task completed email template."""
        html = email_service.render_template(
            "task-crud.html",
            {
                "title": "Complete Project",
                "app_url": "https://hackathon2.testservers.online",
                "action": "completed"
            }
        )

        # Verify completion message
        assert "Great job!" in html
        assert "completed" in html.lower()
        assert "action-completed" in html

    def test_task_deleted_template(self, email_service):
        """Test task deleted email template."""
        html = email_service.render_template(
            "task-crud.html",
            {
                "title": "Deleted Task",
                "app_url": "https://hackathon2.testservers.online",
                "action": "deleted"
            }
        )

        # Verify deletion message
        assert "permanently deleted" in html
        assert "action-deleted" in html
```

## Integration Tests

### End-to-End Event Flow Test

```python
# tests/test_integration.py
import pytest
import asyncio
from dapr.clients import DaprClient

class TestEmailIntegration:
    @pytest.mark.asyncio
    async def test_task_created_email_flow(self, test_task, test_user):
        """Complete flow from event publish to email send."""
        # 1. Publish event via Dapr
        with DaprClient() as dapr:
            dapr.publish_event(
                pubsub_name="todo-pubsub",
                topic_name="task-created",
                data=test_task
            )

        # 2. Wait for async processing
        await asyncio.sleep(3)

        # 3. Verify email was sent (check logs or mock)
        # In real test, use test email service or check SMTP server
        assert email_received(test_user["email"], "Task Created:")

    @pytest.mark.asyncio
    async def test_all_task_events(self):
        """Test all task lifecycle events."""
        events = [
            ("task-created", "Task Created:"),
            ("task-updated", "Task Updated:"),
            ("task-completed", "Task Completed:"),
            ("task-deleted", "Task Deleted:")
        ]

        for topic, subject_prefix in events:
            with DaprClient() as dapr:
                dapr.publish_event(
                    pubsub_name="todo-pubsub",
                    topic_name=topic,
                    data=self.test_task
                )

            await asyncio.sleep(2)
            assert email_received(test_user["email"], subject_prefix)
```

### Dapr Subscription Test

```python
# tests/test_dapr_subscription.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_dapr_subscribe_endpoint():
    """Test Dapr subscription endpoint."""
    async with AsyncClient(base_url="http://localhost:8003") as client:
        response = await client.get("/dapr/subscribe")

    assert response.status_code == 200
    data = response.json()
    assert "subscriptions" in data

    subscriptions = data["subscriptions"]
    topics = [s["topic"] for s in subscriptions]

    expected_topics = [
        "task-created",
        "task-updated",
        "task-completed",
        "task-deleted",
        "task-due-soon",
        "recurring-task-due"
    ]

    for topic in expected_topics:
        assert topic in topics
```

## Manual Testing

### Test Email Endpoint

```bash
# Test email endpoint directly
curl https://api.testservers.online/test-email
```

Expected response:
```json
{
  "status": "success",
  "message": "Test email sent successfully to n00bi2761@gmail.com",
  "timestamp": "2025-12-27T10:00:00"
}
```

### Task CRUD Email Test

```bash
# 1. Create a task (should send "Task Created" email)
curl -X POST https://api.testservers.online/api/tasks \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Email Test Task",
    "description": "Testing email notifications",
    "priority": "high"
  }'

# 2. Update the task (should send "Task Updated" email)
curl -X PATCH https://api.testservers.online/api/tasks/{TASK_ID} \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Email Test Task"}'

# 3. Complete the task (should send "Task Completed" email)
curl -X PATCH https://api.testservers.online/api/tasks/{TASK_ID} \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# 4. Delete the task (should send "Task Deleted" email)
curl -X DELETE https://api.testservers.online/api/tasks/{TASK_ID} \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### Email Verification

Check inbox at `n00bi2761@gmail.com` for:

1. **Task Created Email**
   - Subject: "Task Created: Email Test Task"
   - Green badge: "Task Created"
   - Task details visible

2. **Task Updated Email**
   - Subject: "Task Updated: Updated Email Test Task"
   - Blue badge: "Task Updated"
   - Updated details visible

3. **Task Completed Email**
   - Subject: "Task Completed: Updated Email Test Task"
   - Yellow badge: "Task Completed"
   - "Great job! 🎉" message

4. **Task Deleted Email**
   - Subject: "Task Deleted: Updated Email Test Task"
   - Red badge: "Task Deleted"
   - "Permanently deleted" message

## Performance Testing

### Load Test

```python
# tests/test_performance.py
import pytest
import time
from dapr.clients import DaprClient

class TestEmailPerformance:
    @pytest.mark.asyncio
    async def test_bulk_task_creation(self):
        """Test email worker performance under load."""
        start_time = time.time()

        # Publish 100 task-created events
        with DaprClient() as dapr:
            for i in range(100):
                dapr.publish_event(
                    pubsub_name="todo-pubsub",
                    topic_name="task-created",
                    data={
                        "task_id": f"test-task-{i}",
                        "user_id": "test-user-uuid",
                        "title": f"Test Task {i}",
                        "description": "Performance test"
                    }
                )

        # Wait for processing
        await asyncio.sleep(30)

        # Should complete within 30 seconds
        assert time.time() - start_time < 30
```

## Test Execution

### Run All Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_email_service.py -v

# Run specific test
pytest tests/test_email_service.py::TestEmailService::test_send_email_success -v
```

### Run Tests in Docker

```bash
# Build test image
docker build -t email-worker:test -f Dockerfile.test .

# Run tests
docker run email-worker-test pytest tests/ -v
```

## Test Coverage Goals

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| Email Service | 90% | TBD |
| Subscribers | 85% | TBD |
| Templates | 80% | TBD |
| Configuration | 70% | TBD |

## Troubleshooting Tests

### Common Test Failures

1. **Email API Timeout**
   - Increase timeout in test config
   - Check network connectivity

2. **Database Connection Failed**
   - Ensure test database is running
   - Check DATABASE_URL in test environment

3. **Dapr Not Available**
   - Start Dapr sidecar in test environment
   - Verify Dapr configuration

4. **Assertion Errors**
   - Verify test data matches expected format
   - Check template rendering output

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test-email-worker.yml
name: Test Email Worker

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      - name: Run tests
        run: pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```
