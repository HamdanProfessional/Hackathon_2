"""Console-based TODO List Manager with CRUD operations.

This application provides a menu-driven interface for managing tasks with
full Create, Read, Update, Delete operations plus task completion tracking.
Data is stored in-memory and lost on application exit (Phase I implementation).

Usage:
    python src/main.py
"""

from dataclasses import dataclass
from typing import Optional


# ============================================================================
# MODEL LAYER
# ============================================================================

@dataclass
class Task:
    """Represents a TODO task.

    Attributes:
        id: Unique auto-incrementing identifier
        title: Task name (required, non-empty)
        description: Optional detailed description
        completed: Completion status (default False)
    """
    id: int
    title: str
    description: str
    completed: bool = False


# ============================================================================
# LOGIC LAYER
# ============================================================================

class TaskManager:
    """Manages in-memory collection of tasks.

    Provides CRUD operations (Create, Read, Update, Delete) plus task
    completion tracking. Uses dictionary for O(1) task lookup by ID.

    Attributes:
        _tasks: Dictionary mapping task ID to Task object
        _next_id: Counter for auto-incrementing task IDs (starts at 1)
    """

    def __init__(self) -> None:
        """Initialize TaskManager with empty task collection."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str) -> int:
        """Add new task with auto-assigned ID.

        Args:
            title: Task name (non-empty string, validated by caller)
            description: Task details (can be empty string)

        Returns:
            Assigned task ID (positive integer starting from 1)
        """
        task_id = self._next_id
        task = Task(
            id=task_id,
            title=title,
            description=description,
            completed=False
        )
        self._tasks[task_id] = task
        self._next_id += 1
        return task_id

    def view_tasks(self) -> list[Task]:
        """Return all tasks sorted by ID.

        Returns:
            List of Task objects sorted by ID ascending (empty list if no tasks)
        """
        return sorted(self._tasks.values(), key=lambda task: task.id)

    def update_task(
        self,
        task_id: int,
        title: Optional[str],
        description: Optional[str]
    ) -> bool:
        """Update title and/or description of existing task.

        Args:
            task_id: ID of task to update
            title: New title, or None to keep current value
            description: New description, or None to keep current value

        Returns:
            True if task found and updated, False if task ID not found
        """
        task = self._tasks.get(task_id)
        if task is None:
            return False

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        return True

    def delete_task(self, task_id: int) -> bool:
        """Remove task from collection.

        Args:
            task_id: ID of task to delete

        Returns:
            True if task found and deleted, False if task ID not found
        """
        if task_id not in self._tasks:
            return False

        del self._tasks[task_id]
        return True

    def mark_complete(self, task_id: int) -> bool:
        """Set task's completed status to True.

        Args:
            task_id: ID of task to mark complete

        Returns:
            True if task found and marked, False if task ID not found
        """
        task = self._tasks.get(task_id)
        if task is None:
            return False

        task.completed = True
        return True

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve single task by ID.

        Args:
            task_id: ID of task to retrieve

        Returns:
            Task object if found, None if task ID not found
        """
        return self._tasks.get(task_id)


# ============================================================================
# PRESENTATION LAYER
# ============================================================================

def display_menu() -> None:
    """Print main menu options."""
    print("\n=== TODO List Manager ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Complete")
    print("6. Exit")


def get_menu_choice() -> int:
    """Get and validate menu selection (1-6).

    Loops until valid numeric input in range 1-6 is provided.

    Returns:
        Valid menu choice (1-6)
    """
    while True:
        try:
            choice = int(input("Select option (1-6): "))
            if 1 <= choice <= 6:
                return choice
            else:
                print("Invalid option. Please select 1-6.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_task_id(prompt: str) -> int:
    """Get and validate task ID from user input.

    Args:
        prompt: Prompt message to display

    Returns:
        Valid task ID (positive integer)
    """
    while True:
        try:
            task_id = int(input(prompt))
            return task_id
        except ValueError:
            print("Invalid ID format. Please enter a number.")


def get_non_empty_string(prompt: str) -> str:
    """Get non-empty string from user input.

    Loops until non-empty string (after stripping whitespace) is provided.

    Args:
        prompt: Prompt message to display

    Returns:
        Non-empty string (whitespace trimmed)
    """
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Title cannot be empty. Please try again.")


def handle_add_task(manager: TaskManager) -> None:
    """Prompt for title/description and add task to manager.

    Args:
        manager: TaskManager instance to add task to
    """
    title = get_non_empty_string("Enter task title: ")
    description = input("Enter task description (optional): ")

    task_id = manager.add_task(title, description)
    print(f"Task added with ID {task_id}")


def handle_view_tasks(manager: TaskManager) -> None:
    """Display all tasks with formatting.

    Args:
        manager: TaskManager instance to retrieve tasks from
    """
    print("\n=== Your Tasks ===")
    tasks = manager.view_tasks()

    if not tasks:
        print("No tasks available.")
        return

    for task in tasks:
        status = "[x]" if task.completed else "[ ]"
        print(f"[{task.id}] {status} {task.title}")


def handle_update_task(manager: TaskManager) -> None:
    """Prompt for ID and fields to update, then update task.

    Args:
        manager: TaskManager instance to update task in
    """
    task_id = get_task_id("Enter task ID to update: ")

    # Get new values (empty input = skip field)
    new_title_input = input("Enter new title (press Enter to skip): ").strip()
    new_title = new_title_input if new_title_input else None

    # Note: description does not use .strip() because empty descriptions are valid
    new_description_input = input("Enter new description (press Enter to skip): ")
    new_description = new_description_input if new_description_input else None

    # Check if any changes made
    if new_title is None and new_description is None:
        print("No changes made.")
        return

    # Update task (handles not-found case internally)
    if manager.update_task(task_id, new_title, new_description):
        print(f"Task {task_id} updated successfully.")
    else:
        print(f"Task ID {task_id} not found.")


def handle_delete_task(manager: TaskManager) -> None:
    """Prompt for ID and delete task.

    Args:
        manager: TaskManager instance to delete task from
    """
    task_id = get_task_id("Enter task ID to delete: ")

    if manager.delete_task(task_id):
        print(f"Task {task_id} deleted successfully.")
    else:
        print(f"Task ID {task_id} not found.")


def handle_mark_complete(manager: TaskManager) -> None:
    """Prompt for ID and mark task as complete.

    Args:
        manager: TaskManager instance to mark task in
    """
    task_id = get_task_id("Enter task ID to mark complete: ")

    if manager.mark_complete(task_id):
        print(f"Task {task_id} marked as complete.")
    else:
        print(f"Task ID {task_id} not found.")


def main() -> None:
    """Main application loop.

    Creates TaskManager instance and runs continuous menu loop until
    user selects Exit option.
    """
    manager = TaskManager()

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == 1:
            handle_add_task(manager)
        elif choice == 2:
            handle_view_tasks(manager)
        elif choice == 3:
            handle_update_task(manager)
        elif choice == 4:
            handle_delete_task(manager)
        elif choice == 5:
            handle_mark_complete(manager)
        elif choice == 6:
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
