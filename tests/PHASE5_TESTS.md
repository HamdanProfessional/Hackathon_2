# Phase V: Event-Driven Architecture - Test Documentation

## Overview

Comprehensive End-to-End (E2E) test suite for Phase V event-driven architecture features including recurring tasks API, Dapr event publishing, and notification service integration.

## Test Files

| File | Description | Lines of Code |
|------|-------------|---------------|
| `tests/test_phase5_e2e.py` | Main E2E test suite | ~900 |
| `tests/conftest.py` | Shared pytest fixtures | ~400 |
| `tests/helpers/dapr_client.py` | Dapr test helper client | ~250 |
| `tests/helpers/__init__.py` | Test helpers package | ~10 |

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures
├── test_phase5_e2e.py               # Phase V E2E tests
└── helpers/
    ├── __init__.py
    └── dapr_client.py               # Dapr mock/real client
```

## Test Categories

### 1. Recurring Tasks API Tests (`TestRecurringTasksAPI`)

Tests all 7 recurring task endpoints:

| Endpoint | Method | Tests | Status |
|----------|--------|-------|--------|
| `/api/recurring-tasks` | POST | Create recurring task, all patterns, validation | ✅ |
| `/api/recurring-tasks` | GET | List all, with filters, pagination, sorting | ✅ |
| `/api/recurring-tasks/{id}` | GET | Get by ID, not found, unauthorized | ✅ |
| `/api/recurring-tasks/{id}` | PUT | Update task, empty body validation | ✅ |
| `/api/recurring-tasks/{id}` | DELETE | Delete task | ✅ |
| `/api/recurring-tasks/{id}/pause` | POST | Pause task, already paused | ✅ |
| `/api/recurring-tasks/{id}/resume` | POST | Resume task, already active | ✅ |
| `/api/recurring-tasks/stats/count` | GET | Count with active_only filter | ✅ |

**Total Tests**: 20+

### 2. Event Publishing Tests (`TestEventPublishing`)

Tests Dapr event publishing for all event types:

| Event Type | Topic | Tests |
|------------|-------|-------|
| Task Created | `task-created` | Event published, payload validation |
| Task Updated | `task-updated` | Event published with task_id |
| Task Completed | `task-completed` | Event published on completion |
| Task Deleted | `task-deleted` | Event published on deletion |
| Recurring Task Due | `recurring-task-due` | Event can be published |

**Total Tests**: 7

### 3. Notification Service Tests (`TestNotificationService`)

Tests notification service integration:

| Feature | Tests |
|---------|-------|
| Event Logging | Events logged to `task_event_log` table |
| Multiple Events | All lifecycle events tracked |
| Data Integrity | Log data matches task data |

**Total Tests**: 3

### 4. End-to-End Workflow Tests (`TestEndToEndWorkflows`)

Tests complete user workflows:

| Workflow | Description |
|----------|-------------|
| Recurring Task Full | Create -> List -> Pause -> Resume -> Delete |
| Task Lifecycle | Create -> Update -> Complete with all events |
| Pagination | Large dataset with 10+ pages |
| Filtering | Filter by completed, sort by priority |

**Total Tests**: 4

### 5. Error Handling Tests (`TestErrorHandling`)

Tests edge cases and error scenarios:

| Error Type | Tests |
|------------|-------|
| Unauthorized | 401 without authentication |
| Data Isolation | Users cannot access each other's data |
| Not Found | 404 for non-existent resources |
| Invalid Input | 422 for invalid patterns, dates |
| Cross-User Access | 404 when accessing other user's data |

**Total Tests**: 6

## Test Fixtures

### Database Fixtures

```python
@pytest.fixture
async def db_engine()
    # In-memory SQLite database

@pytest.fixture
async def db_session(db_engine)
    # Database session with rollback
```

### Authentication Fixtures

```python
@pytest.fixture
async def test_user(db_session)
    # Creates authenticated test user

@pytest.fixture
async def auth_token(client, test_user)
    # Returns JWT access token

@pytest.fixture
def auth_headers(auth_token)
    # Returns dict with Authorization header
```

### Task Fixtures

```python
@pytest.fixture
async def test_task(db_session, test_user)
    # Creates test task

@pytest.fixture
async def test_tasks(db_session, test_user)
    # Creates 5 test tasks

@pytest.fixture
async def test_recurring_task(db_session, test_user)
    # Creates recurring task

@pytest.fixture
async def test_recurring_tasks(db_session, test_user)
    # Creates 3 recurring tasks (different patterns)
```

### Dapr Fixtures

```python
@pytest.fixture
def mock_dapr()
    # MockDaprClient for testing

@pytest.fixture
async def mock_dapr_publisher(monkeypatch, mock_dapr)
    # Patches DaprEventPublisher globally
```

## Running Tests

### Run All Tests

```bash
# From project root
pytest tests/test_phase5_e2e.py -v

# With coverage
pytest tests/test_phase5_e2e.py --cov=app --cov-report=html

# With detailed output
pytest tests/test_phase5_e2e.py -v -s
```

### Run Specific Test Class

```bash
# Recurring Tasks API tests
pytest tests/test_phase5_e2e.py::TestRecurringTasksAPI -v

# Event Publishing tests
pytest tests/test_phase5_e2e.py::TestEventPublishing -v

# Notification Service tests
pytest tests/test_phase5_e2e.py::TestNotificationService -v
```

### Run Specific Test

```bash
# Single test
pytest tests/test_phase5_e2e.py::TestRecurringTasksAPI::test_create_recurring_task_success -v

# By keyword
pytest tests/test_phase5_e2e.py -k "pause" -v

# By marker
pytest tests/test_phase5_e2e.py -m integration -v
```

### Run Tests with Different Environments

```bash
# Unit tests (mock Dapr)
pytest tests/test_phase5_e2e.py -v

# Integration tests (requires Dapr sidecar)
DAPR_ENABLED=true pytest tests/test_phase5_e2e.py -v -m integration
```

## Test Dependencies

### Required Packages

```bash
# Core testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0

# HTTP testing
httpx>=0.24.0

# Database testing
aiosqlite>=0.19.0
sqlalchemy>=2.0.0

# Async
asyncio
```

### Install Test Dependencies

```bash
# From project root
pip install pytest pytest-asyncio pytest-cov httpx aiosqlite
```

## Mock Dapr Client Usage

The `MockDaprClient` stores published events in memory for verification:

```python
# In test
async def test_my_event(mock_dapr: MockDaprClient):
    mock_dapr.reset()

    # Trigger event
    await create_task(...)

    # Verify published
    assert mock_dapr.verify_event_published("task-created")

    # Get events by topic
    events = mock_dapr.get_events_by_topic("task-created")

    # Get events by task_id
    events = mock_dapr.get_events_by_task_id(123)
```

## Helper Functions

### `create_test_recurring_task()`

Helper to create recurring task via API:

```python
task = await create_test_recurring_task(
    client=client,
    headers=auth_headers,
    title="Daily Standup",
    recurrence_pattern="daily",
    start_date=date.today()
)
```

### `verify_event_published()`

Helper to verify Dapr event was published:

```python
assert await verify_event_published(
    mock_dapr=mock_dapr,
    topic="task-created",
    task_id=task_id
)
```

### `verify_task_event_log()`

Helper to verify database event log:

```python
assert await verify_task_event_log(
    db_session=db_session,
    task_id=task_id,
    event_type="created"
)
```

## Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Recurring Tasks API | 90%+ | ~ |
| Event Publishing | 80%+ | ~ |
| Event Logging | 85%+ | ~ |
| Error Handling | 100% | ~ |
| E2E Workflows | 100% | ~ |

## Known Limitations

1. **Database Tests**: Use SQLite in-memory for speed. For production-like tests, use PostgreSQL.

2. **Dapr Integration**: Real Dapr sidecar tests require `DAPR_ENABLED=true` and running sidecar.

3. **Background Jobs**: Tests for background task generation from recurring tasks not included.

4. **Performance Tests**: Load testing and stress testing not in scope.

## Troubleshooting

### Import Errors

```bash
# If you get "No module named 'backend'"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/test_phase5_e2e.py
```

### Database Lock Errors

```bash
# Run tests sequentially
pytest tests/test_phase5_e2e.py -v --forked
```

### Async Test Errors

```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Or run with asyncio mode
pytest tests/test_phase5_e2e.py -v --asyncio-mode=auto
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Phase V Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-test.txt
      - run: pytest tests/test_phase5_e2e.py -v --cov=app
      - uses: codecov/codecov-action@v3
```

## Test Results Summary

After running tests, you'll see a summary like:

```
==========================================
  PHASE V: Event-Driven Architecture - Test Summary
==========================================

  Total Tests: 40
  Passed: 38
  Failed: 2
  Skipped: 0

  Success Rate: 95.0%

==========================================
```

## Contributing

When adding new tests:

1. Follow existing test class structure
2. Use descriptive test names (`test_<feature>_<scenario>`)
3. Add docstrings explaining what is being tested
4. Use fixtures for common setup
5. Clean up resources in tests
6. Update this documentation

## Related Documentation

- [Phase V Specification](../../specs/005-cloud-deployment/spec.md)
- [Dapr Documentation](https://docs.dapr.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Documentation](https://docs.pytest.org/)
