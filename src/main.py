"""
TODO List Manager - Phase I (In-Memory Console Application)

A command-line todo list manager with full CRUD operations (Create, Read, Update, Delete).
Tasks are stored in memory only and will be lost when the application exits.

Phase I Constraints:
- Single-file implementation (all code in this file)
- In-memory storage only (no file/database persistence)
- Python 3.13+ standard library only (no external dependencies)
- Console interface with continuous menu loop

Architecture:
- Model Layer: Task TypedDict data structure
- Logic Layer: TaskManager class for CRUD operations
- Presentation Layer: main() function with menu loop and I/O handlers

Author: Generated with Claude Code
Version: 1.0.0 (Phase I)
"""

from typing import Dict, List, Optional, TypedDict


# ============================================================================
# MODEL LAYER - Data Structures
# ============================================================================

class Task(TypedDict):
    """
    Represents a single todo item.

    Attributes:
        id: Unique identifier, auto-incremented, never reused
        title: Required task name/summary
        description: Optional task details (can be empty string)
        completed: Status flag (False=pending, True=completed)
    """
    id: int
    title: str
    description: str
    completed: bool


# ============================================================================
# LOGIC LAYER - Business Logic
# ============================================================================

class TaskManager:
    """
    Manages CRUD operations for in-memory task storage.

    Maintains a list of tasks and an auto-incrementing ID counter.
    Provides methods for create, read, update, delete, and mark complete operations.
    Validates business rules (title non-empty, ID exists, etc.).
    """

    def __init__(self) -> None:
        """Initialize task manager with empty list and ID counter at 1."""
        self._tasks: List[Task] = []
        self._next_id: int = 1

    def add_task(self, title: str, description: str) -> int:
        """
        Add a new task to the list.

        Args:
            title: Non-empty task name
            description: Optional task details (can be empty string)

        Returns:
            The auto-assigned task ID

        Raises:
            ValueError: If title is empty or whitespace-only
        """
        if not title.strip():
            raise ValueError("Title cannot be empty")

        task_id = self._next_id
        task: Task = {
            "id": task_id,
            "title": title.strip(),
            "description": description,
            "completed": False
        }
        self._tasks.append(task)
        self._next_id += 1
        return task_id

    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks.

        Returns:
            List of task dictionaries (may be empty)
        """
        return self._tasks

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Find a task by ID.

        Args:
            task_id: The unique task identifier

        Returns:
            Task dictionary if found, None otherwise
        """
        for task in self._tasks:
            if task["id"] == task_id:
                return task
        return None

    def update_task(self, task_id: int, title: Optional[str],
                    description: Optional[str]) -> bool:
        """
        Update task fields. None values mean 'keep current value'.

        Args:
            task_id: The unique task identifier
            title: New title or None to skip
            description: New description or None to skip

        Returns:
            True if task found and updated, False if task not found

        Raises:
            ValueError: If title is being updated to empty string
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty")
            task["title"] = title.strip()

        if description is not None:
            task["description"] = description

        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Remove a task from the list.

        Args:
            task_id: The unique task identifier

        Returns:
            True if task found and deleted, False if task not found
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        self._tasks.remove(task)
        return True

    def mark_complete(self, task_id: int) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: The unique task identifier

        Returns:
            True if task found and marked, False if task not found
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        task["completed"] = True
        return True


# ============================================================================
# PRESENTATION LAYER - User Interface Helpers
# ============================================================================

def display_menu() -> None:
    """Print the main menu options."""
    print("\n" + "=" * 30)
    print("   TODO LIST MANAGER")
    print("=" * 30)
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Complete")
    print("6. Exit")
    print("=" * 30)


def get_menu_choice() -> int:
    """
    Get user's menu selection with validation.

    Returns:
        Valid menu choice (1-6)

    Note: Loops until valid input received
    """
    while True:
        try:
            choice = int(input("Enter your choice (1-6): ").strip())
            if 1 <= choice <= 6:
                return choice
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
        except ValueError:
            print("Invalid choice. Please enter a number between 1 and 6.")


def get_task_id_input() -> int:
    """
    Prompt for task ID with validation.

    Returns:
        Valid integer task ID

    Note: Loops until valid integer received
    """
    while True:
        try:
            task_id = int(input("Enter task ID: ").strip())
            return task_id
        except ValueError:
            print("Invalid ID. Please enter a number.")


def get_non_empty_input(prompt: str) -> str:
    """
    Prompt until non-empty input received.

    Args:
        prompt: The input prompt to display

    Returns:
        Non-empty string input
    """
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def display_tasks(tasks: List[Task]) -> None:
    """
    Print formatted task list with ID, status, and title.

    Args:
        tasks: List of task dictionaries

    Output format:
        [1] [ ] Buy groceries
        [2] [x] Call dentist
    """
    if not tasks:
        print("\nNo tasks available.")
        return

    print("\n" + "=" * 40)
    print("   YOUR TASKS")
    print("=" * 40)

    completed_count = sum(1 for task in tasks if task["completed"])
    pending_count = len(tasks) - completed_count

    for task in tasks:
        status = "[x]" if task["completed"] else "[ ]"
        print(f"[{task['id']}] {status} {task['title']}")

    print("=" * 40)
    print(f"Total: {len(tasks)} tasks ({completed_count} completed, {pending_count} pending)")
    print()


# ============================================================================
# PRESENTATION LAYER - Menu Handlers
# ============================================================================

def handle_add_task(manager: TaskManager) -> None:
    """
    Handle Add Task menu option.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Add New Task ---")
    title = get_non_empty_input("Enter task title: ")
    description = input("Enter task description (optional, press Enter to skip): ").strip()

    try:
        task_id = manager.add_task(title, description)
        print(f"✓ Task added with ID {task_id}")
    except ValueError as e:
        print(f"✗ Error: {e}")


def handle_view_tasks(manager: TaskManager) -> None:
    """
    Handle View Tasks menu option.

    Args:
        manager: TaskManager instance
    """
    tasks = manager.get_all_tasks()
    display_tasks(tasks)


def handle_update_task(manager: TaskManager) -> None:
    """
    Handle Update Task menu option.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Update Task ---")
    task_id = get_task_id_input()

    # Check if task exists
    task = manager.get_task_by_id(task_id)
    if not task:
        print(f"✗ Task with ID {task_id} not found")
        return

    print("Leave blank to keep current value")
    title_input = input(f"New title (current: '{task['title']}'): ").strip()
    desc_input = input(f"New description (current: '{task['description']}'): ").strip()

    # Convert empty string to None (skip)
    title = None if title_input == "" else title_input
    description = None if desc_input == "" else desc_input

    try:
        if manager.update_task(task_id, title, description):
            print(f"✓ Task {task_id} updated successfully")
        else:
            print(f"✗ Task with ID {task_id} not found")
    except ValueError as e:
        print(f"✗ Error: {e}")


def handle_delete_task(manager: TaskManager) -> None:
    """
    Handle Delete Task menu option.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Delete Task ---")
    task_id = get_task_id_input()

    if manager.delete_task(task_id):
        print(f"✓ Task {task_id} deleted successfully")
    else:
        print(f"✗ Task with ID {task_id} not found")


def handle_mark_complete(manager: TaskManager) -> None:
    """
    Handle Mark Complete menu option.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Mark Task Complete ---")
    task_id = get_task_id_input()

    if manager.mark_complete(task_id):
        print(f"✓ Task {task_id} marked as complete")
    else:
        print(f"✗ Task with ID {task_id} not found")


# ============================================================================
# MAIN FUNCTION - Application Entry Point
# ============================================================================

def main() -> None:
    """
    Main application loop.

    Creates TaskManager instance and runs continuous menu loop until user exits.
    """
    manager = TaskManager()

    print("\n" + "="*50)
    print(" Welcome to TODO List Manager - Phase I")
    print(" (In-memory storage - data will be lost on exit)")
    print("="*50)

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
            print("\nThank you for using TODO List Manager!")
            print("(All data has been cleared)\n")
            break


if __name__ == "__main__":
    main()
