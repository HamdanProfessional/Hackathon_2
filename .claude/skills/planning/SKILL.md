---
name: planning
description: Create implementation plans in specs/[feature]/plan.md with component architecture diagrams (Frontend → API → Database), data model schemas with SQLModel Field() definitions, and API endpoint specifications. Break down features into dependency-ordered tasks in specs/[feature]/tasks.md with story point estimates (1=1-2h, 2=2-4h, 3=4-8h, 5=1-2d). Write Spec-Kit Plus specs in specs/[feature]/spec.md with User Stories/Requirements/Acceptance Criteria. Use when designing new CRUD features, planning sprint backlogs, or creating tasks.md from spec.md.
---

# Planning Skill

Create implementation plans, break down features into tasks, and write Spec-Kit Plus specifications.

## File Structure

```
specs/
└── [feature-name]/
    ├── spec.md            # Feature specification
    ├── plan.md            # Implementation plan
    └── tasks.md           # Dependency-ordered task list
```

## Quick Commands

```bash
# Create feature spec directory
mkdir -p specs/task-reminders
cd specs/task-reminders

# Create specification files
touch spec.md plan.md tasks.md

# Generate plan from spec
python .claude/skills/planning/scripts/generate_plan.py spec.md

# Validate plan completeness
python .claude/skills/planning/scripts/validate_plan.py plan.md
```

## Common Scenarios

### Scenario 1: Plan Implementation of New Feature
**User Request**: "Plan how to add file attachments to tasks"

**Commands**:
```bash
# 1. Create spec directory
mkdir -p specs/file-attachments
cd specs/file-attachments

# 2. Write spec.md with user stories and acceptance criteria
# 3. Create plan.md with architecture and data model
# 4. Generate tasks.md with dependency ordering
```

**File: `specs/file-attachments/plan.md`**
```markdown
# Implementation Plan: File Attachments

## Data Model
- **Files table**: `backend/app/models/file.py`
  - id: int (PK)
  - task_id: int (FK → tasks.id)
  - user_id: UUID (FK → users.id)
  - filename: str(255)
  - file_size: int
  - storage_path: str(500)
  - content_type: str(100)
  - created_at: datetime

## API Endpoints
- POST /api/tasks/{task_id}/files - Upload file
- GET /api/tasks/{task_id}/files - List files
- GET /api/files/{file_id}/download - Download file
- DELETE /api/files/{file_id} - Delete file

## Frontend Components
- FileUpload.tsx - Drag & drop upload zone
- FileList.tsx - Display uploaded files
- FilePreview.tsx - Show file icon and size

## Task Breakdown
1. [Database] Create Files table migration (2 pts)
2. [Backend] Implement upload endpoint (5 pts)
3. [Backend] Implement list/download/delete (3 pts)
4. [Frontend] Create FileUpload component (3 pts)
5. [Frontend] Create FileList component (2 pts)
6. [Tests] E2E file upload workflow (3 pts)

**Total**: 18 points (~1 week)
```

### Scenario 2: Break Down Epic into Sprint Tasks
**User Request**: "Break down the authentication feature into tasks"

**Commands**:
```bash
# Create tasks.md from user stories
cd specs/authentication

# Stories to break down:
# - User registration
# - User login with JWT
# - Password reset
# - Logout and token refresh
```

**File: `specs/authentication/tasks.md`**
```markdown
# Tasks: Authentication Feature

## Database Layer
- [1] Create users table with email/password (2 pts)
  - File: `backend/app/models/user.py`
  - Migration: `alembic revision -m "Add users table"`

## Backend API
- [2] Implement POST /register endpoint (3 pts)
  - Hash password with bcrypt
  - Return JWT token
  - Depends on: [1]

- [3] Implement POST /login endpoint (3 pts)
  - Verify credentials
  - Generate JWT
  - Depends on: [1]

- [4] Implement password reset flow (5 pts)
  - Generate reset token
  - Send email
  - Update password
  - Depends on: [1]

- [5] Add JWT authentication middleware (2 pts)
  - Depends on: [3]

## Frontend UI
- [6] Create registration form (3 pts)
  - Component: `frontend/components/RegisterForm.tsx`
  - API: POST /api/register
  - Depends on: [2]

- [7] Create login form (3 pts)
  - Component: `frontend/components/LoginForm.tsx`
  - Store JWT in localStorage
  - Depends on: [3]

- [8] Create password reset UI (3 pts)
  - Depends on: [4]

## Testing
- [9] Write backend auth tests (3 pts)
  - File: `backend/tests/test_auth.py`
  - Depends on: [2], [3], [5]

- [10] Write E2E auth flow tests (5 pts)
  - File: `e2e/auth-flow.spec.ts`
  - Depends on: [6], [7]

**Total**: 32 points (2-week sprint)
```

### Story Point Estimation Guide

| Points | Time | Example Tasks |
|--------|------|---------------|
| 1 | 1-2 hrs | Add simple validation, fix typo |
| 2 | 2-4 hrs | Add single API endpoint |
| 3 | 4-8 hrs | CRUD resource, form with validation |
| 5 | 1-2 days | Feature with backend + frontend |
| 8 | 2-3 days | External API integration |
| 13 | 3-5 days | Complex multi-system integration |

---

## Quick Templates

### Implementation Plan Structure
```markdown
# Feature: File Attachments

## Data Model
- Files table: id, task_id, filename, size, content_type, storage_path, created_at
- Foreign key: task_id → tasks.id (CASCADE DELETE)

## API Endpoints
- POST /api/tasks/{task_id}/files - Upload file (multipart/form-data)
- GET /api/tasks/{task_id}/files - List files for task
- GET /api/files/{file_id}/download - Download file
- DELETE /api/files/{file_id} - Delete file

## Frontend Components
- FileUpload.tsx - Drag & drop zone, progress bar
- FileList.tsx - Display files with download/delete actions
- FilePreview.tsx - Show file icon/name/size

## Task Breakdown
1. Create Files model and migration (2 pts)
2. Implement upload endpoint with S3 integration (5 pts)
3. Create FileUpload component (3 pts)
4. Implement file deletion (2 pts)
5. Add E2E tests for file workflow (3 pts)

Total: 15 points (~1 week)
```

### Story Point Estimation Guide
| Points | Time | Example Tasks |
|--------|------|---------------|
| 1 | 1-2 hrs | Add simple validation, fix typo, update CSS |
| 2 | 2-4 hrs | Add single API endpoint, simple component |
| 3 | 4-8 hrs | CRUD resource, form with validation |
| 5 | 1-2 days | Feature with backend + frontend |
| 8 | 2-3 days | Complex feature, external API integration |
| 13 | 3-5 days | Very complex, multiple integrations, unknowns |

### Task Dependency Pattern
```
[1] Create database migration (no deps)
   ↓
[2] Create SQLModel (depends on 1)
   ↓
[3] Create Pydantic schemas (depends on 2)
   ↓
[4] Create router endpoints (depends on 2, 3)
   ↓
[5] Create TypeScript types (depends on 3)
   ↓
[6] Create frontend components (depends on 4, 5)
   ↓
[7] Write E2E tests (depends on 1-6)
```

---

See `examples/basic-plan.md` for complete implementation plan template.

### Quick Start

```bash
python .claude/skills/planning/scripts/generate_plan.py specs/001-task-management/spec.md
```

---

## Part 2: Task Breaker

See `examples/task-breakdown.md` for complete task breakdown template.

### Story Point Guidelines

| Points | Time | Complexity |
|--------|------|------------|
| 1 | 1-2 hours | Trivial |
| 2 | 2-4 hours | Simple |
| 3 | 4-8 hours | Moderate |
| 5 | 1-2 days | Complex |
| 8 | 2-3 days | Very Complex |
| 13 | 3-5 days | Extremely Complex |

---

## Part 3: Spec Architect

See `examples/feature-spec.md` for complete feature specification template.

---

## Quality Checklist

Before finalizing plans:
- [ ] Spec has been read completely
- [ ] Architecture aligns with current phase
- [ ] Data model includes all fields and indexes
- [ ] API endpoints follow RESTful conventions
- [ ] All tasks have clear acceptance criteria
- [ ] Task dependencies identified
- [ ] Testing strategy covers unit/integration/E2E
- [ ] Risks identified with mitigations
- [ ] User stories have clear value propositions
- [ ] Acceptance criteria are testable
