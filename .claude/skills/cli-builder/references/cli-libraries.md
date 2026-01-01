# CLI Resources

## Official Documentation
- [Click Documentation](https://click.palletsprojects.com/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [argparse Documentation](https://docs.python.org/3/library/argparse.html)

## When to Use Which

### Click (Recommended)
- **Best for**: Most CLI applications
- **Pros**: Rich features, composable, excellent documentation
- **Use when**: Need subcommands, options, arguments, validation

### Typer (Modern Alternative)
- **Best for**: CLIs with type hints
- **Pros**: Type-safe, automatic help, less boilerplate
- **Use when**: Want modern Python with type hints

### argparse (Stdlib)
- **Best for**: Simple scripts, no dependencies
- **Pros**: Built-in, no installation
- **Use when**: Minimal requirements, want zero dependencies

## Common Patterns

### Rich Output with Click
```python
import click
from rich.console import Console
from rich.table import Table

@click.command()
def list():
    console = Console()
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Status", style="yellow")

    # Add rows
    table.add_row("1", "Buy groceries", "pending")
    table.add_row("2", "Walk dog", "done")

    console.print(table)
```

### Progress Bars
```python
from rich.progress import track
import time

def process_tasks():
    for task in track(tasks, description="Processing"):
        time.sleep(0.1)  # Do work
```

### Configuration Files
```python
import click
import yaml

@click.group()
@click.option('--config', type=click.Path(), help='Config file path')
@click.pass_context
def cli(ctx, config):
    """Todo CLI with config support."""
    ctx.ensure_object(dict)
    if config:
        with open(config) as f:
            ctx.obj['config'] = yaml.safe_load(f)
```
