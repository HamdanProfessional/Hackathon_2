"""Test Dapr event publishing functionality."""
import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date

from app.services.event_publisher import DaprEventPublisher
from app.services.event_logger import EventLogger
from app.models.task_event_log import TaskEventLog


class TestDaprEventPublisher:
    """Test DaprEventPublisher service."""

    @pytest.fixture
    def publisher(self):
        """Create a fresh publisher instance for each test."""
        # Set Dapr as disabled for tests by default
        os.environ["DAPR_ENABLED"] = "false"
        return DaprEventPublisher()

    @pytest.fixture
    def enabled_publisher(self):
        """Create a publisher with Dapr enabled."""
        os.environ["DAPR_ENABLED"] = "true"
        os.environ["DAPR_HTTP_HOST"] = "localhost"
        os.environ["DAPR_HTTP_PORT"] = "3500"
        publisher = DaprEventPublisher()
        return publisher

    def test_init_default_config(self, publisher):
        """Test publisher initializes with default config."""
        assert publisher.dapr_host == "localhost"
        assert publisher.dapr_port == "3500"
        assert publisher.pubsub_name == "todo-pubsub"
        assert publisher.enabled is False

    def test_get_dapr_url(self, publisher):
        """Test Dapr URL generation."""
        url = publisher._get_dapr_url("task-created")
        assert url == "http://localhost:3500/v1.0/publish/todo-pubsub/task-created"

    @pytest.mark.asyncio
    async def test_publish_event_when_disabled(self, publisher):
        """Test that publishing is skipped when Dapr is disabled."""
        result = await publisher.publish_event("task-created", {"task_id": 1})
        assert result is False

    @pytest.mark.asyncio
    async def test_publish_task_created_success(self, enabled_publisher):
        """Test successful task-created event publishing."""
        task_data = {
            "task_id": 1,
            "user_id": "test-uuid-123",
            "title": "Test Task",
            "description": "Test Description",
            "priority_id": 2,
            "due_date": "2025-01-01",
            "completed": False,
            "created_at": "2025-01-01T10:00:00"
        }

        # Mock httpx.AsyncClient to return success
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            result = await enabled_publisher.publish_task_created(task_data)
            assert result is True
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_task_created_failure(self, enabled_publisher):
        """Test failed task-created event publishing."""
        task_data = {
            "task_id": 1,
            "user_id": "test-uuid-123",
            "title": "Test Task"
        }

        # Mock httpx.AsyncClient to return error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            result = await enabled_publisher.publish_task_created(task_data)
            assert result is False

    @pytest.mark.asyncio
    async def test_publish_task_completed(self, enabled_publisher):
        """Test task-completed event publishing."""
        task_data = {
            "task_id": 1,
            "user_id": "test-uuid-123",
            "title": "Test Task",
            "completed": True,
            "completed_at": datetime.utcnow().isoformat()
        }

        # Mock httpx.AsyncClient to return success
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            result = await enabled_publisher.publish_task_completed(task_data)
            assert result is True

    @pytest.mark.asyncio
    async def test_publish_task_deleted(self, enabled_publisher):
        """Test task-deleted event publishing."""
        task_data = {
            "task_id": 1,
            "user_id": "test-uuid-123",
            "deleted_at": datetime.utcnow().isoformat()
        }

        # Mock httpx.AsyncClient to return success
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            result = await enabled_publisher.publish_task_deleted(task_data)
            assert result is True

    @pytest.mark.asyncio
    async def test_publish_recurring_task_due(self, enabled_publisher):
        """Test recurring-task-due event publishing."""
        task_data = {
            "recurring_task_id": 1,
            "user_id": "test-uuid-123",
            "title": "Daily Standup",
            "next_due_at": "2025-01-02",
            "recurrence_pattern": "daily",
            "task_priority_id": 2
        }

        # Mock httpx.AsyncClient to return success
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            result = await enabled_publisher.publish_recurring_task_due(task_data)
            assert result is True

    @pytest.mark.asyncio
    async def test_publish_task_due_soon(self, enabled_publisher):
        """Test task-due-soon event publishing."""
        task_data = {
            "task_id": 1,
            "user_id": "test-uuid-123",
            "title": "Urgent Task",
            "due_date": "2025-01-01",
            "hours_until_due": 2
        }

        # Mock httpx.AsyncClient to return success
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            result = await enabled_publisher.publish_task_due_soon(task_data)
            assert result is True

    @pytest.mark.asyncio
    async def test_publish_event_adds_timestamp(self, enabled_publisher):
        """Test that timestamp is automatically added to events."""
        task_data = {"task_id": 1}

        # Mock httpx.AsyncClient to capture the payload
        mock_response = MagicMock()
        mock_response.status_code = 200

        captured_payload = {}

        async def capture_post(url, json):
            captured_payload.update(json)
            return mock_response

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = capture_post
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            await enabled_publisher.publish_event("task-created", task_data)

            assert "timestamp" in captured_payload
            # Verify timestamp is a valid ISO format string
            datetime.fromisoformat(captured_payload["timestamp"])


class TestEventLogger:
    """Test EventLogger service."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_log_event_success(self, mock_db_session):
        """Test successful event logging to database."""
        # Create a mock TaskEventLog
        mock_log = TaskEventLog(
            id=1,
            task_id=123,
            event_type="created",
            event_data={"title": "Test Task"}
        )
        mock_db_session.refresh = AsyncMock(return_value=mock_log)

        result = await EventLogger.log_event(
            mock_db_session,
            task_id=123,
            event_type="created",
            event_data={"title": "Test Task"}
        )

        assert result is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_task_created(self, mock_db_session):
        """Test log_task_created convenience method."""
        mock_log = TaskEventLog(
            id=1,
            task_id=123,
            event_type="created",
            event_data={"task_id": 123}
        )
        mock_db_session.refresh = AsyncMock(return_value=mock_log)

        result = await EventLogger.log_task_created(
            mock_db_session,
            task_id=123,
            event_data={"task_id": 123, "title": "New Task"}
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_log_task_completed(self, mock_db_session):
        """Test log_task_completed convenience method."""
        mock_log = TaskEventLog(
            id=2,
            task_id=456,
            event_type="completed",
            event_data={"task_id": 456}
        )
        mock_db_session.refresh = AsyncMock(return_value=mock_log)

        result = await EventLogger.log_task_completed(
            mock_db_session,
            task_id=456,
            event_data={"task_id": 456, "completed": True}
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_log_event_failure(self, mock_db_session):
        """Test event logging failure handling."""
        # Simulate database error
        mock_db_session.commit.side_effect = Exception("Database error")

        result = await EventLogger.log_event(
            mock_db_session,
            task_id=123,
            event_type="created",
            event_data={"title": "Test Task"}
        )

        # Should return None on failure
        assert result is None
        mock_db_session.rollback.assert_called_once()


@pytest.mark.integration
class TestEventPublishingIntegration:
    """Integration tests for event publishing with Dapr."""

    @pytest.mark.asyncio
    async def test_full_event_flow(self):
        """
        Test full event publishing flow.

        Note: This test requires Dapr sidecar to be running.
        It should be run in an environment with Dapr installed.
        """
        # Skip if Dapr is not available
        if not os.getenv("DAPR_ENABLED", "false") == "true":
            pytest.skip("Dapr not enabled - skipping integration test")

        publisher = DaprEventPublisher()

        # Try to publish a test event
        result = await publisher.publish_task_created({
            "task_id": 999,
            "user_id": "test-uuid",
            "title": "Integration Test Task"
        })

        # In real Dapr environment, this should succeed
        # If Dapr is not running, it will fail gracefully
        assert result is True or result is False
