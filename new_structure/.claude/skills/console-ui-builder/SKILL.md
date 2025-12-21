---
name: console-ui-builder
description: Creates rich, interactive console UIs using Rich library. Provides components for tables, progress bars, prompts, syntax highlighting, and styled text. Use when building Phase I console todo apps or any CLI application needing professional terminal interfaces with colors, tables, and interactive elements.
---

# Console UI Builder

## Quick Start

```python
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()

# Print styled text
console.print("[bold green]Success![/bold green] Task created.")

# Create tables
table = Table(title="Tasks")
table.add_column("ID", style="cyan")
table.add_column("Title", style="magenta")
table.add_row("1", "Buy groceries")
console.print(table)

# Interactive prompts
name = Prompt.ask("Enter your name")
if Confirm.ask("Continue?"):
    console.print("Proceeding...")
```

## Core Components

### Rich Console
Located in `scripts/console_utils.py`

Provides a configured Console instance with:
- Color support detection
- Error handling
- Logging integration
- Custom styles

### Table Builder
Located in `scripts/table_builder.py`

Creates formatted tables for:
- Task lists
- Statistics
- Search results
- Help content

### Progress Tracking
Located in `scripts/progress.py`

Progress bars and spinners for:
- File operations
- Data processing
- API calls
- Multi-step operations

## Display Components

### Task Display
```python
def display_task_table(tasks, console):
    """Display tasks in a formatted table."""
    table = Table(title="Tasks")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Status", style="green")
    table.add_column("Created", style="dim")

    for task in tasks:
        status = "✓" if task.completed else "✗"
        created = task.created_at.strftime("%Y-%m-%d")
        table.add_row(str(task.id), task.title, status, created)

    console.print(table)
```

### Status Messages
```python
from rich.console import Console

console = Console()

# Success
console.print(":white_check_mark: Task completed!", style="bold green")

# Error
console.print(":x: Task not found", style="bold red")

# Warning
console.print(":warning: Task already exists", style="bold yellow")

# Info
console.print(":information_source: Loading tasks...", style="bold blue")
```

### Progress Bars
```python
from rich.progress import Progress, SpinnerColumn, TextColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
) as progress:
    task1 = progress.add_task("Processing...", total=100)
    while not progress.finished:
        progress.update(task1, advance=1)
```

## Interactive Elements

### Input Prompts
```python
from rich.prompt import Prompt, IntPrompt, Confirm

# Text input
title = Prompt.ask("Task title", default="Untitled")

# Number input
task_id = IntPrompt.ask("Task ID to update")

# Confirmation
if Confirm.ask("Delete this task?"):
    # Delete task
    pass

# Choice selection
priority = Prompt.ask(
    "Select priority",
    choices=["low", "medium", "high"],
    default="medium"
)
```

### Forms
```python
def task_form():
    """Interactive task creation form."""
    console = Console()

    console.print("[bold]Create New Task[/bold]")

    title = Prompt.ask("Title")
    description = Prompt.ask("Description", default="", show_default=False)
    priority = Prompt.ask(
        "Priority",
        choices=["low", "medium", "high"],
        default="medium"
    )

    return {
        'title': title,
        'description': description,
        'priority': priority
    }
```

## Styling Guide

### Color Codes
```python
# Predefined styles
SUCCESS_STYLE = "bold green"
ERROR_STYLE = "bold red"
WARNING_STYLE = "bold yellow"
INFO_STYLE = "bold blue"
DIM_STYLE = "dim"

# Custom styles
console.print("Custom text", style="italic #FF00FF")
```

### Status Icons
- ✅ or ✓: Complete/success
- ❌ or ✗: Incomplete/error
- ⚠️: Warning
- ℹ️: Information
- 🔄: In progress
- ⏳: Waiting/pending

### Table Styling
```python
# Header styles
table.add_column("ID", style="cyan", no_wrap=True)
table.add_column("Title", style="bold white")

# Row styles based on status
if task.completed:
    style = "dim"
elif task.priority == "high":
    style = "bold red"
else:
    style = "white"
```

## Advanced Features

### Syntax Highlighting
```python
from rich.syntax import Syntax

# Display code
syntax = Syntax(python_code, "python", theme="monokai", line_numbers=True)
console.print(syntax)

# Display JSON
syntax = Syntax(json_data, "json", theme="github-dark")
console.print(syntax)
```

### Tree Views
```python
from rich.tree import Tree

tree = Tree("Tasks")
tasks_branch = tree.add("Pending (5)")
done_branch = tree.add("Completed (10)")

tasks_branch.add("[green]Buy groceries[/green]")
tasks_branch.add("[blue]Call mom[/blue]")
done_branch.add("[dim]Write report[/dim]")

console.print(tree)
```

### Panels and Boxes
```python
from rich.panel import Panel
from rich.align import Align

# Information panel
console.print(Panel(
    Align.center("[bold]Todo App v1.0[/bold]\nManage your tasks efficiently"),
    title="Welcome",
    border_style="blue"
))

# Error panel
console.print(Panel(
    "[bold red]Error:[/bold red] Task with ID 999 not found",
    title="Error",
    border_style="red"
))
```

## Integration Examples

### With Task Manager
```python
from task_manager_core import TaskManager
from console_ui_builder import TaskDisplay

tm = TaskManager()
display = TaskDisplay(console)

# Add and display
task = tm.create_task("Buy groceries")
display.show_success(f"Task {task.id} created")

# List with filtering
pending = tm.list_tasks("pending")
display.show_task_table(pending, "Pending Tasks")
```

### With CLI Commands
```python
@app.command()
def list(filter: str = Option("all")):
    """List tasks with rich display."""
    tasks = tm.list_tasks(filter)

    if not tasks:
        console.print("[yellow]No tasks found[/yellow]")
        return

    display_task_table(tasks, console)

    # Show statistics
    stats = tm.get_stats()
    console.print(f"\n[dim]{stats['pending']} pending, {stats['completed']} completed[/dim]")
```

## Error Display

### Error Types
```python
def display_error(error, console):
    """Display errors with appropriate styling."""
    if isinstance(error, KeyError):
        console.print(f"[red]Not Found: {error}[/red]")
    elif isinstance(error, ValueError):
        console.print(f"[yellow]Invalid Input: {error}[/yellow]")
    elif isinstance(error, PermissionError):
        console.print(f"[red]Permission Denied: {error}[/red]")
    else:
        console.print(f"[red]Error: {error}[/red]")
```

### Exception Handling
```python
try:
    task = tm.get_task(task_id)
except KeyError:
    console.print(f"[red]Task {task_id} not found[/red]")
    sys.exit(1)
except Exception as e:
    console.print(f"[red]Unexpected error: {e}[/red]")
    sys.exit(1)
```

## Best Practices

1. **Use colors consistently** for different types of information
2. **Provide feedback** for all user actions
3. **Use progress bars** for operations taking >100ms
4. **Keep it clean** - avoid over-styling
5. **Test terminals** - ensure compatibility with different terminals
6. **Handle no-color** gracefully for CI/CD environments

## Terminal Compatibility

### Color Support Detection
```python
import sys

def has_color_support():
    """Check if terminal supports colors."""
    return (
        hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and
        sys.platform != "win32" or
        "ANSICON" in os.environ
    )
```

### Fallback for No Color
```python
if not has_color_support():
    console = Console(file=sys.stderr, no_color=True)
    console.print("Task created")  # Plain text
else:
    console = Console()
    console.print("[green]Task created[/green]")  # With color
```