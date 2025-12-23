---
name: "e2e-tester"
description: "Creates and runs comprehensive end-to-end tests for the Evolution of TODO project. Tests complete user workflows across frontend and backend, validates API integrations, and verifies production deployments. Works with pytest, Playwright, and production testing."
version: "1.0.0"
---

# E2E Tester Skill

Creates and runs end-to-end tests that validate complete user workflows across the full stack.

## When to Use

Use this skill when:
- User says "run E2E tests" or "test the full flow"
- Need to validate production deployments
- Testing complete user workflows
- Verifying frontend-backend integration
- Validating AI chatbot functionality
- Testing conversation persistence

## Context

This skill provides E2E testing for:
- **Phase II**: Full-stack web app (FastAPI + Next.js)
- **Phase III**: AI chatbot with MCP tools
- **Phase IV**: Kubernetes deployments
- **Production**: Testing deployed services on Vercel

## Quick Start

```bash
# Run all E2E tests
python tests/test_e2e_functional.py

# Run production chat test
python tests/test_production_chat.py

# Run conversation persistence test
python tests/test_conversation_persistence.py
```

## Test Structure

### E2E Test Template

```python
#!/usr/bin/env python3
"""
End-to-end test for [Feature]

Tests complete user workflow:
1. User registration/login
2. [Feature] usage
3. Verification in database
"""

import requests
import time
import json

BACKEND_URL = "https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app"
FRONTEND_URL = "https://frontend-l0e30jmlq-hamdanprofessionals-projects.vercel.app"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def main():
    print_section("[FEATURE] E2E Test")

    timestamp = int(time.time())
    test_user = {
        "email": f"e2e{timestamp}@example.com",
        "password": "E2ETest123!",
        "name": "E2E Test User"
    }

    # Step 1: Register/Login
    print_section("1. Authentication")

    response = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)

    if response.status_code in [200, 201]:
        token = response.json().get("access_token")
        print(f"[OK] Registered and logged in")
    else:
        # Try login
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        token = response.json().get("access_token")
        print(f"[OK] Logged in")

    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Test [Feature]
    print_section("2. [Feature] Workflow")

    # [Add feature-specific tests here]

    # Step 3: Verify
    print_section("3. Verification")

    # [Add verification steps here]

    print_section("Test Complete")
    print("[OK] All checks passed")

if __name__ == "__main__":
    main()
```

## Production Testing

### Test Production Chat

```python
#!/usr/bin/env python3
"""Test production chat functionality."""

import requests
import json

BACKEND_URL = "https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app"

# Login
response = requests.post(f"{BACKEND_URL}/api/auth/login", json={
    "email": "test@example.com",
    "password": "test1234"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test chat with MCP tools
response = requests.post(
    f"{BACKEND_URL}/api/chat",
    headers=headers,
    json={"message": "Create a task to buy groceries"}
)

data = response.json()

# Verify tool was called
tool_calls = data.get("tool_calls", [])
assert any(tc.get("name") == "add_task" for tc in tool_calls if tc), "add_task tool not called"

print("[OK] MCP tools working in production")
```

## E2E Test Examples

### Task Management E2E

```python
def test_task_crud_workflow():
    """Test complete task CRUD workflow."""

    # Setup: Login
    token = login_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    response = requests.post(
        f"{BACKEND_URL}/api/tasks",
        headers=headers,
        json={"title": "E2E Test Task"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    # Read
    response = requests.get(f"{BACKEND_URL}/api/tasks", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert any(t["id"] == task_id for t in tasks)

    # Update (Complete)
    response = requests.patch(
        f"{BACKEND_URL}/api/tasks/{task_id}/complete",
        headers=headers
    )
    assert response.status_code == 200

    # Delete
    response = requests.delete(
        f"{BACKEND_URL}/api/tasks/{task_id}",
        headers=headers
    )
    assert response.status_code == 204
```

### AI Chatbot E2E

```python
def test_ai_chatbot_workflow():
    """Test AI chatbot with MCP tools."""

    token = login_user()
    headers = {"Authorization": f"Bearer {token}"}

    # Test 1: Create task via AI
    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        headers=headers,
        json={"message": "Create a task to test AI"}
    )

    assert response.status_code == 200
    data = response.json()
    tool_calls = data.get("tool_calls", [])

    # Verify MCP tool called
    assert any(tc.get("name") == "add_task" for tc in tool_calls if tc)

    # Test 2: List tasks via AI
    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        headers=headers,
        json={"message": "Show me my tasks"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify list_tasks tool called
    tool_calls = data.get("tool_calls", [])
    assert any(tc.get("name") == "list_tasks" for tc in tool_calls if tc)

    # Test 3: Conversation persistence
    conv_id = data.get("conversation_id")
    assert conv_id is not None

    response = requests.get(
        f"{BACKEND_URL}/api/chat/conversations/{conv_id}/messages",
        headers=headers
    )
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) >= 2
```

## Output Format

After running E2E tests, provide:

```markdown
## E2E Test Results

### Summary
- **Total Tests**: X
- **Passed**: Y
- **Failed**: Z
- **Duration**: XXs

### Test Results
| Test | Status | Details |
|------|--------|---------|
| Authentication | [OK/FAIL] | [Details] |
| Task CRUD | [OK/FAIL] | [Details] |
| AI Chatbot | [OK/FAIL] | [Details] |
| MCP Tools | [OK/FAIL] | [Details] |
| Conversations | [OK/FAIL] | [Details] |

### Production URLs Tested
- Frontend: https://frontend-...
- Backend: https://backend-...

### Issues Found
1. [Any issues discovered]
```

## Quality Checklist

Before considering E2E tests complete:
- [ ] All critical user flows tested
- [ ] Tests run against production URLs
- [ ] MCP tools validated
- [ ] Conversation persistence verified
- [ ] Error scenarios tested
- [ ] Tests are reproducible
- [ ] Test data cleaned up after
- [ ] Results documented
