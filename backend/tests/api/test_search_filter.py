"""Tests for task search and filtering functionality."""
import asyncio
from datetime import date, timedelta
import pytest
import uuid
from httpx import AsyncClient

from app.models.task import TaskPriority


async def register_user(client: AsyncClient, email: str, password: str):
    """Helper to register a user and return their token."""
    user_data = {"email": email, "password": password}

    # Register user
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201

    # Login to get token
    login_response = await client.post("/api/auth/login", json=user_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    return token


@pytest.mark.asyncio
async def test_T067_search_filters_tasks_by_title_and_description(client: AsyncClient):
    """Test T067: Search filters tasks by title or description in real-time."""
    # Register and login a test user
    unique_id = str(uuid.uuid4())[:8]
    token = await register_user(client, f"test_T067_{unique_id}@example.com", "testpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create test tasks
    tomorrow = date.today() + timedelta(days=1)
    yesterday = date.today() - timedelta(days=1)
    next_week = date.today() + timedelta(weeks=1)

    # Task A: "Buy Milk", High Priority, Pending, Due Tomorrow
    task_a_data = {
        "title": "Buy Milk",
        "description": "Buy milk from the grocery store",
        "priority": "high",
        "due_date": tomorrow.isoformat()
    }
    await client.post("/api/tasks", json=task_a_data, headers=headers)

    # Task B: "Walk Dog", Low Priority, Completed, Due Yesterday
    task_b_data = {
        "title": "Walk Dog",
        "description": "Take the dog for a walk",
        "priority": "low",
        "due_date": yesterday.isoformat(),
        "completed": True
    }
    await client.post("/api/tasks", json=task_b_data, headers=headers)

    # Task C: "Buy Eggs", Medium Priority, Pending, Due Next Week
    task_c_data = {
        "title": "Buy Eggs",
        "description": "Pick up eggs from the market",
        "priority": "medium",
        "due_date": next_week.isoformat()
    }
    await client.post("/api/tasks", json=task_c_data, headers=headers)

    # Search for "Buy" - should return Task A and Task C
    response = await client.get("/api/tasks?search=Buy", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    task_titles = [task["title"] for task in tasks]

    # Should contain "Buy Milk" and "Buy Eggs"
    assert "Buy Milk" in task_titles
    assert "Buy Eggs" in task_titles
    # Should NOT contain "Walk Dog"
    assert "Walk Dog" not in task_titles
    assert len(tasks) == 2

    # Search for "Walk" - should return only Task B
    response = await client.get("/api/tasks?search=Walk", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    task_titles = [task["title"] for task in tasks]

    # Should contain only "Walk Dog"
    assert "Walk Dog" in task_titles
    assert "Buy Milk" not in task_titles
    assert "Buy Eggs" not in task_titles
    assert len(tasks) == 1

    # Search for "grocery" (in description) - should return Task A
    response = await client.get("/api/tasks?search=grocery", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    task_titles = [task["title"] for task in tasks]

    # Should contain only "Buy Milk"
    assert "Buy Milk" in task_titles
    assert len(tasks) == 1

    # Case insensitive search
    response = await client.get("/api/tasks?search=milk", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    task_titles = [task["title"] for task in tasks]
    assert "Buy Milk" in task_titles
    assert len(tasks) == 1


@pytest.mark.asyncio
async def test_T068_filter_by_status_shows_only_active_or_completed_tasks(client: AsyncClient):
    """Test T068: Filter by status shows only active or completed tasks."""
    # Register and login a test user
    unique_id = str(uuid.uuid4())[:8]
    token = await register_user(client, f"test_T068_{unique_id}@example.com", "testpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create test tasks
    tomorrow = date.today() + timedelta(days=1)
    yesterday = date.today() - timedelta(days=1)
    next_week = date.today() + timedelta(weeks=1)

    # Task A: "Buy Milk", High Priority, Pending, Due Tomorrow
    task_a_data = {
        "title": "Buy Milk",
        "description": "Buy milk from the grocery store",
        "priority": "high",
        "due_date": tomorrow.isoformat()
    }
    await client.post("/api/tasks", json=task_a_data, headers=headers)

    # Task B: "Walk Dog", Low Priority, Completed, Due Yesterday
    task_b_data = {
        "title": "Walk Dog",
        "description": "Take the dog for a walk",
        "priority": "low",
        "due_date": yesterday.isoformat(),
        "completed": True
    }
    await client.post("/api/tasks", json=task_b_data, headers=headers)

    # Task C: "Buy Eggs", Medium Priority, Pending, Due Next Week
    task_c_data = {
        "title": "Buy Eggs",
        "description": "Pick up eggs from the market",
        "priority": "medium",
        "due_date": next_week.isoformat()
    }
    await client.post("/api/tasks", json=task_c_data, headers=headers)

    # Filter by completed tasks
    response = await client.get("/api/tasks?status=completed", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    task_titles = [task["title"] for task in tasks]

    # Should contain only "Walk Dog" (completed)
    assert "Walk Dog" in task_titles
    assert "Buy Milk" not in task_titles
    assert "Buy Eggs" not in task_titles
    assert len(tasks) == 1

    # Verify all returned tasks are actually completed
    for task in tasks:
        assert task["completed"] is True

    # Filter by pending tasks
    response = await client.get("/api/tasks?status=pending", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    task_titles = [task["title"] for task in tasks]

    # Should contain "Buy Milk" and "Buy Eggs" (pending)
    assert "Buy Milk" in task_titles
    assert "Buy Eggs" in task_titles
    assert "Walk Dog" not in task_titles
    assert len(tasks) == 2

    # Verify all returned tasks are actually pending
    for task in tasks:
        assert task["completed"] is False


@pytest.mark.asyncio
async def test_T069_filter_by_priority_shows_correct_subset(client: AsyncClient):
    """Test T069: Filter by priority shows correct subset."""
    # Register and login a test user
    unique_id = str(uuid.uuid4())[:8]
    token = await register_user(client, f"test_T069_{unique_id}@example.com", "testpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create test tasks
    tomorrow = date.today() + timedelta(days=1)
    yesterday = date.today() - timedelta(days=1)
    next_week = date.today() + timedelta(weeks=1)

    # Task A: "Buy Milk", High Priority, Pending, Due Tomorrow
    task_a_data = {
        "title": "Buy Milk",
        "description": "Buy milk from the grocery store",
        "priority": "high",
        "due_date": tomorrow.isoformat()
    }
    await client.post("/api/tasks", json=task_a_data, headers=headers)

    # Task B: "Walk Dog", Low Priority, Completed, Due Yesterday
    task_b_data = {
        "title": "Walk Dog",
        "description": "Take the dog for a walk",
        "priority": "low",
        "due_date": yesterday.isoformat(),
        "completed": True
    }
    await client.post("/api/tasks", json=task_b_data, headers=headers)

    # Task C: "Buy Eggs", Medium Priority, Pending, Due Next Week
    task_c_data = {
        "title": "Buy Eggs",
        "description": "Pick up eggs from the market",
        "priority": "medium",
        "due_date": next_week.isoformat()
    }
    await client.post("/api/tasks", json=task_c_data, headers=headers)

    # Filter by high priority
    response = await client.get("/api/tasks?priority=high", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    task_titles = [task["title"] for task in tasks]

    # Should contain only "Buy Milk" (high priority)
    assert "Buy Milk" in task_titles
    assert "Walk Dog" not in task_titles
    assert "Buy Eggs" not in task_titles
    assert len(tasks) == 1

    # Verify all returned tasks have high priority
    for task in tasks:
        assert task["priority"] == "high"

    # Filter by low priority
    response = await client.get("/api/tasks?priority=low", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    task_titles = [task["title"] for task in tasks]

    # Should contain only "Walk Dog" (low priority)
    assert "Walk Dog" in task_titles
    assert len(tasks) == 1

    # Filter by medium priority
    response = await client.get("/api/tasks?priority=medium", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    task_titles = [task["title"] for task in tasks]

    # Should contain only "Buy Eggs" (medium priority)
    assert "Buy Eggs" in task_titles
    assert len(tasks) == 1

    # Test invalid priority - should return all tasks (no filtering)
    response = await client.get("/api/tasks?priority=invalid", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3  # All tasks returned


@pytest.mark.asyncio
async def test_T070_sorting_by_due_date_and_priority_works_correctly(client: AsyncClient):
    """Test T070: Sorting by due date and priority works correctly."""
    # Register and login a test user
    unique_id = str(uuid.uuid4())[:8]
    token = await register_user(client, f"test_T070_{unique_id}@example.com", "testpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create test tasks
    tomorrow = date.today() + timedelta(days=1)
    yesterday = date.today() - timedelta(days=1)
    next_week = date.today() + timedelta(weeks=1)

    # Task A: "Buy Milk", High Priority, Pending, Due Tomorrow
    task_a_data = {
        "title": "Buy Milk",
        "description": "Buy milk from the grocery store",
        "priority": "high",
        "due_date": tomorrow.isoformat()
    }
    await client.post("/api/tasks", json=task_a_data, headers=headers)

    # Task B: "Walk Dog", Low Priority, Completed, Due Yesterday
    task_b_data = {
        "title": "Walk Dog",
        "description": "Take the dog for a walk",
        "priority": "low",
        "due_date": yesterday.isoformat(),
        "completed": True
    }
    await client.post("/api/tasks", json=task_b_data, headers=headers)

    # Task C: "Buy Eggs", Medium Priority, Pending, Due Next Week
    task_c_data = {
        "title": "Buy Eggs",
        "description": "Pick up eggs from the market",
        "priority": "medium",
        "due_date": next_week.isoformat()
    }
    await client.post("/api/tasks", json=task_c_data, headers=headers)

    # Sort by due_date ascending
    response = await client.get("/api/tasks?sort_by=due_date&sort_order=asc", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    tasks_with_due_dates = [task for task in tasks if task["due_date"]]

    # Should be ordered: Yesterday (Walk Dog) -> Tomorrow (Buy Milk) -> Next Week (Buy Eggs)
    assert len(tasks_with_due_dates) == 3
    assert tasks_with_due_dates[0]["title"] == "Walk Dog"  # Yesterday
    assert tasks_with_due_dates[1]["title"] == "Buy Milk"  # Tomorrow
    assert tasks_with_due_dates[2]["title"] == "Buy Eggs"  # Next Week

    # Sort by due_date descending
    response = await client.get("/api/tasks?sort_by=due_date&sort_order=desc", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    tasks_with_due_dates = [task for task in tasks if task["due_date"]]

    # Should be ordered: Next Week (Buy Eggs) -> Tomorrow (Buy Milk) -> Yesterday (Walk Dog)
    assert len(tasks_with_due_dates) == 3
    assert tasks_with_due_dates[0]["title"] == "Buy Eggs"  # Next Week
    assert tasks_with_due_dates[1]["title"] == "Buy Milk"  # Tomorrow
    assert tasks_with_due_dates[2]["title"] == "Walk Dog"  # Yesterday

    # Sort by priority ascending (low -> medium -> high)
    response = await client.get("/api/tasks?sort_by=priority&sort_order=asc", headers=headers)
    assert response.status_code == 200

    tasks = response.json()

    # Should be ordered: Low (Walk Dog) -> Medium (Buy Eggs) -> High (Buy Milk)
    assert tasks[0]["priority"] == "low"
    assert tasks[1]["priority"] == "medium"
    assert tasks[2]["priority"] == "high"

    # Sort by title ascending
    response = await client.get("/api/tasks?sort_by=title&sort_order=asc", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    task_titles = [task["title"] for task in tasks]

    # Should be alphabetically ordered
    assert task_titles[0] == "Buy Eggs"
    assert task_titles[1] == "Buy Milk"
    assert task_titles[2] == "Walk Dog"


@pytest.mark.asyncio
async def test_combined_filters_work_together(client: AsyncClient):
    """Test that multiple filters can be combined."""
    # Register and login a test user
    unique_id = str(uuid.uuid4())[:8]
    token = await register_user(client, f"test_combined_{unique_id}@example.com", "testpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create test tasks
    tomorrow = date.today() + timedelta(days=1)
    yesterday = date.today() - timedelta(days=1)
    next_week = date.today() + timedelta(weeks=1)

    # Task A: "Buy Milk", High Priority, Pending, Due Tomorrow
    task_a_data = {
        "title": "Buy Milk",
        "description": "Buy milk from the grocery store",
        "priority": "high",
        "due_date": tomorrow.isoformat()
    }
    await client.post("/api/tasks", json=task_a_data, headers=headers)

    # Task B: "Walk Dog", Low Priority, Completed, Due Yesterday
    task_b_data = {
        "title": "Walk Dog",
        "description": "Take the dog for a walk",
        "priority": "low",
        "due_date": yesterday.isoformat(),
        "completed": True
    }
    await client.post("/api/tasks", json=task_b_data, headers=headers)

    # Task C: "Buy Eggs", Medium Priority, Pending, Due Next Week
    task_c_data = {
        "title": "Buy Eggs",
        "description": "Pick up eggs from the market",
        "priority": "medium",
        "due_date": next_week.isoformat()
    }
    await client.post("/api/tasks", json=task_c_data, headers=headers)

    # Search for "Buy" with status "pending"
    response = await client.get("/api/tasks?search=Buy&status=pending", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    task_titles = [task["title"] for task in tasks]

    # Should contain "Buy Milk" and "Buy Eggs" (both contain "Buy" and are pending)
    assert "Buy Milk" in task_titles
    assert "Buy Eggs" in task_titles
    assert "Walk Dog" not in task_titles
    assert len(tasks) == 2

    # Search for "Buy" with priority "high"
    response = await client.get("/api/tasks?search=Buy&priority=high", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    task_titles = [task["title"] for task in tasks]

    # Should contain only "Buy Milk" (contains "Buy" and is high priority)
    assert "Buy Milk" in task_titles
    assert "Buy Eggs" not in task_titles
    assert "Walk Dog" not in task_titles
    assert len(tasks) == 1


@pytest.mark.asyncio
async def test_default_sorting_and_empty_results(client: AsyncClient):
    """Test default behavior and edge cases."""
    # Register and login a test user
    unique_id = str(uuid.uuid4())[:8]
    token = await register_user(client, f"test_default_{unique_id}@example.com", "testpassword123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create test tasks
    tomorrow = date.today() + timedelta(days=1)
    yesterday = date.today() - timedelta(days=1)
    next_week = date.today() + timedelta(weeks=1)

    # Task A: "Buy Milk", High Priority, Pending, Due Tomorrow
    task_a_data = {
        "title": "Buy Milk",
        "description": "Buy milk from the grocery store",
        "priority": "high",
        "due_date": tomorrow.isoformat()
    }
    await client.post("/api/tasks", json=task_a_data, headers=headers)

    # Task B: "Walk Dog", Low Priority, Completed, Due Yesterday
    task_b_data = {
        "title": "Walk Dog",
        "description": "Take the dog for a walk",
        "priority": "low",
        "due_date": yesterday.isoformat(),
        "completed": True
    }
    await client.post("/api/tasks", json=task_b_data, headers=headers)

    # Task C: "Buy Eggs", Medium Priority, Pending, Due Next Week
    task_c_data = {
        "title": "Buy Eggs",
        "description": "Pick up eggs from the market",
        "priority": "medium",
        "due_date": next_week.isoformat()
    }
    await client.post("/api/tasks", json=task_c_data, headers=headers)

    # Test default sorting (should be created_at desc)
    response = await client.get("/api/tasks", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 3

    # Test search with no matches
    response = await client.get("/api/tasks?search=NonexistentTask", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 0

    # Test empty search term (should return all tasks)
    response = await client.get("/api/tasks?search=", headers=headers)
    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 3