# Quick Start: Running Phase V E2E Tests

## Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL** (optional, for integration tests)
3. **Dapr sidecar** (optional, for integration tests)

## Installation

```bash
# Navigate to project root
cd Hackathon_2

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx aiosqlite

# Or install from requirements file (if exists)
pip install -r requirements-test.txt
```

## Quick Start

### 1. Run All Tests

```bash
pytest tests/test_phase5_e2e.py -v
```

### 2. Run Specific Test Category

```bash
# Recurring Tasks API
pytest tests/test_phase5_e2e.py::TestRecurringTasksAPI -v

# Event Publishing
pytest tests/test_phase5_e2e.py::TestEventPublishing -v

# Notification Service
pytest tests/test_phase5_e2e.py::TestNotificationService -v

# E2E Workflows
pytest tests/test_phase5_e2e.py::TestEndToEndWorkflows -v

# Error Handling
pytest tests/test_phase5_e2e.py::TestErrorHandling -v
```

### 3. Run with Coverage

```bash
pytest tests/test_phase5_e2e.py --cov=app --cov-report=html
open htmlcov/index.html
```

## Common Commands

| Command | Description |
|---------|-------------|
| `pytest tests/test_phase5_e2e.py -v` | Run all tests with verbose output |
| `pytest tests/test_phase5_e2e.py -v -k "pause"` | Run tests matching keyword |
| `pytest tests/test_phase5_e2e.py -v --tb=short` | Shorter traceback format |
| `pytest tests/test_phase5_e2e.py -v -s` | Show print output |
| `pytest tests/test_phase5_e2e.py -x` | Stop on first failure |
| `pytest tests/test_phase5_e2e.py --lf` | Run last failed tests |
| `pytest tests/test_phase5_e2e.py -v -m "not integration"` | Skip integration tests |

## Troubleshooting

### Import Error: No module named 'app'

```bash
# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
pytest tests/test_phase5_e2e.py -v
```

### Asyncio Errors

```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Run with asyncio mode
pytest tests/test_phase5_e2e.py -v --asyncio-mode=auto
```

### Database Errors

```bash
# Install aiosqlite for in-memory SQLite
pip install aiosqlite

# Run tests sequentially
pytest tests/test_phase5_e2e.py -v --forked
```

## Expected Output

Successful test run:

```
tests/test_phase5_e2e.py::TestRecurringTasksAPI::test_create_recurring_task_success PASSED
tests/test_phase5_e2e.py::TestRecurringTasksAPI::test_create_recurring_task_all_patterns PASSED
tests/test_phase5_e2e.py::TestRecurringTasksAPI::test_create_recurring_task_validation_errors PASSED
...
tests/test_phase5_e2e.py::TestEventPublishing::test_task_created_event_published PASSED
tests/test_phase5_e2e.py::TestEventPublishing::test_task_updated_event_published PASSED
...
================================ 40 passed in 5.23s ================================
```

## Next Steps

- See [PHASE5_TESTS.md](./PHASE5_TESTS.md) for detailed documentation
- Check test coverage reports in `htmlcov/`
- Review fixtures in `conftest.py` for custom test setup
