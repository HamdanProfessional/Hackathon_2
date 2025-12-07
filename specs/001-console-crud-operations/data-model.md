# Data Model: Console CRUD Operations

**Feature**: Console CRUD Operations
**Date**: 2025-12-06
**Phase**: 1 (Design & Contracts)

## Entity: Task

A Task represents a single todo item in the user's list.

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | `int` | Yes (system-assigned) | Auto-increment from 1 | Unique identifier, never reused after deletion |
| `title` | `str` | Yes (user-provided) | N/A | Task name/summary, cannot be empty |
| `description` | `str` | No | `""` (empty string) | Optional task details, can be empty |
| `completed` | `bool` | Yes (system-assigned) | `False` | Completion status flag |

### Field Specifications

#### `id` (int)
- **Assignment**: System-assigned automatically during task creation
- **Uniqueness**: Must be unique across all tasks (active and deleted)
- **Incrementing**: Starts at 1, increments by 1 for each new task
- **Never Reused**: Once assigned, an ID is never reassigned to another task, even after deletion
- **Validation**: Must be positive integer (>= 1)
- **User Interaction**: User references tasks by ID for update/delete/complete operations

#### `title` (str)
- **Assignment**: User-provided during task creation
- **Required**: Cannot be empty or whitespace-only
- **Max Length**: No limit (Python string, Phase I accepts any length)
- **Validation**:
  - Must not be empty string after `.strip()`
  - Leading/trailing whitespace should be trimmed
- **Update**: Can be modified via update operation
- **Display**: Shown in task list view

#### `description` (str)
- **Assignment**: User-provided during task creation (optional)
- **Required**: No (can be empty string)
- **Default**: Empty string `""` if user presses Enter without input
- **Max Length**: No limit (Phase I accepts any length)
- **Validation**: No validation required (empty is valid)
- **Update**: Can be modified via update operation
- **Display**: Not shown in list view (only ID, status, title), but stored

#### `completed` (bool)
- **Assignment**: System-assigned during task creation
- **Default**: `False` (all new tasks start as pending)
- **Values**: Only `True` or `False` (no null/None)
- **Modification**: Changed via "Mark Complete" operation (False → True)
- **Idempotency**: Marking completed task complete again is allowed (True → True)
- **Update Operation**: NOT affected by update operation (only title/description update)
- **Display**: Shown as `[x]` (completed) or `[ ]` (pending) in list view

### State Transitions

```
[NEW TASK]
    ↓
    id: auto-assigned (next_id++)
    title: user input (validated non-empty)
    description: user input (can be empty)
    completed: False
    ↓
[CREATED - PENDING STATE]
    ↓
    ├── Update Title/Description → [UPDATED - PENDING STATE]
    ├── Mark Complete → [COMPLETED STATE]
    └── Delete → [REMOVED from storage]

[COMPLETED STATE]
    ↓
    ├── Update Title/Description → [UPDATED - COMPLETED STATE]
    ├── Mark Complete (again) → [COMPLETED STATE] (no change)
    └── Delete → [REMOVED from storage]
```

**Notes**:
- Once deleted, task is removed from storage entirely
- ID of deleted task is never reused
- No "uncomplete" operation in Phase I (completed is one-way transition)

### Storage Implementation

**Option 1: TypedDict** (Recommended for type safety)

```python
from typing import TypedDict

class Task(TypedDict):
    id: int
    title: str
    description: str
    completed: bool

# Storage
tasks: List[Task] = []

# Example data
example_tasks = [
    {"id": 1, "title": "Buy groceries", "description": "Milk, eggs, bread", "completed": False},
    {"id": 2, "title": "Call dentist", "description": "", "completed": True},
    {"id": 3, "title": "Write report", "description": "Q4 summary", "completed": False}
]
```

**Option 2: dataclass** (Alternative, also type-safe)

```python
from dataclasses import dataclass

@dataclass
class Task:
    id: int
    title: str
    description: str
    completed: bool

# Storage
tasks: List[Task] = []

# Example data
example_tasks = [
    Task(id=1, title="Buy groceries", description="Milk, eggs, bread", completed=False),
    Task(id=2, title="Call dentist", description="", completed=True),
    Task(id=3, title="Write report", description="Q4 summary", completed=False)
]
```

**Choice**: Either option is acceptable. TypedDict allows dictionary-style access `task["id"]`, dataclass allows dot notation `task.id`. Both provide type hints and IDE support.

### Validation Rules

#### Creation Validation
```python
def validate_new_task(title: str, description: str) -> None:
    """Validate inputs for task creation."""
    if not title.strip():
        raise ValueError("Title cannot be empty")
    # description: no validation needed (empty allowed)
```

#### Update Validation
```python
def validate_task_update(task_id: int, title: Optional[str],
                         description: Optional[str]) -> None:
    """Validate inputs for task update."""
    # Check task exists (caller responsibility)

    # If title is being updated, ensure it's not empty
    if title is not None and not title.strip():
        raise ValueError("Title cannot be empty")

    # description: no validation needed (None = skip, empty = allowed)
```

#### ID Validation
```python
def validate_task_id(task_id: int) -> None:
    """Validate task ID type and range."""
    if not isinstance(task_id, int):
        raise TypeError("Task ID must be an integer")
    if task_id < 1:
        raise ValueError("Task ID must be positive")
```

### Relationships

**Phase I**: No relationships - tasks are independent entities

**Future Phases** (Out of Scope):
- Task → Category (many-to-one)
- Task → Tag (many-to-many)
- Task → User (many-to-one for multi-user)
- Task → Subtask (self-referential hierarchy)

### Indexing & Lookup

**Primary Key**: `id` (unique identifier)

**Lookup Operations**:
- **By ID**: Linear search O(n) - acceptable for <100 tasks
  ```python
  def find_by_id(tasks: List[Task], task_id: int) -> Optional[Task]:
      for task in tasks:
          if task["id"] == task_id:
              return task
      return None
  ```

- **All Tasks**: Direct list access O(1)
  ```python
  def get_all(tasks: List[Task]) -> List[Task]:
      return tasks  # Return reference or copy
  ```

**Future Optimization** (Phase II):
- Maintain dictionary index: `{id: task}` for O(1) lookup
- Sort by creation time, completion status, etc.

### Data Integrity Constraints

| Constraint | Rule | Enforcement |
|------------|------|-------------|
| ID Uniqueness | Each task has unique ID | Counter increments, never reuses |
| ID Positive | ID >= 1 | Counter starts at 1, only increments |
| Title Non-Empty | Title must have content | Validation on create/update |
| Type Safety | Fields match declared types | Type hints + runtime checks |
| Completed Boolean | Only True/False allowed | Type system enforces |

### Example Task Lifecycle

```python
# 1. Creation
task = {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": False
}
tasks.append(task)

# 2. Update title
task["title"] = "Buy organic groceries"
# completed remains False

# 3. Mark complete
task["completed"] = True

# 4. Update description
task["description"] = "Milk, eggs, bread, cheese"
# completed remains True

# 5. Delete
tasks.remove(task)
# ID 1 is never reused
```

### Display Format

**List View** (FR-008):
```
[1] [ ] Buy groceries
[2] [x] Call dentist
[3] [ ] Write report
```

**Format Specification**:
- `[ID]` - Task ID in square brackets
- ` ` - Single space
- `[x]` - Completed status (x if True)
- `[ ]` - Pending status (space if False)
- ` ` - Single space
- `Title` - Task title (description not shown)

**Implementation**:
```python
def format_task_line(task: Task) -> str:
    """Format task for display in list view."""
    status = "[x]" if task["completed"] else "[ ]"
    return f"[{task['id']}] {status} {task['title']}"
```

### Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty title on create | Validation error, re-prompt |
| Empty title on update | Validation error, re-prompt |
| Empty description on create | Accepted, stored as `""` |
| Empty description on update | Interpreted as "skip" (unless explicitly setting to empty) |
| Very long title (1000+ chars) | Accepted, no length limit Phase I |
| Very long description | Accepted, no length limit Phase I |
| Duplicate titles | Allowed, ID is unique identifier |
| Delete task ID 2 from [1,2,3] | ID 2 removed, next new task gets ID 4 |
| All tasks deleted | Empty list, next new task gets next ID (not 1) |

---

## Summary

The Task entity is a simple, flat data structure with four fields optimized for Phase I constraints. Storage uses Python built-in types (list + dict or dataclass), validation is minimal but effective, and all operations are designed for small-scale in-memory use. Future phases can extend with relationships, persistence, and optimization.
