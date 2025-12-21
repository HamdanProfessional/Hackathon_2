#!/usr/bin/env python3
"""
Task Manager Core - In-memory task management for console todo apps.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
import re


@dataclass
class Task:
    """Task data model for in-memory storage."""
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate task data after creation."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        if len(self.description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")


class TaskManager:
    """In-memory task manager with CRUD operations."""

    def __init__(self):
        """Initialize task manager with empty storage."""
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        """
        Create a new task.

        Args:
            title: Task title (1-200 characters)
            description: Optional task description (max 1000 characters)

        Returns:
            Created Task object

        Raises:
            ValueError: If title is empty or too long
        """
        task = Task(
            id=self._next_id,
            title=title.strip(),
            description=description.strip() if description else ""
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id: int) -> Task:
        """
        Get a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task object

        Raises:
            KeyError: If task not found
        """
        if task_id not in self._tasks:
            raise KeyError(f"Task with ID {task_id} not found")
        return self._tasks[task_id]

    def list_tasks(self, filter_status: Optional[str] = None) -> List[Task]:
        """
        List all tasks with optional filtering.

        Args:
            filter_status: "all", "pending", or "completed"

        Returns:
            List of Task objects
        """
        tasks = list(self._tasks.values())

        if filter_status == "pending":
            tasks = [t for t in tasks if not t.completed]
        elif filter_status == "completed":
            tasks = [t for t in tasks if t.completed]
        elif filter_status == "all":
            pass
        else:
            raise ValueError(f"Invalid filter status: {filter_status}")

        return tasks

    def update_task(self, task_id: int, **kwargs) -> Task:
        """
        Update task fields.

        Args:
            task_id: Task identifier
            **kwargs: Fields to update (title, description)

        Returns:
            Updated Task object

        Raises:
            KeyError: If task not found
            ValueError: If invalid data provided
        """
        task = self.get_task(task_id)

        # Create a copy with updates to validate
        updated_data = {
            'id': task.id,
            'title': kwargs.get('title', task.title),
            'description': kwargs.get('description', task.description),
            'completed': task.completed,
            'created_at': task.created_at
        }

        # Validate by creating new task (will raise ValueError if invalid)
        try:
            updated_task = Task(**updated_data)
            self._tasks[task_id] = updated_task
            return updated_task
        except ValueError as e:
            raise ValueError(f"Invalid update: {e}")

    def toggle_complete(self, task_id: int) -> Task:
        """
        Toggle task completion status.

        Args:
            task_id: Task identifier

        Returns:
            Updated Task object

        Raises:
            KeyError: If task not found
        """
        task = self.get_task(task_id)
        task.completed = not task.completed
        return task

    def delete_task(self, task_id: int) -> Task:
        """
        Delete a task.

        Args:
            task_id: Task identifier

        Returns:
            Deleted Task object

        Raises:
            KeyError: If task not found
        """
        if task_id not in self._tasks:
            raise KeyError(f"Task with ID {task_id} not found")

        task = self._tasks.pop(task_id)
        return task

    def get_stats(self) -> dict:
        """
        Get task statistics.

        Returns:
            Dictionary with task counts
        """
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks.values() if t.completed)
        pending = total - completed

        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'completion_rate': completed / total if total > 0 else 0
        }

    def search_tasks(self, query: str) -> List[Task]:
        """
        Search tasks by title and description.

        Args:
            query: Search query

        Returns:
            List of matching Task objects
        """
        query = query.lower()
        matches = []

        for task in self._tasks.values():
            if (query in task.title.lower() or
                query in task.description.lower()):
                matches.append(task)

        return matches

    def clear_all(self) -> int:
        """
        Clear all tasks.

        Returns:
            Number of tasks deleted
        """
        count = len(self._tasks)
        self._tasks.clear()
        self._next_id = 1
        return count


# Example usage
if __name__ == "__main__":
    # Create task manager
    tm = TaskManager()

    # Add some tasks
    task1 = tm.create_task("Buy groceries", "Milk, eggs, bread")
    task2 = tm.create_task("Call mom")
    task3 = tm.create_task("Finish project", "Complete the todo app by Friday")

    # List all tasks
    print("All tasks:")
    for task in tm.list_tasks():
        status = "✓" if task.completed else "✗"
        print(f"  {task.id}: {task.title} {status}")

    # Mark task as complete
    tm.toggle_complete(task1.id)

    # Get statistics
    stats = tm.get_stats()
    print(f"\nStats: {stats['pending']} pending, {stats['completed']} completed")

    # Search tasks
    print("\nSearch results for 'project':")
    for task in tm.search_tasks("project"):
        print(f"  {task.id}: {task.title}")