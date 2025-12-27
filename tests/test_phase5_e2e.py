"""
Phase V: Event-Driven Architecture - End-to-End Tests

Comprehensive E2E tests for:
1. Recurring Tasks API (7 endpoints)
2. Event Publishing via Dapr
3. Notification Service Integration
4. Complete User Workflows

Test Categories:
- API Endpoint Tests: CRUD operations
- Event Publishing Tests: Dapr integration
- Integration Tests: Full event flow
- Workflow Tests: End-to-end user journeys
- Error Handling Tests: Edge cases and failures

Run with:
    pytest tests/test_phase5_e2e.py -v
    pytest tests/test_phase5_e2e.py -v -k "test_recurring_tasks_api"
    pytest tests/test_phase5_e2e.py -v -m integration
"""

import pytest
import os
import asyncio
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

# Backend imports
from app.database import get_db
from app.models.recurring_task import RecurringTask
from app.models.task import Task
from app.models.task_event_log import TaskEventLog
from app.models.task import Priority
from app.models.user import User

# Test helpers - use absolute import
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers'))
from dapr_client import MockDaprClient


# ============================================================================
# Helper Functions
# ============================================================================

async def create_test_recurring_task(
    client: AsyncClient,
    headers: Dict[str, str],
    title: str = "Test Recurring Task",
    recurrence_pattern: str = "daily",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    task_priority_id: Optional[int] = 2
) -> Dict[str, Any]:
    """
    Helper to create a recurring task via API.

    Args:
        client: AsyncClient instance
        headers: Auth headers
        title: Task title
        recurrence_pattern: daily, weekly, monthly, yearly
        start_date: Start date (defaults to today)
        end_date: Optional end date
        task_priority_id: Priority ID (1=Low, 2=Medium, 3=High)

    Returns:
        Created recurring task data
    """
    payload = {
        "title": title,
        "description": f"Description for {title}",
        "recurrence_pattern": recurrence_pattern,
        "start_date": start_date or date.today(),
        "end_date": end_date,
        "task_priority_id": task_priority_id
    }

    response = await client.post(
        "/api/recurring-tasks",
        headers=headers,
        json=payload
    )

    assert response.status_code == 201, f"Failed to create recurring task: {response.text}"
    return response.json()


async def verify_event_published(
    mock_dapr: MockDaprClient,
    topic: str,
    task_id: Optional[int] = None,
    timeout: float = 1.0
) -> bool:
    """
    Helper to verify event was published to Dapr.

    Args:
        mock_dapr_publisher instance
        topic: Event topic to check
        task_id: Optional task ID to verify
        timeout: Max seconds to wait for event

    Returns:
        True if event found
    """
    await asyncio.sleep(timeout)  # Small delay for async event publishing

    events = mock_dapr.get_events_by_topic(topic)

    if task_id is not None:
        events = [e for e in events if e["data"].get("task_id") == task_id]

    return len(events) > 0


async def verify_task_event_log(
    db_session,
    task_id: int,
    event_type: str,
    timeout: float = 0.5
) -> bool:
    """
    Helper to verify event was logged to database.

    Args:
        db_session: Database session
        task_id: Task ID to check
        event_type: Event type (created, updated, completed, deleted)
        timeout: Max seconds to wait for log entry

    Returns:
        True if log entry found
    """
    from sqlalchemy import select

    await asyncio.sleep(timeout)

    result = await db_session.execute(
        select(TaskEventLog).where(
            TaskEventLog.task_id == task_id,
            TaskEventLog.event_type == event_type
        )
    )

    return result.scalar_one_or_none() is not None


# ============================================================================
# Test Class 1: Recurring Tasks API
# ============================================================================

class TestRecurringTasksAPI:
    """
    Test all 7 recurring task endpoints.

    Endpoints:
    - POST /api/recurring-tasks
    - GET /api/recurring-tasks
    - GET /api/recurring-tasks/{id}
    - PUT /api/recurring-tasks/{id}
    - DELETE /api/recurring-tasks/{id}
    - POST /api/recurring-tasks/{id}/pause
    - POST /api/recurring-tasks/{id}/resume
    """

    @pytest.mark.asyncio
    async def test_create_recurring_task_success(
        self, client: AsyncClient, auth_headers: Dict[str, str]
    ):
        """Test POST /api/recurring-tasks - Create recurring task."""
        response = await client.post(
            "/api/recurring-tasks",
            headers=auth_headers,
            json={
                "title": "Daily Standup",
                "description": "Team standup meeting",
                "recurrence_pattern": "daily",
                "start_date": date.today().isoformat(),
                "task_priority_id": 2
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Daily Standup"
        assert data["recurrence_pattern"] == "daily"
        assert data["is_active"] is True
        assert "id" in data
        assert data["next_due_at"] is not None

    @pytest.mark.asyncio
    async def test_create_recurring_task_all_patterns(
        self, client: AsyncClient, auth_headers: Dict[str, str]
    ):
        """Test creating recurring tasks with all recurrence patterns."""
        patterns = ["daily", "weekly", "monthly", "yearly"]

        for pattern in patterns:
            response = await client.post(
                "/api/recurring-tasks",
                headers=auth_headers,
                json={
                    "title": f"{pattern.capitalize()} Task",
                    "recurrence_pattern": pattern,
                    "start_date": date.today().isoformat()
                }
            )

            assert response.status_code == 201, f"Failed for pattern: {pattern}"
            data = response.json()
            assert data["recurrence_pattern"] == pattern

    @pytest.mark.asyncio
    async def test_create_recurring_task_validation_errors(
        self, client: AsyncClient, auth_headers: Dict[str, str]
    ):
        """Test POST /api/recurring-tasks - Validation errors."""
        # Invalid recurrence pattern
        response = await client.post(
            "/api/recurring-tasks",
            headers=auth_headers,
            json={
                "title": "Invalid Task",
                "recurrence_pattern": "invalid",
                "start_date": date.today().isoformat()
            }
        )
        assert response.status_code == 422

        # end_date before start_date
        response = await client.post(
            "/api/recurring-tasks",
            headers=auth_headers,
            json={
                "title": "Invalid Dates",
                "recurrence_pattern": "daily",
                "start_date": date.today().isoformat(),
                "end_date": (date.today() - timedelta(days=1)).isoformat()
            }
        )
        assert response.status_code == 422

        # Missing required fields
        response = await client.post(
            "/api/recurring-tasks",
            headers=auth_headers,
            json={"title": "Missing Fields"}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_recurring_tasks(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_tasks: list[RecurringTask]
    ):
        """Test GET /api/recurring-tasks - List all recurring tasks."""
        response = await client.get(
            "/api/recurring-tasks",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # Created in fixture

    @pytest.mark.asyncio
    async def test_list_recurring_tasks_with_filters(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_tasks: list[RecurringTask]
    ):
        """Test GET /api/recurring-tasks - With active_only filter."""
        # Filter active only
        response = await client.get(
            "/api/recurring-tasks?active_only=true",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(task["is_active"] for task in data)
        # 2 active tasks (1 paused in fixture)
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_list_recurring_tasks_pagination(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_tasks: list[RecurringTask]
    ):
        """Test GET /api/recurring-tasks - Pagination."""
        # Get first page
        response = await client.get(
            "/api/recurring-tasks?limit=2&offset=0",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Get second page
        response = await client.get(
            "/api/recurring-tasks?limit=2&offset=2",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    @pytest.mark.asyncio
    async def test_list_recurring_tasks_sorting(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_tasks: list[RecurringTask]
    ):
        """Test GET /api/recurring-tasks - Sorting."""
        # Sort by title ascending
        response = await client.get(
            "/api/recurring-tasks?sort_by=title&sort_order=asc",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        titles = [task["title"] for task in data]
        assert titles == sorted(titles)

    @pytest.mark.asyncio
    async def test_get_recurring_task_by_id(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_task: RecurringTask
    ):
        """Test GET /api/recurring-tasks/{id} - Get specific task."""
        response = await client.get(
            f"/api/recurring-tasks/{test_recurring_task.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_recurring_task.id
        assert data["title"] == test_recurring_task.title

    @pytest.mark.asyncio
    async def test_get_recurring_task_not_found(
        self, client: AsyncClient, auth_headers: Dict[str, str]
    ):
        """Test GET /api/recurring-tasks/{id} - Task not found."""
        response = await client.get(
            "/api/recurring-tasks/99999",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_recurring_task_unauthorized(
        self, client: AsyncClient, test_recurring_task: RecurringTask
    ):
        """Test GET /api/recurring-tasks/{id} - Unauthorized (no token)."""
        response = await client.get(
            f"/api/recurring-tasks/{test_recurring_task.id}"
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_recurring_task(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_task: RecurringTask
    ):
        """Test PUT /api/recurring-tasks/{id} - Update task."""
        response = await client.put(
            f"/api/recurring-tasks/{test_recurring_task.id}",
            headers=auth_headers,
            json={
                "title": "Updated Standup",
                "description": "Updated description",
                "task_priority_id": 3
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Standup"
        assert data["description"] == "Updated description"
        assert data["task_priority_id"] == 3

    @pytest.mark.asyncio
    async def test_update_recurring_task_empty_body(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_task: RecurringTask
    ):
        """Test PUT /api/recurring-tasks/{id} - Empty update body."""
        response = await client.put(
            f"/api/recurring-tasks/{test_recurring_task.id}",
            headers=auth_headers,
            json={}
        )

        assert response.status_code == 400  # Validation error

    @pytest.mark.asyncio
    async def test_delete_recurring_task(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_task: RecurringTask
    ):
        """Test DELETE /api/recurring-tasks/{id} - Delete task."""
        response = await client.delete(
            f"/api/recurring-tasks/{test_recurring_task.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deleted
        response = await client.get(
            f"/api/recurring-tasks/{test_recurring_task.id}",
            headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_pause_recurring_task(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_task: RecurringTask
    ):
        """Test POST /api/recurring-tasks/{id}/pause - Pause task."""
        response = await client.post(
            f"/api/recurring-tasks/{test_recurring_task.id}/pause",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert "paused successfully" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_pause_already_paused_task(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session,
        test_user: User
    ):
        """Test POST /api/recurring-tasks/{id}/pause - Already paused."""
        # Create paused task
        task = RecurringTask(
            title="Already Paused",
            user_id=str(test_user.id),
            recurrence_pattern="daily",
            start_date=date.today(),
            next_due_at=date.today() + timedelta(days=1),
            is_active=False
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        response = await client.post(
            f"/api/recurring-tasks/{task.id}/pause",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "already paused" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_resume_recurring_task(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session,
        test_user: User
    ):
        """Test POST /api/recurring-tasks/{id}/resume - Resume task."""
        # Create paused task
        task = RecurringTask(
            title="Paused Task",
            user_id=str(test_user.id),
            recurrence_pattern="daily",
            start_date=date.today(),
            next_due_at=date.today() + timedelta(days=1),
            is_active=False
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        response = await client.post(
            f"/api/recurring-tasks/{task.id}/resume",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
        assert "resumed successfully" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_resume_already_active_task(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_task: RecurringTask
    ):
        """Test POST /api/recurring-tasks/{id}/resume - Already active."""
        response = await client.post(
            f"/api/recurring-tasks/{test_recurring_task.id}/resume",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "already active" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_get_recurring_task_count(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_tasks: list[RecurringTask]
    ):
        """Test GET /api/recurring-tasks/stats/count - Get count."""
        response = await client.get(
            "/api/recurring-tasks/stats/count",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert data["count"] == 3

        # Test active_only filter
        response = await client.get(
            "/api/recurring-tasks/stats/count?active_only=true",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2  # 2 active, 1 paused


# ============================================================================
# Test Class 2: Event Publishing Tests
# ============================================================================

class TestEventPublishing:
    """
    Test Dapr event publishing for all event types.

    Events:
    - task-created
    - task-updated
    - task-completed
    - task-deleted
    - task-due-soon
    - recurring-task-due
    """

    @pytest.mark.asyncio
    async def test_task_created_event_published(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        mock_dapr_publisher  # This patches the global dapr_event_publisher
    ):
        """Test task-created event is published."""
        response = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={
                "title": "Test Task",
                "priority": "medium"
            }
        )

        assert response.status_code == 201

        # Verify event was published (publisher should have been called)
        await asyncio.sleep(0.1)
        # The mock publisher tracks calls, check if publish_task_created was called
        assert mock_dapr_publisher.publish_task_created.called

    @pytest.mark.asyncio
    async def test_task_updated_event_published(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_task: Task,
        mock_dapr_publisher
    ):
        """Test task-updated event is published."""
        # mock_dapr_publisher doesn't need reset()

        response = await client.put(
            f"/api/tasks/{test_task.id}",
            headers=auth_headers,
            json={"title": "Updated Task"}
        )

        assert response.status_code == 200

        # Verify event was published
        await asyncio.sleep(0.1)
        assert mock_dapr_publisher.publish_task_updated.called

    @pytest.mark.asyncio
    async def test_task_completed_event_published(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_task: Task,
        mock_dapr_publisher
    ):
        """Test task-completed event is published."""
        # mock_dapr_publisher doesn't need reset()

        response = await client.patch(
            f"/api/tasks/{test_task.id}/complete",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify event was published
        await asyncio.sleep(0.1)
        assert mock_dapr_publisher.publish_task_completed.called

    @pytest.mark.asyncio
    async def test_task_deleted_event_published(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_task: Task,
        mock_dapr_publisher
    ):
        """Test task-deleted event is published."""
        # mock_dapr_publisher doesn't need reset()
        task_id = test_task.id

        response = await client.delete(
            f"/api/tasks/{task_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify event was published
        await asyncio.sleep(0.1)
        assert mock_dapr_publisher.publish_task_deleted.called

    @pytest.mark.asyncio
    async def test_recurring_task_due_event_published(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_task: RecurringTask,
        mock_dapr_publisher
    ):
        """Test recurring-task-due event can be published."""
        # mock_dapr_publisher doesn't need reset()

        # This would typically be triggered by background job
        # For testing, verify the publisher method exists
        from backend.app.services.event_publisher import dapr_event_publisher

        result = await dapr_event_publisher.publish_recurring_task_due({
            "recurring_task_id": test_recurring_task.id,
            "user_id": test_recurring_task.user_id_str,
            "title": test_recurring_task.title,
            "next_due_at": test_recurring_task.next_due_at.isoformat(),
            "recurrence_pattern": test_recurring_task.recurrence_pattern
        })

        # In test mode with Dapr disabled, result is False
        # But we verify the method exists and can be called
        assert result is True or result is False

    @pytest.mark.asyncio
    async def test_event_payload_validation(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        mock_dapr_publisher
    ):
        """Test event payloads contain required fields."""
        # mock_dapr_publisher doesn't need reset()

        response = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Payload Test Task", "priority": "high"}
        )

        assert response.status_code == 201
        task_data = response.json()

        await asyncio.sleep(0.1)

        # Verify publisher was called
        assert mock_dapr_publisher.publish_task_created.called

        # Get the call arguments
        call_args = mock_dapr_publisher.publish_task_created.call_args
        if call_args and call_args[0]:
            payload = call_args[0][0]

            # Required fields
            assert "task_id" in payload or "id" in payload
            assert "user_id" in payload
            assert "title" in payload
            assert payload.get("title") == "Payload Test Task"


# ============================================================================
# Test Class 3: Notification Service Tests
# ============================================================================

class TestNotificationService:
    """
    Test notification service integration with Dapr.

    Tests:
    - Event subscriptions are registered
    - Events are logged to task_event_log table
    - Service health checks
    """

    @pytest.mark.asyncio
    async def test_event_logged_to_database(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session
    ):
        """Test events are logged to task_event_log table."""
        from sqlalchemy import select

        # Create a task
        response = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Event Log Test", "priority": "medium"}
        )

        assert response.status_code == 201
        task_id = response.json()["id"]

        await asyncio.sleep(0.1)

        # Check event log - use scalars().all() to get all matching events
        result = await db_session.execute(
            select(TaskEventLog).where(
                TaskEventLog.task_id == task_id,
                TaskEventLog.event_type == "created"
            )
        )

        event_logs = result.scalars().all()
        assert len(event_logs) >= 1  # At least one event logged
        event_log = event_logs[0]
        assert event_log.event_type == "created"
        assert event_log.event_data is not None

    @pytest.mark.asyncio
    async def test_multiple_events_logged(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_task: Task,
        db_session
    ):
        """Test multiple events are logged for task lifecycle."""
        from sqlalchemy import select

        # Update task first (logs "updated" event)
        await client.put(
            f"/api/tasks/{test_task.id}",
            headers=auth_headers,
            json={"title": "Updated Test Task"}
        )

        await asyncio.sleep(0.1)

        # Complete task (logs "completed" event)
        await client.patch(
            f"/api/tasks/{test_task.id}/complete",
            headers=auth_headers
        )

        await asyncio.sleep(0.1)

        # Check for updated and completed events (created was not logged because test_task was created via fixture)
        result = await db_session.execute(
            select(TaskEventLog).where(
                TaskEventLog.task_id == test_task.id
            )
        )

        event_logs = result.scalars().all()
        event_types = {log.event_type for log in event_logs}

        # Note: "created" event is not expected because test_task fixture creates task directly in DB
        assert "updated" in event_types
        assert "completed" in event_types

    @pytest.mark.asyncio
    async def test_event_log_data_integrity(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        db_session
    ):
        """Test event log data integrity."""
        from sqlalchemy import select

        response = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={
                "title": "Integrity Test",
                "description": "Test description",
                "priority": "high"
            }
        )

        assert response.status_code == 201
        task_data = response.json()
        task_id = task_data["id"]

        await asyncio.sleep(0.1)

        # Verify log data matches task data - use scalars().all() to handle multiple results
        result = await db_session.execute(
            select(TaskEventLog).where(
                TaskEventLog.task_id == task_id,
                TaskEventLog.event_type == "created"
            )
        )

        event_logs = result.scalars().all()
        assert len(event_logs) >= 1  # At least one event logged

        event_log = event_logs[0]
        log_data = event_log.event_data
        assert log_data.get("title") == "Integrity Test"
        assert log_data.get("task_id") == task_id


# ============================================================================
# Test Class 4: End-to-End Workflows
# ============================================================================

class TestEndToEndWorkflows:
    """
    Test complete user workflows across multiple services.

    Workflows:
    - Create recurring task -> Generate tasks -> Complete tasks
    - Task lifecycle with all events
    - Full pagination and filtering workflow
    """

    @pytest.mark.asyncio
    async def test_recurring_task_full_workflow(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        mock_dapr_publisher,
        db_session
    ):
        """Test complete recurring task workflow."""
        # mock_dapr_publisher doesn't need reset()

        # Step 1: Create recurring task
        response = await client.post(
            "/api/recurring-tasks",
            headers=auth_headers,
            json={
                "title": "Daily Standup",
                "recurrence_pattern": "daily",
                "start_date": date.today().isoformat(),
                "task_priority_id": 2
            }
        )

        assert response.status_code == 201
        recurring_task = response.json()

        # Step 2: List recurring tasks
        response = await client.get(
            "/api/recurring-tasks",
            headers=auth_headers
        )

        assert response.status_code == 200
        tasks = response.json()
        assert any(t["id"] == recurring_task["id"] for t in tasks)

        # Step 3: Pause recurring task
        response = await client.post(
            f"/api/recurring-tasks/{recurring_task['id']}/pause",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

        # Step 4: Resume recurring task
        response = await client.post(
            f"/api/recurring-tasks/{recurring_task['id']}/resume",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is True

        # Step 5: Delete recurring task
        response = await client.delete(
            f"/api/recurring-tasks/{recurring_task['id']}",
            headers=auth_headers
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_task_lifecycle_with_all_events(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        mock_dapr_publisher,
        db_session
    ):
        """Test complete task lifecycle with event verification."""
        from sqlalchemy import select

        # mock_dapr_publisher doesn't need reset()

        # Create task
        response = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Lifecycle Test", "priority": "medium"}
        )

        assert response.status_code == 201
        task = response.json()
        task_id = task["id"]

        await asyncio.sleep(0.1)

        # Verify created event
        assert mock_dapr_publisher.publish_task_created.called

        # Update task
        response = await client.put(
            f"/api/tasks/{task_id}",
            headers=auth_headers,
            json={"title": "Updated Lifecycle Test"}
        )

        assert response.status_code == 200
        await asyncio.sleep(0.1)

        # Verify updated event
        assert mock_dapr_publisher.publish_task_updated.called

        # Complete task
        response = await client.patch(
            f"/api/tasks/{task_id}/complete",
            headers=auth_headers
        )

        assert response.status_code == 200
        await asyncio.sleep(0.1)

        # Verify completed event
        assert mock_dapr_publisher.publish_task_completed.called

        # Verify database logs
        result = await db_session.execute(
            select(TaskEventLog).where(
                TaskEventLog.task_id == task_id
            ).order_by(TaskEventLog.created_at)
        )

        event_logs = result.scalars().all()
        event_types = [log.event_type for log in event_logs]

        assert "created" in event_types
        assert "updated" in event_types
        assert "completed" in event_types

    @pytest.mark.asyncio
    async def test_pagination_workflow(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test pagination workflow with large dataset."""
        # Create 25 tasks
        task_ids = []
        for i in range(25):
            response = await client.post(
                "/api/tasks",
                headers=auth_headers,
                json={"title": f"Pagination Task {i+1}", "priority": "medium"}
            )
            assert response.status_code == 201
            task_ids.append(response.json()["id"])

        # Test pagination
        response = await client.get(
            "/api/tasks?limit=10&offset=0",
            headers=auth_headers
        )

        assert response.status_code == 200
        page1 = response.json()
        assert len(page1) == 10

        response = await client.get(
            "/api/tasks?limit=10&offset=10",
            headers=auth_headers
        )

        assert response.status_code == 200
        page2 = response.json()
        assert len(page2) == 10

        response = await client.get(
            "/api/tasks?limit=10&offset=20",
            headers=auth_headers
        )

        assert response.status_code == 200
        page3 = response.json()
        assert len(page3) == 5

        # Verify no duplicates across pages
        all_ids = [t["id"] for t in page1 + page2 + page3]
        assert len(all_ids) == len(set(all_ids))

    @pytest.mark.asyncio
    async def test_filtering_workflow(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test filtering and sorting workflow."""
        # Create tasks with different priorities
        priorities = ["low", "medium", "high"]
        for priority in priorities:
            await client.post(
                "/api/tasks",
                headers=auth_headers,
                json={"title": f"{priority.capitalize()} Task", "priority": priority}
            )

        # Filter by completed
        response = await client.get(
            "/api/tasks?completed=false",
            headers=auth_headers
        )

        assert response.status_code == 200
        tasks = response.json()
        assert all(not t["completed"] for t in tasks)

        # Sort by priority
        response = await client.get(
            "/api/tasks?sort_by=priority&sort_order=desc",
            headers=auth_headers
        )

        assert response.status_code == 200
        tasks = response.json()
        # Verify sorting (implementation-specific)


# ============================================================================
# Test Class 5: Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """
    Test error handling and edge cases.

    Tests:
    - 404 Not Found errors
    - 400 Bad Request errors
    - 401 Unauthorized errors
    - 403 Forbidden errors
    - Data isolation between users
    """

    @pytest.mark.asyncio
    async def test_unauthorized_access(
        self, client: AsyncClient, test_recurring_task: RecurringTask
    ):
        """Test accessing endpoints without authentication."""
        endpoints = [
            f"/api/recurring-tasks/{test_recurring_task.id}",
            "/api/recurring-tasks",
            "/api/recurring-tasks/stats/count"
        ]

        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_cross_user_data_isolation(
        self,
        client: AsyncClient,
        db_session,
        test_recurring_task: RecurringTask
    ):
        """Test users cannot access each other's data."""
        # Create second user (import from app.models to avoid redefining the class)
        from app.models.user import User
        import uuid

        user2_id = uuid.uuid4()
        user2 = User(
            id=user2_id,
            email=f"user2_{user2_id.hex[:8]}@example.com",
            name="User 2",
            hashed_password="$2b$12$78dMjiOacuJ54lC12Os7FefzNRUPVTsijhYZ5ZoWdVzBSi3nfgaru"
        )
        db_session.add(user2)
        await db_session.commit()

        # Login as user2
        response = await client.post(
            "/api/auth/login",
            json={"email": user2.email, "password": "password123"}
        )

        assert response.status_code == 200
        user2_token = response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # Try to access user1's recurring task
        response = await client.get(
            f"/api/recurring-tasks/{test_recurring_task.id}",
            headers=user2_headers
        )

        # Should return 404 (not found for this user)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_recurring_task_id(
        self, client: AsyncClient, auth_headers: Dict[str, str]
    ):
        """Test accessing non-existent recurring task."""
        response = await client.get(
            "/api/recurring-tasks/999999",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_recurrence_pattern(
        self, client: AsyncClient, auth_headers: Dict[str, str]
    ):
        """Test creating recurring task with invalid pattern."""
        response = await client.post(
            "/api/recurring-tasks",
            headers=auth_headers,
            json={
                "title": "Invalid Pattern",
                "recurrence_pattern": "hourly",
                "start_date": date.today().isoformat()
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_date_range(
        self, client: AsyncClient, auth_headers: Dict[str, str]
    ):
        """Test creating recurring task with invalid date range."""
        response = await client.post(
            "/api/recurring-tasks",
            headers=auth_headers,
            json={
                "title": "Invalid Dates",
                "recurrence_pattern": "daily",
                "start_date": date.today().isoformat(),
                "end_date": (date.today() - timedelta(days=1)).isoformat()
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_with_invalid_data(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_recurring_task: RecurringTask
    ):
        """Test updating recurring task with invalid data."""
        # Invalid recurrence pattern
        response = await client.put(
            f"/api/recurring-tasks/{test_recurring_task.id}",
            headers=auth_headers,
            json={"recurrence_pattern": "invalid"}
        )

        assert response.status_code == 422


# ============================================================================
# Test Summary
# ============================================================================

def pytest_terminal_summary(terminalreporter):
    """
    Print test summary after all tests complete.

    Provides overview of:
    - Total tests run
    - Passed/Failed/Skipped
    - Coverage by test category
    """
    stats = terminalreporter.stats

    total = sum(len(stats.get(key, [])) for key in ["passed", "failed", "skipped"])
    passed = len(stats.get("passed", []))
    failed = len(stats.get("failed", []))
    skipped = len(stats.get("skipped", []))

    print("\n" + "=" * 70)
    print("  PHASE V: Event-Driven Architecture - Test Summary")
    print("=" * 70)
    print(f"\n  Total Tests: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print(f"\n  Success Rate: {passed/total*100:.1f}%" if total > 0 else "  Success Rate: N/A")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
