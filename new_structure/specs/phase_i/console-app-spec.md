# Phase I: Console Todo App Specification

## Overview
Build a command-line todo application that stores tasks in memory using Claude Code and Spec-Kit Plus.

## Technology Stack
- **Language**: Python 3.13+
- **Package Manager**: UV
- **CLI Framework**: Click or Typer
- **Console UI**: Rich or Textual
- **Development**: Claude Code + Spec-Kit Plus

## Core Requirements

### Basic Level Features (All Required)
1. **Add Task** - Create new todo items with title and description
2. **Delete Task** - Remove tasks from the list by ID
3. **Update Task** - Modify existing task details (title, description)
4. **View Task List** - Display all tasks with status indicators
5. **Mark as Complete** - Toggle task completion status

### User Stories

#### Adding Tasks
- As a user, I want to add a task with a title and optional description
- The system should assign a unique ID automatically
- Tasks should default to incomplete status

#### Viewing Tasks
- As a user, I want to see all my tasks in a formatted table
- The display should show ID, title, description, and completion status
- Completed tasks should be visually distinct (e.g., strikethrough)

#### Managing Tasks
- As a user, I want to update task details by referencing the task ID
- As a user, I want to delete tasks by ID with confirmation
- As a user, I want to mark tasks as complete/incomplete

## Technical Specifications

### Data Model
```python
class Task:
    id: int (auto-increment, unique)
    title: str (required, max 200 chars)
    description: str (optional, max 1000 chars)
    completed: bool (default False)
    created_at: datetime (auto-generated)
```

### CLI Interface Structure
```bash
todo
├── add                    # Add a new task
├── list                  # List all tasks
├── update <id>          # Update a task
├── delete <id>          # Delete a task
├── complete <id>        # Mark task as complete
└── help                 # Show help
```

### Command Specifications

#### add command
```bash
todo add "Task title" [--description "Task description"]
```
- Creates new task with unique ID
- Returns success message with task ID
- Example: `todo add "Buy groceries" --description "Milk, eggs, bread"`

#### list command
```bash
todo list [--filter all|pending|completed]
```
- Displays tasks in a formatted table
- Optional filtering by completion status
- Shows ID, title, description, status, created date

#### update command
```bash
todo update <id> [--title "New title"] [--description "New description"]
```
- Updates specified task
- Interactive mode if no flags provided
- Must validate task exists

#### delete command
```bash
todo delete <id> [--confirm]
```
- Deletes task by ID
- Requires confirmation unless --confirm flag used
- Shows deleted task details

#### complete command
```bash
todo complete <id>
```
- Toggles task completion status
- Shows updated status
- Can mark complete or incomplete

### Console UI Requirements
- Use Rich library for formatted output
- Color coding for task status
- Progress bars for task completion
- Syntax highlighting for task descriptions
- Error messages in red
- Success messages in green

### Error Handling
- Invalid task IDs: "Task with ID {id} not found"
- Empty titles: "Task title cannot be empty"
- Title too long: "Task title exceeds 200 characters"
- Description too long: "Task description exceeds 1000 characters"

## Implementation Constraints

### Phase I Limitations
- **In-memory storage only** - No external databases
- **Single session** - Data lost on application exit
- **No user authentication** - Single user mode
- **No persistence** - Optional JSON export/import

### Code Quality Standards
- Type hints required for all functions
- Docstrings for all public functions
- Maximum function length: 50 lines
- Use dataclasses for models
- Follow PEP 8 style guide

### Testing Requirements
- Unit tests for all Task operations
- CLI command tests
- Edge case validation tests
- Minimum 90% code coverage

## Acceptance Criteria

### Functional Requirements
1. User can add a task with title and optional description
2. Tasks are displayed with unique IDs
3. User can view all tasks in a formatted table
4. User can update task title and/or description
5. User can delete tasks with confirmation
6. User can mark tasks as complete/incomplete
7. Application provides helpful error messages

### Non-Functional Requirements
1. Application starts in < 1 second
2. All commands complete in < 100ms
3. Memory usage < 10MB for 1000 tasks
4. Console output is clean and readable

### Success Metrics
- All 5 basic features implemented
- Passes all test cases
- Clean, readable code
- Comprehensive help documentation
- Ready for Phase II migration

## Deliverables

### Code Structure
```
src/
├── main.py              # CLI entry point
├── models/
│   └── task.py         # Task data model
├── commands/
│   ├── __init__.py
│   ├── add.py          # Add task command
│   ├── list.py         # List tasks command
│   ├── update.py       # Update task command
│   ├── delete.py       # Delete task command
│   └── complete.py     # Complete task command
├── services/
│   └── task_manager.py # Task business logic
└── utils/
    ├── console.py      # Rich console utilities
    └── validators.py   # Input validation

tests/
├── test_models.py
├── test_commands.py
└── test_services.py
```

### Documentation
- README.md with setup and usage instructions
- CLI help for all commands
- API documentation for internal modules

### Migration Path for Phase II
- Task model ready for SQLModel conversion
- Command structure ready for API endpoint mapping
- Service layer ready for database integration
- Console UI components reusable for frontend inspiration