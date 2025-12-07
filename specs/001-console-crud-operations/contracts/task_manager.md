# Contract: TaskManager Class

**Feature**: Console CRUD Operations
**Date**: 2025-12-06
**Type**: Internal API Contract (Single-File Application)

## Overview

The `TaskManager` class encapsulates all business logic for CRUD operations on tasks. It maintains the task list and ID counter, provides methods for all operations, and handles business rule validation.

**Location**: `src/main.py` (Logic Layer section)

**Responsibility**: Business logic only - no user I/O, no presentation concerns

---

## Class Definition

```python
class TaskManager:
    """
    Manages CRUD operations for in-memory task storage.

    Maintains a list of tasks and an auto-incrementing ID counter.
    Provides methods for create, read, update, delete, and mark complete operations.
    Validates business rules (title non-empty, ID exists, etc.).

    Attributes:
        _tasks: List of task dictionaries (private)
        _next_id: Next available ID counter (private)
    """

    def __init__(self) -> None:
        """Initialize task manager with empty list and ID counter at 1."""
        self._tasks: List[Task] = []
        self._next_id: int = 1
```

---

## Method Contracts

### `add_task`

**Purpose**: Create a new task with auto-assigned ID

**Signature**:
```python
def add_task(self, title: str, description: str) -> int:
```

**Parameters**:
- `title` (str): Task name, must be non-empty after strip()
- `description` (str): Task details, can be empty string

**Returns**:
- `int`: The auto-assigned task ID (always positive, unique)

**Raises**:
- `ValueError`: If title is empty or whitespace-only

**Behavior**:
1. Validate title is non-empty (after strip)
2. Assign current `_next_id` to new task
3. Increment `_next_id` for next task
4. Create task dict/dataclass with id, title, description, completed=False
5. Append to `_tasks` list
6. Return assigned ID

**Example**:
```python
manager = TaskManager()
task_id = manager.add_task("Buy groceries", "Milk, eggs")  # Returns 1
task_id = manager.add_task("Call dentist", "")             # Returns 2
```

**Business Rules**:
- Title cannot be empty (enforced)
- Description can be empty (allowed)
- ID auto-assigned (user cannot specify)
- Completed always starts as False (enforced)

---

### `get_all_tasks`

**Purpose**: Retrieve all tasks in the list

**Signature**:
```python
def get_all_tasks(self) -> List[Task]:
```

**Parameters**: None

**Returns**:
- `List[Task]`: List of all task dictionaries/dataclasses (may be empty list)

**Raises**: None

**Behavior**:
1. Return `_tasks` list (or copy to prevent external mutation)

**Example**:
```python
manager = TaskManager()
manager.add_task("Task 1", "")
manager.add_task("Task 2", "Details")

tasks = manager.get_all_tasks()
# Returns: [
#   {"id": 1, "title": "Task 1", "description": "", "completed": False},
#   {"id": 2, "title": "Task 2", "description": "Details", "completed": False}
# ]
```

**Business Rules**:
- Returns all tasks, no filtering
- Empty list if no tasks exist
- Order: Insertion order (list order)

---

### `get_task_by_id`

**Purpose**: Find a specific task by its ID

**Signature**:
```python
def get_task_by_id(self, task_id: int) -> Optional[Task]:
```

**Parameters**:
- `task_id` (int): The unique task identifier

**Returns**:
- `Task`: Task dictionary/dataclass if found
- `None`: If no task with that ID exists

**Raises**: None (returns None instead)

**Behavior**:
1. Iterate through `_tasks`
2. Return first task where `task["id"] == task_id`
3. Return None if no match found

**Example**:
```python
manager = TaskManager()
manager.add_task("Task 1", "")

task = manager.get_task_by_id(1)  # Returns task dict
task = manager.get_task_by_id(999)  # Returns None
```

**Business Rules**:
- Linear search O(n) acceptable for Phase I
- Returns None (not exception) if task not found
- Caller responsible for checking None

---

### `update_task`

**Purpose**: Update task title and/or description

**Signature**:
```python
def update_task(self, task_id: int, title: Optional[str],
                description: Optional[str]) -> bool:
```

**Parameters**:
- `task_id` (int): The unique task identifier
- `title` (Optional[str]): New title, or None to skip (keep current)
- `description` (Optional[str]): New description, or None to skip (keep current)

**Returns**:
- `bool`: True if task found and updated successfully
- `bool`: False if task not found

**Raises**:
- `ValueError`: If task found but new title is empty (only when title is not None)

**Behavior**:
1. Find task by ID using `get_task_by_id()`
2. If not found, return False
3. If title is not None:
   - Validate title is non-empty
   - Update task["title"]
4. If description is not None:
   - Update task["description"] (no validation, empty allowed)
5. If both None, no changes made (but still returns True)
6. Return True

**Example**:
```python
manager = TaskManager()
id = manager.add_task("Original Title", "Original Desc")

# Update both fields
manager.update_task(id, "New Title", "New Desc")  # Returns True

# Update only title (skip description)
manager.update_task(id, "Newer Title", None)  # Returns True

# Update only description (skip title)
manager.update_task(id, None, "Newer Desc")  # Returns True

# Skip both (no change, but valid)
manager.update_task(id, None, None)  # Returns True

# Non-existent ID
manager.update_task(999, "Title", "Desc")  # Returns False

# Empty title (validation error)
manager.update_task(id, "", "Desc")  # Raises ValueError
```

**Business Rules**:
- None parameter = skip field (keep current value)
- Empty string for title = validation error
- Empty string for description = allowed (but presentation layer treats empty as skip)
- Completed status NOT affected by update
- Both None = no-op but valid (returns True if task exists)

---

### `delete_task`

**Purpose**: Remove a task from the list

**Signature**:
```python
def delete_task(self, task_id: int) -> bool:
```

**Parameters**:
- `task_id` (int): The unique task identifier

**Returns**:
- `bool`: True if task found and deleted
- `bool`: False if task not found

**Raises**: None

**Behavior**:
1. Find task by ID using `get_task_by_id()`
2. If not found, return False
3. Remove task from `_tasks` list
4. Return True
5. **Important**: Do NOT decrement `_next_id` (IDs never reused)

**Example**:
```python
manager = TaskManager()
id1 = manager.add_task("Task 1", "")  # ID 1
id2 = manager.add_task("Task 2", "")  # ID 2
id3 = manager.add_task("Task 3", "")  # ID 3

manager.delete_task(2)  # Returns True, task 2 removed

id4 = manager.add_task("Task 4", "")  # ID 4 (not 2!)

manager.delete_task(999)  # Returns False (not found)
```

**Business Rules**:
- Task removed from list entirely
- ID never reused (FR-004)
- Returns False (not exception) if task not found
- Can delete completed or pending tasks

---

### `mark_complete`

**Purpose**: Mark a task as completed

**Signature**:
```python
def mark_complete(self, task_id: int) -> bool:
```

**Parameters**:
- `task_id` (int): The unique task identifier

**Returns**:
- `bool`: True if task found and marked complete
- `bool`: False if task not found

**Raises**: None

**Behavior**:
1. Find task by ID using `get_task_by_id()`
2. If not found, return False
3. Set task["completed"] = True
4. Return True
5. **Idempotent**: If already True, set to True again (no error)

**Example**:
```python
manager = TaskManager()
id = manager.add_task("Task", "")

manager.mark_complete(id)  # Returns True, completed=True
manager.mark_complete(id)  # Returns True, still completed=True (idempotent)

manager.mark_complete(999)  # Returns False (not found)
```

**Business Rules**:
- Changes completed from False → True
- Idempotent (True → True is allowed)
- No "uncomplete" operation in Phase I
- Returns False (not exception) if task not found

---

## Usage Example

```python
from typing import List, Optional, TypedDict

class Task(TypedDict):
    id: int
    title: str
    description: str
    completed: bool

class TaskManager:
    # ... implementation

# Usage
def main():
    manager = TaskManager()

    # Add tasks
    id1 = manager.add_task("Buy groceries", "Milk, eggs, bread")
    id2 = manager.add_task("Call dentist", "")

    # View all
    tasks = manager.get_all_tasks()
    for task in tasks:
        print(f"[{task['id']}] {task['title']}")

    # Mark complete
    if manager.mark_complete(id1):
        print("Task 1 marked complete")

    # Update
    if manager.update_task(id2, "Call dentist ASAP", None):
        print("Task 2 updated")

    # Delete
    if manager.delete_task(id1):
        print("Task 1 deleted")

    # Get by ID
    task = manager.get_task_by_id(id2)
    if task:
        print(f"Found: {task['title']}")
```

---

## Error Handling Patterns

### Validation Errors (Exceptions)
```python
try:
    manager.add_task("", "Description")
except ValueError as e:
    print(f"Error: {e}")  # "Title cannot be empty"
```

### Not Found (Boolean Returns)
```python
success = manager.delete_task(999)
if not success:
    print("Task not found")
```

### Idempotent Operations
```python
manager.mark_complete(1)  # First time
manager.mark_complete(1)  # Safe to call again
```

---

## Testing Checklist

- [ ] Add task with valid title and description
- [ ] Add task with valid title and empty description
- [ ] Add task with empty title (should raise ValueError)
- [ ] Get all tasks when list is empty
- [ ] Get all tasks when list has multiple tasks
- [ ] Get task by valid ID
- [ ] Get task by non-existent ID (should return None)
- [ ] Update task with both title and description
- [ ] Update task with title only (None for description)
- [ ] Update task with description only (None for title)
- [ ] Update task with both None (no-op)
- [ ] Update task with empty title (should raise ValueError)
- [ ] Update non-existent task (should return False)
- [ ] Delete existing task
- [ ] Delete non-existent task (should return False)
- [ ] Verify ID not reused after delete
- [ ] Mark pending task complete
- [ ] Mark completed task complete again (idempotent)
- [ ] Mark non-existent task complete (should return False)

---

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| add_task | O(1) | O(1) per task |
| get_all_tasks | O(1) | O(n) return list |
| get_task_by_id | O(n) | O(1) |
| update_task | O(n) | O(1) |
| delete_task | O(n) | O(1) |
| mark_complete | O(n) | O(1) |

**Note**: O(n) operations are acceptable for Phase I (<100 tasks). Phase II can optimize with dictionary index.

---

## Dependencies

**Standard Library Only**:
- `typing.List` - for type hints
- `typing.Optional` - for optional parameters
- `typing.TypedDict` or `dataclasses.dataclass` - for Task structure

**No External Dependencies**

---

## Future Enhancements (Out of Scope for Phase I)

- `unmark_complete()` - toggle completed back to pending
- `find_tasks_by_title()` - search/filter by title
- `get_completed_tasks()` - filter by status
- `get_pending_tasks()` - filter by status
- `sort_tasks_by()` - custom sorting
- `bulk_delete()` - delete multiple tasks
- `bulk_mark_complete()` - mark multiple tasks
- Index by ID for O(1) lookup

---

This contract defines the complete interface for the TaskManager class, ensuring clear separation between business logic and presentation concerns.
