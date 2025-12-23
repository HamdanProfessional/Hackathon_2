"""Tests for Subtasks API endpoints.

Tests the CRUD operations for subtasks including:
- Creating subtasks for a task
- Listing subtasks for a task
- Updating subtask completion status
- Deleting subtasks
- Data isolation (user can only access subtasks of their own tasks)
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio

from app.main import app
from app.database import get_db
from app.models import Base, User, Task, Subtask
from app.utils.security import hash_password


# In-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


async def override_get_db():
    """Override database dependency for testing."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="module")
async def setup_database():
    """Set up test database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database):
    """Create a test database session."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def auth_headers(test_user: User):
    """Get authentication headers for test user."""
    from app.utils.security import create_access_token
    token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_task(db_session: AsyncSession, test_user: User):
    """Create a test task."""
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test task description",
        completed=False,
        priority_id=2,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.mark.asyncio
async def test_create_subtask(test_task: Task, auth_headers: dict, setup_database):
    """Test creating a subtask."""
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            f"/api/tasks/{test_task.id}/subtasks",
            json={"title": "Test Subtask", "description": "Test description"},
            headers=auth_headers,
        )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Subtask"
    assert data["description"] == "Test description"
    assert data["completed"] is False
    assert data["task_id"] == test_task.id

    # Clean up
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_subtasks(test_task: Task, auth_headers: dict, setup_database):
    """Test listing subtasks for a task."""
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    # Create a subtask directly in the database
    async with TestingSessionLocal() as session:
        subtask = Subtask(
            task_id=test_task.id,
            title="Subtask 1",
            description="First subtask",
            completed=False,
            sort_order=0,
        )
        session.add(subtask)
        await session.commit()

    # Fetch subtasks via API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/tasks/{test_task.id}/subtasks",
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(s["title"] == "Subtask 1" for s in data)

    # Clean up
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_subtask_completion(test_task: Task, auth_headers: dict, setup_database):
    """Test updating subtask completion status."""
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    # Create a subtask directly in the database
    async with TestingSessionLocal() as session:
        subtask = Subtask(
            task_id=test_task.id,
            title="Subtask to complete",
            description="Complete this",
            completed=False,
            sort_order=0,
        )
        session.add(subtask)
        await session.commit()
        await session.refresh(subtask)
        subtask_id = subtask.id

    # Update via API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch(
            f"/api/subtasks/{subtask_id}",
            json={"completed": True},
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True

    # Clean up
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_subtask(test_task: Task, auth_headers: dict, setup_database):
    """Test deleting a subtask."""
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    # Create a subtask directly in the database
    async with TestingSessionLocal() as session:
        subtask = Subtask(
            task_id=test_task.id,
            title="Subtask to delete",
            description="Delete this",
            completed=False,
            sort_order=0,
        )
        session.add(subtask)
        await session.commit()
        await session.refresh(subtask)
        subtask_id = subtask.id

    # Delete via API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete(
            f"/api/subtasks/{subtask_id}",
            headers=auth_headers,
        )

    assert response.status_code == 204

    # Verify it's deleted
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/tasks/{test_task.id}/subtasks",
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert not any(s["id"] == subtask_id for s in data)

    # Clean up
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_subtask_data_isolation(db_session: AsyncSession, auth_headers: dict, setup_database):
    """Test that users can only access subtasks of their own tasks."""
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    # Create another user and task
    other_user = User(
        email="other@example.com",
        hashed_password=hash_password("testpass123"),
        name="Other User",
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    other_task = Task(
        user_id=other_user.id,
        title="Other User Task",
        description="Not accessible to test user",
        completed=False,
        priority_id=2,
    )
    db_session.add(other_task)
    await db_session.commit()
    await db_session.refresh(other_task)

    # Create a subtask for the other user's task
    other_subtask = Subtask(
        task_id=other_task.id,
        title="Other user's subtask",
        description="Should not be accessible",
        completed=False,
        sort_order=0,
    )
    db_session.add(other_subtask)
    await db_session.commit()

    # Try to access the other user's subtask
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/tasks/{other_task.id}/subtasks",
            headers=auth_headers,
        )

    assert response.status_code == 404  # Task not found for this user

    # Try to update the other user's subtask directly
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch(
            f"/api/subtasks/{other_subtask.id}",
            json={"completed": True},
            headers=auth_headers,
        )

    assert response.status_code == 403  # Forbidden

    # Clean up
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_subtask_sort_order(test_task: Task, auth_headers: dict, setup_database):
    """Test that subtasks are assigned sort_order correctly."""
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create first subtask
        response1 = await client.post(
            f"/api/tasks/{test_task.id}/subtasks",
            json={"title": "First subtask"},
            headers=auth_headers,
        )
        assert response1.status_code == 201
        assert response1.json()["sort_order"] == 0

        # Create second subtask
        response2 = await client.post(
            f"/api/tasks/{test_task.id}/subtasks",
            json={"title": "Second subtask"},
            headers=auth_headers,
        )
        assert response2.status_code == 201
        assert response2.json()["sort_order"] == 1

        # Create third subtask
        response3 = await client.post(
            f"/api/tasks/{test_task.id}/subtasks",
            json={"title": "Third subtask"},
            headers=auth_headers,
        )
        assert response3.status_code == 201
        assert response3.json()["sort_order"] == 2

    # Clean up
    app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
