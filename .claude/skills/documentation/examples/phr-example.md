# PHR Example

Prompt History Record for tracking work completion.

```markdown
---
id: 001
title: Implement Task CRUD with FastAPI and SQLModel
stage: green
date: 2025-01-15T10:30:00Z
surface: agent
model: claude-sonnet-4-5-20250929
feature: task-management
branch: feature/task-crud
user: developer
command: /skill fastapi-crud
labels: feature, backend, crud
links:
  spec: specs/001-task-management/spec.md
  ticket: #123
  pr: #124
files:
  - backend/app/models/task.py (created)
  - backend/app/schemas/task.py (created)
  - backend/app/routers/task.py (created)
  - backend/tests/test_task.py (created)
tests:
  - backend/tests/test_task.py (all passing)
---

## Prompt

Create complete CRUD operations for Task resource using FastAPI and SQLModel.
Include JWT authentication, pagination, and user isolation.

## Response snapshot

[Full AI response with generated code...]

## Outcome

- [x] Impact: Task CRUD fully implemented with 5 endpoints
- [x] Tests: All 12 tests passing (create, read, update, delete, pagination, user isolation)
- [x] Files: 4 files created (model, schema, router, tests)
- [x] Next prompts: Run migration, integrate with frontend
- [x] Reflection: User isolation working correctly, pagination tested

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results: PASS (all acceptance criteria met)
- Prompt variant: None used
- Next experiment: Add task search endpoint
```
