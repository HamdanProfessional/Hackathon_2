# Tasks: Phase II Full-Stack Web Application

**Input**: Design documents from `/specs/002-web-app/`
**Prerequisites**: plan.md, spec.md

**Tests**: Manual testing for Phase II (automated tests in future phases)

**Organization**: Tasks grouped by user story for independent implementation

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files/modules, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, US4, US5, US6)
- File paths in descriptions

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure and initialize frontend/backend

- [X] T001 Create backend/ directory structure per plan.md (app/, models/, schemas/, crud/, api/, utils/, alembic/, tests/)
- [X] T002 Create frontend/ directory structure per plan.md (app/, components/, lib/, types/, public/)
- [X] T003 Initialize backend Python project with requirements.txt (fastapi, sqlalchemy, alembic, pydantic, python-jose, passlib, uvicorn, psycopg2-binary, pytest, httpx)
- [X] T004 Initialize frontend Next.js project with package.json (next@15, react@18, typescript, tailwind

css, shadcn/ui dependencies)
- [X] T005 Create backend/.env.example with DATABASE_URL, JWT_SECRET, CORS_ORIGIN placeholders
- [X] T006 Create frontend/.env.local.example with NEXT_PUBLIC_API_URL placeholder
- [X] T007 Create root README.md with project overview and links to backend/frontend READMEs
- [X] T008 Create backend/README.md with setup instructions
- [X] T009 Create frontend/README.md with setup instructions

**Checkpoint**: Project structure created, dependencies defined, ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that ALL user stories depend on

**� CRITICAL**: No user story work can begin until this phase is complete

- [X] T010 [P] Create backend/app/config.py with settings class (database URL, JWT secret, CORS origins)
- [X] T011 [P] Create backend/app/database.py with SQLAlchemy async engine and session management
- [X] T012 Create backend/app/main.py with FastAPI app instance, CORS middleware, and root route
- [X] T013 Initialize Alembic in backend/ with alembic init alembic
- [X] T014 Configure backend/alembic/env.py to use SQLAlchemy models and async engine
- [X] T015 Create backend/app/utils/security.py with password hashing (bcrypt) and JWT token functions (create_access_token, decode_token)
- [X] T016 Create backend/app/utils/exceptions.py with custom exception classes (NotFoundException, UnauthorizedException, ValidationException)
- [X] T017 Create frontend/lib/api.ts with axios/fetch wrapper and base URL configuration
- [X] T018 Create frontend/lib/auth.ts with token management functions (saveToken, getToken, clearToken, isAuthenticated)
- [X] T019 Configure frontend/tailwind.config.ts with shadcn/ui color scheme and theme
- [X] T020 Create frontend/app/layout.tsx with root layout, global styles, and metadata

**Checkpoint**: Foundation ready - user story implementation can now begin in any order

---

## Phase 3: User Story 1 + 6 - Authentication & Data Isolation (Priority: P1) <� MVP FOUNDATION

**Goal**: Users can register, log in, and each user's data is isolated

**Independent Test**: Register two users (Alice, Bob). Create task as Alice. Log out, log in as Bob. Verify Bob cannot see Alice's task. Delivers secure multi-user foundation.

### Backend Implementation for US1 + US6

- [X] T021 [P] [US1] Create backend/app/models/user.py with User SQLAlchemy model (id, email, hashed_password, created_at)
- [X] T022 [P] [US1] Create backend/app/schemas/user.py with UserCreate, UserResponse Pydantic schemas
- [X] T023 [P] [US1] Create backend/app/schemas/auth.py with LoginRequest, TokenResponse Pydantic schemas
- [X] T024 [US1] Create backend/app/crud/user.py with create_user, get_user_by_email, get_user_by_id functions
- [ ] T025 [US1] Generate initial Alembic migration for users table with alembic revision --autogenerate -m "Create users table" (requires .env setup)
- [ ] T026 [US1] Apply Alembic migration with alembic upgrade head (creates users table in Neon database) (requires database connection)
- [X] T027 [US1] Create backend/app/api/deps.py with get_db dependency (yields database session) and get_current_user dependency (validates JWT, returns User)
- [X] T028 [US1] Create backend/app/api/auth.py with POST /api/auth/register endpoint (creates user, returns token)
- [X] T029 [US1] Create backend/app/api/auth.py with POST /api/auth/login endpoint (validates credentials, returns JWT token)
- [X] T030 [US1] Add auth router to backend/app/main.py with app.include_router(auth_router, prefix="/api/auth")
- [ ] T031 [US1] Test auth endpoints manually with curl/Postman (register, login, token validation) (requires running server + database)

### Frontend Implementation for US1

- [X] T032 [P] [US1] Create frontend/types/user.ts with User, LoginRequest, RegisterRequest, TokenResponse TypeScript types
- [X] T033 [P] [US1] Create frontend/components/auth/login-form.tsx with email/password form and validation
- [X] T034 [P] [US1] Create frontend/components/auth/register-form.tsx with email/password form and validation
- [X] T035 [US1] Create frontend/app/login/page.tsx with login page using LoginForm component
- [X] T036 [US1] Create frontend/app/register/page.tsx with registration page using RegisterForm component
- [X] T037 [US1] Implement frontend/lib/api.ts authentication functions (register, login) calling backend endpoints
- [X] T038 [US1] Create frontend middleware.ts for route protection (redirect to /login if not authenticated)
- [X] T039 [US1] Update frontend/app/page.tsx to redirect authenticated users to /dashboard, unauthenticated to /login

**Manual Test Scenarios for US1 + US6**:
1. Navigate to /register, create account with alice@example.com / password123
2. Verify redirect to /dashboard after successful registration
3. Log out, navigate to /login
4. Log in with alice@example.com / password123, verify redirect to /dashboard
5. Open /dashboard in private/incognito tab, verify redirect to /login (auth check working)
6. Register second account bob@example.com / password456
7. (Data isolation tested in Phase 4 after task creation implemented)

**Checkpoint**: User Story 1 + 6 foundation complete - Multi-user authentication working

---

## Phase 4: User Story 2 - Task Creation and Viewing (Priority: P1) <� MVP DELIVERABLE

**Goal**: Authenticated users can create and view their tasks via web UI

**Independent Test**: Log in, create 3 tasks with different titles. Refresh page. Verify all 3 tasks persist and display. Delivers core CRUD functionality.

### Backend Implementation for US2

- [X] T040 [P] [US2] Create backend/app/models/task.py with Task SQLAlchemy model (id, user_id, title, description, completed, created_at, updated_at)
- [X] T041 [P] [US2] Create backend/app/schemas/task.py with TaskCreate, TaskUpdate, TaskResponse Pydantic schemas
- [X] T042 [US2] Create backend/app/crud/task.py with create_task, get_tasks_by_user, get_task_by_id functions (includes user_id filtering for US6 isolation)
- [ ] T043 [US2] Generate Alembic migration for tasks table with alembic revision --autogenerate -m "Create tasks table with user relationship" (requires .env setup)
- [ ] T044 [US2] Apply Alembic migration with alembic upgrade head (creates tasks table with foreign key to users) (requires database connection)
- [X] T045 [US2] Create backend/app/api/tasks.py with POST /api/tasks endpoint (requires authentication, uses current_user from JWT)
- [X] T046 [US2] Create backend/app/api/tasks.py with GET /api/tasks endpoint (requires authentication, filters by current_user.id for US6 isolation)
- [X] T047 [US2] Create backend/app/api/tasks.py with GET /api/tasks/{id} endpoint (requires authentication, validates task ownership for US6)
- [X] T048 [US2] Add tasks router to backend/app/main.py with app.include_router(tasks_router, prefix="/api/tasks", dependencies=[Depends(get_current_user)])
- [ ] T049 [US2] Test task endpoints manually with curl/Postman (create task, view tasks with auth token) (requires running server + database)

### Frontend Implementation for US2

- [X] T050 [P] [US2] Create frontend/types/task.ts with Task, TaskCreate, TaskUpdate TypeScript types
- [ ] T051 [P] [US2] Install and configure shadcn/ui components (button, input, card, dialog) with npx shadcn-ui@latest add (optional - using Tailwind CSS instead)
- [X] T052 [P] [US2] Create frontend/components/tasks/task-create-form.tsx with title/description input form
- [X] T053 [P] [US2] Create frontend/components/tasks/task-item.tsx with single task display (shows title, description, created date)
- [X] T054 [P] [US2] Create frontend/components/tasks/task-list.tsx with list of TaskItem components and empty state
- [X] T055 [US2] Implement frontend/lib/api.ts task functions (createTask, getTasks, getTaskById)
- [X] T056 [US2] Create frontend/app/dashboard/page.tsx with task list and create form (protected route)
- [X] T057 [US2] Add loading states to dashboard (show spinner while fetching tasks)
- [X] T058 [US2] Add error handling to dashboard (display error message if API calls fail)
- [X] T059 [US2] Add success feedback to dashboard (show toast/message after task created)

**Manual Test Scenarios for US2 + US6 Data Isolation**:
1. Log in as alice@example.com
2. Create task "Buy groceries" with description "Milk, eggs, bread"
3. Create task "Call dentist" with description ""
4. Refresh page, verify both tasks display
5. Log out, log in as bob@example.com
6. Verify Bob sees 0 tasks (Alice's tasks not visible - US6 working!)
7. Create task as Bob "Submit report"
8. Verify Bob sees only his task
9. Log out, log back in as Alice
10. Verify Alice still sees only her 2 tasks (data isolation confirmed)

**Checkpoint**: MVP COMPLETE! Users can register, log in, create tasks, view tasks. Data isolation working.

---

## Phase 5: User Story 3 - Task Completion Tracking (Priority: P2)

**Goal**: Users can mark tasks as complete/incomplete with visual indicators

**Independent Test**: Create task, click checkbox to mark complete. Verify strikethrough/visual change. Refresh page. Verify completion status persists.

### Backend Implementation for US3

- [X] T060 [US3] Create backend/app/api/tasks.py with PATCH /api/tasks/{id}/complete endpoint (toggles completed field, validates ownership)
- [X] T061 [US3] Update backend/app/crud/task.py with toggle_task_completion function (sets completed=True or False based on current state)
- [ ] T062 [US3] Test completion endpoint manually with curl/Postman (toggle task, verify completed field changes) (requires running server + database)

### Frontend Implementation for US3

- [ ] T063 [P] [US3] Install shadcn/ui checkbox component with npx shadcn-ui@latest add checkbox (optional - using HTML checkbox instead)
- [X] T064 [US3] Update frontend/components/tasks/task-item.tsx to display checkbox and apply strikethrough style when completed
- [X] T065 [US3] Implement frontend/lib/api.ts toggleTaskCompletion function
- [X] T066 [US3] Add checkbox click handler to task-item.tsx that calls toggleTaskCompletion and refreshes list
- [X] T067 [US3] Add optimistic UI update (immediately apply strikethrough, then call API)

**Manual Test Scenarios for US3**:
1. View task list with incomplete tasks
2. Click checkbox on task "Buy groceries", verify strikethrough applied immediately
3. Refresh page, verify task still shows as completed
4. Click checkbox again, verify strikethrough removed
5. Test with multiple tasks (mark 2 complete, 1 incomplete, verify correct visual states)

**Checkpoint**: User Stories 1, 2, 3, and 6 complete - Full task tracking system working

---

## Phase 6: User Story 4 - Task Editing and Updating (Priority: P2)

**Goal**: Users can modify task title and description after creation

**Independent Test**: Click edit button on task. Change title. Save. Verify title updates and persists after page refresh.

### Backend Implementation for US4

- [X] T068 [US4] Create backend/app/api/tasks.py with PUT /api/tasks/{id} endpoint (updates title/description, validates ownership, requires at least one field)
- [X] T069 [US4] Update backend/app/crud/task.py with update_task function (updates fields, sets updated_at timestamp)
- [ ] T070 [US4] Test update endpoint manually with curl/Postman (update title only, description only, both) (requires running server + database)

### Frontend Implementation for US4

- [ ] T071 [P] [US4] Install shadcn/ui dialog component with npx shadcn-ui@latest add dialog (optional - using custom dialog)
- [X] T072 [US4] Create frontend/components/tasks/task-edit-dialog.tsx with edit form (pre-filled title/description, save/cancel buttons)
- [X] T073 [US4] Implement frontend/lib/api-client.ts updateTask function (already existed)
- [X] T074 [US4] Update frontend/components/tasks/task-item.tsx to include edit icon/button that opens TaskEditDialog (already existed)
- [X] T075 [US4] Add form validation to edit dialog (title required, max lengths)
- [X] T076 [US4] Add save handler that calls updateTask API and refreshes task list

**Manual Test Scenarios for US4**:
1. Click edit icon on task "Buy groceries"
2. Change title to "Buy groceries and toiletries"
3. Save, verify task list updates immediately
4. Refresh page, verify title change persisted
5. Edit task, change only description, verify description updates
6. Edit task, clear title field, verify validation error prevents save

**Checkpoint**: User Stories 1, 2, 3, 4, and 6 complete - Full edit capability working

---

## Phase 7: User Story 5 - Task Deletion (Priority: P3)

**Goal**: Users can permanently remove tasks with confirmation

**Independent Test**: Click delete button on task. Confirm deletion. Verify task removed from list and does not reappear after page refresh.

### Backend Implementation for US5

- [X] T077 [US5] Create backend/app/api/tasks.py with DELETE /api/tasks/{id} endpoint (deletes task, validates ownership)
- [X] T078 [US5] Update backend/app/crud/task.py with delete_task function
- [ ] T079 [US5] Test delete endpoint manually with curl/Postman (delete task, verify 404 on subsequent GET) (requires running server + database)

### Frontend Implementation for US5

- [X] T080 [US5] Create frontend/components/tasks/task-delete-dialog.tsx with confirmation dialog ("Are you sure?", Delete/Cancel buttons)
- [X] T081 [US5] Implement frontend/lib/api-client.ts deleteTask function (already existed)
- [X] T082 [US5] Update frontend/components/tasks/task-item.tsx to include delete icon/button that opens TaskDeleteDialog (already existed)
- [X] T083 [US5] Add delete handler that calls deleteTask API and refreshes task list
- [X] T084 [US5] Add optimistic UI update (immediately remove from list after confirmation)

**Manual Test Scenarios for US5**:
1. Create 3 tasks (IDs 1, 2, 3)
2. Click delete icon on task ID 2
3. Confirm deletion in dialog
4. Verify task ID 2 removed from list immediately
5. Refresh page, verify task ID 2 still gone
6. Create new task, verify it gets ID 4 (not reusing ID 2)
7. Test cancel button - verify task not deleted when cancel clicked

**Checkpoint**: All user stories complete - Full CRUD functionality working

---

## Phase 8: Polish & Deployment

**Purpose**: Error handling, loading states, responsive design, and deployment

### Error Handling & UX Improvements

- [ ] T085 Add comprehensive error handling to all backend endpoints (try-except blocks, proper HTTP status codes)
- [ ] T086 Add request validation error messages to backend (Pydantic validation errors with field details)
- [ ] T087 Create frontend/components/ui/error-message.tsx component for displaying API errors
- [ ] T088 Create frontend/components/ui/loading-spinner.tsx component for loading states
- [ ] T089 Add loading spinners to all async operations (login, register, task create/update/delete)
- [ ] T090 Add error toast notifications to frontend (success/error messages for all operations)
- [ ] T091 Add input validation to all frontend forms (email format, password length, title required)
- [ ] T092 Add empty state components (no tasks yet message with call-to-action)

### Responsive Design & Accessibility

- [ ] T093 Test frontend on mobile viewport (320px-768px) and adjust Tailwind classes for responsive design
- [ ] T094 Test frontend on tablet viewport (768px-1024px) and adjust layout
- [ ] T095 Add keyboard navigation support (Tab, Enter, Escape keys)
- [ ] T096 Add ARIA labels to interactive elements (buttons, forms, dialogs)
- [ ] T097 Test with screen reader and fix accessibility issues

### Security & Performance

- [ ] T098 Add rate limiting to backend auth endpoints (prevent brute force attacks)
- [ ] T099 Add HTTPS redirect middleware to backend (force HTTPS in production)
- [ ] T100 Add security headers to backend responses (CORS, CSP, X-Frame-Options)
- [ ] T101 Add database query optimization (add indexes on user_id, created_at columns)
- [ ] T102 Add frontend bundle optimization (code splitting, tree shaking)
- [ ] T103 Add frontend image optimization (use Next.js Image component)

### Testing & Validation

- [ ] T104 Write backend pytest tests for auth endpoints (register, login, token validation)
- [ ] T105 Write backend pytest tests for task CRUD endpoints (create, read, update, delete, complete)
- [ ] T106 Write backend pytest tests for authorization (user A cannot access user B's tasks)
- [ ] T107 Run all backend tests with pytest and fix any failures
- [ ] T108 Write frontend Jest tests for auth components (login form, register form)
- [ ] T109 Write frontend Jest tests for task components (task list, task item, task forms)
- [ ] T110 Run all frontend tests with npm test and fix any failures
- [ ] T111 Perform manual end-to-end testing of all user stories (US1-US6)
- [ ] T112 Test edge cases (empty strings, special characters, very long inputs, SQL injection attempts)

### Documentation

- [ ] T113 Update backend/README.md with complete setup instructions (prerequisites, Neon setup, env vars, migrations, running server)
- [ ] T114 Update frontend/README.md with complete setup instructions (prerequisites, env vars, running dev server)
- [ ] T115 Create root-level DEPLOYMENT.md with production deployment guide (Neon, Vercel, Railway/Render)
- [ ] T116 Add inline code comments to complex logic (JWT validation, task filtering, etc.)
- [ ] T117 Generate API documentation (FastAPI Swagger UI at /docs already auto-generated)

### Deployment

- [ ] T118 Create Neon PostgreSQL project and get connection string
- [ ] T119 Deploy backend to Railway/Render/Fly.io with environment variables configured
- [ ] T120 Run Alembic migrations on production database with alembic upgrade head
- [ ] T121 Deploy frontend to Vercel with NEXT_PUBLIC_API_URL pointing to production backend
- [ ] T122 Configure CORS in backend to allow production frontend domain
- [ ] T123 Test production deployment end-to-end (register, login, create task, CRUD operations)
- [ ] T124 Set up SSL/TLS certificates (automatic with Vercel and most cloud providers)
- [ ] T125 Configure custom domain (optional)

**Manual Test - Complete Application**:
1. Test all functional requirements (FR-001 through FR-042) from spec.md
2. Test all user stories (US1 through US6) end-to-end
3. Test all success criteria (SC-001 through SC-012) from spec.md
4. Test all edge cases from spec.md
5. Test on multiple browsers (Chrome, Firefox, Safari, Edge)
6. Test on multiple devices (desktop, tablet, mobile)
7. Test with multiple concurrent users (simulate 10+ users)

**Checkpoint**: Phase II complete - Production-ready web application deployed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1 + US6)**: Depends on Phase 2 - MVP foundation (auth + isolation)
- **Phase 4 (US2)**: Depends on Phase 2 and Phase 3 - Core CRUD functionality (MVP deliverable)
- **Phase 5 (US3)**: Depends on Phase 2 and Phase 4 - Can run parallel to US4/US5 after US2 complete
- **Phase 6 (US4)**: Depends on Phase 2 and Phase 4 - Can run parallel to US3/US5 after US2 complete
- **Phase 7 (US5)**: Depends on Phase 2 and Phase 4 - Can run parallel to US3/US4 after US2 complete
- **Phase 8 (Polish)**: Depends on all user stories complete

### Recommended Execution Order

**Sequential (Single Developer)**:
1. Phase 1: Setup � Phase 2: Foundational
2. Phase 3: US1 + US6 (Auth + Isolation) � Test independently
3. Phase 4: US2 (Task CRUD) � Test independently � **MVP DELIVERABLE!**
4. Phase 5: US3 (Completion) � Test independently
5. Phase 6: US4 (Edit) � Test independently
6. Phase 7: US5 (Delete) � Test independently
7. Phase 8: Polish � Final validation and deployment

**Optimal Strategy**:
- Complete Phase 1 & 2 first (foundation)
- Implement Phase 3 (auth) and test thoroughly
- Implement Phase 4 (task CRUD) and test � **Deliverable MVP!**
- Add Phase 5, 6, 7 incrementally
- Each addition tested before next
- Commit after each user story validates

### Within Each User Story

- Backend tasks first (T001-T031 for US1, etc.)
- Then frontend tasks (T032-T039 for US1, etc.)
- Test after completing each user story phase
- Commit after each user story validates

### Parallel Opportunities

**Phase 2 Foundational** (different modules):
- T010 (config) || T011 (database) can run in parallel
- T015 (security) || T016 (exceptions) || T017 (frontend API) can run in parallel

**Phase 3 US1** (different models):
- T021 (User model) || T022 (User schema) || T023 (Auth schema) can run in parallel
- T032 (User types) || T033 (Login form) || T034 (Register form) can run in parallel

**Phase 4 US2** (different models):
- T040 (Task model) || T041 (Task schema) can run in parallel
- T050 (Task types) || T051 (UI components) || T052 (Create form) || T053 (Task item) || T054 (Task list) can run in parallel

**After US2 MVP Complete**:
- US3, US4, US5 can be worked on in parallel (different endpoints, different components)

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 6 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T020)
3. Complete Phase 3: US1 + US6 Auth (T021-T039)
4. Complete Phase 4: US2 Task CRUD (T040-T059)
5. **STOP and VALIDATE**: Manually test all US1, US2, US6 scenarios
6. **Deploy MVP**: Working web app with auth and task creation
7. Commit as MVP (basic todo web app working!)

**MVP Deliverable**: Users can register, log in, create tasks, view tasks. Data persists to database. Multi-user isolation working. Deployed to production.

### Incremental Delivery

1. Foundation (Phase 1-2) � 20 tasks
2. Add US1 + US6 (Phase 3) � Test auth + isolation � 19 more tasks
3. Add US2 (Phase 4) � Test task CRUD � **MVP!** � 20 more tasks
4. Add US3 (Phase 5) � Test completion � 8 more tasks
5. Add US4 (Phase 6) � Test editing � 9 more tasks
6. Add US5 (Phase 7) � Test deletion � 8 more tasks
7. Polish (Phase 8) � Final quality � 41 more tasks
8. Each increment adds value without breaking previous features

### Full Implementation Path

**Total tasks**: 125
- Phase 1 (Setup): 9 tasks
- Phase 2 (Foundational): 11 tasks
- Phase 3 (US1 + US6 Auth): 19 tasks � MVP foundation
- Phase 4 (US2 Task CRUD): 20 tasks � MVP deliverable
- Phase 5 (US3 Completion): 8 tasks
- Phase 6 (US4 Edit): 9 tasks
- Phase 7 (US5 Delete): 8 tasks
- Phase 8 (Polish): 41 tasks

**Estimated time**: 2-3 weeks for experienced full-stack developer

---

## Task Summary

**Total Tasks**: 125
- Phase 1 (Setup): 9 tasks
- Phase 2 (Foundational): 11 tasks
- Phase 3 (US1 + US6): 19 tasks
- Phase 4 (US2): 20 tasks
- Phase 5 (US3): 8 tasks
- Phase 6 (US4): 9 tasks
- Phase 7 (US5): 8 tasks
- Phase 8 (Polish): 41 tasks

**Parallel Opportunities**: 15+ tasks can run in parallel (marked with [P])

**MVP Scope**: Phase 1-4 (59 tasks) = Auth + Task CRUD with data isolation

**Independent Test Criteria**:
- US1 + US6: Can register, log in, data isolated between users
- US2: Can create tasks and view list with correct persistence
- US3: Can mark tasks complete with visual indicator persisting
- US4: Can update task details while preserving ID/status
- US5: Can delete tasks with confirmation, gaps handled correctly

**Format Validation**:  All tasks follow checklist format with ID, [P] where applicable, [Story] label, and file paths

---

## Notes

- Frontend and backend developed in parallel after foundational phase
- [P] markers identify parallelizable tasks (different files/modules)
- [US1], [US2], [US3], [US4], [US5], [US6] labels map tasks to user stories from spec.md
- Manual testing against acceptance criteria (automated tests in Phase III+)
- Each user story independently testable after its phase completes
- Constitution compliant: Next.js + FastAPI + Neon PostgreSQL, no Phase III tech
- Backend-first recommended within each story (API contracts before UI)
- Ready for /sp.implement command execution

---

**Generated**: 2025-12-13
**Branch**: 002-web-app
**Spec**: specs/002-web-app/spec.md
**Plan**: specs/002-web-app/plan.md
