# E2E Testing Example - Evolution of TODO Production

This example shows the actual testing patterns used in the Evolution of TODO project for testing production deployments.

## Comprehensive Test Script (tests/test_chatbot.py)

```python
#!/usr/bin/env python3
"""
Comprehensive Chatbot Testing Script
Tests the deployed Todo AI Assistant with both mock and real AI functionality
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, List

class ChatbotTester:
    def __init__(self):
        self.frontend_url = "https://frontend-hamdanprofessionals-projects.vercel.app"
        self.backend_url = "https://backend-hamdanprofessionals-projects.vercel.app"
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []

    def log_result(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status_icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")

    def test_backend_connectivity(self):
        """Test if backend is accessible"""
        try:
            response = self.session.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Backend Health Check", "PASS", f"Status: {data.get('status')}")
                return True
            else:
                self.log_result("Backend Health Check", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Backend Health Check", "FAIL", str(e))
            return False

    def test_frontend_connectivity(self):
        """Test if frontend is accessible"""
        try:
            response = self.session.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.log_result("Frontend Connectivity", "PASS", f"HTTP {response.status_code}")
                return True
            else:
                self.log_result("Frontend Connectivity", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Frontend Connectivity", "FAIL", str(e))
            return False

    def register_test_user(self):
        """Register a test user for testing"""
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": test_email,
            "password": "TestPassword123!",
            "name": "Test User"
        }

        try:
            response = self.session.post(f"{self.backend_url}/api/auth/register",
                                       json=payload, timeout=10)
            if response.status_code in [200, 201]:
                data = response.json()
                self.user_id = data.get("id")
                self.log_result("User Registration", "PASS", f"User ID: {self.user_id}")
                return test_email
            else:
                self.log_result("User Registration", "FAIL", f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_result("User Registration", "FAIL", str(e))
            return None

    def login_user(self, email: str):
        """Login and get auth token"""
        payload = {
            "email": email,
            "password": "TestPassword123!"
        }

        try:
            response = self.session.post(f"{self.backend_url}/api/auth/login",
                                       json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_result("User Login", "PASS", "Authentication successful")
                return True
            else:
                self.log_result("User Login", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("User Login", "FAIL", str(e))
            return False

    def test_task_operations(self):
        """Test all task CRUD operations"""
        if not self.auth_token:
            self.log_result("Task Operations", "SKIP", "No auth token")
            return

        # Test creating a task
        task_payload = {
            "title": "Test Task from Chatbot",
            "description": "This is a test task created during automated testing",
            "priority_id": 1
        }

        try:
            # Create task
            response = self.session.post(f"{self.backend_url}/api/tasks/",
                                       json=task_payload, timeout=10)
            if response.status_code in [200, 201]:
                task_data = response.json()
                task_id = task_data.get("id")
                self.log_result("Task Creation", "PASS", f"Task ID: {task_id}")

                # List tasks
                response = self.session.get(f"{self.backend_url}/api/tasks/", timeout=10)
                if response.status_code == 200:
                    tasks = response.json()
                    self.log_result("Task Listing", "PASS", f"Found {len(tasks)} tasks")
                else:
                    self.log_result("Task Listing", "FAIL", f"HTTP {response.status_code}")

                # Update task
                update_payload = {"completed": True}
                response = self.session.patch(f"{self.backend_url}/api/tasks/{task_id}/complete",
                                            json=update_payload, timeout=10)
                if response.status_code == 200:
                    self.log_result("Task Update", "PASS", "Task marked as completed")
                else:
                    self.log_result("Task Update", "FAIL", f"HTTP {response.status_code}")

                # Delete task
                response = self.session.delete(f"{self.backend_url}/api/tasks/{task_id}", timeout=10)
                if response.status_code == 204:
                    self.log_result("Task Deletion", "PASS", "Task deleted successfully")
                else:
                    self.log_result("Task Deletion", "FAIL", f"HTTP {response.status_code}")

            else:
                self.log_result("Task Creation", "FAIL", f"HTTP {response.status_code}")

        except Exception as e:
            self.log_result("Task Operations", "FAIL", str(e))

    def test_chat_endpoint(self):
        """Test the chat endpoint with various messages"""
        if not self.auth_token:
            self.log_result("Chat Endpoint", "SKIP", "No auth token")
            return

        test_messages = [
            "Hello, can you help me manage my tasks?",
            "Create a new task called 'Review project documentation'",
            "Show me all my tasks",
            "What tasks do I have pending?",
        ]

        for i, message in enumerate(test_messages):
            try:
                payload = {"message": message}
                response = self.session.post(f"{self.backend_url}/api/chat/",
                                           json=payload, timeout=30)

                if response.status_code == 200:
                    chat_response = response.json()
                    if "response" in chat_response or "message" in chat_response:
                        response_text = chat_response.get("response", chat_response.get("message", ""))
                        self.log_result(f"Chat Message {i+1}", "PASS",
                                      f"Response length: {len(response_text)} chars")
                    else:
                        self.log_result(f"Chat Message {i+1}", "FAIL",
                                      "No response field in API response")
                else:
                    self.log_result(f"Chat Message {i+1}", "FAIL",
                                  f"HTTP {response.status_code}")

                time.sleep(1)

            except Exception as e:
                self.log_result(f"Chat Message {i+1}", "FAIL", str(e))

    def test_cors_configuration(self):
        """Test CORS configuration between frontend and backend"""
        try:
            headers = {"Origin": self.frontend_url}
            response = self.session.options(f"{self.backend_url}/health",
                                          headers=headers, timeout=10)

            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }

            if cors_headers["Access-Control-Allow-Origin"]:
                self.log_result("CORS Configuration", "PASS",
                              f"Origin allowed: {cors_headers['Access-Control-Allow-Origin']}")
            else:
                self.log_result("CORS Configuration", "WARN", "No CORS headers detected")

        except Exception as e:
            self.log_result("CORS Configuration", "FAIL", str(e))

    def run_all_tests(self):
        """Run all tests and generate report"""
        print("Starting Comprehensive Chatbot Testing")
        print("=" * 50)

        # Connectivity tests
        self.test_backend_connectivity()
        self.test_frontend_connectivity()
        self.test_cors_configuration()

        # Authentication tests
        print("\nAuthentication Tests")
        print("-" * 30)
        test_email = self.register_test_user()
        if test_email:
            self.login_user(test_email)

        # Task management tests
        print("\nTask Management Tests")
        print("-" * 30)
        self.test_task_operations()

        # Chat functionality tests
        print("\nChat Functionality Tests")
        print("-" * 30)
        self.test_chat_endpoint()

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warned_tests = len([r for r in self.test_results if r["status"] == "WARN"])

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Warnings: {warned_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")

        # Save detailed report
        with open("chatbot_test_report.json", "w") as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "warned": warned_tests,
                    "success_rate": passed_tests/total_tests*100
                },
                "results": self.test_results
            }, f, indent=2)

        print(f"\nDetailed report saved to: chatbot_test_report.json")

if __name__ == "__main__":
    tester = ChatbotTester()
    tester.run_all_tests()
```

## Pytest Backend Tests

```python
# tests/test_tasks_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db
from app.models.user import User
from app.core.security import create_access_token


class TestTasksAPI:
    """Test task CRUD operations."""

    @pytest.fixture
    async def test_user(self, db: AsyncSession):
        """Create a test user."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @pytest.fixture
    def auth_headers(self, test_user: User):
        """Create auth headers for test user."""
        token = create_access_token(data={"sub": str(test_user.id)})
        return {"Authorization": f"Bearer {token}"}

    def test_create_task(self, client: TestClient, auth_headers: dict):
        """Test creating a new task."""
        response = client.post(
            "/api/tasks",
            json={"title": "Test Task", "description": "Test description"},
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["completed"] is False

    def test_get_tasks(self, client: TestClient, auth_headers: dict):
        """Test getting all tasks."""
        response = client.get("/api/tasks", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_update_task(self, client: TestClient, auth_headers: dict):
        """Test updating a task."""
        # First create a task
        create_response = client.post(
            "/api/tasks",
            json={"title": "Original Title"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Update the task
        response = client.put(
            f"/api/tasks/{task_id}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_delete_task(self, client: TestClient, auth_headers: dict):
        """Test deleting a task."""
        # First create a task
        create_response = client.post(
            "/api/tasks",
            json={"title": "To Delete"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Delete the task
        response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify task is gone
        get_response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
        assert get_response.status_code == 404


# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base


@pytest.fixture
async def engine():
    """Create test database engine."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db(engine):
    """Create test database session."""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(db: AsyncSession):
    """Create test client with database override."""
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

## Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks_api.py

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x

# Run E2E tests against production
python tests/test_chatbot.py
```

## Key Testing Patterns

### 1. Test Organization
- Unit tests for individual functions
- Integration tests for API endpoints
- E2E tests for full user flows
- Separate test database (SQLite in-memory)

### 2. Fixtures
- Create test data with fixtures
- Clean up after tests
- Override dependencies (like database)

### 3. Authentication
- Create test users
- Generate JWT tokens
- Pass auth headers in requests

### 4. Assertions
- Check status codes
- Verify response structure
- Validate data integrity

### 5. Error Cases
- Test unauthorized access
- Test invalid input
- Test missing resources
