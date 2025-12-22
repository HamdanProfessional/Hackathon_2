"""
Data models for the Todo Console Application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Represents a single todo item."""

    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        """Return string representation of task."""
        status = "✓" if self.completed else " "
        desc = f" - {self.description}" if self.description else ""
        return f"[{self.id}] [{status}] {self.title}{desc}"


class TaskList:
    """In-memory storage for tasks."""

    def __init__(self) -> None:
        """Initialize empty task list."""
        self._tasks: list[Task] = []
        self._next_id: int = 1

    def add(self, title: str, description: Optional[str] = None) -> Task:
        """
        Add a new task.

        Args:
            title: Task title (required)
            description: Optional task description

        Returns:
            The created task

        Raises:
            ValueError: If title is empty
        """
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        task = Task(
            id=self._next_id,
            title=title.strip(),
            description=description.strip() if description else None,
        )
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_all(self) -> list[Task]:
        """Return all tasks."""
        return self._tasks.copy()

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """
        Get task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task if found, None otherwise
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def update(self, task_id: int, title: Optional[str] = None,
               description: Optional[str] = None) -> Optional[Task]:
        """
        Update a task.

        Args:
            task_id: Task identifier
            title: New title (optional)
            description: New description (optional)

        Returns:
            Updated task if found, None otherwise

        Raises:
            ValueError: If new title is empty
        """
        task = self.get_by_id(task_id)
        if not task:
            return None

        if title is not None:
            if not title.strip():
                raise ValueError("Task title cannot be empty")
            task.title = title.strip()

        if description is not None:
            task.description = description.strip() if description.strip() else None

        return task

    def delete(self, task_id: int) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task identifier

        Returns:
            True if deleted, False if not found
        """
        task = self.get_by_id(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False

    def toggle_complete(self, task_id: int) -> Optional[Task]:
        """
        Toggle task completion status.

        Args:
            task_id: Task identifier

        Returns:
            Updated task if found, None otherwise
        """
        task = self.get_by_id(task_id)
        if task:
            task.completed = not task.completed
        return task

    def set_complete(self, task_id: int, completed: bool) -> Optional[Task]:
        """
        Set task completion status.

        Args:
            task_id: Task identifier
            completed: Desired completion status

        Returns:
            Updated task if found, None otherwise
        """
        task = self.get_by_id(task_id)
        if task:
            task.completed = completed
        return task
