---
id: 003
title: "email notification task breakdown"
stage: tasks
date: 2025-12-27
surface: agent
model: claude-sonnet-4-5-20250929
feature: 006-fix-email
branch: 006-fix-email
user: Hamdan
command: /sp.tasks
labels: ["tasks", "implementation", "breakdown"]
links:
  spec: specs/006-fix-email/spec.md
  plan: specs/006-fix-email/plan.md
  contract: specs/006-fix-email/contracts/email-api.yaml
  ticket: null
  adr: specs/006-fix-email/adr.md
  pr: null
files:
  - specs/006-fix-email/tasks.md
tests:
  - Tasks generated for all user stories (US1, US2, US3)
  - Dependency graph created
  - Parallel execution opportunities identified
  - Implementation strategy defined
  - MVP scope clearly marked
---

## Prompt

Generate actionable task breakdown for email notification system

CONTEXT:
Specification and implementation plan are complete. Need to generate detailed, dependency-ordered tasks.md following Spec-Kit Plus template.

INSTRUCTIONS:

1. **Load Design Documents**:
   - `specs/006-fix-email/spec.md` - User stories (US1: P1 Creation, US2: P2 Completion, US3: P3 Update/Delete)
   - `specs/006-fix-email/plan.md` - Technical stack and architecture
   - `specs/006-fix-email/data-model.md` - Email event structures
   - `specs/006-fix-email/contracts/email-api.yaml` - API contract

2. **Generate Task Breakdown** (`specs/006-fix-email/tasks.md`):
   - Phase 1: Setup (environment, dependencies)
   - Phase 2: Foundational (blocking prerequisites)
   - Phase 3: User Story 1 - Task Creation (P1 MVP)
   - Phase 4: User Story 2 - Task Completion (P2)
   - Phase 5: User Story 3 - Update/Delete (P3)
   - Phase 6: Polish & Deployment

3. **Task Format Requirements**:
   - ALL tasks must follow: `- [ ] [ID] [P?] [Story?] Description with file path`
   - [P] marker for parallelizable tasks
   - [Story] label for user story tasks (US1, US2, US3)
   - Exact file paths in descriptions
   - Task ID sequential (T001, T002, T003...)

4. **Include**:
   - Total task count
   - Tasks per user story
   - Parallel opportunities
   - Dependency graph (mermaid)
   - Independent test criteria per story
   - MVP scope (US1 only)
   - Implementation strategy (incremental delivery)

USER STORIES FROM SPEC:

### US1 (P1) - Task Creation Email Notification
- Users receive immediate email when creating task
- Independent test: Create task → verify email arrives
- MVP candidate

### US2 (P2) - Task Completion Email Notification
- Users receive congratulatory email when completing task
- Independent test: Complete task → verify email arrives

### US3 (P3) - Task Update/Delete Notifications
- Users receive notification when updating or deleting task
- Independent test: Update/delete task → verify email arrives

TECHNICAL COMPONENTS TO IMPLEMENT:

## Backend Files
- `backend/app/utils/email_notifier.py` - Email sending utility (NEW)
- `backend/app/api/tasks.py` - Modified to send emails

## Kubernetes Configuration
- `k8s/backend/deployment.yaml` - Add EMAIL_API_URL and EMAIL_API_KEY env vars
- `k8s/backend/secrets.yaml` - Add EMAIL_API_KEY secret

## Implementation Tasks (Estimated ~30 tasks)

### Setup Phase (3 tasks)
- Verify email API access
- Configure Kubernetes secrets
- Update requirements.txt

### Foundational Phase (5 tasks)
- Create email_notifier.py utility
- Implement HTML template
- Add httpx client
- Add send functions (4 event types)
- Add error handling

### US1 Implementation (5 tasks)
- Import BackgroundTasks
- Add background_tasks parameter to create_task
- Create helper function
- Call send_task_created_email
- Add logging

### US2 Implementation (4 tasks)
- Add background_tasks to toggle_task_completion
- Call send_task_completed_email
- Add conditional logic (only when completed=True)
- Add logging

### US3 Implementation (5 tasks)
- Add background_tasks to update_task
- Call send_task_updated_email
- Add background_tasks to delete_task
- Call send_task_deleted_email
- Add logging

### Polish Phase (11 tasks)
- Build Docker image
- Push to registry
- Update deployment
- Verify rollout
- Test all 4 event types
- Verify email rendering
- Check logs
- Create quickstart guide

DELIVERABLES:
1. Complete tasks.md with ~30 tasks
2. Tasks organized by user story
3. Dependency graph (mermaid)
4. Parallel execution examples
5. MVP scope clearly marked
6. Independent test criteria per story
