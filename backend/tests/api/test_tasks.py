"""Task API tests."""
import pytest
import asyncio
from httpx import AsyncClient


async def register_user(client: AsyncClient, email: str, password: str):
    """Helper to register a user and return their token."""
    user_data = {"email": email, "password": password}

    # Register user (returns token directly)
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201

    resp_data = response.json()
    assert "access_token" in resp_data
    token = resp_data["access_token"]
    assert token is not None
    assert len(token) > 0

    return token


@pytest.mark.asyncio
async def test_create_task_requires_title(client: AsyncClient):
    """
    Test T050 (Scenario 1): Creating a task without title returns 422.

    This test validates that the API properly rejects task creation attempts
    when the required title field is missing or empty.
    """
    # Register and login a user
    token = await register_user(client, "testuser@example.com", "testpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    # Try to create task with empty title
    response = await client.post("/api/tasks", json={"title": ""}, headers=headers)
    assert response.status_code == 422

    # Try to create task with missing title
    response = await client.post("/api/tasks", json={"description": "A task without title"}, headers=headers)
    assert response.status_code == 422

    # Try to create task with only whitespace title
    response = await client.post("/api/tasks", json={"title": "   "}, headers=headers)
    assert response.status_code == 422

    # Create a valid task to ensure authentication works
    response = await client.post("/api/tasks", json={"title": "Valid Task"}, headers=headers)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_task_associates_with_user(client: AsyncClient):
    """
    Test T050 (Scenario 2): Created task is associated with authenticated user.

    This test validates that when a user creates a task, it's properly
    associated with that user's ID.
    """
    # Register and login a user
    token = await register_user(client, "usera@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create task
    task_data = {
        "title": "User's Task",
        "description": "This task belongs to the user",
        "priority": "HIGH"
    }

    response = await client.post("/api/tasks", json=task_data, headers=headers)
    if response.status_code != 201:
        print(f"Error response: {response.text}")
    assert response.status_code == 201
    created_task = response.json()

    # Verify task has valid user_id
    assert created_task["user_id"] > 0  # Should have a valid user_id
    assert created_task["title"] == task_data["title"]
    assert created_task["description"] == task_data["description"]
    assert created_task["priority"] == task_data["priority"]
    assert created_task["completed"] is False


@pytest.mark.asyncio
async def test_task_update_ownership_validation(client: AsyncClient):
    """
    Test T051: Users cannot update tasks they don't own.

    This test validates that a user cannot update another user's task
    and receives a 404 Not Found error (to prevent existence disclosure).
    """
    # Register and login two users
    token_a = await register_user(client, "alice@example.com", "alicepass123")
    token_b = await register_user(client, "bob@example.com", "bobpass123")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a task
    task_data = {
        "title": "Alice's Secret Task",
        "description": "This task should only be visible to Alice"
    }

    create_response = await client.post("/api/tasks", json=task_data, headers=headers_a)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # User B tries to update User A's task
    update_data = {
        "title": "Hacked by Bob!",
        "description": "This should not be possible"
    }

    response = await client.put(f"/api/tasks/{task_id}", json=update_data, headers=headers_b)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

    # Verify the task wasn't modified by fetching it as User A
    response = await client.get(f"/api/tasks/{task_id}", headers=headers_a)
    assert response.status_code == 200
    task = response.json()
    assert task["title"] == task_data["title"]
    assert task["description"] == task_data["description"]


@pytest.mark.asyncio
async def test_task_delete_ownership_validation(client: AsyncClient):
    """
    Test T052: Users cannot delete tasks they don't own.

    This test validates that a user cannot delete another user's task
    and receives a 404 Not Found error.
    """
    # Register and login two users
    token_a = await register_user(client, "charlie@example.com", "charliepass123")
    token_b = await register_user(client, "diana@example.com", "dianapass123")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a task
    task_data = {
        "title": "Charlie's Important Task",
        "description": "This task must not be deleted by others"
    }

    create_response = await client.post("/api/tasks", json=task_data, headers=headers_a)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # User B tries to delete User A's task
    response = await client.delete(f"/api/tasks/{task_id}", headers=headers_b)
    assert response.status_code == 404

    # Verify the task still exists by fetching it as User A
    response = await client.get(f"/api/tasks/{task_id}", headers=headers_a)
    assert response.status_code == 200
    assert response.json()["title"] == task_data["title"]

    # User A can successfully delete their own task
    response = await client.delete(f"/api/tasks/{task_id}", headers=headers_a)
    assert response.status_code == 204

    # Verify the task is gone
    response = await client.get(f"/api/tasks/{task_id}", headers=headers_a)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_task_completion_persistence(client: AsyncClient):
    """
    Test T053: Task completion status persists correctly.

    This test validates that toggling a task's completion status
    properly persists in the database.
    """
    # Register and login a user
    token = await register_user(client, "eve@example.com", "evepass123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a task
    task_data = {
        "title": "Test Completion Task",
        "description": "Testing if completion status persists"
    }

    create_response = await client.post("/api/tasks", json=task_data, headers=headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Verify task starts as incomplete
    response = await client.get(f"/api/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    task = response.json()
    assert task["completed"] is False

    # Mark task as complete
    response = await client.patch(f"/api/tasks/{task_id}/complete", headers=headers)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["completed"] is True

    # Fetch task again to verify persistence
    response = await client.get(f"/api/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    task = response.json()
    assert task["completed"] is True

    # Mark task as incomplete again
    response = await client.patch(f"/api/tasks/{task_id}/complete", headers=headers)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["completed"] is False

    # Fetch task again to verify persistence
    response = await client.get(f"/api/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    task = response.json()
    assert task["completed"] is False


@pytest.mark.asyncio
async def test_task_create_with_all_fields(client: AsyncClient):
    """
    Additional test: Create a task with all optional fields.

    This test validates that tasks can be created with all fields
    including priority and due date.
    """
    # Register and login a user
    token = await register_user(client, "frank@example.com", "frankpass123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create task with all fields
    tomorrow = "2025-12-16"  # Format: YYYY-MM-DD
    task_data = {
        "title": "Complete Task Management Tests",
        "description": "Write comprehensive tests for all task operations",
        "priority": "HIGH",
        "due_date": tomorrow
    }

    response = await client.post("/api/tasks", json=task_data, headers=headers)
    assert response.status_code == 201
    task = response.json()

    assert task["title"] == task_data["title"]
    assert task["description"] == task_data["description"]
    assert task["priority"] == task_data["priority"]
    assert task["due_date"] == tomorrow
    assert task["completed"] is False


@pytest.mark.asyncio
async def test_get_tasks_only_returns_user_tasks(client: AsyncClient):
    """
    Additional test: GET /api/tasks only returns tasks for authenticated user.

    This test validates data isolation - users can only see their own tasks.
    """
    # Register two users
    token1 = await register_user(client, "grace@example.com", "gracepass123")
    token2 = await register_user(client, "henry@example.com", "henrypass123")

    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User 1 creates tasks
    await client.post("/api/tasks", json={"title": "Grace's Task 1"}, headers=headers1)
    await client.post("/api/tasks", json={"title": "Grace's Task 2"}, headers=headers1)

    # User 2 creates tasks
    await client.post("/api/tasks", json={"title": "Henry's Task 1"}, headers=headers2)

    # User 1 fetches tasks - should only see their own
    response = await client.get("/api/tasks", headers=headers1)
    assert response.status_code == 200
    tasks1 = response.json()
    assert len(tasks1) == 2
    assert all(task["title"].startswith("Grace") for task in tasks1)

    # User 2 fetches tasks - should only see their own
    response = await client.get("/api/tasks", headers=headers2)
    assert response.status_code == 200
    tasks2 = response.json()
    assert len(tasks2) == 1
    assert tasks2[0]["title"] == "Henry's Task 1"


@pytest.mark.asyncio
async def test_task_crud_edge_cases(client: AsyncClient):
    """
    Test T105: CRUD operations edge cases.

    This test validates edge cases for CRUD operations including:
    - Special characters in titles/descriptions
    - Maximum length boundaries
    - Invalid priority values
    - Invalid date formats
    """
    # Register and login a user
    token = await register_user(client, "edgetest@example.com", "edgepass123")
    headers = {"Authorization": f"Bearer {token}"}

    # Test with special characters
    special_chars_task = {
        "title": "Task with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
        "description": "Description with emojis 🚀 and unicode: café résumé 中文"
    }
    response = await client.post("/api/tasks", json=special_chars_task, headers=headers)
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == special_chars_task["title"]
    assert task["description"] == special_chars_task["description"]

    # Test maximum title length (500 chars)
    max_title = "A" * 500
    max_title_task = {"title": max_title}
    response = await client.post("/api/tasks", json=max_title_task, headers=headers)
    assert response.status_code == 201

    # Test title too long (501 chars)
    too_long_title = "B" * 501
    response = await client.post("/api/tasks", json={"title": too_long_title}, headers=headers)
    assert response.status_code == 422

    # Test invalid priority
    invalid_priority_task = {
        "title": "Test Task",
        "priority": "invalid_priority"
    }
    response = await client.post("/api/tasks", json=invalid_priority_task, headers=headers)
    assert response.status_code == 422

    # Test invalid date format
    invalid_date_task = {
        "title": "Test Task",
        "due_date": "not-a-date"
    }
    response = await client.post("/api/tasks", json=invalid_date_task, headers=headers)
    assert response.status_code == 422

    # Test past date
    past_date_task = {
        "title": "Test Task",
        "due_date": "2020-01-01"
    }
    response = await client.post("/api/tasks", json=past_date_task, headers=headers)
    assert response.status_code == 201  # Should accept past dates

    # Update task with partial data
    update_partial = {"description": "Updated description"}
    response = await client.patch(f"/api/tasks/{task['id']}", json=update_partial, headers=headers)
    assert response.status_code == 200
    updated = response.json()
    assert updated["description"] == update_partial["description"]
    assert updated["title"] == task["title"]  # Title should remain unchanged


@pytest.mark.asyncio
async def test_task_sql_injection_protection(client: AsyncClient):
    """
    Test T112: SQL injection protection.

    This test validates that the API is protected against SQL injection attacks
    in task titles, descriptions, and query parameters.
    """
    # Register and login a user
    token = await register_user(client, "sqltest@example.com", "sqlpass123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a normal task first for comparison
    normal_task = {"title": "Normal Task", "description": "Normal description"}
    response = await client.post("/api/tasks", json=normal_task, headers=headers)
    assert response.status_code == 201
    normal_task_id = response.json()["id"]

    # Test SQL injection in title
    sql_injection_title = {
        "title": "'; DROP TABLE tasks; --",
        "description": "Attempting SQL injection in title"
    }
    response = await client.post("/api/tasks", json=sql_injection_title, headers=headers)
    assert response.status_code == 201  # Should be safely stored as text

    # Test SQL injection in description
    sql_injection_desc = {
        "title": "Test Task",
        "description": "'; DELETE FROM users WHERE '1'='1'; --"
    }
    response = await client.post("/api/tasks", json=sql_injection_desc, headers=headers)
    assert response.status_code == 201

    # Test SQL injection in search/filter parameters
    injection_payload = "'; SELECT * FROM users; --"

    # Test in search endpoint
    response = await client.get(f"/api/tasks/search?q={injection_payload}", headers=headers)
    assert response.status_code == 422  # Should be rejected as invalid input

    # Test in filter endpoint
    response = await client.get(
        f"/api/tasks/filter?priority={injection_payload}&completed=true",
        headers=headers
    )
    assert response.status_code == 422  # Should be rejected as invalid input

    # Test in pagination parameters
    response = await client.get(
        f"/api/tasks?limit={injection_payload}&offset=0",
        headers=headers
    )
    assert response.status_code == 422  # Should be rejected

    # Verify our normal task still exists (proves tables weren't dropped)
    response = await client.get(f"/api/tasks/{normal_task_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == normal_task["title"]

    # Verify all tasks are still intact
    response = await client.get("/api/tasks", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 3  # Should have our created tasks

    # Test that special characters are safely escaped
    for task in tasks:
        if task["title"] == sql_injection_title["title"]:
            # Should be stored as-is, not executed
            assert task["title"] == sql_injection_title["title"]
            break
    else:
        pytest.fail("SQL injection title task not found")