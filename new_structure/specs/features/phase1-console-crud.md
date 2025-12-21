# Phase I: Console CRUD Application Specification

## Overview
Phase I implements a command-line interface (CLI) for basic task management. This phase focuses on core functionality with an in-memory data store, providing a foundation for evolution through subsequent phases.

## Scope: Basic Level (Core Essentials)

This phase implements the five core operations that form the foundation of any todo application:
1. **Add Task** - Create new todo items
2. **Delete Task** - Remove tasks from the list
3. **Update Task** - Modify existing task details
4. **View Task** - Display all tasks
5. **Mark Complete** - Toggle task completion status

## User Stories

### Story 1: Create Tasks
**As a** user
**I want to** add new tasks to my todo list
**So that** I can track what I need to accomplish

**Acceptance Criteria:**
- User can add a task with a title
- User can optionally add a description
- System provides confirmation when task is created
- Empty titles are rejected with error message
- Tasks are automatically assigned a unique ID

### Story 2: List Tasks
**As a** user
**I want to** view all my tasks
**So that** I can see what I need to do at a glance

**Acceptance Criteria:**
- Tasks are displayed in a clean, numbered list
- Each task shows ID, title, completion status
- Completed tasks are visually distinguished
- Empty state shows friendly message when no tasks exist

### Story 3: Update Tasks
**As a** user
**I want to** edit existing tasks
**So that** I can correct mistakes or add details

**Acceptance Criteria:**
- User can update task title and/or description by ID
- System confirms the update
- Invalid task IDs show appropriate error message
- Empty titles are rejected

### Story 4: Delete Tasks
**As a** user
**I want to** remove completed tasks
**So that** I can keep my list clean

**Acceptance Criteria:**
- User can delete a task by ID
- System asks for confirmation before deletion
- Invalid task IDs show appropriate error message
- Task is permanently removed from memory

### Story 5: Mark Complete
**As a** user
**I want to** mark tasks as completed
**So that** I can track my progress

**Acceptance Criteria:**
- User can mark any task as completed by ID
- Completed tasks show clear visual indication
- User can unmark tasks to make them pending again
- Invalid task IDs show appropriate error message

## Interface Specification: CLI Only

### Command Structure
The application uses a command-line interface with the following structure:

```bash
# Main commands
todo add "Task title" [--description "Task description"]
todo list [--completed|--pending|--all]
todo update <task-id> [--title "New title"] [--description "New description"]
todo delete <task-id>
todo complete <task-id>
todo help

# Short aliases
todo a "Title" -d "Description"  # add
todo l [-c] [-p]             # list
todo u <id> -t "Title"         # update
todo d <id>                   # delete
todo c <id>                   # complete
```

### Menu System
When run without arguments, display an interactive menu:

```
=== Todo Manager ===
1. List tasks
2. Add task
3. Update task
4. Delete task
5. Mark complete
6. Exit

Enter choice (1-6): _
```

## Technical Implementation

### Data Model

#### Task Class
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class Task:
    id: int = field(default=0)
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
```

### In-Memory Storage
```python
class TodoManager:
    def __init__(self):
        self.tasks: list[Task] = []
        self.next_id: int = 1

    def add_task(self, title: str, description: Optional[str] = None) -> Task:
        task = Task(id=self.next_id, title=title.strip(), description=description)
        self.tasks.append(task)
        self.next_id += 1
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: int, title: Optional[str] = None,
                    description: Optional[str] = None) -> bool:
        task = self.get_task(task_id)
        if task:
            if title:
                task.title = title.strip()
            if description is not None:
                task.description = description
            task.updated_at = datetime.now()
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                return True
        return False

    def complete_task(self, task_id: int, completed: bool = True) -> bool:
        task = self.get_task(task_id)
        if task:
            task.completed = completed
            task.updated_at = datetime.now()
            return True
        return False

    def list_tasks(self, status_filter: Optional[str] = None) -> list[Task]:
        if status_filter == "completed":
            return [t for t in self.tasks if t.completed]
        elif status_filter == "pending":
            return [t for t in self.tasks if not t.completed]
        else:
            return self.tasks.copy()
```

### CLI Implementation (Click/Typer)
```python
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from rich.text import Text
from rich.panel import Panel
from typing import Optional

console = Console()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Todo Manager - A simple command-line todo application."""
    pass

@cli.command()
@click.argument("title")
@click.option("--description", "-d", help="Task description")
@click.option("--priority", "-p", type=click.Choice(["low", "medium", "high"]), default="medium")
def add(title: str, description: Optional[str], priority: str):
    """Add a new task to the todo list."""
    manager = TodoManager()
    task = manager.add_task(title, description)

    console.print(Panel(
        f"[green]✓[/green] Task added successfully!\n"
        f"ID: {task.id}\n"
        f"Title: {task.title}\n"
        f"Description: {task.description or 'None'}\n"
        f"Priority: {priority}",
        title="Task Created",
        border_style="green"
    ))

@cli.command()
@click.option("--completed", "-c", is_flag=True, help="Show only completed tasks")
@click.option("--pending", "-p", is_flag=True, help="Show only pending tasks")
@click.option("--all", "-a", "show_all", is_flag=True, help="Show all tasks (default)")
def list(completed: bool, pending: bool, show_all: bool):
    """List all tasks."""
    manager = TodoManager()

    # Determine filter
    if completed:
        status_filter = "completed"
    elif pending:
        status_filter = "pending"
    else:
        status_filter = None

    tasks = manager.list_tasks(status_filter)

    if not tasks:
        message = "No tasks found"
        if completed:
            message = "No completed tasks found"
        elif pending:
            message = "No pending tasks found"

        console.print(Panel(
            Text(message, style="italic"),
            title="Task List",
            border_style="blue"
        )
        return

    table = Table(title="Tasks")
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Status", style="magenta", width=8)
    table.add_column("Title", style="white")
    table.add_column("Description", style="dim")
    table.add_column("Created", style="green", width=12)

    for task in tasks:
        status = "✓" if task.completed else "○"
        status_style = "green" if task.completed else "yellow"
        title_style = "dim" if task.completed else "white"

        table.add_row(
            str(task.id),
            Text(status, style=status_style),
            Text(task.title, style=title_style),
            task.description or "",
            task.created_at.strftime("%Y-%m-%d %H:%M")
        )

    console.print(table)

@cli.command()
@click.argument("task_id", type=int)
@click.option("--title", "-t", help="New task title")
@click.option("--description", "-d", help="New task description")
def update(task_id: int, title: Optional[str], description: Optional[str]):
    """Update an existing task."""
    manager = TodoManager()

    if manager.update_task(task_id, title, description):
        console.print(
            f"[green]✓[/green] Task {task_id} updated successfully"
        )
    else:
        console.print(
            f"[red]✗[/red] Task {task_id} not found"
        )

@cli.command()
@click.argument("task_id", type=int)
def delete(task_id: int):
    """Delete a task."""
    manager = TodoManager()

    # Find task for confirmation
    task = manager.get_task(task_id)
    if not task:
        console.print(f"[red]✗[/red] Task {task_id} not found")
        return

    if Confirm.ask(f"Delete task '{task.title}'?"):
        if manager.delete_task(task_id):
            console.print(f"[green]✓[/green] Task {task_id} deleted")
        else:
            console.print(f"[red]✗[/red] Failed to delete task {task_id}")

@cli.command()
@click.argument("task_id", type=int)
@click.option("--unmark", "-u", is_flag=True, help="Mark as pending (uncomplete)")
def complete(task_id: int, unmark: bool):
    """Mark a task as completed or pending."""
    manager = TodoManager()

    if manager.complete_task(task_id, not unmark):
        action = "unmarked" if unmark else "marked as completed"
        console.print(f"[green]✓[/green] Task {task_id} {action}")
    else:
        console.print(f"[red]✗[/red] Task {task_id} not found")

@cli.command()
def interactive():
    """Run in interactive menu mode."""
    while True:
        console.print("\n" + "="*50)
        console.print("[bold cyan]Todo Manager - Interactive Mode[/bold cyan]")
        console.print("="*50)

        table = Table()
        table.add_column("Choice", style="cyan")
        table.add_column("Command", style="white")

        table.add_row("1", "List tasks")
        table.add_row("2", "Add task")
        table.add_row("3", "Update task")
        table.add_row("4", "Delete task")
        table.add_row("5", "Complete task")
        table.add_row("6", "Exit")

        console.print(table)

        choice = console.input("Enter your choice (1-6): ")

        if choice == "1":
            list.callback(standalone_mode=False)
        elif choice == "2":
            title = console.input("Task title: ")
            description = console.input("Description (optional): ")
            add.callback(standalone_mode=False, title, description)
        elif choice == "3":
            task_id = int(console.input("Task ID to update: "))
            title = console.input("New title (optional): ")
            description = console.input("New description (optional): ")
            update.callback(standalone_mode=False, task_id, title or None, description or None)
        elif choice == "4":
            task_id = int(console.input("Task ID to delete: "))
            delete.callback(standalone_mode=False, task_id)
        elif choice == "5":
            task_id = int(console.input("Task ID to complete: "))
            complete.callback(standalone_mode=False, task_id)
        elif choice == "6":
            console.print("[green]Goodbye![/green]")
            break
        else:
            console.print("[red]Invalid choice. Please enter 1-6.[/red]")
```

## Requirements Compliance

### Forward Compatibility Notes
**Phase I models MUST be compatible with OpenAI Agents SDK requirements in Phase III:**
- While Phase I is a simple console app, the `Task` data model defined here must be compatible with the Pydantic models required by the **OpenAI Agents SDK** in Phase III
- Keep the model schema clean and typed to ensure smooth transition to AI agent tool definitions
- Task fields should align with MCP (Model Context Protocol) tool parameter requirements

### Project Structure
```
src/
├── main.py              # Entry point
├── models/
│   └── task.py          # Task data model
├── services/
│   └── todo.py          # Business logic
├── cli/
│   └── commands.py      # CLI commands
└── utils/
    └── rich_ui.py        # Rich formatting
```

## Testing Strategy

### Manual Testing Checklist
- [ ] All CRUD operations work correctly
- [ ] Empty input validation
- [ ] Invalid task ID handling
- [ ] Interactive menu navigation
- [ ] Command-line parsing
- [ ] Rich UI formatting displays correctly

### Edge Cases to Test
- Adding tasks with special characters
- Updating non-existent task IDs
- Completing already completed tasks
- Deleting already deleted tasks
- Empty task list display

## Performance Requirements
- Application startup: < 100ms
- Command execution: < 50ms
- Memory usage: < 50MB for 1000 tasks
- UI responsiveness: No noticeable lag

## Success Metrics
- All 5 core operations implemented
- User-friendly error messages
- Clean, professional terminal appearance
- Commands execute as expected
- Data persistence during session
- Easy navigation for power users

## Out of Scope
- Persistent data storage (database or file)
- User authentication
- Web interface
- Task categories or tags
- Due date reminders
- Collaborative features
- Import/export functionality

## Dependencies
- Python 3.13+
- Rich (for terminal UI)
- Click or Typer (for CLI parsing)
- Optional: pytest (for testing)