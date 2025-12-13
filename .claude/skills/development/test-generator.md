# Test Generator Skill

**Type**: Agent Skill
**Category**: Development
**Phases**: Phase II+

---

## Purpose

This skill generates comprehensive test suites for the Evolution of TODO project, including unit tests, integration tests, and E2E tests based on the spec and acceptance criteria.

---

## Skill Invocation

```
/skill test-generator feature=todo-crud
```

---

## What This Skill Does

1. **Analyzes Specifications**
   - Reads acceptance criteria from spec.md
   - Identifies testable requirements
   - Maps user stories to test scenarios
   - Extracts edge cases

2. **Generates Unit Tests**
   - Backend: pytest tests for FastAPI
   - Frontend: Jest/Vitest tests for React components
   - Coverage for all functions/components
   - Mock external dependencies

3. **Creates Integration Tests**
   - API endpoint tests
   - Database interaction tests
   - MCP tool tests
   - Service integration tests

4. **Builds E2E Tests**
   - Playwright tests for user flows
   - Complete user journey testing
   - Cross-browser testing
   - Visual regression tests

5. **Adds Test Infrastructure**
   - Test configuration files
   - CI/CD integration
   - Coverage reporting
   - Test data fixtures

---

## Example: Phase I Tests (Python Console App)

### Generated: `tests/test_task_manager.py`
```python
"""
Unit tests for Task Manager (Phase I)
Generated from specs/001-todo-crud/spec.md

[Task]: T-Test-001
[From]: specs/001-todo-crud/spec.md §3 (Acceptance Criteria)
"""
import pytest
from src.main import TaskManager, Task

class TestTaskCreation:
    """Test Suite: FR-001 - Add Task"""

    def setup_method(self):
        """Setup: Create fresh TaskManager for each test"""
        self.manager = TaskManager()

    def test_add_task_with_valid_title(self):
        """
        SC-001: User can create task with title and description
        Given: Empty task list
        When: User adds task with title "Buy groceries" and description "Milk, eggs"
        Then: Task is created with ID 1 and status "pending"
        """
        task = self.manager.add_task("Buy groceries", "Milk, eggs")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs"
        assert task.completed == False
        assert len(self.manager.list_tasks()) == 1

    def test_add_task_without_description(self):
        """
        SC-002: User can create task with title only
        Given: Empty task list
        When: User adds task with title "Call mom" and no description
        Then: Task is created with empty description
        """
        task = self.manager.add_task("Call mom")

        assert task.id == 1
        assert task.title == "Call mom"
        assert task.description == ""

    def test_add_task_increments_id(self):
        """
        SC-003: Task IDs auto-increment
        Given: Task list with 2 tasks
        When: User adds a third task
        Then: New task gets ID 3
        """
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        task3 = self.manager.add_task("Task 3")

        assert task3.id == 3

    def test_add_task_with_empty_title_raises_error(self):
        """
        SC-004: Empty title is rejected
        Given: Empty task list
        When: User tries to add task with empty title
        Then: ValueError is raised
        """
        with pytest.raises(ValueError, match="Title cannot be empty"):
            self.manager.add_task("")

class TestTaskRetrieval:
    """Test Suite: FR-002 - View Tasks"""

    def setup_method(self):
        self.manager = TaskManager()
        self.manager.add_task("Task 1", "Description 1")
        self.manager.add_task("Task 2", "Description 2")

    def test_list_all_tasks(self):
        """
        SC-005: User can view all tasks
        Given: Task list with 2 tasks
        When: User requests task list
        Then: All 2 tasks are returned
        """
        tasks = self.manager.list_tasks()

        assert len(tasks) == 2
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"

    def test_list_tasks_empty(self):
        """
        SC-006: Empty task list returns empty array
        Given: Empty task list
        When: User requests task list
        Then: Empty list is returned
        """
        manager = TaskManager()
        tasks = manager.list_tasks()

        assert tasks == []

class TestTaskUpdate:
    """Test Suite: FR-003 - Update Task"""

    def setup_method(self):
        self.manager = TaskManager()
        self.task = self.manager.add_task("Original Title", "Original Desc")

    def test_update_task_title(self):
        """
        SC-007: User can update task title
        Given: Task with ID 1 exists
        When: User updates title to "Updated Title"
        Then: Task title is changed
        """
        self.manager.update_task(1, title="Updated Title")
        task = self.manager.get_task(1)

        assert task.title == "Updated Title"
        assert task.description == "Original Desc"  # Unchanged

    def test_update_nonexistent_task_raises_error(self):
        """
        SC-008: Updating non-existent task raises error
        Given: Task list with task ID 1
        When: User tries to update task ID 999
        Then: ValueError is raised
        """
        with pytest.raises(ValueError, match="Task not found"):
            self.manager.update_task(999, title="New Title")

# ... more test classes for Delete, Complete, etc.
```

---

## Example: Phase II Tests (FastAPI Backend)

### Generated: `backend/tests/test_api.py`
```python
"""
Integration tests for Task API (Phase II)
Generated from specs/001-todo-crud/spec.md

[Task]: T-Test-002
[From]: specs/001-todo-crud/plan.md §4 (API Endpoints)
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_session
from models import Task

@pytest.fixture
def client():
    """Test client with in-memory database"""
    # Override database dependency with test DB
    def override_get_session():
        # Use in-memory SQLite for tests
        pass

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_headers():
    """Generate JWT token for authenticated requests"""
    # Create test user and generate token
    token = generate_test_token(user_id="test-user")
    return {"Authorization": f"Bearer {token}"}

class TestTaskAPI:
    """API Endpoint Tests"""

    def test_create_task_success(self, client, auth_headers):
        """
        POST /api/{user_id}/tasks - Success case
        SC-009: API creates task and returns 201
        """
        response = client.post(
            "/api/test-user/tasks",
            json={"title": "New Task", "description": "Test"},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert "id" in data

    def test_create_task_unauthorized(self, client):
        """
        POST /api/{user_id}/tasks - No auth token
        SC-010: API returns 401 for unauthenticated requests
        """
        response = client.post(
            "/api/test-user/tasks",
            json={"title": "New Task"}
        )

        assert response.status_code == 401

    def test_create_task_wrong_user(self, client, auth_headers):
        """
        POST /api/{user_id}/tasks - Token user mismatch
        SC-011: API returns 403 if token user != URL user
        """
        response = client.post(
            "/api/different-user/tasks",
            json={"title": "New Task"},
            headers=auth_headers
        )

        assert response.status_code == 403

    def test_get_tasks_filters_by_user(self, client, auth_headers):
        """
        GET /api/{user_id}/tasks - User isolation
        SC-012: API returns only authenticated user's tasks
        """
        # Create tasks for different users
        # ... setup code ...

        response = client.get(
            "/api/test-user/tasks",
            headers=auth_headers
        )

        tasks = response.json()
        assert all(task["user_id"] == "test-user" for task in tasks)
```

---

## Example: Phase III Tests (MCP Tools)

### Generated: `mcp-server/tests/test_tools.py`
```python
"""
MCP Tool Tests (Phase III)
Generated from specs/001-todo-crud/contracts/mcp-tools.md

[Task]: T-Test-003
[From]: specs/001-todo-crud/spec.md §5 (MCP Tools)
"""
import pytest
from server import mcp_server

@pytest.mark.asyncio
class TestMCPTools:
    """MCP Tool Invocation Tests"""

    async def test_add_task_tool(self):
        """
        Tool: add_task
        SC-013: MCP tool creates task via stateless call
        """
        result = await mcp_server.call_tool(
            "add_task",
            arguments={
                "user_id": "test-user",
                "title": "MCP Task",
                "description": "Created via MCP"
            }
        )

        assert result["status"] == "created"
        assert result["task_id"] is not None
        assert result["title"] == "MCP Task"

    async def test_list_tasks_tool(self):
        """
        Tool: list_tasks
        SC-014: MCP tool retrieves user's tasks
        """
        # Create test tasks first
        # ... setup ...

        result = await mcp_server.call_tool(
            "list_tasks",
            arguments={
                "user_id": "test-user",
                "status": "all"
            }
        )

        assert isinstance(result, list)
        assert len(result) > 0
```

---

## Test Configuration Files

### `backend/pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --cov=src
    --cov-report=html
    --cov-report=term
    --cov-fail-under=80
```

### `frontend/vitest.config.ts`
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['**/*.config.{ts,js}', '**/node_modules/**']
    }
  }
})
```

---

## CI Integration

### `.github/workflows/test.yml`
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ --cov --cov-report=xml
      - uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
        working-directory: frontend
      - run: npm test -- --coverage
        working-directory: frontend
```

---

## Success Criteria

Test generation is successful when:

1. ✅ All acceptance criteria have tests
2. ✅ Coverage >= 80%
3. ✅ Tests pass in CI/CD
4. ✅ Edge cases covered
5. ✅ Integration tests included
6. ✅ E2E tests for user flows

---

**Skill Version**: 1.0.0
**Created**: 2025-12-13
**Phase**: II+
