# Implementation Plan: Console CRUD Operations

**Branch**: `001-console-crud-operations` | **Date**: 2025-12-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-console-crud-operations/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an in-memory console todo list application with full CRUD operations (Create, Read, Update, Delete). The application will run as a continuous menu-driven interface allowing users to manage tasks with auto-incremented IDs, titles, descriptions, and completion status. The implementation uses a three-layer architecture (Model, Logic, Presentation) within a single Python file, following strict constitution principles for Phase I development.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None - Python standard library only
**Storage**: In-memory using Python list to store Task dictionaries
**Testing**: Manual testing via console interaction (automated tests not requested)
**Target Platform**: Cross-platform CLI (Windows, macOS, Linux)
**Project Type**: Single-file console application
**Performance Goals**: Handle 50+ tasks without performance degradation
**Constraints**: Single file (`src/main.py`), no persistence, no external libraries, must handle errors gracefully without crashes
**Scale/Scope**: Personal todo list management, expected <100 tasks per session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Spec-Driven Development (NON-NEGOTIABLE)
**Status**: PASS
- Specification created at `specs/001-console-crud-operations/spec.md`
- Contains 4 prioritized user stories with acceptance scenarios
- 12 functional requirements + 7 non-functional requirements defined
- Planning proceeding only after spec completion

### ✅ Principle II: Single-File Simplicity
**Status**: PASS
- All code will reside in `src/main.py`
- No modules, packages, or file splits
- Logical separation via classes/functions within single file

### ✅ Principle III: In-Memory Only
**Status**: PASS
- Storage: Python list containing Task dictionaries
- No file I/O, no databases, no external services
- Data loss on restart is expected and acceptable
- FR-005 and NFR-007 enforce this constraint

### ✅ Principle IV: Clean Python Standards
**Status**: PASS
- Type hints required for all functions (NFR-003)
- Docstrings required for all functions (NFR-004)
- PEP 8 naming conventions (NFR-005)
- Standard library only (NFR-001)
- Error handling required (NFR-006)

### ✅ Principle V: Continuous Loop Interface
**Status**: PASS
- FR-002 requires continuous loop until Exit
- FR-001 specifies 6-option menu
- Application returns to menu after each operation

### ✅ Principle VI: Test-First When Requested
**Status**: PASS (N/A)
- Automated tests NOT requested in specification
- Manual testing via console interaction is acceptable
- Tests are optional per constitution Principle VI

**GATE RESULT**: ✅ ALL CHECKS PASS - Proceeding to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-console-crud-operations/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 research findings
├── data-model.md        # Phase 1 data model definition
├── quickstart.md        # Phase 1 user guide
└── contracts/           # Phase 1 API contracts (internal function signatures)
```

### Source Code (repository root)

```text
src/
└── main.py              # Single-file implementation (all code here)

tests/
└── (empty - no automated tests requested)
```

**Structure Decision**: Using Option 1 (Single project) as this is a standalone CLI application with no web/mobile components. All application logic resides in `src/main.py` per constitution Principle II. The file will be logically organized into three layers as specified in user's strategy:

1. **Model Layer**: Task data structure (dictionary or dataclass)
2. **Logic Layer**: TaskManager class for CRUD operations
3. **Presentation Layer**: main() function with menu loop and I/O

## Complexity Tracking

> **No violations detected** - All constitution principles are satisfied by the design.

---

## Phase 0: Research & Requirements Analysis

### Research Questions

All technical decisions are straightforward for this Phase I implementation. No NEEDS CLARIFICATION items remain:

**Q1: Data structure for Task storage?**
- **Decision**: Use Python list containing dictionaries
- **Rationale**: Simple, built-in, supports all CRUD operations, maintains insertion order
- **Alternatives considered**:
  - `dict` with ID as key (rejected: harder to maintain ID auto-increment)
  - Custom class instances (accepted but optional: can use dict or dataclass)

**Q2: ID generation strategy?**
- **Decision**: Maintain a global counter that increments and never reuses
- **Rationale**: FR-003 and FR-004 require unique, auto-incremented, never-reused IDs
- **Implementation**: Counter variable outside TaskManager or as class attribute

**Q3: Input validation approach?**
- **Decision**: Try/except blocks for type errors + explicit checks for business rules
- **Rationale**: NFR-006 requires graceful error handling, FR-012 requires handling invalid types
- **Pattern**: Validate at presentation layer before calling logic layer

**Q4: Empty input handling for update operation?**
- **Decision**: Empty string input means "skip field, keep current value"
- **Rationale**: FR-009 explicitly requires this behavior per user story 3
- **Implementation**: Check for empty string before assignment

### Best Practices Applied

**Architecture Pattern**: Three-layer separation (Model-Logic-Presentation)
- **Model**: Task data structure with 4 fields (id, title, description, completed)
- **Logic**: TaskManager class encapsulating CRUD operations and validation
- **Presentation**: main() function handling menu, user input, output formatting

**Error Handling Strategy**:
- **Input validation**: Check type (try/except ValueError), check business rules (ID exists, title non-empty)
- **User feedback**: Clear error messages per FR-011
- **Recovery**: Return to menu on error, allow retry (continuous loop per FR-002)

**Code Organization** (within single file):
1. Module docstring
2. Type imports (from typing import Dict, List, Optional)
3. Task data structure definition (dict TypedDict or dataclass)
4. TaskManager class
5. Helper functions for I/O and formatting
6. main() function with menu loop
7. if __name__ == "__main__": entry point

---

## Phase 1: Design & Contracts

### Data Model (`data-model.md`)

**Entity**: Task

**Fields**:
- `id` (int): Unique identifier, auto-assigned starting from 1, never reused after deletion
- `title` (str): Required, non-empty, user-provided task name
- `description` (str): Optional, can be empty string, user-provided details
- `completed` (bool): Status flag, defaults to False, becomes True when marked complete

**Validation Rules**:
- **id**: System-assigned, must be positive integer, must be unique across all tasks (active and deleted)
- **title**: User-provided, cannot be empty string, no max length
- **description**: User-provided, can be empty string, no max length
- **completed**: System-managed, boolean only (False or True)

**State Transitions**:
- **Creation**: Task created with `completed=False`
- **Mark Complete**: `completed` changes from False → True (idempotent: True → True is allowed)
- **Update**: `title` and/or `description` can change, `completed` unchanged by update operation
- **Delete**: Task removed from storage, ID never reused

**Storage Implementation**:
```python
# Option 1: List of dictionaries
tasks: List[Dict[str, any]] = []
# Example: [
#   {"id": 1, "title": "Buy groceries", "description": "Milk, eggs", "completed": False},
#   {"id": 2, "title": "Call dentist", "description": "", "completed": True}
# ]

# Option 2: TypedDict (preferred for type safety)
from typing import TypedDict
class Task(TypedDict):
    id: int
    title: str
    description: str
    completed: bool
```

### API Contracts (`contracts/task_manager.md`)

Since this is a single-file console application (not a web API), "contracts" refer to the internal function signatures of the TaskManager class:

**TaskManager Class Contract**:

```python
class TaskManager:
    """Manages CRUD operations for in-memory task storage."""

    def __init__(self) -> None:
        """Initialize task manager with empty task list and ID counter."""

    def add_task(self, title: str, description: str) -> int:
        """
        Add a new task to the list.

        Args:
            title: Non-empty task name
            description: Optional task details (can be empty string)

        Returns:
            The auto-assigned task ID

        Raises:
            ValueError: If title is empty
        """

    def get_all_tasks(self) -> List[Dict[str, any]]:
        """
        Retrieve all tasks.

        Returns:
            List of task dictionaries (may be empty)
        """

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, any]]:
        """
        Find a task by ID.

        Args:
            task_id: The unique task identifier

        Returns:
            Task dictionary if found, None otherwise
        """

    def update_task(self, task_id: int, title: Optional[str],
                    description: Optional[str]) -> bool:
        """
        Update task fields. None values mean "keep current value".

        Args:
            task_id: The unique task identifier
            title: New title or None to skip
            description: New description or None to skip

        Returns:
            True if task found and updated, False if task not found
        """

    def delete_task(self, task_id: int) -> bool:
        """
        Remove a task from the list.

        Args:
            task_id: The unique task identifier

        Returns:
            True if task found and deleted, False if task not found
        """

    def mark_complete(self, task_id: int) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: The unique task identifier

        Returns:
            True if task found and marked, False if task not found
        """
```

**Helper Functions Contract**:

```python
def display_menu() -> None:
    """Print the main menu options."""

def get_menu_choice() -> int:
    """
    Get user's menu selection with validation.

    Returns:
        Valid menu choice (1-6)

    Note: Loops until valid input received
    """

def get_task_id_input() -> int:
    """
    Prompt for task ID with validation.

    Returns:
        Valid integer task ID

    Note: Loops until valid integer received
    """

def display_tasks(tasks: List[Dict[str, any]]) -> None:
    """
    Print formatted task list with ID, status, and title.

    Args:
        tasks: List of task dictionaries

    Output format:
        [1] [ ] Buy groceries
        [2] [x] Call dentist
    """
```

### Quickstart Guide (`quickstart.md`)

**Running the Application**:

1. Ensure Python 3.13+ is installed:
   ```bash
   python --version  # Should show 3.13 or higher
   ```

2. Navigate to project root:
   ```bash
   cd /path/to/Hackathon_2
   ```

3. Run the application:
   ```bash
   python src/main.py
   ```

4. You'll see the main menu:
   ```
   === TODO LIST MANAGER ===
   1. Add Task
   2. View Tasks
   3. Update Task
   4. Delete Task
   5. Mark Complete
   6. Exit
   Enter your choice (1-6):
   ```

**Basic Workflow**:

**Adding a Task**:
- Select option 1
- Enter title when prompted (required)
- Enter description when prompted (optional - press Enter to skip)
- See confirmation: "Task added with ID 1"

**Viewing Tasks**:
- Select option 2
- See formatted list of all tasks with status markers

**Marking Complete**:
- Select option 5
- Enter the task ID number
- Task status changes from [ ] to [x]

**Updating a Task**:
- Select option 3
- Enter the task ID number
- Enter new title (or press Enter to keep current)
- Enter new description (or press Enter to keep current)

**Deleting a Task**:
- Select option 4
- Enter the task ID number
- Task is removed from list

**Exiting**:
- Select option 6
- Application terminates (all data lost)

**Error Handling**:
- Invalid menu choice → Error message, menu redisplays
- Non-existent task ID → "Task with ID X not found"
- Empty title when adding → Re-prompts until non-empty
- Text input when number expected → "Invalid input" error, re-prompts

---

## Implementation Strategy

### User Story Implementation Order

**Phase 1: MVP (P1) - Add and View Tasks**
- Implement Task data structure
- Implement TaskManager with add_task() and get_all_tasks()
- Implement main menu loop
- Implement options 1 (Add) and 2 (View) and 6 (Exit)
- **Deliverable**: User can add tasks and view them - core value achieved

**Phase 2: P2 - Mark Complete**
- Implement mark_complete() in TaskManager
- Implement menu option 5
- Update display_tasks() to show [x] vs [ ]
- **Deliverable**: User can track task completion

**Phase 3: P3 - Update Task Details**
- Implement update_task() with skip-field logic
- Implement menu option 3
- **Deliverable**: User can modify existing tasks

**Phase 4: P4 - Delete Tasks**
- Implement delete_task() in TaskManager
- Implement menu option 4
- **Deliverable**: User can remove unwanted tasks

**Phase 5: Polish & Edge Cases**
- Add comprehensive error handling for all edge cases
- Validate all acceptance scenarios from spec.md
- Ensure all FR and NFR requirements met

### Architecture Decisions

**Decision 1: Task Storage Structure**
- **Chosen**: List of dictionaries with TypedDict for type hints
- **Rationale**: Simple, type-safe, maintains order, easy CRUD operations
- **Tradeoff**: Linear search for ID lookup vs dict with O(1) lookup - acceptable for <100 tasks

**Decision 2: ID Management**
- **Chosen**: Separate `next_id` counter as TaskManager attribute
- **Rationale**: Ensures IDs never reuse even after deletion
- **Tradeoff**: IDs may have gaps (acceptable per spec)

**Decision 3: Update Skip Logic**
- **Chosen**: Empty string input at presentation layer → None passed to logic layer
- **Rationale**: Separates UI concern (empty input) from logic concern (skip field)
- **Implementation**:
  ```python
  title_input = input("New title (Enter to skip): ").strip()
  title = None if title_input == "" else title_input
  ```

**Decision 4: Error Handling Layers**
- **Chosen**: Validation at both presentation and logic layers
- **Rationale**:
  - Presentation layer: Type validation (int parsing), user-friendly re-prompting
  - Logic layer: Business rule validation (ID exists, title non-empty)
- **Benefit**: Clean separation of concerns, reusable logic layer

**Decision 5: Display Format**
- **Chosen**: `[ID] [status] Title` format, description not shown in list view
- **Rationale**: Keeps list view concise, matches spec requirement FR-008
- **Future**: Could add "view details" option in Phase II

---

## Post-Design Constitution Re-Check

### ✅ Principle I: Spec-Driven Development
- Spec created and approved before plan
- Plan references spec requirements throughout
- Implementation will follow plan

### ✅ Principle II: Single-File Simplicity
- All code in `src/main.py` confirmed
- Three-layer architecture fits within single file
- No modules or imports beyond standard library

### ✅ Principle III: In-Memory Only
- Storage: Python list of dictionaries
- No file I/O in any design decision
- Data loss accepted and documented

### ✅ Principle IV: Clean Python Standards
- TypedDict for type safety
- All function signatures documented with types
- Docstrings planned for all functions
- PEP 8 naming (snake_case, PascalCase)

### ✅ Principle V: Continuous Loop Interface
- Main loop structure planned in architecture
- Menu redisplays after each operation
- Only option 6 breaks the loop

### ✅ Principle VI: Test-First
- Not applicable (tests not requested)
- Manual testing via console confirmed

**FINAL GATE RESULT**: ✅ ALL PRINCIPLES SATISFIED

---

## Risk Analysis

### Risk 1: User Input Validation Complexity
**Likelihood**: Medium | **Impact**: Low
**Mitigation**: Comprehensive try/except blocks, clear error messages, re-prompting loops
**Fallback**: User can always exit (option 6) if stuck

### Risk 2: Large Task Lists (100+)
**Likelihood**: Low (Phase I scope) | **Impact**: Low
**Mitigation**: Linear search acceptable for Phase I, in-memory constraint limits practical size
**Future**: Phase II could add pagination or search

### Risk 3: Accidental Data Loss
**Likelihood**: High (by design) | **Impact**: Accepted
**Mitigation**: None - this is expected behavior for Phase I per NFR-007
**User Communication**: Documented clearly in quickstart.md

---

## Next Steps

1. **User Review**: Approve this plan before proceeding
2. **Generate Tasks**: Run `/sp.tasks` to create dependency-ordered task list from this plan
3. **Implementation**: Execute tasks in order (P1 → P2 → P3 → P4 → Polish)
4. **Validation**: Test each user story independently per acceptance scenarios
5. **Phase II Planning**: After Phase I complete, plan file persistence feature

---

## Appendix: Architectural Layers Detail

### Model Layer
```python
# Task data structure
from typing import TypedDict

class Task(TypedDict):
    id: int
    title: str
    description: str
    completed: bool
```

### Logic Layer
```python
# TaskManager class encapsulating business logic
class TaskManager:
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id: int = 1

    # CRUD methods (see contracts section)
```

### Presentation Layer
```python
# Main menu loop and I/O handling
def main():
    manager = TaskManager()
    while True:
        display_menu()
        choice = get_menu_choice()
        # Route to appropriate handler
        if choice == 6:
            break
```

This layered approach maintains clean separation while staying within a single file per constitution requirements.
