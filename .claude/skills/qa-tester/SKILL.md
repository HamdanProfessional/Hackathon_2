---
name: qa-tester
description: Write pytest tests in tests/test_api.py with @pytest.fixture for test setup, def test_create_task() for CRUD validation, and AsyncClient for FastAPI integration tests. Create Playwright E2E tests in tests/e2e/ with test('user logs in and creates task', async ({ page }) => { await page.fill()... }). Generate Jest/Vitest tests in frontend/components/__tests__/ with describe() and it() blocks. Measure coverage via pytest --cov=backend --cov-report=html. Use when validating POST /api/tasks, testing JWT login flows, or ensuring MCP tools are invoked by AI.
---

# QA Tester Skill

Write pytest tests for FastAPI, Playwright E2E tests for user workflows, and Jest tests for React components.

## File Structure

```
tests/
├── backend/
│   ├── test_tasks.py       # FastAPI endpoint tests
│   ├── test_auth.py        # Authentication tests
│   ├── test_chat.py        # AI chat integration tests
│   └── conftest.py         # Shared fixtures
├── frontend/
│   ├── TaskForm.test.tsx   # Component unit tests
│   ├── setup.ts            # Test setup for Jest
│   └── test-utils.tsx      # Testing utilities
└── e2e/
    ├── auth-flow.spec.ts   # Login/registration E2E
    ├── task-flow.spec.ts   # Task CRUD E2E
    └── chat-flow.spec.ts   # AI chat E2E tests
```

## Quick Reference

| Action | Command | File |
|--------|---------|------|
| Run backend tests | `cd backend && pytest tests/ -v` | All backend tests |
| Run with coverage | `pytest tests/ --cov=app --cov-report=html` | Coverage report |
| Run specific test | `pytest tests/test_tasks.py::test_create_task -v` | Single test |
| Run frontend tests | `cd frontend && npm test` | Jest tests |
| Run E2E tests | `npx playwright test` | Playwright tests |
| Run E2E with UI | `npx playwright test --ui` | Playwright UI mode |
| Run E2E headed | `npx playwright test --headed` | Show browser |
| Coverage threshold | `pytest --cov=app --cov-fail-under=80` | Enforce 80% coverage |

## When to Use This Skill

| User Request | Action | Files to Create |
|--------------|--------|-----------------|
| "Test the task API" | Write pytest tests for CRUD | `tests/backend/test_tasks.py` |
| "Test authentication" | Write login/register tests | `tests/backend/test_auth.py` |
| "Test E2E flow" | Create Playwright test | `tests/e2e/task-flow.spec.ts` |
| "Test React component" | Write Jest component test | `tests/frontend/TaskForm.test.tsx` |
| "Check coverage" | Run pytest with --cov | Coverage report in htmlcov/ |
| "Test MCP tools" | Write AI tool invocation test | `tests/backend/test_mcp_tools.py` |

---

## Part 1: Backend Pytest Tests

### File: tests/backend/test_tasks.py

```python
"""
Tests for Task API endpoints.
File: tests/backend/test_tasks.py
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestTaskCRUD:
    """Test CRUD operations for tasks."""

    @pytest.mark.asyncio
    async def test_create_task(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test POST /api/tasks creates a new task."""
        response = await async_client.post(
            "/api/tasks/",
            json={
                "title": "Test Task",
                "description": "Test description",
                "priority": "high"
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test description"
        assert data["priority"] == "high"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_list_tasks(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_task: dict
    ):
        """Test GET /api/tasks returns user's tasks."""
        response = await async_client.get(
            "/api/tasks/",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_get_task_by_id(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_task: dict
    ):
        """Test GET /api/tasks/{id} returns task."""
        response = await async_client.get(
            f"/api/tasks/{test_task['id']}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task["id"]

    @pytest.mark.asyncio
    async def test_update_task(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_task: dict
    ):
        """Test PATCH /api/tasks/{id} updates task."""
        response = await async_client.patch(
            f"/api/tasks/{test_task['id']}",
            json={"status": "completed"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_delete_task(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_task: dict
    ):
        """Test DELETE /api/tasks/{id} removes task."""
        response = await async_client.delete(
            f"/api/tasks/{test_task['id']}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify task is deleted
        get_response = await async_client.get(
            f"/api/tasks/{test_task['id']}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_unauthorized_access(
        self,
        async_client: AsyncClient
    ):
        """Test that requests without JWT token are rejected."""
        response = await async_client.get("/api/tasks/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_user_isolation(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        async_session: AsyncSession,
        test_user_id: str
    ):
        """Test User A cannot access User B's tasks."""
        # Create task for different user
        from app.models.task import Task
        from uuid import uuid4

        other_task = Task(
            user_id=uuid4(),  # Different user
            title="Other User Task"
        )
        async_session.add(other_task)
        await async_session.commit()

        # Try to access with different user token
        response = await async_client.get(
            f"/api/tasks/{other_task.id}",
            headers=auth_headers
        )
        assert response.status_code == 404  # Should not find other user's data


class TestTaskStatistics:
    """Test task statistics endpoint."""

    @pytest.mark.asyncio
    async def test_task_statistics(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test GET /api/tasks/stats/summary returns stats."""
        response = await async_client.get(
            "/api/tasks/stats/summary",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "pending" in data
        assert "in_progress" in data
        assert "completed" in data
        assert "completion_rate" in data
```

### File: tests/backend/conftest.py

```python
"""
Pytest configuration and fixtures.
File: tests/backend/conftest.py
"""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base
from app.models.task import Task
from app.models.user import User


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost/test_db"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_engine():
    """Create async engine for testing."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession]:
    """Create async session for testing."""
    async_session_maker = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def async_client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """Create async client for testing."""
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_id() -> str:
    """Return test user ID."""
    from uuid import uuid4
    return str(uuid4())


@pytest.fixture
def auth_headers(test_user_id: str) -> dict:
    """Return auth headers with JWT token."""
    from app.auth.jwt import create_access_token
    token = create_access_token(data={"sub": test_user_id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_task(async_session: AsyncSession, test_user_id: str) -> dict:
    """Create a test task in database."""
    task = Task(
        title="Test Task",
        description="Test description",
        user_id=test_user_id,
        priority="normal"
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority
    }
```

### Run Backend Tests

```bash
cd backend
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks.py -v

# Run specific test
pytest tests/test_tasks.py::TestTaskCRUD::test_create_task -v

# Run with coverage threshold
pytest tests/ --cov=app --cov-fail-under=80
```

---

## Part 2: Authentication Tests

### File: tests/backend/test_auth.py

```python
"""
Tests for authentication endpoints.
File: tests/backend/test_auth.py
"""
import pytest
from httpx import AsyncClient


class TestAuthentication:
    """Test login and registration flows."""

    @pytest.mark.asyncio
    async def test_register_user(self, async_client: AsyncClient):
        """Test POST /api/auth/register creates new user."""
        response = await async_client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "full_name": "Test User"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client: AsyncClient):
        """Test registration with duplicate email fails."""
        # First registration
        await async_client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "Pass123!"}
        )

        # Duplicate registration
        response = await async_client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "Pass123!"}
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient):
        """Test POST /api/auth/login with valid credentials."""
        # Register user first
        await async_client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "Pass123!"}
        )

        # Login
        response = await async_client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "Pass123!"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, async_client: AsyncClient):
        """Test login with wrong password returns 401."""
        response = await async_client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "WrongPassword"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(
        self,
        async_client: AsyncClient
    ):
        """Test accessing protected endpoint without token returns 401."""
        response = await async_client.get("/api/tasks/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_invalid_token(
        self,
        async_client: AsyncClient
    ):
        """Test accessing protected endpoint with invalid token returns 401."""
        response = await async_client.get(
            "/api/tasks/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
```

---

## Part 3: MCP Tool Tests

### File: tests/backend/test_mcp_tools.py

```python
"""
Tests for MCP tool invocation by AI agent.
File: tests/backend/test_mcp_tools.py
"""
import pytest
from httpx import AsyncClient


class TestMCPToolInvocation:
    """Test that AI agent invokes MCP tools correctly."""

    @pytest.mark.asyncio
    async def test_agent_invokes_get_tasks_tool(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test AI agent invokes get_tasks tool when user asks for tasks."""
        response = await async_client.post(
            "/api/chat/message",
            json={"message": "Show me my tasks"},
            headers=auth_headers
        )

        assert response.status_code == 200
        # Verify AI responded
        assert "response" in response.json()

    @pytest.mark.asyncio
    async def test_agent_invokes_create_task_tool(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test AI agent invokes create_task tool."""
        response = await async_client.post(
            "/api/chat/message",
            json={"message": "Create a task called 'Buy groceries'"},
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify task was actually created
        tasks_response = await async_client.get(
            "/api/tasks/",
            headers=auth_headers
        )
        tasks = tasks_response.json()["items"]
        assert any(t["title"] == "Buy groceries" for t in tasks)

    @pytest.mark.asyncio
    async def test_agent_invokes_update_task_tool(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_task: dict
    ):
        """Test AI agent invokes update_task tool."""
        response = await async_client.post(
            "/api/chat/message",
            json={"message": f"Mark task {test_task['id']} as complete"},
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify task was updated
        task_response = await async_client.get(
            f"/api/tasks/{test_task['id']}",
            headers=auth_headers
        )
        assert task_response.json()["status"] == "completed"

    @pytest.mark.asyncio
    async def test_agent_invokes_delete_task_tool(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_task: dict
    ):
        """Test AI agent invokes delete_task tool."""
        response = await async_client.post(
            "/api/chat/message",
            json={"message": f"Delete task {test_task['id']}"},
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify task was deleted
        task_response = await async_client.get(
            f"/api/tasks/{test_task['id']}",
            headers=auth_headers
        )
        assert task_response.status_code == 404
```

---

## Part 4: Playwright E2E Tests

### File: tests/e2e/auth-flow.spec.ts

```typescript
/**
 * E2E tests for authentication flow.
 * File: tests/e2e/auth-flow.spec.ts
 */
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('user can register and login', async ({ page }) => {
    // Navigate to registration
    await page.goto('/en/register');

    // Fill registration form
    await page.fill('[name=email]', 'test@example.com');
    await page.fill('[name=password]', 'SecurePass123!');
    await page.fill('[name=full_name]', 'Test User');

    // Submit registration
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Verify JWT token stored
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
  });

  test('user can login with valid credentials', async ({ page }) => {
    // Navigate to login
    await page.goto('/en/login');

    // Fill login form
    await page.fill('[name=email]', 'test@example.com');
    await page.fill('[name=password]', 'SecurePass123!');

    // Submit login
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Verify user is logged in
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('login fails with invalid credentials', async ({ page }) => {
    // Navigate to login
    await page.goto('/en/login');

    // Fill with invalid credentials
    await page.fill('[name=email]', 'test@example.com');
    await page.fill('[name=password]', 'WrongPassword');

    // Submit login
    await page.click('button[type="submit"]');

    // Should show error message
    await expect(page.locator('text=Invalid credentials')).toBeVisible();

    // Should not redirect
    await expect(page).toHaveURL(/.*\/login/);
  });

  test('unauthorized user cannot access dashboard', async ({ page }) => {
    // Try to access dashboard without login
    await page.goto('/en/dashboard');

    // Should redirect to login
    await expect(page).toHaveURL(/.*\/login/);
  });
});
```

### File: tests/e2e/task-flow.spec.ts

```typescript
/**
 * E2E tests for task CRUD workflow.
 * File: tests/e2e/task-flow.spec.ts
 */
import { test, expect } from '@playwright/test';

test.describe('Task CRUD Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/en/login');
    await page.fill('[name=email]', 'test@example.com');
    await page.fill('[name=password]', 'SecurePass123!');
    await page.click('button[type="submit"]');
    await page.waitForURL(/.*\/dashboard/);
  });

  test('user can create a new task', async ({ page }) => {
    // Click new task button
    await page.click('text=New Task');

    // Fill task form
    await page.fill('[name=title]', 'Test Task');
    await page.fill('[name=description]', 'Test description');
    await page.selectOption('[name=priority]', 'high');

    // Submit form
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Verify task appears in list
    await expect(page.locator('text=Test Task')).toBeVisible();
  });

  test('user can update a task', async ({ page }) => {
    // Navigate to dashboard
    await expect(page.locator('text=Test Task')).isVisible();

    // Click edit button on first task
    await page.click('[data-testid="edit-task-0"]');

    // Update task
    await page.fill('[name=title]', 'Updated Task Title');

    // Submit
    await page.click('button[type="submit"]');

    // Verify update
    await expect(page.locator('text=Updated Task Title')).toBeVisible();
  });

  test('user can delete a task', async ({ page }) => {
    // Get initial task count
    const initialCount = await page.locator('[data-testid^="task-"]').count();

    // Click delete button on first task
    await page.click('[data-testid="delete-task-0"]');

    // Confirm deletion
    await page.click('button:has-text("Delete")');

    // Verify task count decreased
    const newCount = await page.locator('[data-testid^="task-"]').count();
    expect(newCount).toBe(initialCount - 1);
  });

  test('user can search tasks', async ({ page }) => {
    // Enter search query
    await page.fill('[data-testid="search-input"]', 'Test');

    // Verify filtered results
    await expect(page.locator('text=Test Task')).toBeVisible();
  });

  test('user can filter tasks by status', async ({ page }) => {
    // Click pending filter
    await page.click('button:has-text("Pending")');

    // Verify only pending tasks shown
    const tasks = await page.locator('[data-testid^="task-"]').all();
    for (const task of tasks) {
      await expect(task.locator('.status-pending')).isVisible();
    }
  });
});
```

### Run E2E Tests

```bash
# Install Playwright browsers
npx playwright install

# Run all E2E tests
npx playwright test

# Run with UI (interactive mode)
npx playwright test --ui

# Run with headed mode (show browser)
npx playwright test --headed

# Run specific test file
npx playwright test tests/e2e/auth-flow.spec.ts

# Run specific test
npx playwright test --grep "user can login"
```

---

## Part 5: Frontend Jest Tests

### File: tests/frontend/TaskForm.test.tsx

```typescript
/**
 * Unit tests for TaskForm component.
 * File: tests/frontend/TaskForm.test.tsx
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskForm from '@/components/task-form';

// Mock fetch API
global.fetch = jest.fn();

describe('TaskForm', () => {
  beforeEach(() => {
    (global.fetch as jest.Mock).mockClear();
  });

  test('renders form fields', () => {
    render(<TaskForm />);

    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create task/i })).toBeInTheDocument();
  });

  test('submits form with valid data', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, title: 'Test Task' }),
    });

    render(<TaskForm />);

    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'Test Task' }
    });
    fireEvent.change(screen.getByLabelText(/description/i), {
      target: { value: 'Test description' }
    });

    fireEvent.click(screen.getByRole('button', { name: /create task/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/tasks'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('Test Task'),
        })
      );
    });
  });

  test('displays error message on submission failure', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(
      new Error('Network error')
    );

    render(<TaskForm />);

    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'Test Task' }
    });

    fireEvent.click(screen.getByRole('button', { name: /create task/i }));

    await waitFor(() => {
      expect(screen.getByText(/failed to create task/i)).toBeInTheDocument();
    });
  });

  test('validates required fields', async () => {
    render(<TaskForm />);

    // Try to submit without filling required fields
    const submitButton = screen.getByRole('button', { name: /create task/i });
    fireEvent.click(submitButton);

    // Form should prevent submission
    expect(global.fetch).not.toHaveBeenCalled();
  });
});
```

### Run Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test TaskForm.test.tsx
```

---

## Quality Checklist

Before finalizing tests:

- [ ] **Backend Tests**: Pytest tests for all CRUD operations
- [ ] **Fixtures**: Proper pytest fixtures for database and auth
- [ ] **User Isolation**: Tests verify users can't access each other's data
- [ ] **Authentication**: Login/register/logout test coverage
- [ ] **MCP Tools**: Tests verify AI agent invokes tools correctly
- [ ] **E2E Tests**: Playwright tests for critical user journeys
- [ ] **Component Tests**: Jest tests for React components
- [ ] **Coverage**: pytest --cov shows 80%+ coverage
- [ ] **Async Tests**: All async tests use @pytest.mark.asyncio
- [ ] **Cleanup**: Test data cleaned up after tests
- [ ] **No Flaky Tests**: Tests pass consistently
- [ ] **Error Cases**: Both success and failure paths tested
- [ ] **Fast Execution**: Tests complete in reasonable time
