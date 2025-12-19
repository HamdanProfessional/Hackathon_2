"""Simple test to verify search functionality works without authentication issues."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_endpoint_exists(client: AsyncClient):
    """Test that the search endpoint accepts query parameters without errors."""
    # First, create a user and get token
    register_data = {"email": "test@example.com", "password": "testpassword123"}

    # Register
    response = await client.post("/api/auth/register", json=register_data)
    assert response.status_code == 201

    # Login
    login_response = await client.post("/api/auth/login", json=register_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Test that we can create a task
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "title": "Test Task",
        "description": "A test task for search",
        "priority": "medium"
    }
    response = await client.post("/api/tasks", json=task_data, headers=headers)
    assert response.status_code == 201

    # Test that we can get tasks with search parameter
    response = await client.get("/api/tasks?search=Test", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Test Task"