# Research: Console CRUD Operations

**Feature**: Console CRUD Operations
**Date**: 2025-12-06
**Phase**: 0 (Research & Requirements Analysis)

## Overview

This document captures research findings and technical decisions made during planning for the Console CRUD Operations feature. All decisions align with Phase I constitution constraints (single-file, in-memory, Python standard library only).

---

## Research Question 1: Task Data Structure

### Decision
Use Python `list` containing dictionaries, with `typing.TypedDict` for type safety.

### Rationale
- **Built-in**: No external dependencies required
- **Simple**: Easy to understand and maintain for Phase I learning objectives
- **Ordered**: List maintains insertion order, useful for display
- **Type-safe**: TypedDict provides IDE autocomplete and type checking
- **CRUD-friendly**: Supports all required operations (add, read, update, delete)

### Alternatives Considered

**Option 1: Dictionary with ID as key**
```python
tasks = {1: {"title": "...", "description": "...", "completed": False}}
```
- ✅ O(1) lookup by ID
- ❌ Harder to maintain auto-increment counter
- ❌ No natural order for display
- **Rejected**: Complexity outweighs benefit for <100 tasks

**Option 2: List of custom class instances**
```python
class Task:
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        # ...
```
- ✅ More object-oriented
- ✅ Encapsulation opportunities
- ❌ More code for same functionality
- **Deferred**: Could be used but TypedDict is simpler for Phase I

**Option 3: dataclass instances**
```python
from dataclasses import dataclass

@dataclass
class Task:
    id: int
    title: str
    description: str
    completed: bool
```
- ✅ Built-in, type-safe, clean syntax
- ✅ Good alternative to TypedDict
- ✅ Immutable variant available (@dataclass(frozen=True))
- **Accepted**: Valid alternative, implementation can choose between this and TypedDict

### Implementation Choice
Either TypedDict or dataclass is acceptable. Recommended: TypedDict for simplicity (dict-like access), dataclass for dot notation preference.

---

## Research Question 2: ID Generation Strategy

### Decision
Maintain a `_next_id` counter as TaskManager class attribute, increment on each add, never decrement or reuse.

### Rationale
- **Requirement**: FR-003 (auto-assign unique IDs starting from 1)
- **Requirement**: FR-004 (never reuse IDs of deleted tasks)
- **Simple**: Single integer counter, increment only
- **Predictable**: IDs are sequential (with gaps after deletions)

### Implementation Pattern
```python
class TaskManager:
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id: int = 1  # Start from 1

    def add_task(self, title: str, description: str) -> int:
        task_id = self._next_id
        self._next_id += 1  # Increment for next task
        # ... create and add task
        return task_id
```

### Alternatives Considered

**Option 1: Max ID + 1**
```python
next_id = max([t["id"] for t in tasks], default=0) + 1
```
- ❌ Violates FR-004 (would reuse IDs if all tasks deleted)
- ❌ More complex, slower (O(n) vs O(1))
- **Rejected**

**Option 2: UUID**
```python
import uuid
task_id = uuid.uuid4()
```
- ❌ Not sequential integers per FR-003
- ❌ Harder for users to type
- **Rejected**

---

## Research Question 3: Input Validation Approach

### Decision
Two-layer validation:
1. **Presentation layer**: Type validation (int parsing) with try/except, re-prompting loops
2. **Logic layer**: Business rule validation (ID exists, title non-empty) with boolean returns or exceptions

### Rationale
- **Requirement**: NFR-006 (graceful error handling)
- **Requirement**: FR-011 (appropriate error messages)
- **Requirement**: FR-012 (handle invalid types without crashing)
- **Separation of concerns**: UI validation separate from business logic
- **User experience**: Clear error messages, retry opportunities

### Patterns

**Presentation Layer - Type Validation**:
```python
def get_task_id_input() -> int:
    """Prompt for task ID with validation."""
    while True:
        try:
            task_id = int(input("Enter task ID: ").strip())
            return task_id
        except ValueError:
            print("Invalid ID. Please enter a number.")
```

**Presentation Layer - Empty Input Detection**:
```python
def get_non_empty_input(prompt: str) -> str:
    """Prompt until non-empty input received."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")
```

**Logic Layer - Business Rule Validation**:
```python
def get_task_by_id(self, task_id: int) -> Optional[Task]:
    """Return task if found, None otherwise."""
    for task in self._tasks:
        if task["id"] == task_id:
            return task
    return None  # Caller checks for None

def add_task(self, title: str, description: str) -> int:
    """Add task. Raises ValueError if title empty."""
    if not title.strip():
        raise ValueError("Title cannot be empty")
    # ... proceed with add
```

### Error Message Standards
- **Invalid menu choice**: "Invalid choice. Please enter a number between 1 and 6"
- **Invalid ID input**: "Invalid ID. Please enter a number"
- **Task not found**: "Task with ID {id} not found"
- **Empty title**: "Title cannot be empty. Please enter a title:"

---

## Research Question 4: Update Operation Skip Logic

### Decision
Empty string input at presentation layer translates to `None` passed to logic layer, meaning "skip this field".

### Rationale
- **Requirement**: FR-009 (empty input means keep current value)
- **User Story 3**: Acceptance scenario 1 and 4 explicitly require skip feature
- **Clear intent**: Empty input is distinct from "set to empty string"
- **Type-safe**: Optional[str] type hint communicates skip semantics

### Implementation Pattern

**Presentation Layer**:
```python
def handle_update_task(manager: TaskManager):
    task_id = get_task_id_input()

    print("Leave blank to keep current value")
    title_input = input("New title (Enter to skip): ").strip()
    desc_input = input("New description (Enter to skip): ").strip()

    # Convert empty string to None (skip)
    title = None if title_input == "" else title_input
    description = None if desc_input == "" else desc_input

    success = manager.update_task(task_id, title, description)
    # ... handle result
```

**Logic Layer**:
```python
def update_task(self, task_id: int, title: Optional[str],
                description: Optional[str]) -> bool:
    """Update task. None values mean 'skip field'."""
    task = self.get_task_by_id(task_id)
    if not task:
        return False  # Task not found

    # Update only non-None values
    if title is not None:
        if not title.strip():
            raise ValueError("Title cannot be empty")
        task["title"] = title

    if description is not None:
        task["description"] = description

    return True
```

### Edge Case: Setting Description to Empty
If a user wants to *clear* a description (set to empty string), they cannot do this with the skip logic in Phase I. This is acceptable - they can either:
1. Enter a space (will be stored as " ")
2. Delete and re-add the task
3. Wait for Phase II feature enhancement

---

## Best Practices Applied

### 1. Three-Layer Architecture

**Model Layer** (data structures):
- Task TypedDict or dataclass
- No business logic, pure data

**Logic Layer** (TaskManager class):
- CRUD operations
- Business rule validation
- No I/O, no user interaction
- Returns values/booleans, raises exceptions on invalid business rules

**Presentation Layer** (main loop + helpers):
- User I/O (input/print)
- Menu display
- Type validation and re-prompting
- Calls logic layer, formats results for display

### 2. Error Handling Strategy

**Graceful Degradation**:
- Invalid input → Error message → Re-prompt (never crash)
- Task not found → Error message → Return to menu
- Type error → Catch exception → User-friendly message → Re-prompt

**User Communication**:
- All error messages are actionable ("Please enter a number")
- All prompts indicate what is expected ("Enter task ID:")
- Optional inputs clearly marked ("Enter to skip")

### 3. Code Organization (Single File)

```python
"""
TODO List Manager - Phase I
In-memory console CRUD application for task management.
"""

# 1. Type imports
from typing import Dict, List, Optional, TypedDict

# 2. Model layer - data structures
class Task(TypedDict):
    # ...

# 3. Logic layer - TaskManager class
class TaskManager:
    # ...

# 4. Presentation layer - helper functions
def display_menu() -> None:
    # ...

def get_menu_choice() -> int:
    # ...

def display_tasks(tasks: List[Task]) -> None:
    # ...

def handle_add_task(manager: TaskManager) -> None:
    # ...

# ... more handlers

# 5. Main function
def main() -> None:
    # ...

# 6. Entry point
if __name__ == "__main__":
    main()
```

### 4. Type Safety

- All function signatures include type hints
- TypedDict or dataclass for Task structure
- Optional[T] for nullable parameters
- List[T], Dict[K, V] for collections
- Enables IDE autocomplete and type checking

### 5. Documentation Standards

- Module docstring at top of file
- Class docstring explaining purpose
- Function docstrings with Args, Returns, Raises sections
- Inline comments only where logic non-obvious

---

## Performance Considerations

### Phase I Constraints
- **Expected scale**: <100 tasks per session
- **Storage**: In-memory, no persistence
- **Operations**: All O(n) or better acceptable

### Operation Complexity
- **Add task**: O(1) - append to list
- **View all tasks**: O(n) - iterate list
- **Find by ID**: O(n) - linear search
- **Update task**: O(n) - find then update
- **Delete task**: O(n) - find then remove
- **Mark complete**: O(n) - find then update

### Optimization Opportunities (Not for Phase I)
- Dictionary index by ID for O(1) lookups (Phase II)
- Binary search if sorted (Phase II)
- Pagination for large lists (Phase II)

For Phase I: Linear search is acceptable and keeps code simple per constitution Principle II.

---

## Security & Data Integrity

### Phase I Scope
**No security requirements** - this is a local, single-user, non-persistent application.

### Data Integrity Rules
1. **ID uniqueness**: Enforced by incrementing counter, never reuse
2. **Title required**: Enforced by validation in add/update
3. **Type safety**: Enforced by type hints and validation
4. **Completed flag**: Boolean only, no other values

### No Concerns for Phase I
- Authentication/Authorization (single user)
- Input sanitization for SQL injection (no database)
- XSS prevention (no web interface)
- Data encryption (no sensitive data, no persistence)

---

## Summary of Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Task storage | List of TypedDict/dataclass | Simple, type-safe, built-in, CRUD-friendly |
| ID generation | Incrementing counter, never reuse | Meets FR-003/FR-004, simple, predictable |
| Validation | Two-layer (presentation + logic) | Separation of concerns, good UX |
| Update skip logic | Empty string → None → skip field | Meets FR-009, clear intent, type-safe |
| Architecture | Three-layer (Model-Logic-Presentation) | Clean separation within single file |
| Error handling | Try/except + boolean returns | Graceful, user-friendly, never crashes |

---

## Ready for Phase 1

All research questions resolved. No NEEDS CLARIFICATION items remaining. Proceeding to Phase 1 design (data-model.md, contracts, quickstart.md).
