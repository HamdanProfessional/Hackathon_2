# ADR-001: Migration from Phase I (CLI) to Phase II (Full-Stack Web App)

**Status**: Accepted
**Date**: 2025-12-13
**Deciders**: System Architect, Lead Engineer
**Phase Transition**: Phase I → Phase II

---

## Context

Phase I successfully delivered a working console-based TODO CRUD application with:
- ✅ All 36 tasks completed (T001-T036)
- ✅ 11/11 validation tests passed
- ✅ Single file Python implementation (src/main.py, 339 lines)
- ✅ In-memory storage with complete CRUD operations
- ✅ Excellent code quality (100/100 after code review)

**Business Driver**: Users need persistent storage, multi-user access, and web-based interface for practical real-world usage.

**Technical Driver**: Demonstrate evolutionary architecture from monolithic script to modular web application.

**Constraints**:
- Must preserve all Phase I CRUD functionality
- Data must persist between sessions (database required)
- Multi-user support needed (authentication required)
- Web interface for broader accessibility

---

## Decision

We will transition to **Phase II: Modular Monolith** architecture with the following technology stack:

### Frontend
- **Next.js 15** with TypeScript
- React Server Components for performance
- Tailwind CSS for styling
- shadcn/ui component library

### Backend
- **FastAPI** (Python 3.13+)
- RESTful API design
- Pydantic models for validation
- CORS configuration for Next.js communication

### Database
- **Neon PostgreSQL** (serverless)
- SQLAlchemy ORM
- Alembic for migrations
- Connection pooling

### Authentication
- **Better Auth**
- JWT tokens
- Session management
- User registration and login

### Project Structure
```
├── frontend/          # Next.js application
│   ├── app/          # App router pages
│   ├── components/   # React components
│   ├── lib/          # Utilities and API client
│   └── public/       # Static assets
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── crud/     # CRUD operations
│   │   └── main.py   # FastAPI app
│   ├── alembic/      # Database migrations
│   └── tests/        # Backend tests
├── src/              # Phase I (preserved for reference)
│   └── main.py       # Original CLI app
└── specs/            # Specifications and planning
```

---

## Migration Strategy

### Step 1: Backend API Development
1. Setup FastAPI project structure
2. Define SQLAlchemy models (User, Task)
3. Create database migrations with Alembic
4. Implement CRUD endpoints matching Phase I operations:
   - POST /api/tasks (create)
   - GET /api/tasks (read all)
   - GET /api/tasks/{id} (read one)
   - PUT /api/tasks/{id} (update)
   - DELETE /api/tasks/{id} (delete)
   - PATCH /api/tasks/{id}/complete (mark complete)
5. Add authentication endpoints (login, register, logout)
6. Configure CORS for Next.js origin
7. Write API tests

### Step 2: Database Schema
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT DEFAULT '',
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

### Step 3: Frontend Development
1. Setup Next.js 15 with TypeScript
2. Configure Tailwind CSS and shadcn/ui
3. Create API client library (fetch wrapper with auth)
4. Build authentication pages (login, register)
5. Build task management pages:
   - Dashboard (view all tasks)
   - Task creation form
   - Task update modal
   - Task deletion confirmation
6. Implement client-side state management
7. Add loading states and error handling

### Step 4: Data Migration
- Phase I has no persistent data (in-memory only)
- No data migration needed from Phase I
- Users will create new data in Phase II database

### Step 5: Deployment
- Frontend: Vercel (automatic deployment from Git)
- Backend: Railway/Render/Fly.io (FastAPI container)
- Database: Neon (PostgreSQL serverless)

---

## Consequences

### Positive
✅ **Persistence**: Data survives application restarts
✅ **Multi-User**: Support for multiple users with isolated data
✅ **Web Access**: Accessible from any device with browser
✅ **Scalability**: Database can handle large datasets
✅ **Modern UX**: Rich web interface vs. CLI
✅ **API Foundation**: REST API enables future integrations (Phase III AI agents)
✅ **Authentication**: Secure user data and access control
✅ **Production Ready**: Deployable to cloud platforms

### Negative
⚠️ **Complexity Increase**: From 1 file to multi-directory monorepo
⚠️ **Dependency Management**: npm packages + pip packages to manage
⚠️ **Infrastructure Cost**: Database hosting, backend hosting (though free tiers available)
⚠️ **Deployment Complexity**: Multiple services to deploy and monitor
⚠️ **Learning Curve**: Next.js, FastAPI, PostgreSQL for new developers

### Mitigations
- 📖 Comprehensive documentation for setup and deployment
- 🧪 Automated tests for API and frontend
- 🔧 Docker Compose for local development environment
- 📝 Step-by-step migration guide in spec
- 🎯 Preserve Phase I code for reference

---

## Alternatives Considered

### Alternative 1: Stay with CLI + Add File Persistence
**Pros**: Simpler, no infrastructure, single file
**Cons**: No multi-user, no web access, file locking issues, not cloud-ready
**Rejected**: Doesn't meet business requirements for web access and multi-user

### Alternative 2: Use Django instead of FastAPI + Next.js
**Pros**: Single framework, batteries-included, admin panel
**Cons**: Monolithic, harder to separate frontend, less modern DX
**Rejected**: FastAPI + Next.js provides better separation and modern stack

### Alternative 3: Use SQLite instead of PostgreSQL
**Pros**: Simpler setup, no external database
**Cons**: Not cloud-native, file-based (deployment issues), limited concurrency
**Rejected**: Neon PostgreSQL is serverless and easier for deployment

### Alternative 4: Skip Phase II, go directly to Phase III (AI)
**Pros**: Faster to AI features
**Cons**: Violates evolutionary architecture principle, skips learning
**Rejected**: Constitution forbids skipping phases

---

## Implementation Plan Reference

See **specs/002-phase-ii-web-app/spec.md** for complete Phase II feature specification.

Tasks generated in **specs/002-phase-ii-web-app/tasks.md** following spec-driven workflow.

---

## Success Criteria

Phase II transition complete when:
1. ✅ All Phase I CRUD operations work via web UI
2. ✅ Data persists to PostgreSQL database
3. ✅ User authentication working (register, login, logout)
4. ✅ Multi-user isolation (users see only their own tasks)
5. ✅ API tests passing (CRUD + auth endpoints)
6. ✅ Frontend deployed to Vercel
7. ✅ Backend deployed to cloud platform
8. ✅ Database hosted on Neon
9. ✅ End-to-end manual testing complete

---

## Backward Compatibility

- Phase I CLI preserved in `src/main.py` (not removed)
- Phase I can still run locally with `python src/main.py`
- No breaking changes to Phase I (frozen as reference implementation)
- Phase II is additive, not replacement

---

## Related Decisions

- **ADR-002** (future): API versioning strategy for Phase III
- **ADR-003** (future): Authentication provider selection for Phase III AI agents
- **ADR-004** (future): Microservices decomposition strategy for Phase IV

---

## References

- [Constitution v3.0.0](../../.specify/memory/constitution.md) - Phase II technology stack
- [Phase I Implementation PHR](../prompts/001-todo-crud/005-phase-i-implementation-complete.green.prompt.md)
- [Next.js 15 Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neon PostgreSQL](https://neon.tech/)
- [Better Auth](https://www.better-auth.com/)

---

**Signed**: System Architect
**Date**: 2025-12-13
**Constitution Version**: 3.0.0
