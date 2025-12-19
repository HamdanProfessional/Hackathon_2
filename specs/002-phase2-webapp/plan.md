# Implementation Plan: Phase II - Full-Stack Modern Web Application

**Feature Branch**: `002-phase2-webapp`
**Created**: 2025-12-15
**Status**: In Progress
**Spec**: [spec.md](spec.md)

## 1. Technical Context

### Monorepo Architecture
- Frontend: `/frontend` - Next.js 16+ with TypeScript
- Backend: `/backend` - Python FastAPI
- Development: `docker-compose.yml` for local orchestration

### Authentication Strategy
- Frontend: Better Auth with JWT issuance
- Backend: FastAPI dependency `get_current_user` for token verification
- Shared secret between services for JWT validation

### UI Design System
- Theme: "Nebula 2025" - Dark mode first
- Colors: Zinc-950 background, Electric Violet to Fuchsia gradients
- Components: Bento-grid dashboard layout
- Libraries: shadcn/ui, framer-motion, lucide-react, sonner

### Database Schema
- User model: id, email, hashed_password, created_at
- Task model: id, user_id(FK), title, description, priority, due_date, completed, created_at, updated_at

## 2. Constitution Check

**Phase II Compliance**: ✅ All technologies align with Phase II requirements
- Next.js 16+ (App Router) ✅
- Python FastAPI ✅
- Neon Serverless PostgreSQL ✅
- Better Auth with JWT ✅

**Architecture Principles**:
- Monorepo structure maintains clear separation of concerns ✅
- Stateless backend with JWT authentication ✅
- RESTful API design pattern ✅

## 3. Phase 0: Research & Decisions

### Better Auth Integration Pattern
**Decision**: Use Better Auth's JWT strategy with shared secret
**Rationale**:
- Simplifies token validation between services
- Better Auth handles frontend auth flows
- FastAPI can verify JWTs without database calls
- Established pattern for Next.js + FastAPI integrations

**Implementation**:
- Frontend: Better Auth configuration with JWT adapter
- Backend: Middleware dependency to extract and verify JWT from Authorization header
- Shared secret: Environment variable `JWT_SECRET` in both services

### Database Schema Design
**Decision**: SQLModel with explicit relationships
**Rationale**:
- Type-safe ORM for Python
- Automatic table generation
- Built-in validation
- Async support for FastAPI

**Task Priority Handling**:
- Enum type: Priority = Enum('low', 'medium', 'high')
- Database level constraint for valid values
- Color mapping in frontend (low=gray, medium=yellow, high=red)

### "Nebula 2025" UI Implementation
**Tailwind Configuration**:
- Custom color palette extension
- CSS variables for theme consistency
- Dark mode as default (no light variant)

**Component Strategy**:
- shadcn/ui as base component library
- Custom theme override for Nebula colors
- Bento-grid using CSS Grid with responsive breakpoints
- Glassmorphism via backdrop-blur and semi-transparent backgrounds

## 4. Phase 1: Design & Contracts

### 4.1 Data Model

#### User Entity
```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tasks: List["Task"] = Relationship(back_populates="user")
```

#### Task Entity
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(max_length=2000)
    priority: Priority = Priority.medium
    due_date: Optional[date] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="tasks")
```

### 4.2 API Contracts

#### Authentication Endpoints
```
POST /api/auth/register
  Request: { email: string, password: string }
  Response: { token: string, user: UserResponse }

POST /api/auth/login
  Request: { email: string, password: string }
  Response: { token: string, user: UserResponse }
```

#### Task Management Endpoints
```
GET /api/tasks
  Response: [TaskResponse]

POST /api/tasks
  Request: CreateTaskRequest
  Response: TaskResponse

PUT /api/tasks/{id}
  Request: UpdateTaskRequest
  Response: TaskResponse

DELETE /api/tasks/{id}
  Response: { success: boolean }
```

### 4.3 Component Hierarchy

```
AppLayout
  ├── Header (user menu, logout)
  └── Dashboard
      ├── SearchBar
      ├── FilterBar (status, priority, sort)
      └── BentoGrid
          └── TaskCard
              ├── TaskContent
              ├── TaskActions (edit, delete)
              └── TaskCheckbox
```

## 5. Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant BetterAuth
    participant Backend
    participant Database

    User->>Frontend: Login with email/password
    Frontend->>BetterAuth: Authenticate credentials
    BetterAuth->>Database: Verify user
    Database-->>BetterAuth: User data
    BetterAuth-->>Frontend: JWT token
    Frontend->>Frontend: Store token in secure storage

    User->>Frontend: Access protected route
    Frontend->>Backend: Request with Authorization: Bearer <token>
    Backend->>Backend: Verify JWT with shared secret
    Backend-->>Frontend: User data or 401
    Frontend-->>User: Render dashboard
```

## 6. Development Setup

### Docker Compose Configuration
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - BETTER_AUTH_SECRET=${JWT_SECRET}
    volumes:
      - ./frontend:/app

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/todos
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - ./backend:/app

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=todos
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### Environment Variables
```bash
# .env
JWT_SECRET=your-super-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/todos
```

## 7. Implementation Phases

### Phase 1: Infrastructure (Days 1-2)
- [ ] Set up monorepo structure
- [ ] Configure Docker Compose
- [ ] Initialize FastAPI with basic structure
- [ ] Set up Next.js with TypeScript and Tailwind
- [ ] Configure Better Auth

### Phase 2: Authentication (Days 3-4)
- [ ] Implement User/Task SQLModel
- [ ] Create database migrations
- [ ] Build JWT token verification middleware
- [ ] Implement register/login endpoints
- [ ] Create auth UI components

### Phase 3: Task CRUD (Days 5-7)
- [ ] Build task management endpoints
- [ ] Implement task API client
- [ ] Create task UI components
- [ ] Implement Bento-grid layout
- [ ] Add toast notifications

### Phase 4: Polish & Performance (Days 8-10)
- [ ] Add search and filtering
- [ ] Implement micro-animations
- [ ] Optimize database queries
- [ ] Add error boundaries
- [ ] Write integration tests

## 8. Success Metrics

### Performance Targets
- Page load: < 3 seconds
- API response: < 500ms
- Search latency: < 200ms
- Concurrent users: 1000+

### Quality Gates
- 100% test coverage for auth flows
- Accessibility WCAG 2.1 AA compliance
- Mobile responsiveness 100% parity
- Zero security vulnerabilities

## 9. Risks & Mitigations

### Technical Risks
1. **JWT Secret Synchronization**
   - Risk: Desync between frontend/backend
   - Mitigation: Single source of truth in .env file

2. **Database Performance**
   - Risk: Slow queries with many tasks
   - Mitigation: Proper indexing and pagination

3. **State Management**
   - Risk: Complex client state
   - Mitigation: Server state with React Query

### Timeline Risks
1. **Better Auth Learning Curve**
   - Mitigation: Start with basic JWT, add social later

2. **UI Complexity**
   - Mitigation: Use shadcn/ui components as base

## 10. Next Steps

1. Execute Phase 1: Infrastructure setup
2. Verify authentication flow end-to-end
3. Implement MVP with basic CRUD
4. Add "Nebula 2025" styling
5. Complete full feature set
6. Performance optimization and testing

---

This plan provides a complete blueprint for Phase II implementation. All architectural decisions have been made, allowing the implementation phase to proceed without additional architectural considerations.