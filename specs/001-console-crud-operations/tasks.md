---
description: "Task list for Console CRUD Operations implementation"
---

# Tasks: Console CRUD Operations

**Input**: Design documents from `/specs/001-console-crud-operations/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/task_manager.md

**Tests**: Manual testing via console interaction (automated tests not requested in specification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/main.py` at repository root (ALL code in one file per constitution)
- No tests/ directory (automated tests not requested)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create src/ directory in project root
- [ ] T002 Create empty src/main.py file for single-file implementation
- [ ] T003 Add module docstring to src/main.py explaining project purpose and Phase I constraints

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [P] Import type hints (List, Dict, Optional, TypedDict) in src/main.py
- [ ] T005 [P] Define Task TypedDict with 4 fields (id, title, description, completed) in src/main.py
- [ ] T006 Create TaskManager class skeleton with __init__ method in src/main.py
- [ ] T007 Initialize TaskManager._tasks as empty list and _next_id as 1 in src/main.py
- [ ] T008 [P] Implement display_menu() helper function to print 6 menu options in src/main.py
- [ ] T009 [P] Implement get_menu_choice() helper function with input validation and error handling in src/main.py
- [ ] T010 [P] Implement get_task_id_input() helper function with int parsing and error handling in src/main.py
- [ ] T011 [P] Implement get_non_empty_input() helper function for title validation in src/main.py
- [ ] T012 Create main() function skeleton with while loop structure in src/main.py
- [ ] T013 Add if __name__ == "__main__": entry point that calls main() in src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to add tasks to the list and view all tasks with formatted display

**Independent Test**: Launch app, add 3 tasks with various titles/descriptions, view list to confirm IDs auto-assigned starting from 1, all tasks show [ ] status

### Implementation for User Story 1

- [ ] T014 [P] [US1] Implement TaskManager.add_task(title, description) method with ID assignment and validation in src/main.py
- [ ] T015 [P] [US1] Implement TaskManager.get_all_tasks() method returning task list in src/main.py
- [ ] T016 [US1] Implement display_tasks(tasks) helper function with formatted output ([ID] [status] title) in src/main.py
- [ ] T017 [US1] Implement handle_add_task(manager) function for menu option 1 in src/main.py
- [ ] T018 [US1] Implement handle_view_tasks(manager) function for menu option 2 with empty list check in src/main.py
- [ ] T019 [US1] Add menu routing in main() for options 1 (Add), 2 (View), 6 (Exit) in src/main.py
- [ ] T020 [US1] Add error handling for empty title input with re-prompting in handle_add_task() in src/main.py
- [ ] T021 [US1] Test edge case: view tasks when list is empty (should display "No tasks available") in src/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Mark Tasks Complete (Priority: P2)

**Goal**: Enable users to mark tasks as complete and see status change in view

**Independent Test**: Add 3 tasks, mark task ID 2 complete, view list to confirm task 2 shows [x] while others show [ ]

### Implementation for User Story 2

- [ ] T022 [P] [US2] Implement TaskManager.get_task_by_id(task_id) method returning task or None in src/main.py
- [ ] T023 [US2] Implement TaskManager.mark_complete(task_id) method with idempotent behavior in src/main.py
- [ ] T024 [US2] Update display_tasks() to show [x] for completed=True and [ ] for completed=False in src/main.py
- [ ] T025 [US2] Implement handle_mark_complete(manager) function for menu option 5 in src/main.py
- [ ] T026 [US2] Add menu routing in main() for option 5 (Mark Complete) in src/main.py
- [ ] T027 [US2] Add error handling for non-existent task ID with message "Task with ID X not found" in src/main.py
- [ ] T028 [US2] Add error handling for invalid ID input (non-numeric) with re-prompting in src/main.py
- [ ] T029 [US2] Test edge case: mark already completed task (should remain completed, no error) in src/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Enable users to update task title and/or description with skip feature for unchanged fields

**Independent Test**: Add task, update only title (skip description), then update only description (skip title), view to confirm both updates worked

### Implementation for User Story 3

- [ ] T030 [US3] Implement TaskManager.update_task(task_id, title, description) method with None=skip logic in src/main.py
- [ ] T031 [US3] Implement handle_update_task(manager) function for menu option 3 in src/main.py
- [ ] T032 [US3] Add menu routing in main() for option 3 (Update Task) in src/main.py
- [ ] T033 [US3] Add input handling to convert empty string to None for skip feature in handle_update_task() in src/main.py
- [ ] T034 [US3] Add validation to prevent updating title to empty string in TaskManager.update_task() in src/main.py
- [ ] T035 [US3] Add error handling for non-existent task ID in handle_update_task() in src/main.py
- [ ] T036 [US3] Test edge case: press Enter on both prompts (both fields skip, no change) in src/main.py
- [ ] T037 [US3] Test edge case: update title only, description unchanged in src/main.py
- [ ] T038 [US3] Test edge case: update description only, title unchanged in src/main.py

**Checkpoint**: All user stories 1, 2, AND 3 should now be independently functional

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Enable users to delete tasks permanently while ensuring IDs never reuse

**Independent Test**: Add 5 tasks (IDs 1-5), delete task 3, add new task, verify new task gets ID 6 (not 3)

### Implementation for User Story 4

- [ ] T039 [US4] Implement TaskManager.delete_task(task_id) method removing task from list in src/main.py
- [ ] T040 [US4] Implement handle_delete_task(manager) function for menu option 4 in src/main.py
- [ ] T041 [US4] Add menu routing in main() for option 4 (Delete Task) in src/main.py
- [ ] T042 [US4] Add error handling for non-existent task ID in handle_delete_task() in src/main.py
- [ ] T043 [US4] Verify _next_id counter is NOT decremented after deletion (IDs never reuse) in src/main.py
- [ ] T044 [US4] Test edge case: delete task, add new task, confirm ID increments (never reuses) in src/main.py
- [ ] T045 [US4] Test edge case: delete all tasks, list becomes empty, next task still gets sequential ID in src/main.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T046 [P] Add type hints to all function signatures (parameters and return values) in src/main.py
- [ ] T047 [P] Add docstrings to all functions (purpose, parameters, returns, raises) in src/main.py
- [ ] T048 [P] Add docstring to TaskManager class explaining its role in src/main.py
- [ ] T049 [P] Add docstring to Task TypedDict explaining field meanings in src/main.py
- [ ] T050 Verify PEP 8 naming conventions (snake_case for functions/variables, PascalCase for classes) in src/main.py
- [ ] T051 Add comprehensive error handling for invalid menu choice with clear message in main() in src/main.py
- [ ] T052 Test edge case: enter "7" or "abc" for menu choice (should show error and re-prompt) in src/main.py
- [ ] T053 Test edge case: enter very long title (1000+ chars) and verify it's accepted in src/main.py
- [ ] T054 Test edge case: add 50+ tasks and verify view performance is acceptable in src/main.py
- [ ] T055 Validate all 12 functional requirements (FR-001 through FR-012) are satisfied in src/main.py
- [ ] T056 Validate all 7 non-functional requirements (NFR-001 through NFR-007) are met in src/main.py
- [ ] T057 Manual testing: Complete full CRUD cycle (add, view, update, mark complete, delete, exit) in src/main.py
- [ ] T058 Manual testing: Verify all acceptance scenarios from spec.md pass in src/main.py
- [ ] T059 Manual testing: Verify all edge cases from spec.md are handled gracefully in src/main.py
- [ ] T060 Final review: Ensure continuous loop returns to menu after each operation until Exit in src/main.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses get_task_by_id from logic layer but stories are independent
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses get_task_by_id from logic layer but stories are independent
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Uses get_task_by_id from logic layer but stories are independent

### Within Each User Story

- Models/data structures before services
- Services before handlers
- Handlers before menu routing
- Core implementation before edge cases
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: All 3 tasks can run in parallel
- **Foundational (Phase 2)**: Tasks T004, T005, T008, T009, T010, T011 marked [P] can run in parallel
- **User Story 1**: Tasks T014, T015 marked [P] can run in parallel (different methods)
- **User Story 2**: Tasks T022, T023 marked [P] can run in parallel (different methods)
- **User Story 4**: No parallel tasks (small scope)
- **Polish (Phase 7)**: Tasks T046, T047, T048, T049, T050 marked [P] can run in parallel (documentation work)
- **Once Foundational completes**: All 4 user stories can be worked on in parallel by different team members

---

## Parallel Example: Foundational Phase

```bash
# Launch foundational tasks together:
Task: "Import type hints in src/main.py" [T004]
Task: "Define Task TypedDict in src/main.py" [T005]
Task: "Implement display_menu() in src/main.py" [T008]
Task: "Implement get_menu_choice() in src/main.py" [T009]
Task: "Implement get_task_id_input() in src/main.py" [T010]
Task: "Implement get_non_empty_input() in src/main.py" [T011]
```

---

## Parallel Example: User Story 1

```bash
# After foundational is complete, launch US1 tasks together:
Task: "Implement TaskManager.add_task() in src/main.py" [T014]
Task: "Implement TaskManager.get_all_tasks() in src/main.py" [T015]
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (3 tasks)
2. Complete Phase 2: Foundational (10 tasks) - **CRITICAL - blocks all stories**
3. Complete Phase 3: User Story 1 (8 tasks)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Confirm app can add tasks and view them - core value achieved

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (13 tasks)
2. Add User Story 1 → Test independently → MVP complete! (21 tasks total)
3. Add User Story 2 → Test independently → Mark complete feature added (29 tasks total)
4. Add User Story 3 → Test independently → Update feature added (38 tasks total)
5. Add User Story 4 → Test independently → Delete feature added (45 tasks total)
6. Polish → All requirements validated → Production ready (60 tasks total)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (13 tasks)
2. Once Foundational is done:
   - Developer A: User Story 1 (8 tasks)
   - Developer B: User Story 2 (8 tasks)
   - Developer C: User Story 3 (9 tasks)
   - Developer D: User Story 4 (7 tasks)
3. Stories complete and integrate independently
4. Team completes Polish together (15 tasks)

---

## Task Summary

**Total Tasks**: 60

**By Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 10 tasks
- Phase 3 (User Story 1 - P1 MVP): 8 tasks
- Phase 4 (User Story 2 - P2): 8 tasks
- Phase 5 (User Story 3 - P3): 9 tasks
- Phase 6 (User Story 4 - P4): 7 tasks
- Phase 7 (Polish): 15 tasks

**Parallel Opportunities**: 11 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Add 3 tasks, view list, confirm auto-assigned IDs and [ ] status
- US2: Add 3 tasks, mark one complete, view list, confirm [x] status change
- US3: Add task, update title only, update description only, view to confirm both
- US4: Add 5 tasks, delete middle task, add new task, confirm ID increments (no reuse)

**Suggested MVP Scope**: Phases 1-3 only (21 tasks) delivers core value - add and view tasks

---

## Notes

- All tasks target single file `src/main.py` per constitution Principle II
- [P] tasks = different methods/functions, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No automated tests (not requested in spec), all testing is manual console interaction
- Commit after completing each user story phase
- Stop at any checkpoint to validate story independently
- Constitution compliance embedded in tasks (type hints, docstrings, error handling, PEP 8)
