---
name: test-generator
description: Generate comprehensive test suites for Evolution of TODO project including unit tests, integration tests, and E2E tests. Use when Claude needs to create test coverage for FastAPI backend, React frontend, MCP tools, or API endpoints based on specifications and acceptance criteria.
license: Complete terms in LICENSE.txt
---

# Test Generator

Generates test suites from specifications.

## Quick Start

Generate tests for feature:
```bash
/skill test-generator feature=todo-crud
```

## Test Types Generated

### Unit Tests
- Backend: pytest for FastAPI services
- Frontend: Vitest/Jest for React components
- Coverage: Functions, methods, classes
- Mocking: External dependencies

### Integration Tests
- API endpoints with authentication
- Database operations
- MCP tool invocations
- Service interactions

### E2E Tests
- Playwright user journeys
- Cross-browser testing
- Visual regression tests
- Complete workflows

## Implementation Steps

### 1. Analyze Specifications
Read from spec files:
- Acceptance criteria (SC-XXX)
- User stories
- Functional requirements
- Edge cases

### 2. Generate Test Structure
Create test files:
```python
backend/tests/test_{feature}.py
frontend/tests/{component}.test.tsx
e2e/tests/{workflow}.spec.ts
```

### 3. Write Test Cases
Map requirements to tests:
```python
def test_feature_success(self):
    """
    SC-XXX: Feature requirement
    Given: Precondition
    When: Action
    Then: Expected result
    """
```

### 4. Add Test Infrastructure
Configure test runners:
- `pytest.ini` for backend
- `vitest.config.ts` for frontend
- `playwright.config.ts` for E2E

### 5. Setup CI Integration
GitHub Actions workflow:
- Run tests on PR/push
- Generate coverage reports
- Upload to codecov

## Example Generated Test

### Backend Unit Test
```python
# backend/tests/test_tasks.py
"""
Tests for Task CRUD operations
[Task]: T-Test-001
[From]: specs/001-todo-crud/spec.md §3
"""
import pytest
from fastapi.testclient import TestClient

class TestTaskCreation:
    def test_create_task_success(self, client, auth_headers):
        """SC-001: API creates task and returns 201"""
        response = client.post(
            "/api/tasks",
            json={"title": "New Task", "description": "Test"},
            headers=auth_headers
        )
        assert response.status_code == 201
        assert response.json()["title"] == "New Task"
```

### Frontend Component Test
```tsx
// frontend/tests/TodoList.test.tsx
import { render, screen } from '@testing-library/react'
import TodoList from '../components/TodoList'

test('displays task items', () => {
  render(<TodoList tasks={[{id: 1, title: 'Test'}]} />)
  expect(screen.getByText('Test')).toBeInTheDocument()
})
```

### E2E Workflow Test
```ts
// e2e/tests/task-management.spec.ts
import { test, expect } from '@playwright/test'

test('complete task workflow', async ({ page }) => {
  await page.goto('/')
  await page.fill('[data-testid=new-task]', 'Buy milk')
  await page.click('[data-testid=add-button]')
  await expect(page.locator('text=Buy milk')).toBeVisible()
})
```

## Test Configuration

### Backend (pytest.ini)
```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = --cov=src --cov-report=html --cov-fail-under=80
```

### Frontend (vitest.config.ts)
```typescript
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: { reporter: ['text', 'html'] }
  }
})
```

## Success Criteria

Test generation complete when:
- [ ] All acceptance criteria have tests
- [ ] Coverage >= 80%
- [ ] Tests pass locally
- [ ] CI workflow configured
- [ ] E2E tests cover main flows
- [ ] Integration tests verify APIs

## Test Categories

### Happy Path Tests
- Normal operation flows
- Expected user interactions
- Successful API responses

### Edge Case Tests
- Empty inputs
- Boundary conditions
- Error scenarios
- Invalid data

### Security Tests
- Authentication required
- Authorization checks
- Input validation
- SQL injection prevention

### Performance Tests
- Load testing
- Response time limits
- Concurrent users
- Database query efficiency