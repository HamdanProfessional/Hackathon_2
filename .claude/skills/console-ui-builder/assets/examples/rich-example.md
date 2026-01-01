# Rich Console UI Example

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Prompt
from rich.layout import Layout
import time

console = Console()

# 1. Beautiful Tables
def show_tasks_table():
    table = Table(title="📋 My Tasks")
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Task", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Priority", style="red")

    table.add_row("1", "Buy groceries", "✅ Done", "🔴 High")
    table.add_row("2", "Walk the dog", "⏳ Pending", "🟡 Medium")
    table.add_row("3", "Read book", "⏳ Pending", "🟢 Low")

    console.print(table)

# 2. Panels
def show_welcome():
    console.print(Panel(
        "[bold green]Welcome to Todo CLI![/bold green]\n"
        "Manage your tasks with style ✨",
        title="Todo App",
        border_style="blue"
    ))

# 3. Progress Bars
def process_tasks():
    tasks = ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5"]
    for task in track(tasks, description="Processing tasks..."):
        time.sleep(0.5)

# 4. Interactive Prompts
def add_task_interactive():
    title = Prompt.ask("Enter task title")
    priority = Prompt.ask(
        "Select priority",
        choices=["low", "medium", "high"],
        default="medium"
    )
    console.print(f"✅ Added: [bold]{title}[/bold] ({priority})")

# 5. Layouts
def show_dashboard():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["header"].update(Panel("🎯 Todo Dashboard", style="bold blue"))
    layout["body"].update(Panel("Your tasks here..."))
    layout["footer"].update(Panel("Press q to quit", style="dim"))
    console.print(layout)

if __name__ == "__main__":
    show_welcome()
    show_tasks_table()
```
