"""
Command-line interface for the Todo Console Application.
"""

import re
import sys
from typing import Optional

from rich.console import Console
from rich.table import Table

from .models import TaskList, Task

console = Console()


class TodoCLI:
    """Interactive command-line interface for todo management."""

    def __init__(self) -> None:
        """Initialize the CLI with an empty task list."""
        self.tasks = TaskList()
        self.running = True

    def print_welcome(self) -> None:
        """Print welcome message."""
        console.print(
            "\n[bold violet]📝 Evolution of TODO - Phase I[/bold violet]"
            "\n[dim]In-Memory Console Application[/dim]\n"
        )

    def print_help(self) -> None:
        """Print help message with available commands."""
        help_table = Table(title="Available Commands", show_header=False, padding=(0, 2))
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description")

        help_table.add_row("add <title> [-d <desc>]", "Add a new task")
        help_table.add_row("list", "List all tasks")
        help_table.add_row("update <id> [-t <title>] [-d <desc>]", "Update a task")
        help_table.add_row("delete <id>", "Delete a task")
        help_table.add_row("complete <id>", "Mark task as complete")
        help_table.add_row("uncomplete <id>", "Mark task as incomplete")
        help_table.add_row("help", "Show this help")
        help_table.add_row("exit", "Exit the application")

        console.print(help_table)

    def cmd_add(self, args: list[str]) -> None:
        """
        Add a new task.

        Usage: add <title> [-d <description>]
        """
        if not args:
            console.print("[red]Error: Title is required[/red]")
            console.print("Usage: [cyan]add <title> [-d <description>][/cyan]")
            return

        # Parse arguments
        title_parts = []
        description: Optional[str] = None
        i = 0

        while i < len(args):
            if args[i] == "-d" and i + 1 < len(args):
                description = " ".join(args[i + 1:])
                break
            title_parts.append(args[i])
            i += 1

        title = " ".join(title_parts)

        try:
            task = self.tasks.add(title, description)
            console.print(
                f"[green]✓[/green] Task added: [bold]{task.title}[/bold] "
                f"[dim](ID: {task.id})[/dim]"
            )
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")

    def cmd_list(self, _args: list[str]) -> None:
        """List all tasks."""
        tasks = self.tasks.get_all()

        if not tasks:
            console.print(
                "\n[dim]No tasks yet. Use 'add <title>' to create your first task.[/dim]\n"
            )
            return

        table = Table(title="\n📋 Your Tasks")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Status", width=8)
        table.add_column("Title", style="white")
        table.add_column("Description", style="dim")

        for task in tasks:
            status = "[green]✓ Done[/green]" if task.completed else "[yellow]○ Todo[/yellow]"
            table.add_row(str(task.id), status, task.title, task.description or "")

        console.print(table)

        # Show summary
        completed = sum(1 for t in tasks if t.completed)
        total = len(tasks)
        console.print(
            f"\n[dim]Summary: {completed}/{total} tasks completed[/dim]\n"
        )

    def cmd_update(self, args: list[str]) -> None:
        """
        Update a task.

        Usage: update <id> [-t <title>] [-d <description>]
        """
        if not args or not args[0].isdigit():
            console.print("[red]Error: Task ID is required[/red]")
            console.print("Usage: [cyan]update <id> [-t <title>] [-d <description>][/cyan]")
            return

        task_id = int(args[0])
        remaining = args[1:]

        title: Optional[str] = None
        description: Optional[str] = None

        i = 0
        while i < len(remaining):
            if remaining[i] == "-t" and i + 1 < len(remaining):
                # Extract title until next flag or end
                i += 1
                title_parts = []
                while i < len(remaining) and not remaining[i].startswith("-"):
                    title_parts.append(remaining[i])
                    i += 1
                title = " ".join(title_parts) if title_parts else None
            elif remaining[i] == "-d" and i + 1 < len(remaining):
                i += 1
                description = " ".join(remaining[i:])
                break
            else:
                i += 1

        if not title and not description:
            console.print("[red]Error: At least one of -t or -d is required[/red]")
            return

        try:
            task = self.tasks.update(task_id, title, description)
            if task:
                console.print(
                    f"[green]✓[/green] Task updated: [bold]{task.title}[/bold] "
                    f"[dim](ID: {task.id})[/dim]"
                )
            else:
                console.print(f"[red]Error: Task {task_id} not found[/red]")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")

    def cmd_delete(self, args: list[str]) -> None:
        """
        Delete a task.

        Usage: delete <id>
        """
        if not args or not args[0].isdigit():
            console.print("[red]Error: Task ID is required[/red]")
            console.print("Usage: [cyan]delete <id>[/cyan]")
            return

        task_id = int(args[0])
        task = self.tasks.get_by_id(task_id)

        if task:
            if self.tasks.delete(task_id):
                console.print(
                    f"[green]✓[/green] Task deleted: [bold]{task.title}[/bold] "
                    f"[dim](ID: {task_id})[/dim]"
                )
        else:
            console.print(f"[red]Error: Task {task_id} not found[/red]")

    def cmd_complete(self, args: list[str]) -> None:
        """
        Mark task as complete.

        Usage: complete <id>
        """
        if not args or not args[0].isdigit():
            console.print("[red]Error: Task ID is required[/red]")
            console.print("Usage: [cyan]complete <id>[/cyan]")
            return

        task_id = int(args[0])
        task = self.tasks.set_complete(task_id, True)

        if task:
            console.print(
                f"[green]✓[/green] Task marked as complete: [bold]{task.title}[/bold] "
                f"[dim](ID: {task_id})[/dim]"
            )
        else:
            console.print(f"[red]Error: Task {task_id} not found[/red]")

    def cmd_uncomplete(self, args: list[str]) -> None:
        """
        Mark task as incomplete.

        Usage: uncomplete <id>
        """
        if not args or not args[0].isdigit():
            console.print("[red]Error: Task ID is required[/red]")
            console.print("Usage: [cyan]uncomplete <id>[/cyan]")
            return

        task_id = int(args[0])
        task = self.tasks.set_complete(task_id, False)

        if task:
            console.print(
                f"[yellow]○[/yellow] Task marked as incomplete: [bold]{task.title}[/bold] "
                f"[dim](ID: {task_id})[/dim]"
            )
        else:
            console.print(f"[red]Error: Task {task_id} not found[/red]")

    def cmd_exit(self, _args: list[str]) -> None:
        """Exit the application."""
        self.running = False
        console.print("\n[bold violet]Goodbye! 👋[/bold violet]\n")

    def execute(self, command: str) -> None:
        """
        Execute a command.

        Args:
            command: Raw command string from user input
        """
        parts = command.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        commands = {
            "add": self.cmd_add,
            "list": self.cmd_list,
            "update": self.cmd_update,
            "delete": self.cmd_delete,
            "complete": self.cmd_complete,
            "uncomplete": self.cmd_uncomplete,
            "help": lambda _: self.print_help(),
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
        }

        handler = commands.get(cmd)
        if handler:
            handler(args)
        else:
            console.print(f"[red]Unknown command: '{cmd}'[/red]")
            console.print("Type [cyan]help[/cyan] to see available commands")

    def run(self) -> None:
        """Run the interactive CLI loop."""
        self.print_welcome()
        self.print_help()

        while self.running:
            try:
                command = console.input("\n[bold cyan]todo>[/bold cyan] ")
                if command.strip():
                    self.execute(command)
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
            except EOFError:
                self.cmd_exit([])
            except Exception as e:
                console.print(f"[red]Unexpected error: {e}[/red]")


def main() -> int:
    """Entry point for the console application."""
    cli = TodoCLI()
    cli.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
