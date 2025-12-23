"""Test task templates API endpoints."""
import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
class TestTaskTemplates:
    """Test suite for task templates API."""

    async def test_create_template(self, async_client: AsyncClient, auth_token: str):
        """Test creating a new task template."""
        response = await async_client.post(
            "/api/task-templates",
            json={
                "title": "Weekly Review",
                "description": "Weekly task review template",
                "priority_id": 2,
                "tags": ["review", "weekly"]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Weekly Review"
        assert data["description"] == "Weekly task review template"
        assert data["priority_id"] == 2
        assert data["tags"] == ["review", "weekly"]
        assert "id" in data

    async def test_create_template_with_recurrence(self, async_client: AsyncClient, auth_token: str):
        """Test creating a template with recurrence settings."""
        response = await async_client.post(
            "/api/task-templates",
            json={
                "title": "Daily Standup",
                "description": "Daily standup meeting",
                "priority_id": 2,
                "is_recurring": True,
                "recurrence_pattern": "daily"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["is_recurring"] is True
        assert data["recurrence_pattern"] == "daily"

    async def test_create_template_invalid_recurrence(self, async_client: AsyncClient, auth_token: str):
        """Test that creating a template with is_recurring=True but no pattern fails."""
        response = await async_client.post(
            "/api/task-templates",
            json={
                "title": "Invalid Template",
                "is_recurring": True
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 422  # Validation error

    async def test_create_template_invalid_pattern(self, async_client: AsyncClient, auth_token: str):
        """Test that invalid recurrence pattern is rejected."""
        response = await async_client.post(
            "/api/task-templates",
            json={
                "title": "Invalid Pattern Template",
                "is_recurring": True,
                "recurrence_pattern": "invalid_pattern"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 422  # Validation error

    async def test_get_templates(self, async_client: AsyncClient, auth_token: str):
        """Test getting all templates for current user."""
        # First create a template
        await async_client.post(
            "/api/task-templates",
            json={"title": "Test Template", "priority_id": 2},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Get all templates
        response = await async_client.get(
            "/api/task-templates",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(t["title"] == "Test Template" for t in data)

    async def test_get_template_by_id(self, async_client: AsyncClient, auth_token: str):
        """Test getting a specific template by ID."""
        # Create a template first
        create_response = await async_client.post(
            "/api/task-templates",
            json={"title": "Specific Template", "priority_id": 3},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        template_id = create_response.json()["id"]

        # Get the template
        response = await async_client.get(
            f"/api/task-templates/{template_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == template_id
        assert data["title"] == "Specific Template"
        assert data["priority_id"] == 3

    async def test_get_template_not_found(self, async_client: AsyncClient, auth_token: str):
        """Test getting a non-existent template returns 404."""
        response = await async_client.get(
            "/api/task-templates/99999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 404

    async def test_update_template(self, async_client: AsyncClient, auth_token: str):
        """Test updating a template."""
        # Create a template first
        create_response = await async_client.post(
            "/api/task-templates",
            json={"title": "Original Title", "priority_id": 2},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        template_id = create_response.json()["id"]

        # Update the template
        response = await async_client.put(
            f"/api/task-templates/{template_id}",
            json={"title": "Updated Title", "priority_id": 3},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority_id"] == 3

    async def test_update_template_empty_body(self, async_client: AsyncClient, auth_token: str):
        """Test updating a template with no fields returns validation error."""
        # Create a template first
        create_response = await async_client.post(
            "/api/task-templates",
            json={"title": "Test Template", "priority_id": 2},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        template_id = create_response.json()["id"]

        # Try to update with empty body
        response = await async_client.put(
            f"/api/task-templates/{template_id}",
            json={},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 422  # Validation error

    async def test_delete_template(self, async_client: AsyncClient, auth_token: str):
        """Test deleting a template."""
        # Create a template first
        create_response = await async_client.post(
            "/api/task-templates",
            json={"title": "To Delete", "priority_id": 2},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        template_id = create_response.json()["id"]

        # Delete the template
        response = await async_client.delete(
            f"/api/task-templates/{template_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 204

        # Verify it's gone
        get_response = await async_client.get(
            f"/api/task-templates/{template_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert get_response.status_code == 404

    async def test_use_template_create_task(self, async_client: AsyncClient, auth_token: str):
        """Test creating a task from a template."""
        # Create a template first
        create_response = await async_client.post(
            "/api/task-templates",
            json={
                "title": "Template for Task",
                "description": "Default description",
                "priority_id": 3
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        template_id = create_response.json()["id"]

        # Use the template to create a task
        response = await async_client.post(
            f"/api/task-templates/{template_id}/use",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Template for Task"
        assert data["description"] == "Default description"
        assert data["priority_id"] == 3
        assert data["completed"] is False
        assert "id" in data

    async def test_use_template_with_overrides(self, async_client: AsyncClient, auth_token: str):
        """Test creating a task from a template with overrides."""
        # Create a template first
        create_response = await async_client.post(
            "/api/task-templates",
            json={
                "title": "Original Template",
                "description": "Original description"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        template_id = create_response.json()["id"]

        # Use the template with overrides
        response = await async_client.post(
            f"/api/task-templates/{template_id}/use",
            json={
                "title": "Overridden Title",
                "description": "Overridden description",
                "due_date": "2025-12-31"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Overridden Title"
        assert data["description"] == "Overridden description"
        assert data["due_date"] == "2025-12-31"

    async def test_save_task_as_template(self, async_client: AsyncClient, auth_token: str):
        """Test saving an existing task as a template."""
        # Create a task first
        task_response = await async_client.post(
            "/api/tasks",
            json={
                "title": "Task to Save",
                "description": "Original task",
                "priority_id": 3
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        task_id = task_response.json()["id"]

        # Save the task as a template
        response = await async_client.post(
            f"/api/task-templates/from-task/{task_id}",
            json={
                "template_title": "Saved from Task",
                "include_description": True,
                "include_priority": True
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Saved from Task"
        assert data["description"] == "Original task"
        assert data["priority_id"] == 3

    async def test_template_data_isolation(self, async_client: AsyncClient, auth_token: str, second_user_token: str):
        """Test that users cannot access each other's templates."""
        # Create a template with first user
        create_response = await async_client.post(
            "/api/task-templates",
            json={"title": "Private Template", "priority_id": 2},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        template_id = create_response.json()["id"]

        # Try to access with second user
        response = await async_client.get(
            f"/api/task-templates/{template_id}",
            headers={"Authorization": f"Bearer {second_user_token}"}
        )

        assert response.status_code == 404

    async def test_template_pagination(self, async_client: AsyncClient, auth_token: str):
        """Test pagination of templates list."""
        # Create multiple templates
        for i in range(5):
            await async_client.post(
                "/api/task-templates",
                json={"title": f"Template {i}", "priority_id": 2},
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        # Get first page
        response = await async_client.get(
            "/api/task-templates?limit=3&offset=0",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

        # Get second page
        response = await async_client.get(
            "/api/task-templates?limit=3&offset=3",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200

    async def test_unauthorized_access(self, async_client: AsyncClient):
        """Test that requests without auth token are rejected."""
        response = await async_client.get("/api/task-templates")
        assert response.status_code == 401

        response = await async_client.post(
            "/api/task-templates",
            json={"title": "Test", "priority_id": 2}
        )
        assert response.status_code == 401

    async def test_template_with_subtasks(self, async_client: AsyncClient, auth_token: str):
        """Test creating a template with subtask templates."""
        response = await async_client.post(
            "/api/task-templates",
            json={
                "title": "Project Template",
                "description": "Template with subtasks",
                "priority_id": 2,
                "subtasks": [
                    {"title": "Research", "description": "Do initial research"},
                    {"title": "Draft", "description": "Create first draft"},
                    {"title": "Review", "description": "Review and finalize"}
                ]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["subtasks_template"] is not None
        assert len(data["subtasks_template"]) == 3
        assert data["subtasks_template"][0]["title"] == "Research"


# Pytest fixtures
@pytest.fixture
async def auth_token(async_client: AsyncClient) -> str:
    """Get auth token for test user."""
    # Register/login a test user
    response = await async_client.post(
        "/api/auth/register",
        json={
            "email": "template_test@example.com",
            "password": "testpass123",
            "name": "Template Test User"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]

    # If user exists, login
    response = await async_client.post(
        "/api/auth/login",
        json={
            "email": "template_test@example.com",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
async def second_user_token(async_client: AsyncClient) -> str:
    """Get auth token for second test user."""
    response = await async_client.post(
        "/api/auth/register",
        json={
            "email": "template_test2@example.com",
            "password": "testpass123",
            "name": "Second Test User"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]

    # If user exists, login
    response = await async_client.post(
        "/api/auth/login",
        json={
            "email": "template_test2@example.com",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]
