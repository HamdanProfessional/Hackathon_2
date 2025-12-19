# Tasks: Console CRUD Operations

**Input**: Design documents from `/specs/001-todo-crud/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/cli-interface.md

**Tests**: Phase I uses manual testing - NO automated test tasks

**Organization**: Tasks grouped by user story for independent implementation

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different sections, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, US4)
- File paths in descriptions

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure and import statements

- [ ] T001 Create src/ directory in repository root
- [ ] T002 Create src/main.py with docstring and import statements (typing, dataclasses modules)

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Foundational (Model Layer - Blocking Prerequisites)

**Purpose**: Core data structures that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 [P] Create Task dataclass with attributes (id, title, description, completed) in src/main.py
- [ ] T004 [P] Create TaskManager class skeleton with __init__ method in src/main.py
- [ ] T005 Implement TaskManager.__init__ with _tasks dict and _next_id counter in src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can add tasks and see their todo list

**Independent Test**: Add 3 tasks with different titles/descriptions, view list, verify all appear with correct IDs and [ ] status

### Implementation for User Story 1

- [ ] T006 [US1] Implement TaskManager.add_task(title, description) method in src/main.py
- [ ] T007 [US1] Implement TaskManager.view_tasks() method returning sorted list in src/main.py
- [ ] T008 [US1] Implement display_menu() function showing 6 menu options in src/main.py
- [ ] T009 [US1] Implement get_menu_choice() function with validation (1-6) in src/main.py
- [ ] T010 [US1] Implement handle_add_task(manager) function with prompts and validation in src/main.py
- [ ] T011 [US1] Implement handle_view_tasks(manager) function with formatting in src/main.py
- [ ] T012 [US1] Implement main() function with TaskManager creation and while loop in src/main.py
- [ ] T013 [US1] Add menu choice routing for options 1 (Add) and 2 (View) in src/main.py
- [ ] T014 [US1] Add __name__ == "__main__" guard and main() call in src/main.py

**Manual Test Scenarios for US1**:
1. Run python src/main.py
2. Select option 1, enter "Buy groceries" / "Milk, eggs, bread", verify "Task added with ID 1"
3. Select option 1, enter "Call dentist" / "", verify "Task added with ID 2"
4. Select option 2, verify both tasks display as `[1] [ ] Buy groceries` and `[2] [ ] Call dentist`
5. Select option 2 with empty list, verify "No tasks available." message

**Checkpoint**: User Story 1 complete - Users can add and view tasks (MVP functional!)

---

## Phase 4: User Story 2 - Mark Tasks Complete (Priority: P2)

**Goal**: Users can mark tasks as done and see [x] status

**Independent Test**: Add 2 tasks (US1), mark task 1 complete, view list, verify task 1 shows [x] and task 2 shows [ ]

### Implementation for User Story 2

- [ ] T015 [US2] Implement TaskManager.mark_complete(task_id) method returning bool in src/main.py
- [ ] T016 [US2] Implement handle_mark_complete(manager) function with ID prompt and validation in src/main.py
- [ ] T017 [US2] Add menu choice routing for option 5 (Mark Complete) in main() function in src/main.py
- [ ] T018 [US2] Update handle_view_tasks() to display [x] for completed tasks in src/main.py

**Manual Test Scenarios for US2**:
1. Add task "Submit report" (ID 1) and "Review PR" (ID 2)
2. Select option 5, enter ID 1, verify "Task 1 marked as complete"
3. Select option 2, verify task 1 shows [x] and task 2 shows [ ]
4. Select option 5, enter ID 999, verify "Task ID 999 not found" error

**Checkpoint**: User Stories 1 AND 2 complete - Users can track progress

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Users can edit task title and description

**Independent Test**: Add task (US1), update title only, verify title changed and ID/status unchanged; update description only, verify description changed

### Implementation for User Story 3

- [ ] T019 [US3] Implement TaskManager.update_task(task_id, title, description) method returning bool in src/main.py
- [ ] T020 [US3] Implement handle_update_task(manager) function with prompts for ID and fields in src/main.py
- [ ] T021 [US3] Add empty input handling (press Enter to skip field) in handle_update_task() in src/main.py
- [ ] T022 [US3] Add "No changes made" message when both fields skipped in handle_update_task() in src/main.py
- [ ] T023 [US3] Add menu choice routing for option 3 (Update) in main() function in src/main.py

**Manual Test Scenarios for US3**:
1. Add task "Call dentist" with description "Schedule appointment"
2. Select option 3, enter ID 1, new title "Call dentist for cleaning", skip description
3. Verify task 1 title updated, description unchanged
4. Select option 3, enter ID 1, skip title, new description "Schedule cleaning for next month"
5. Verify task 1 description updated, title unchanged
6. Select option 3, enter ID 1, skip both fields, verify "No changes made"

**Checkpoint**: User Stories 1, 2, AND 3 complete - Users can edit tasks

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P3)

**Goal**: Users can remove tasks from list

**Independent Test**: Add 3 tasks (US1), delete task 2, view list, verify only tasks 1 and 3 remain

### Implementation for User Story 4

- [ ] T024 [US4] Implement TaskManager.delete_task(task_id) method returning bool in src/main.py
- [ ] T025 [US4] Implement handle_delete_task(manager) function with ID prompt and validation in src/main.py
- [ ] T026 [US4] Add menu choice routing for option 4 (Delete) in main() function in src/main.py

**Manual Test Scenarios for US4**:
1. Add tasks with IDs 1, 2, 3
2. Select option 4, enter ID 2, verify "Task 2 deleted successfully"
3. Select option 2, verify only tasks 1 and 3 display
4. Select option 4, enter ID 999, verify "Task ID 999 not found" error
5. Add new task, verify it gets ID 4 (not reusing ID 2)

**Checkpoint**: All user stories complete - Full CRUD functionality working

---

## Phase 7: Exit Functionality & Polish

**Purpose**: Application termination and final quality improvements

- [ ] T027 Add menu choice routing for option 6 (Exit) in main() function in src/main.py
- [ ] T028 Implement exit logic printing "Goodbye!" and breaking while loop in src/main.py
- [ ] T029 Add type hints to all function signatures in src/main.py
- [ ] T030 Add Google-style docstrings to Task class, TaskManager class, and all functions in src/main.py
- [ ] T031 Add error handling for invalid menu options (non-numeric, out of range) in src/main.py
- [ ] T032 Add input validation for task IDs (non-numeric handling) in src/main.py
- [ ] T033 Add title validation (empty string rejection) in handle_add_task() in src/main.py
- [ ] T034 Review code for PEP 8 compliance (snake_case, spacing) in src/main.py
- [ ] T035 Run manual validation against all acceptance criteria from spec.md
- [ ] T036 Run edge case validation from spec.md (empty list, invalid inputs, etc.)

**Manual Test - Complete Application**:
1. Test all 16 functional requirements (FR-001 through FR-016) from spec.md
2. Test all 7 success criteria (SC-001 through SC-007) from spec.md
3. Test all 6 edge cases from spec.md
4. Test all 12 acceptance scenarios from user stories in spec.md
5. Verify constitution compliance (Python 3.13+, stdlib only, in-memory, CLI loop)

**Checkpoint**: Phase I complete - Ready for demo and commit

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 - MVP functionality
- **Phase 4 (US2)**: Depends on Phase 2 - Can run parallel to US3/US4 after US1 complete
- **Phase 5 (US3)**: Depends on Phase 2 - Can run parallel to US2/US4 after US1 complete
- **Phase 6 (US4)**: Depends on Phase 2 - Can run parallel to US2/US3 after US1 complete
- **Phase 7 (Polish)**: Depends on all user stories complete

### Recommended Execution Order

**Sequential (Single Developer)**:
1. Phase 1: Setup → Phase 2: Foundational
2. Phase 3: US1 (MVP) → Test independently
3. Phase 4: US2 → Test independently
4. Phase 5: US3 → Test independently
5. Phase 6: US4 → Test independently
6. Phase 7: Polish → Final validation

**Optimal Strategy**:
- Complete Phase 1 & 2 first (foundation)
- Implement US1 fully and test (deliverable MVP!)
- Add US2, US3, US4 incrementally
- Each addition tested before next

### Within Each User Story

- Implement in task order (T001 → T002 → T003...)
- Test after completing each user story phase
- Commit after each user story validates

### Parallel Opportunities

- Phase 2 tasks T003 and T004 marked [P] can run in parallel
- After US1 complete, US2/US3/US4 can be worked on in parallel (if multiple developers)
- Polish tasks can be distributed if desired

---

## Parallel Example: Foundational Phase

```bash
# These can be implemented simultaneously (different class/dataclass):
Task T003: "Create Task dataclass..."
Task T004: "Create TaskManager class skeleton..."
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T005)
3. Complete Phase 3: User Story 1 (T006-T014)
4. **STOP and VALIDATE**: Manually test add and view operations
5. Commit as MVP (basic todo list working!)

### Incremental Delivery

1. Foundation (Phase 1-2) → 5 tasks
2. Add US1 (Phase 3) → Test add/view → MVP! → 9 more tasks
3. Add US2 (Phase 4) → Test mark complete → 4 more tasks
4. Add US3 (Phase 5) → Test update → 5 more tasks
5. Add US4 (Phase 6) → Test delete → 3 more tasks
6. Polish (Phase 7) → Final quality → 10 more tasks
7. Each increment adds value without breaking previous features

### Full Implementation Path

Total tasks: 36
- Setup: 2 tasks
- Foundation: 3 tasks
- US1 (P1): 9 tasks ← MVP deliverable
- US2 (P2): 4 tasks
- US3 (P3): 5 tasks
- US4 (P3): 3 tasks
- Polish: 10 tasks

Estimated time: 3-4 hours for experienced developer

---

## Task Summary

**Total Tasks**: 36
- Phase 1 (Setup): 2 tasks
- Phase 2 (Foundational): 3 tasks
- Phase 3 (US1 - Add/View): 9 tasks
- Phase 4 (US2 - Complete): 4 tasks
- Phase 5 (US3 - Update): 5 tasks
- Phase 6 (US4 - Delete): 3 tasks
- Phase 7 (Polish): 10 tasks

**Parallel Opportunities**: 2 tasks can run in parallel (T003, T004 in Phase 2)

**MVP Scope**: Phase 1-3 (14 tasks) = Add and View functionality

**Independent Test Criteria**:
- US1: Can add tasks and view list with correct formatting
- US2: Can mark tasks complete with [x] indicator
- US3: Can update task details while preserving ID/status
- US4: Can delete tasks with ID gaps handled correctly

**Format Validation**: ✅ All tasks follow checklist format with ID, [P] where applicable, [Story] label, and file paths

---

## Notes

- Single file implementation (src/main.py) - all tasks modify same file sequentially
- [P] markers minimal due to single-file constraint
- [US1], [US2], [US3], [US4] labels map tasks to user stories from spec.md
- Manual testing against acceptance criteria (no automated test framework for Phase I)
- Each user story independently testable after its phase completes
- Constitution compliant: Python 3.13+, stdlib only, in-memory, CLI loop
- Ready for /sp.implement command execution
