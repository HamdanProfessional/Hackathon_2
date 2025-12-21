---
name: task-manager-core
description: Implements core CRUD operations for in-memory task management in console todo applications. Provides Task model, task storage, and basic operations (create, read, update, delete, toggle complete) with validation and error handling. Use when building Phase I console todo apps or any application needing simple in-memory task management.
---

# Task Manager Core

## Quick Start

Use the TaskManager class for in-memory task operations:

```python
from task_manager_core import TaskManager, Task

# Initialize
tm = TaskManager()

# Create task
task = tm.create_task("Buy groceries", "Milk, eggs, bread")

# List tasks
tasks = tm.list_tasks()

# Update task
tm.update_task(task_id=1, title="Buy groceries and fruits")

# Toggle completion
tm.toggle_complete(task_id=1)

# Delete task
tm.delete_task(task_id=1)
```

## Core Components

### Task Model
Located in `references/task-model.md`

Defines the Task dataclass with fields:
- `id`: int (auto-increment)
- `title`: str (required, max 200 chars)
- `description`: str (optional, max 1000 chars)
- `completed`: bool (default False)
- `created_at`: datetime

### TaskManager Class
Located in `scripts/task_manager.py`

Provides all CRUD operations:
- `create_task(title, description=None)`
- `get_task(task_id)`
- `list_tasks(filter_status=None)`
- `update_task(task_id, **kwargs)`
- `toggle_complete(task_id)`
- `delete_task(task_id)`

## Validation Rules

All operations enforce these constraints:
- Task titles: 1-200 characters, not empty
- Task descriptions: max 1000 characters
- Task IDs: must exist for operations
- Auto-increment IDs starting from 1

## Error Handling

Common exceptions:
- `ValueError`: Invalid input (empty title, too long)
- `KeyError`: Task ID not found
- `TypeError`: Wrong data types

## Integration Examples

### With CLI Commands
```python
# Add command
@app.command()
def add(title: str, description: str = None):
    try:
        task = tm.create_task(title, description)
        console.print(f"[green]Task {task.id} created![/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
```

### With Rich Display
```python
def display_tasks(tasks):
    table = Table(title="Tasks")
    table.add_column("ID", justify="right")
    table.add_column("Title")
    table.add_column("Status")

    for task in tasks:
        status = "✓" if task.completed else "✗"
        table.add_row(str(task.id), task.title, status)

    console.print(table)
```

## Performance

- In-memory storage with O(1) access for ID lookups
- O(n) for listing all tasks
- Handles 10,000+ tasks efficiently
- Memory usage ~100 bytes per task

## Migration Path

Ready for Phase II migration:
1. Replace in-memory storage with SQLModel database
2. Task model already compatible
3. Method signatures stay the same
4. Add database session management

See `references/migration-guide.md` for Phase II migration details.