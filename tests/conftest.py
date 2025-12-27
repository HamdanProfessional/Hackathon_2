"""
Shared pytest fixtures for all test suites.

Provides database sessions, test clients, authenticated users,
and other common test utilities.
"""

import os
import sys
import asyncio
import pytest
import uuid
from datetime import date, datetime, timedelta
from typing import AsyncGenerator, Generator, Optional
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

# Load test environment variables
from dotenv import load_dotenv
test_env_path = os.path.join(os.path.dirname(__file__), "..", ".env.test")
if os.path.exists(test_env_path):
    load_dotenv(test_env_path, override=True)
    # Set TESTING flag for config.py
    os.environ["TESTING"] = "true"

# Add backend to path for imports
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from sqlalchemy import text

# Import database and models
from app.database import Base, get_db
from app.models.user import User
from app.models.task import Task
from app.models.recurring_task import RecurringTask
from app.models.task_event_log import TaskEventLog
from app.models.task import Priority
from app.config import settings

# Import main app
from app.main import app

# Import test helpers - use absolute import
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers'))
from dapr_client import MockDaprClient


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """
    Create PostgreSQL database engine for testing.

    Creates tables fresh for each test and drops them after.
    """
    # Get test database URL from environment or use default PostgreSQL
    test_db_url = os.getenv("TEST_DATABASE_URL",
                           "postgresql+asyncpg://postgres:postgres@localhost:5433/test_db")

    # Use PostgreSQL for JSONB support
    engine = create_async_engine(
        test_db_url,
        poolclass=NullPool,
        echo=False
    )

    # Create tables fresh for each test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Seed priorities
        insert_sql = """INSERT INTO priorities (id, name, level, color) VALUES
            (1, 'Low', 1, 'green'),
            (2, 'Medium', 2, 'yellow'),
            (3, 'High', 3, 'red')
            ON CONFLICT (id) DO NOTHING"""
        await conn.execute(text(insert_sql))

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create database session for testing.

    Since db_engine creates and drops tables for each test,
    we don't need additional cleanup.
    """
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    async with async_session() as session:
        yield session


# ============================================================================
# FastAPI Test Client Fixtures
# ============================================================================

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create FastAPI test client with database override.

    Injects test database session and provides async HTTP client.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """
    Create authenticated test user.

    Returns User instance with UUID and hashed password.
    """
    user_id = uuid.uuid4()

    # Direct DB insert for test user
    # Note: This is the correct bcrypt hash for "password123"
    user = User(
        id=user_id,
        email=f"test_{user_id.hex[:8]}@example.com",
        name="Test User",
        hashed_password="$2b$12$78dMjiOacuJ54lC12Os7FefzNRUPVTsijhYZ5ZoWdVzBSi3nfgaru"  # "password123"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture(scope="function")
async def auth_token(client: AsyncClient, test_user: User) -> str:
    """
    Get JWT authentication token for test user.

    Registers user and returns access token.
    """
    response = await client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "password123"
        }
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("access_token", "")

    # If login fails, try register
    response = await client.post(
        "/api/auth/register",
        json={
            "email": test_user.email,
            "password": "password123",
            "name": test_user.name
        }
    )

    if response.status_code in [200, 201]:
        data = response.json()
        return data.get("access_token", "")

    pytest.fail("Could not authenticate test user")


@pytest.fixture(scope="function")
def auth_headers(auth_token: str) -> dict:
    """
    Get HTTP headers with JWT authorization.

    Returns dict with Authorization header set.
    """
    return {"Authorization": f"Bearer {auth_token}"}


# ============================================================================
# Task Fixtures
# ============================================================================

@pytest.fixture(scope="function")
async def test_task(db_session: AsyncSession, test_user: User) -> Task:
    """
    Create test task for authenticated user.

    Returns Task instance with standard test data.
    """
    task = Task(
        title="Test Task",
        description="Test task description",
        user_id=str(test_user.id),
        priority_id=2,  # Medium (correct column name)
        due_date=date.today() + timedelta(days=7),
        completed=False
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    return task


@pytest.fixture(scope="function")
async def test_tasks(db_session: AsyncSession, test_user: User) -> list[Task]:
    """
    Create multiple test tasks for pagination/filtering tests.

    Returns list of 5 Task instances.
    """
    tasks = []
    priorities = [1, 2, 3, 2, 1]  # Low, Medium, High, Medium, Low

    for i, priority_id in enumerate(priorities):
        task = Task(
            title=f"Test Task {i+1}",
            description=f"Test task description {i+1}",
            user_id=str(test_user.id),
            priority_id=priority_id,  # Correct column name
            due_date=date.today() + timedelta(days=i+1),
            completed=False
        )
        db_session.add(task)
        tasks.append(task)

    await db_session.commit()
    for task in tasks:
        await db_session.refresh(task)

    return tasks


# ============================================================================
# Recurring Task Fixtures
# ============================================================================

@pytest.fixture(scope="function")
async def test_recurring_task(db_session: AsyncSession, test_user: User) -> RecurringTask:
    """
    Create test recurring task.

    Returns RecurringTask instance with daily recurrence.
    """
    recurring_task = RecurringTask(
        title="Daily Standup",
        description="Daily team standup meeting",
        user_id=str(test_user.id),
        recurrence_pattern="daily",
        start_date=date.today(),
        next_due_at=date.today() + timedelta(days=1),
        is_active=True,
        task_priority_id=2  # Medium
    )
    db_session.add(recurring_task)
    await db_session.commit()
    await db_session.refresh(recurring_task)

    return recurring_task


@pytest.fixture(scope="function")
async def test_recurring_tasks(db_session: AsyncSession, test_user: User) -> list[RecurringTask]:
    """
    Create multiple test recurring tasks.

    Returns list of 3 RecurringTask instances with different patterns.
    """
    tasks = [
        RecurringTask(
            title="Daily Standup",
            description="Daily team standup",
            user_id=str(test_user.id),
            recurrence_pattern="daily",
            start_date=date.today(),
            next_due_at=date.today() + timedelta(days=1),
            is_active=True,
            task_priority_id=2
        ),
        RecurringTask(
            title="Weekly Review",
            description="Weekly team review",
            user_id=str(test_user.id),
            recurrence_pattern="weekly",
            start_date=date.today(),
            next_due_at=date.today() + timedelta(days=7),
            is_active=True,
            task_priority_id=3
        ),
        RecurringTask(
            title="Monthly Report",
            description="Monthly status report",
            user_id=str(test_user.id),
            recurrence_pattern="monthly",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            next_due_at=date.today() + timedelta(days=30),
            is_active=False,  # Paused
            task_priority_id=1
        )
    ]

    for task in tasks:
        db_session.add(task)

    await db_session.commit()
    for task in tasks:
        await db_session.refresh(task)

    return tasks


# ============================================================================
# Event Log Fixtures
# ============================================================================

@pytest.fixture(scope="function")
async def test_event_log(db_session: AsyncSession, test_task: Task) -> TaskEventLog:
    """
    Create test event log entry.

    Returns TaskEventLog instance.
    """
    event_log = TaskEventLog(
        task_id=test_task.id,
        event_type="created",
        event_data={
            "task_id": test_task.id,
            "title": test_task.title,
            "user_id": test_task.user_id
        }
    )
    db_session.add(event_log)
    await db_session.commit()
    await db_session.refresh(event_log)

    return event_log


# ============================================================================
# Dapr Mock Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def mock_dapr() -> MockDaprClient:
    """
    Create mock Dapr client for testing.

    Returns MockDaprClient that stores events in memory.
    """
    mock_client = MockDaprClient()
    return mock_client


@pytest.fixture(scope="function")
async def mock_dapr_publisher(monkeypatch, mock_dapr: MockDaprClient):
    """
    Patch DaprEventPublisher to use mock client.

    Automatically patches the global dapr_event_publisher.
    """
    from unittest.mock import AsyncMock
    import backend.app.services.event_publisher as ep_module
    import app.services.task_notification as tn_module
    import app.services.event_publisher as app_ep_module

    # Create async wrapper functions for proper awaiting
    async def publish_task_created_wrapper(data):
        return await mock_dapr.publish_event("todo-pubsub", "task-created", data)

    async def publish_task_updated_wrapper(data):
        return await mock_dapr.publish_event("todo-pubsub", "task-updated", data)

    async def publish_task_completed_wrapper(data):
        return await mock_dapr.publish_event("todo-pubsub", "task-completed", data)

    async def publish_task_deleted_wrapper(data):
        return await mock_dapr.publish_event("todo-pubsub", "task-deleted", data)

    async def publish_task_due_soon_wrapper(data):
        return await mock_dapr.publish_event("todo-pubsub", "task-due-soon", data)

    async def publish_recurring_task_due_wrapper(data):
        return await mock_dapr.publish_event("todo-pubsub", "recurring-task-due", data)

    # Create a mock publisher instance
    mock_publisher = AsyncMock()
    mock_publisher.publish_event = AsyncMock(side_effect=mock_dapr.publish_event)
    mock_publisher.publish_task_created = AsyncMock(side_effect=publish_task_created_wrapper)
    mock_publisher.publish_task_updated = AsyncMock(side_effect=publish_task_updated_wrapper)
    mock_publisher.publish_task_completed = AsyncMock(side_effect=publish_task_completed_wrapper)
    mock_publisher.publish_task_deleted = AsyncMock(side_effect=publish_task_deleted_wrapper)
    mock_publisher.publish_task_due_soon = AsyncMock(side_effect=publish_task_due_soon_wrapper)
    mock_publisher.publish_recurring_task_due = AsyncMock(side_effect=publish_recurring_task_due_wrapper)

    # Patch all the places where dapr_event_publisher is imported
    monkeypatch.setattr(ep_module, "dapr_event_publisher", mock_publisher)
    monkeypatch.setattr(app_ep_module, "dapr_event_publisher", mock_publisher)
    monkeypatch.setattr(tn_module, "dapr_event_publisher", mock_publisher)

    yield mock_publisher

    # Cleanup
    mock_dapr.reset()


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture(scope="function", autouse=True)
def disable_dapr_for_tests(monkeypatch):
    """
    Disable real Dapr for unit tests.

    Automatically applied to all tests unless overridden.
    """
    monkeypatch.setenv("DAPR_ENABLED", "false")
    yield


@pytest.fixture(scope="function")
def enable_dapr_for_tests(monkeypatch):
    """
    Enable Dapr for integration tests.

    Use this fixture when testing real Dapr integration.
    """
    monkeypatch.setenv("DAPR_ENABLED", "true")
    monkeypatch.setenv("DAPR_HTTP_HOST", "localhost")
    monkeypatch.setenv("DAPR_HTTP_PORT", "3500")
    yield
