# Skill: CLI Builder

## Description
Creates command-line interface (CLI) applications using Click or Typer. Specializes in building intuitive, well-structured CLI tools with proper argument parsing, help text, and error handling.

## Usage Context
Use when building Phase I console todo applications or any CLI-based tool that needs:
- Multiple commands and subcommands
- Argument and option parsing
- Interactive prompts
- Help system integration
- Error handling and validation

## Capabilities

### 1. CLI Framework Setup
```python
# Click-based CLI
import click

@click.group()
def cli():
    """Todo CLI Application"""
    pass

# Typer-based CLI
import typer

app = typer.Typer(help="Todo CLI Application")
```

### 2. Command Creation
```python
# Basic command with arguments
@app.command()
def add(title: str, description: str = typer.Option(None, "--desc")):
    """Add a new task"""
    pass

# Command with choices
@app.command()
def list(filter: str = typer.Option("all", "--filter", choice=["all", "pending", "completed"])):
    """List tasks with optional filter"""
    pass
```

### 3. Interactive Prompts
```python
# Click prompts
def interactive_update():
    title = click.prompt("Enter new title", type=str)
    description = click.prompt("Enter description", type=str, default="", show_default=False)
    return title, description

# Typer prompts with confirmation
def confirm_delete(task_id: int):
    if typer.confirm(f"Delete task {task_id}?"):
        # Delete logic
        pass
```

### 4. Validation and Error Handling
```python
# Custom validation
def validate_task_id(ctx, param, value):
    if value <= 0:
        raise click.BadParameter("Task ID must be positive")
    return value

@app.command()
def delete(task_id: int = typer.Argument(..., callback=validate_task_id)):
    """Delete a task by ID"""
    pass
```

### 5. Rich Integration
```python
from rich.console import Console
from rich.table import Table

console = Console()

def display_tasks_table(tasks):
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Status", style="green")

    for task in tasks:
        status = "✓" if task.completed else "✗"
        table.add_row(str(task.id), task.title, status)

    console.print(table)
```

## Integration Examples

### With Task Manager Core
```python
from task_manager_core import TaskManager

task_manager = TaskManager()

@app.command()
def add(title: str, description: str = None):
    """Add a new task"""
    task = task_manager.create_task(title, description)
    console.print(f"[green]Task {task.id} created successfully![/green]")
```

### With Console UI Builder
```python
from console_ui_builder import create_progress_bar, show_success

@app.command()
def import_tasks(file_path: str):
    """Import tasks from file"""
    with create_progress_bar() as progress:
        task = progress.add_task("Importing...", total=100)
        # Import logic
        progress.update(task, advance=100)

    show_success(f"Imported {count} tasks from {file_path}")
```

## Common Patterns

### 1. Command Structure
```python
# Main entry point
if __name__ == "__main__":
    app()  # Typer
    # or
    cli()  # Click
```

### 2. Environment Configuration
```python
import os
from pathlib import Path

# Configuration
CONFIG_DIR = Path.home() / ".todo"
DATA_FILE = CONFIG_DIR / "tasks.json"

# Ensure config directory exists
CONFIG_DIR.mkdir(exist_ok=True)
```

### 3. Logging Setup
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

## Best Practices

### 1. Command Design
- Use clear, verb-based command names
- Provide helpful default values
- Include comprehensive help text
- Use type hints for automatic validation

### 2. User Experience
- Provide progress feedback for long operations
- Use colors to indicate status (green=success, red=error)
- Include confirmation prompts for destructive actions
- Show clear success/error messages

### 3. Error Messages
- Be specific about what went wrong
- Suggest how to fix the issue
- Use consistent formatting
- Log errors for debugging

## CLI Commands for Todo App

### Complete Implementation Template
```python
import typer
from typing import Optional
from rich.console import Console

app = typer.Typer(help="Todo CLI Application")
console = Console()

@app.command()
def add(title: str, description: Optional[str] = typer.Option(None, "--desc", help="Task description")):
    """Add a new task to the list"""
    # Implementation
    pass

@app.command()
def list(filter: str = typer.Option("all", "--filter", help="Filter tasks",
                                  choice=["all", "pending", "completed"])):
    """List all tasks with optional filter"""
    # Implementation
    pass

@app.command()
def update(task_id: int, title: Optional[str] = typer.Option(None, help="New title"),
          description: Optional[str] = typer.Option(None, help="New description")):
    """Update an existing task"""
    # Implementation
    pass

@app.command()
def delete(task_id: int, confirm: bool = typer.Option(False, "--confirm", help="Skip confirmation")):
    """Delete a task by ID"""
    # Implementation
    pass

@app.command()
def complete(task_id: int):
    """Mark a task as complete (or incomplete if already complete)"""
    # Implementation
    pass
```

## Testing CLI Commands

### Using Click Testing
```python
from click.testing import CliRunner

def test_add_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['add', 'Test task'])
    assert result.exit_code == 0
    assert 'Task created' in result.output
```

### Using Typer Testing
```python
from typer.testing import CliRunner

runner = CliRunner()

def test_list_command():
    result = runner.invoke(app, ['list'])
    assert result.exit_code == 0
    assert 'Tasks' in result.output
```

## Integration with Spec-Kit

When using spec-driven development:
1. Read command specifications from speckit.specify
2. Map commands to tasks in speckit.tasks
3. Reference implementation plan from speckit.plan
4. Validate against acceptance criteria

## Migration Path to Phase II

CLI commands will map to API endpoints:
- `todo add` → POST /api/tasks
- `todo list` → GET /api/tasks
- `todo update` → PUT /api/tasks/{id}
- `todo delete` → DELETE /api/tasks/{id}
- `todo complete` → PATCH /api/tasks/{id}/complete