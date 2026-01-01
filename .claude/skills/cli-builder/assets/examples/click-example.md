# Click CLI Example

```python
import click
from typing import Optional

@click.group()
def cli():
    """Todo CLI - Manage your tasks from the terminal."""
    pass

@cli.command()
@click.argument('title')
@click.option('--description', '-d', help='Task description')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']), default='medium')
def add(title: str, description: Optional[str], priority: str):
    """Add a new task."""
    click.echo(f"Adding task: {title}")
    if description:
        click.echo(f"Description: {description}")
    click.echo(f"Priority: {priority}")

@cli.command()
@click.option('--status', type=click.Choice(['all', 'pending', 'done']), default='pending')
def list(status: str):
    """List all tasks."""
    click.echo(f"Listing {status} tasks...")

@cli.command()
@click.argument('task_id', type=int)
def complete(task_id: int):
    """Mark a task as complete."""
    click.echo(f"Marking task {task_id} as complete ✅")

@cli.command()
@click.argument('task_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this task?')
def delete(task_id: int):
    """Delete a task."""
    click.echo(f"Deleting task {task_id}")

if __name__ == '__main__':
    cli()
```

## Usage

```bash
# Add a task
python cli.py add "Buy groceries" -d "Milk, eggs, bread" -p high

# List all tasks
python cli.py list --status all

# Complete a task
python cli.py complete 1

# Delete a task
python cli.py delete 1
```
