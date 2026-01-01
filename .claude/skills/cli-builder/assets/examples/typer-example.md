# Typer CLI Example

```python
import typer
from typing import Optional

app = typer.Typer(help="Todo CLI - Modern command-line interface")

@app.command()
def add(
    title: str,
    description: Optional[str] = typer.Option(None, "-d", "--description", help="Task description"),
    priority: str = typer.Option("medium", "-p", "--priority", help="Task priority")
):
    """Add a new task to your todo list."""
    typer.echo(f"✅ Added task: {title}")
    if description:
        typer.echo(f"   📝 {description}")
    typer.echo(f"   ⚡ Priority: {priority}")

@app.command()
def list(
    status: str = typer.Option("pending", "--status", help="Filter by status")
):
    """List all tasks."""
    typer.echo(f"📋 Tasks ({status}):")
    # Fetch and display tasks here

@app.command()
def complete(task_id: int):
    """Mark a task as complete."""
    typer.echo(f"✨ Marked task {task_id} as complete!")

@app.command()
def delete(task_id: int, confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")):
    """Delete a task."""
    if not confirm:
        if not typer.confirm(f"Delete task {task_id}?"):
            raise typer.Abort()
    typer.echo(f"🗑️  Deleted task {task_id}")

if __name__ == "__main__":
    app()
```

## Usage

```bash
# Add a task
python cli.py add "Buy groceries" -d "Milk, eggs, bread" -p high

# List pending tasks
python cli.py list --status pending

# Complete a task
python cli.py complete 1

# Delete without confirmation
python cli.py delete 1 --yes
```
