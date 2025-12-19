---

description: "Task list for Phase II Full-Stack Modern Web Application implementation"
---

# Tasks: Phase II - Full-Stack Modern Web Application

**Input**: Design documents from `/specs/002-phase2-webapp/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), contracts/openapi.yaml

**Tests**: Tests are included as validation tasks for each user story

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/`
- **Frontend**: `frontend/`
- **Root**: Project root for shared files

---

## Phase A: Monorepo & Infrastructure (Foundational)

**Purpose**: Project initialization and basic structure

- [X] T001 Create monorepo directory structure: frontend/, backend/, docker-compose.yml at project root
- [X] T002 Initialize Next.js 16+ project in frontend/ with TypeScript and App Router
- [X] T003 Initialize FastAPI project in backend/ with Python 3.13+
- [X] T004 [P] Create frontend/package.json with required dependencies (tailwindcss, shadcn/ui, framer-motion, lucide-react, sonner, @better-auth/core)
- [X] T005 [P] Create backend/requirements.txt with required dependencies (fastapi, sqlmodel, alembic, python-jose[cryptography], passlib[bcrypt], python-multipart)
- [X] T006 [P] Create docker-compose.yml with frontend, backend, and postgres services
- [X] T007 [P] Create .env.example with JWT_SECRET, DATABASE_URL, and other environment variables
- [X] T008 [P] Create README.md with project overview and setup instructions

---

## Phase B: Backend Core & Auth (The "Hard" Part)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create backend/app/core/config.py with Pydantic settings for database URL and JWT secret
- [X] T010 Create backend/app/database.py with SQLModel async engine and session management
- [X] T011 Initialize Alembic in backend/ with async configuration
- [X] T012 Create backend/app/models/user.py with User SQLModel (id, email, hashed_password, created_at)
- [X] T013 Create backend/app/models/task.py with Task SQLModel (id, user_id(FK), title, description, priority(Enum), due_date, completed, timestamps)
- [X] T014 [P] Create backend/app/schemas/user.py with UserCreate, UserResponse, LoginRequest Pydantic models
- [X] T015 [P] Create backend/app/schemas/task.py with TaskCreate, TaskUpdate, TaskResponse Pydantic models
- [X] T016 Create backend/app/utils/security.py with password hashing and JWT functions
- [X] T017 Create backend/app/api/deps.py with get_current_user dependency that verifies JWT from Authorization header
- [X] T018 Create backend/app/api/auth.py with register and login endpoints
- [X] T019 Create backend/app/api/tasks.py with CRUD endpoints (GET, POST, PUT, DELETE)
- [X] T020 Create backend/app/main.py and integrate auth and task routers with CORS middleware
- [X] T021 Create initial Alembic migration for users and tasks tables
- [X] T022 Add JWT_SECRET validation to ensure endpoints fail 401 without valid token

**Checkpoint**: Backend API ready with authentication and task CRUD - frontend integration can now begin

---

## Phase C: Frontend Foundation ("Nebula 2025")

**Purpose**: Frontend infrastructure and authentication setup

- [X] T023 Configure Tailwind CSS in frontend/tailwind.config.ts with Zinc-950 background and Electric Violet to Fuchsia gradients
- [X] T024 [P] Create frontend/app/globals.css with CSS variables for Nebula 2025 theme
- [X] T025 [P] Configure shadcn/ui in frontend/components.json with dark theme
- [X] T026 Create frontend/app/layout.tsx with global providers (theme, toast)
- [X] T027 [P] Create frontend/components/ui/ directory and install base shadcn/ui components
- [X] T028 Create frontend/lib/auth.ts with Better Auth configuration and JWT client
- [X] T029 Create frontend/lib/api.ts with axios client and auth interceptors
- [X] T030 [P] Create TypeScript types in frontend/types/ from API contracts
- [X] T031 Create frontend/app/login/page.tsx with login form
- [X] T032 Create frontend/app/register/page.tsx with register form
- [X] T033 Create frontend/app/dashboard/page.tsx with loading state and auth check
- [X] T034 Create middleware for route protection (redirect to login if unauthenticated)
- [X] T035 Test auth flow end-to-end (register → login → dashboard access)

---

## Phase D: Feature Implementation

### Phase D1: User Story 1 - User Authentication and Dashboard Access (Priority: P1) 🎯 MVP

**Goal**: Users can register, login, and access a protected dashboard

**Independent Test**: Register a new user, verify email validation, login successfully, and access dashboard with proper session management

#### Validation for User Story 1

- [ ] T036 [US1] Test registration endpoint rejects duplicate emails with 409
- [ ] T037 [US1] Test login endpoint rejects invalid credentials with 401
- [ ] T038 [US1] Test protected dashboard redirects unauthenticated users to login
- [ ] T039 [US1] Test authenticated user can access dashboard without redirect

#### Implementation for User Story 1

- [ ] T040 [P] [US1] Implement email validation in backend/auth.py endpoint
- [ ] T041 [P] [US1] Implement password hashing in backend/utils/security.py
- [ ] T042 [US1] Add JWT token generation in backend/auth.py
- [ ] T043 [US1] Implement frontend/login-form.tsx with error handling
- [ ] T044 [US1] Implement frontend/register-form.tsx with validation
- [ ] T045 [US1] Connect auth forms to API endpoints
- [ ] T046 [US1] Store JWT token in localStorage with automatic injection
- [ ] T047 [US1] Implement logout functionality that clears token
- [ ] T048 [US1] Add loading states during auth operations
- [ ] T049 [US1] Display user email in dashboard header

**Checkpoint**: User Story 1 should be fully functional and testable independently

---

### Phase D2: User Story 2 - Task Creation and Management (Priority: P1) 🎯 MVP

**Goal**: Users can create, view, edit, and delete tasks with rich details

**Independent Test**: Create tasks with various attributes, edit them, mark complete, and delete with proper confirmation

#### Validation for User Story 2

- [X] T050 [US2] Test task creation requires title and associates with authenticated user
  - Created comprehensive tests in `backend/tests/api/test_tasks.py`
  - Validates 422 error for empty/missing title
  - Confirms task is associated with authenticated user via user_id
- [X] T051 [US2] Test task update validates user ownership
  - Tests that users cannot update others' tasks (returns 404)
  - Ensures data isolation between users
- [X] T052 [US2] Test task deletion requires confirmation and validates ownership
  - Validates ownership protection on delete operations
  - Confirms 404 error when trying to delete others' tasks
- [X] T053 [US2] Test task completion toggle persists state
  - Tests PATCH /api/tasks/{id}/complete endpoint
  - Verifies completion status persists across fetches
  - Tests toggle functionality (True ↔ False)

#### Implementation for User Story 2

- [X] T054 [P] [US2] Create backend/crud/task.py with CRUD operations and user filtering
- [X] T055 [US2] Implement user ownership validation in all task endpoints
- [X] T056 [P] [US2] Create frontend/components/task/task-card.tsx with glassmorphism effect
- [X] T057 [P] [US2] Create frontend/components/task/task-form.tsx for create/edit
- [X] T058 [P] [US2] Create frontend/components/task/task-checkbox.tsx with strikethrough animation
- [X] T059 [US2] Create frontend/components/task/priority-badge.tsx (Low=gray, Medium=yellow, High=red)
- [X] T060 [US2] Implement task creation in dashboard with modal or inline form
- [X] T061 [US2] Implement task editing with pre-filled form
- [X] T062 [US2] Implement task completion toggle with visual feedback
- [X] T063 [US2] Implement task deletion with confirmation dialog
- [X] T064 [US2] Add toast notifications for all CRUD operations
- [X] T065 [US2] Implement empty state when no tasks exist
- [X] T066 [US2] Add Framer Motion animations for task state transitions

**Checkpoint**: User Stories 1 AND 2 should both work independently

---

### Phase D3: User Story 3 - Task Organization and Search (Priority: P2)

**Goal**: Users can search, filter, and sort tasks efficiently

**Independent Test**: Create multiple tasks with varied attributes and test all search, filter, and sort combinations

#### Validation for User Story 3

- [X] T067 [US3] Test search filters tasks by title and description in real-time
- [X] T068 [US3] Test filter by status shows only active or completed tasks
- [X] T069 [US3] Test filter by priority shows correct subset
- [X] T070 [US3] Test sorting by due date and priority works correctly

#### Implementation for User Story 3

- [X] T071 [P] [US3] Add search, status, priority, and sort parameters to backend GET /api/tasks
- [X] T072 [P] [US3] Implement database query filtering in backend/crud/task.py
- [X] T073 [US3] Create frontend/components/search/search-bar.tsx with debounced input
- [X] T074 [P] [US3] Create frontend/components/filters/filter-bar.tsx with dropdowns
- [X] T075 [P] [US3] Create frontend/components/filters/sort-controls.tsx
- [X] T076 [US3] Implement real-time search on frontend with React state
- [X] T077 [US3] Implement filter state management (all/active/completed, priority levels)
- [X] T078 [US3] Implement sort state management (created_at, due_date, priority, asc/desc)
- [X] T079 [US3] Update dashboard to show task count for each filter
- [X] T080 [US3] Maintain filter/sort state in URL query params

**Checkpoint**: All user stories should now be independently functional

---

## Phase E: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T081 [P] Implement error boundaries for graceful error handling
- [X] T082 [P] Add loading skeletons for better perceived performance
- [X] T083 Implement responsive design for mobile devices
- [X] T084 Add keyboard navigation support (Escape to close modals, Tab navigation)
- [X] T085 [P] Implement rate limiting on auth endpoints
- [X] T086 [P] Add database indexes for performance (user_id, priority, due_date)
- [X] T087 Implement pagination for task lists (limit/offset)
- [X] T088 [P] Add accessibility ARIA labels and roles
- [X] T089 Implement optimistic updates for better UX
- [X] T090 Add favicon and meta tags for SEO
- [X] T091 [P] Validate WCAG 2.1 AA compliance
- [X] T092 Implement backup and restore functionality
- [X] T093 Add user preferences (theme customization in future)
- [X] T094 [P] Performance audit and optimization
- [X] T095 Update documentation with API endpoints and component usage
- [X] T096 Validate quickstart.md setup instructions
- [X] T097 Security audit for common vulnerabilities

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase A (Monorepo)**: No dependencies - can start immediately
- **Phase B (Backend)**: Depends on Phase A completion - BLOCKS all user stories
- **Phase C (Frontend)**: Depends on Phase B backend being ready for integration
- **Phase D (User Stories)**: All depend on Phases A, B, C completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Phase E (Polish)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase C - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Phase C - Depends on US1 for auth context but independently testable
- **User Story 3 (P2)**: Can start after US2 completion - Requires tasks to exist for search/filter

### Within Each User Story

- Validation tasks MUST be written and verified before implementation
- Backend endpoints before frontend components
- Core implementation before integration and polish
- Story complete before moving to next priority

### Parallel Opportunities

- All Phase A tasks marked [P] can run in parallel
- All Phase B tasks marked [P] can run in parallel (within constraints)
- All Phase C tasks marked [P] can run in parallel
- Within each story, frontend components can be built in parallel with backend CRUD
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 2

```bash
# Backend tasks (can run together):
Task: "Create backend/crud/task.py with CRUD operations"
Task: "Implement user ownership validation in endpoints"

# Frontend tasks (can run together):
Task: "Create task-card.tsx with glassmorphism"
Task: "Create task-form.tsx for create/edit"
Task: "Create priority-badge.tsx (Low=gray, Medium=yellow, High=red)"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase A: Monorepo setup
2. Complete Phase B: Backend core and auth
3. Complete Phase C: Frontend foundation
4. Complete Phase D1: User Story 1 (Auth) - **STOP and VALIDATE**
5. Complete Phase D2: User Story 2 (Task CRUD) - **STOP and VALIDATE**
6. Deploy/demo MVP with auth and basic task management

### Incremental Delivery

1. Complete Phases A, B, C → Foundation ready
2. Add User Story 1 → Test auth flow independently → Deploy/Demo
3. Add User Story 2 → Test task CRUD independently → Deploy/Demo (MVP!)
4. Add User Story 3 → Test search/filter → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Phases A, B, C together (critical path)
2. Once Phase C completes:
   - Developer A: User Story 1 (auth)
   - Developer B: User Story 2 (task UI)
   - Developer C: Prepare for User Story 3 (search)
3. Stories integrate as they complete

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- JWT secret must be identical between frontend and backend
- All task operations must validate user ownership
- Glassmorphism effect = backdrop-blur + semi-transparent backgrounds
- Priority colors: Low (zinc-500), Medium (yellow-500), High (red-500)
- Electric Violet gradient = from-violet-600 to-fuchsia-600
- Stop at any checkpoint to validate story independently