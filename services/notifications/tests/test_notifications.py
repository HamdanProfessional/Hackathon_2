"""Test suite for notification service."""
import os
import asyncio
import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from httpx import AsyncClient

# Set testing environment
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ENVIRONMENT"] = "test"

from app.main import app
from app.database import engine, Base
from app.config import settings


@pytest.fixture(scope="function")
async def test_db():
    """Create test database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    """Test client for FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint returns service info."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == settings.APP_NAME
        assert data["status"] == "running"
        assert "features" in data

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == settings.APP_NAME

    @pytest.mark.asyncio
    async def test_workers_status(self, client):
        """Test workers status endpoint."""
        response = await client.get("/workers/status")
        assert response.status_code == 200
        data = response.json()
        assert "due_checker" in data
        assert "recurring_processor" in data


class TestSubscriptionEndpoints:
    """Tests for Dapr subscription endpoints."""

    @pytest.mark.asyncio
    async def test_task_created_subscription(self, client):
        """Test task-created subscription handler."""
        payload = {
            "task_id": 1,
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Test Task",
            "description": "Test description",
            "priority_id": 2,
            "due_date": "2025-12-27",
            "completed": False,
            "created_at": datetime.utcnow().isoformat()
        }

        response = await client.post("/subscribe/task-created", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["task_id"] == 1

    @pytest.mark.asyncio
    async def test_task_updated_subscription(self, client):
        """Test task-updated subscription handler."""
        payload = {
            "task_id": 1,
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Updated Task",
            "description": "Updated description",
            "priority_id": 3,
            "due_date": "2025-12-28",
            "completed": False,
            "updated_at": datetime.utcnow().isoformat()
        }

        response = await client.post("/subscribe/task-updated", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"

    @pytest.mark.asyncio
    async def test_task_completed_subscription(self, client):
        """Test task-completed subscription handler."""
        payload = {
            "task_id": 1,
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "completed": True,
            "completed_at": datetime.utcnow().isoformat()
        }

        response = await client.post("/subscribe/task-completed", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"

    @pytest.mark.asyncio
    async def test_task_deleted_subscription(self, client):
        """Test task-deleted subscription handler."""
        payload = {
            "task_id": 1,
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "deleted_at": datetime.utcnow().isoformat()
        }

        response = await client.post("/subscribe/task-deleted", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"

    @pytest.mark.asyncio
    async def test_task_due_soon_subscription(self, client):
        """Test task-due-soon subscription handler."""
        payload = {
            "task_id": 1,
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Due Task",
            "due_date": "2025-12-27",
            "hours_until_due": 12
        }

        response = await client.post("/subscribe/task-due-soon", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"

    @pytest.mark.asyncio
    async def test_recurring_task_due_subscription(self, client):
        """Test recurring-task-due subscription handler."""
        payload = {
            "recurring_task_id": 1,
            "task_id": 10,
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Recurring Task",
            "next_due_at": "2025-12-27",
            "recurrence_pattern": "daily"
        }

        response = await client.post("/subscribe/recurring-task-due", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"


class TestNotificationService:
    """Tests for notification service."""

    @pytest.mark.asyncio
    async def test_send_email_disabled(self):
        """Test email sending when disabled."""
        from app.services.notification import notification_service

        # Ensure email is disabled
        notification_service.email_enabled = False

        result = await notification_service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_body="<h1>Test</h1>",
            text_body="Test"
        )

        # Should return False when disabled
        assert result is False

    @pytest.mark.asyncio
    async def test_send_task_due_notification(self):
        """Test task due notification."""
        from app.services.notification import notification_service

        # Mock the send_email method
        with patch.object(notification_service, 'send_email', return_value=True) as mock_send:
            result = await notification_service.send_task_due_notification(
                user_email="test@example.com",
                user_name="Test User",
                task_title="Test Task",
                task_description="Test Description",
                due_date=date.today() + timedelta(days=1),
                hours_until_due=24,
                task_id=1
            )

            # Verify send_email was called
            mock_send.assert_called_once()
            # Extract args from the call
            args, kwargs = mock_send.call_args
            assert args[0] == "test@example.com"
            assert "Task Due Soon" in args[1]

    @pytest.mark.asyncio
    async def test_send_recurring_task_notification(self):
        """Test recurring task notification."""
        from app.services.notification import notification_service

        # Mock the send_email method
        with patch.object(notification_service, 'send_email', return_value=True) as mock_send:
            result = await notification_service.send_recurring_task_notification(
                user_email="test@example.com",
                user_name="Test User",
                task_title="Recurring Task",
                recurrence_pattern="daily",
                next_due_date=date.today() + timedelta(days=1)
            )

            # Verify send_email was called
            mock_send.assert_called_once()
            args, kwargs = mock_send.call_args
            assert args[0] == "test@example.com"
            assert "Recurring Task" in args[1]


class TestDueChecker:
    """Tests for due date checker worker."""

    @pytest.mark.asyncio
    async def test_calculate_next_due_date_daily(self):
        """Test next due date calculation for daily pattern."""
        from app.workers.recurring_processor import calculate_next_due_date

        current = date(2025, 12, 26)
        next_due = calculate_next_due_date(current, "daily")

        assert next_due == date(2025, 12, 27)

    @pytest.mark.asyncio
    async def test_calculate_next_due_date_weekly(self):
        """Test next due date calculation for weekly pattern."""
        from app.workers.recurring_processor import calculate_next_due_date

        current = date(2025, 12, 26)
        next_due = calculate_next_due_date(current, "weekly")

        assert next_due == date(2026, 1, 2)

    @pytest.mark.asyncio
    async def test_calculate_next_due_date_monthly(self):
        """Test next due date calculation for monthly pattern."""
        from app.workers.recurring_processor import calculate_next_due_date

        current = date(2025, 12, 26)
        next_due = calculate_next_due_date(current, "monthly")

        assert next_due == date(2026, 1, 26)

    @pytest.mark.asyncio
    async def test_calculate_next_due_date_yearly(self):
        """Test next due date calculation for yearly pattern."""
        from app.workers.recurring_processor import calculate_next_due_date

        current = date(2025, 12, 26)
        next_due = calculate_next_due_date(current, "yearly")

        assert next_due == date(2026, 12, 26)

    @pytest.mark.asyncio
    async def test_calculate_next_due_date_leap_year(self):
        """Test next due date calculation handles leap years."""
        from app.workers.recurring_processor import calculate_next_due_date

        # Feb 29 in a leap year
        current = date(2024, 2, 29)
        next_due = calculate_next_due_date(current, "yearly")

        # Should handle non-leap year by moving to Feb 28
        assert next_due == date(2025, 2, 28)


class TestConfiguration:
    """Tests for configuration settings."""

    def test_settings_loaded(self):
        """Test settings are loaded correctly."""
        assert settings.APP_NAME == "Notification Service"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.ENVIRONMENT == "test"

    def test_dapr_settings(self):
        """Test Dapr settings are configured."""
        assert settings.DAPR_HTTP_HOST == "localhost"
        assert settings.DAPR_HTTP_PORT == "3500"
        assert settings.DAPR_PUBSUB_NAME == "todo-pubsub"

    def test_worker_settings(self):
        """Test worker settings are configured."""
        assert settings.DUE_CHECK_INTERVAL_SECONDS == 3600
        assert settings.RECURRING_CHECK_INTERVAL_SECONDS == 3600
        assert settings.DUE_THRESHOLD_HOURS == 24
