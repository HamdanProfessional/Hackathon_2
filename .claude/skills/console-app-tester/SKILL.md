---
name: console-app-tester
description: Interactive testing and validation of Python console applications with Rich UI. Use when Claude needs to: (1) Test command-line interfaces (CLI) built with Rich/Click/Typer, (2) Verify console app functionality matches specifications, (3) Create automated tests for console applications, (4) Validate user input handling and error messages, (5) Test in-memory data operations
---

# Console App Tester Skill

Automated testing and validation for Python console applications.

## Quick Start

```bash
# Run console app interactively
cd src && python -m src

# Run automated tests
pytest tests/test_console.py -v
```

## Test Coverage Areas

### Basic Operations
- Add task with valid input
- Add task with empty title (should fail)
- List tasks when empty
- List tasks with data
- Update existing task
- Update non-existent task (should fail)
- Delete task
- Toggle completion status

### Input Validation
- Empty task title rejection
- Invalid command handling
- Malformed command arguments
- Special characters in input

### Edge Cases
- Duplicate task titles
- Very long descriptions
- Unicode characters (Urdu, etc.)
- Rapid successive operations

## Scripts

### `scripts/test_interactive.sh`
Interactive test runner that simulates user input.

### `scripts/validate_spec.py`
Validates implementation against spec requirements.

## Test Data

See [scripts/test_data.py](scripts/test_data.py) for sample test inputs.

## Acceptance Criteria

Each console app must pass:
1. ✅ All 5 basic CRUD operations work
2. ✅ Invalid input handled gracefully
3. ✅ Help command displays usage
4. ✅ Empty list shows helpful message
5. ✅ Task IDs increment correctly
