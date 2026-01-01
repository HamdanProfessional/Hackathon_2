# Console UI Builder - Evolution of TODO Edition

While the Evolution of TODO project moved from CLI to web, this guide documents console UI patterns used in testing and utilities.

## Rich Terminal Output

The project uses Rich for beautiful terminal output in tests and scripts.

### Installation

```bash
pip install rich
```

### Progress Bars

```python
# tests/test_chatbot.py
from rich.console import Console
from rich.progress import Progress

console = Console()

with Progress() as progress:
    task1 = progress.add_task("[cyan]Running tests...", total=100)

    while not progress.finished:
        progress.update(task1, advance=1)
        time.sleep(0.02)
```

### Colored Output

```python
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "pass": "bold green",
    "fail": "bold red",
})

console = Console(theme=custom_theme)

# Usage
console.print("[info]Backend Health Check[/info]: [pass]PASS[/pass]")
console.print("[error]Connection failed[/error]")
```

### Tables

```python
from rich.table import Table
from rich.console import Console

console = Console()

table = Table(title="Test Results")
table.add_column("Test", style="cyan")
table.add_column("Status", style="magenta")
table.add_column("Details", style="green")

table.add_row("Backend Health", "PASS", "Status: healthy")
table.add_row("Task Creation", "PASS", "Task ID: 123")
table.add_row("CORS Config", "WARN", "No CORS headers")

console.print(table)
```

### Panels

```python
from rich.panel import Panel
from rich.console import Console

console = Console()

console.print(Panel.fit(
    "[bold green]All tests passed![/bold green]",
    title="Test Summary",
    subtitle="Success Rate: 95.5%"
))
```

### Syntax Highlighting

```python
from rich.syntax import Syntax
from rich.console import Console

console = Console()

code = """
async def create_task(db: AsyncSession, task_data: TaskCreate):
    task = Task(**task_data.dict())
    db.add(task)
    await db.commit()
    return task
"""

console.print(Syntax(code, "python", theme="monokai"))
```

## Logging Patterns

### Structured Logging

```python
# backend/app/services/event_publisher.py
import logging

logger = logging.getLogger(__name__)

# Contextual logging
logger.info(f"Published task-created event: {event_data.get('task_id')}")
logger.warning(f"Failed to publish event: HTTP {response.status_code}")
logger.error(f"Failed to publish task-created event: {e}")

# Debug logging (only in development)
if settings.DEBUG:
    logger.debug(f"[AGENT] User ID: {user_id}, Message: {user_message[:50]}...")
```

### Pretty Print for Debug

```python
import json

# Pretty print JSON
print(json.dumps(event_data, indent=2))

# Pretty print model
from sqlalchemy import inspect
from pprint import pprint

pprint(inspect(task).mapper.attrs)
```

## ASCII Art

### ASCII Status Banner

```python
def print_banner():
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   Evolution of TODO - Test Suite                          ║
║   Phase V: Event-Driven Cloud Deployment                  ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")
```

### ASCII Charts

```python
def print_results_chart(results):
    print("\nTest Results:")
    print("═══════════════════════════════════════")

    passed = len([r for r in results if r["status"] == "PASS"])
    failed = len([r for r in results if r["status"] == "FAIL"])
    total = len(results)

    bar_width = 40
    passed_bar = int(passed / total * bar_width)
    failed_bar = bar_width - passed_bar

    print(f"✓ Passed: [{'█' * passed_bar}{' ' * failed_bar}] {passed}/{total}")
    print(f"✗ Failed: [{' ' * passed_bar}{'█' * failed_bar}] {failed}/{total}")
    print()
```

## Interactive CLI with Questions

### Confirm Before Destructive Actions

```python
def confirm_action(message: str) -> bool:
    """Ask user for confirmation."""
    response = input(f"{message} [y/N]: ").strip().lower()
    return response in ['y', 'yes']

# Usage
if confirm_action("Delete all tasks?"):
    delete_all_tasks()
```

### Multiple Choice

```python
from typing import List

def choose_option(prompt: str, options: List[str]) -> int:
    """Present options and get user choice."""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    while True:
        try:
            choice = int(input("Choose: "))
            if 1 <= choice <= len(options):
                return choice - 1
            print("Invalid choice, try again")
        except ValueError:
            print("Please enter a number")

# Usage
options = ["Production", "Staging", "Development"]
env = choose_option("Select environment:", options)
print(f"Selected: {options[env]}")
```

## Error Display

### Color-Coded Errors

```python
def print_error(message: str, details: str = ""):
    """Print error message with details."""
    print(f"\n❌ [bold red]Error:[/bold red] {message}")
    if details:
        print(f"   {details}\n")

# Usage
print_error("Database connection failed", "Check DATABASE_URL in .env")
```

### Success Messages

```python
def print_success(message: str):
    """Print success message."""
    print(f"\n✅ [bold green]Success:[/bold green] {message}\n")

# Usage
print_success("Database migrated successfully")
```

## Test Runner Output

### Comprehensive Test Report

```python
# tests/test_chatbot.py
def generate_summary(self):
    """Generate test summary with ASCII art."""
    print("\n" + "=" * 60)
    print("[bold cyan]TEST SUMMARY[/bold cyan]")
    print("=" * 60)

    total = len(self.test_results)
    passed = len([r for r in self.test_results if r["status"] == "PASS"])
    failed = len([r for r in self.test_results if r["status"] == "FAIL"])

    print(f"\n[green]✓ Total Tests:[/green] {total}")
    print(f"[green]✓ Passed:[/green] {passed}")
    print(f"[red]✗ Failed:[/red] {failed}")
    print(f"[cyan]Success Rate:[/cyan] {(passed/total*100):.1f}%\n")

    if failed > 0:
        print("[red]Failed Tests:[/red]")
        for result in self.test_results:
            if result["status"] == "FAIL":
                print(f"  • {result['test']}: {result['details']}")
```

## Console UI Best Practices

1. **Use Rich for beautiful output** - Tables, progress bars, panels
2. **Color-code status** - Green for success, red for errors
3. **Clear error messages** - Show what went wrong and how to fix
4. **Progress indicators** - For long-running operations
5. **Confirmation prompts** - Before destructive actions
6. **Structured logging** - Use logging module, not print
7. **Timestamps** - Include in logs for debugging
8. **Consistent formatting** - Use same style throughout

## Example: Complete Test Runner

```python
#!/usr/bin/env python3
"""
Comprehensive Test Runner with Rich UI
"""
import sys
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from rich.panel import Panel

console = Console()


def main():
    # Print banner
    console.print(Panel.fit(
        "[bold cyan]Evolution of TODO - Test Suite[/bold cyan]",
        subtitle="Phase V: Event-Driven Cloud"
    ))

    # Run tests with progress bar
    with Progress() as progress:
        task = progress.add_task("[cyan]Running tests...", total=100)

        results = []
        for i in range(100):
            # Run test
            result = run_test(i)
            results.append(result)

            # Update progress
            progress.update(task, advance=1)

    # Display results table
    table = Table(title="Test Results")
    table.add_column("Test", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Time", justify="right")

    for result in results:
        status = "[green]✓[/green]" if result["passed"] else "[red]✗[/red]"
        table.add_row(result["name"], status, f"{result['time']}ms")

    console.print(table)

    # Summary
    passed = sum(1 for r in results if r["passed"])
    console.print(Panel.fit(
        f"[bold green]Passed: {passed}/{len(results)}[/bold green]",
        title="Summary"
    ))

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
```
