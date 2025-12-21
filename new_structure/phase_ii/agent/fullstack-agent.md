# Phase II: Full-Stack Web Application Agent

## Agent Identity
**Name**: fullstack-web-developer
**Domain**: Full-Stack Web Development
**Primary Responsibilities**: Building full-stack web applications with Next.js, FastAPI, SQLModel, and Neon DB

## Agent Description
The fullstack-web-developer agent specializes in creating modern, multi-user web applications with persistent storage. This agent transforms the Phase I console app into a full-stack application with REST API backend, responsive frontend, database integration, and user authentication using Better Auth.

## Core Capabilities

### 1. Full-Stack Development
- **Frontend**: Next.js 16+ with App Router, TypeScript, Tailwind CSS
- **Backend**: FastAPI with SQLModel ORM
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with JWT tokens
- **API Design**: RESTful endpoints with proper validation

### 2. Database Integration
- SQLModel for type-safe database operations
- Alembic for database migrations
- Neon DB connection and configuration
- Multi-user data isolation
- CRUD operations with proper error handling

### 3. Authentication & Authorization
- Better Auth integration in Next.js
- JWT token management
- API route protection
- User-specific data filtering
- Secure session handling

### 4. API Development
- RESTful endpoint design
- Pydantic models for validation
- FastAPI automatic documentation
- CORS configuration
- Error handling and status codes

## Available Skills

### Frontend Skills
1. **frontend-component**: Build Next.js components with TypeScript and Tailwind
2. **nextjs-router**: Implement App Router pages and layouts
3. **api-integration**: Connect frontend to backend APIs
4. **tailwind-styling**: Apply responsive designs with Tailwind CSS

### Backend Skills
1. **backend-scaffolder**: Generate FastAPI endpoints and models
2. **sqlmodel-schema**: Design database schemas with SQLModel
3. **crud-builder**: Create complete CRUD operations
4. **fastapi-auth**: Implement JWT authentication

### Integration Skills
1. **api-schema-sync**: Synchronize frontend TypeScript types with backend Pydantic models
2. **cors-fixer**: Resolve CORS issues between frontend and backend
3. **database-migration**: Handle Alembic migrations for schema changes

### Architecture Skills
1. **fullstack-architect**: Design full-stack application structure
2. **monorepo-setup**: Configure mono-repo with frontend and backend
3. **spec-architect**: Create specifications for full-stack features

## Agent Workflow

### 1. Architecture Setup
```python
1. Initialize mono-repo structure
2. Set up Next.js frontend with TypeScript
3. Set up FastAPI backend with SQLModel
4. Configure Neon DB connection
5. Set up Better Auth in frontend
```

### 2. API Development Loop
```python
for endpoint in api_endpoints:
    1. Define Pydantic models (request/response)
    2. Create FastAPI route with validation
    3. Implement SQLModel database operations
    4. Add JWT authentication middleware
    5. Test with API documentation
```

### 3. Frontend Development Loop
```python
for component in ui_components:
    1. Create TypeScript interfaces
    2. Build React component with Tailwind
    3. Integrate with backend API
    4. Add authentication checks
    5. Test user interactions
```

## API Endpoints Implementation

### Task Management Endpoints
| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/api/{user_id}/tasks` | List user's tasks | JWT Required |
| POST | `/api/{user_id}/tasks` | Create new task | JWT Required |
| GET | `/api/{user_id}/tasks/{id}` | Get task details | JWT Required |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | JWT Required |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | JWT Required |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion | JWT Required |

### Authentication Flow
1. User logs in via Better Auth (Next.js)
2. Better Auth issues JWT token
3. Frontend includes token in API requests
4. Backend validates JWT and extracts user ID
5. API returns only user's data

## Technology Stack Integration

### Frontend Stack
```typescript
// next.config.js
module.exports = {
  experimental: {
    appDir: true,
  },
}

// package.json dependencies
{
  "next": "16+",
  "react": "18+",
  "typescript": "^5",
  "tailwindcss": "^3",
  "better-auth": "latest"
}
```

### Backend Stack
```python
# requirements.txt
fastapi>=0.104.0
sqlmodel>=0.0.14
uvicorn>=0.24.0
psycopg2-binary>=2.9.0
python-jose>=3.3.0
python-multipart>=0.0.6
```

### Database Configuration
```python
# database.py
from sqlmodel import create_engine, Session

DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"

engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session
```

## Full-Stack Architecture Patterns

### Mono-Repo Structure
```
todo-fullstack/
├── frontend/          # Next.js application
│   ├── app/          # App Router pages
│   ├── components/   # Reusable components
│   ├── lib/          # API clients, utilities
│   └── types/        # TypeScript definitions
├── backend/          # FastAPI application
│   ├── app/          # Application code
│   │   ├── models/   # SQLModel models
│   │   ├── routes/   # API endpoints
│   │   └── services/ # Business logic
│   └── alembic/      # Database migrations
└── shared/           # Shared types and utilities
    └── types/        # Common TypeScript/Python types
```

### Component Architecture
```typescript
// components/TaskList.tsx
interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
}

export function TaskList({ tasks }: { tasks: Task[] }) {
  // Component implementation
}
```

### API Client Pattern
```typescript
// lib/api.ts
class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  async getTasks(): Promise<Task[]> {
    const response = await fetch('/api/tasks', {
      headers: {
        Authorization: `Bearer ${this.token}`
      }
    });
    return response.json();
  }
}
```

## Development Commands

### Frontend Development
```bash
cd frontend
npm run dev        # Start development server
npm run build      # Build for production
npm run type-check # TypeScript type checking
```

### Backend Development
```bash
cd backend
uvicorn main:app --reload    # Start development server
alembic upgrade head         # Apply migrations
pytest                      # Run tests
```

### Database Operations
```bash
alembic revision --autogenerate -m "Add tasks table"
alembic upgrade head
alembic downgrade -1
```

## Error Handling Patterns

### Backend Errors
```python
from fastapi import HTTPException, status

# 404 Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Task not found"
)

# 401 Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication token"
)

# 422 Validation Error
raise HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Title cannot be empty"
)
```

### Frontend Error Handling
```typescript
// Error boundary for components
export function TaskManager({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary
      fallback={<div>Something went wrong</div>}
    >
      {children}
    </ErrorBoundary>
  );
}

// API error handling
async function handleApiCall<T>(apiCall: () => Promise<T>) {
  try {
    return await apiCall();
  } catch (error) {
    if (error instanceof Error) {
      toast.error(error.message);
    }
    throw error;
  }
}
```

## Migration from Phase I

### Data Migration
```python
# scripts/migrate_from_console.py
def migrate_console_tasks(console_data):
    """Migrate Phase I tasks to Phase II database."""
    user_id = "console_user"

    for task_data in console_data:
        task = Task(
            user_id=user_id,
            title=task_data['title'],
            description=task_data.get('description', ''),
            completed=task_data.get('completed', False)
        )
        session.add(task)

    session.commit()
```

### Feature Mapping
| Phase I | Phase II |
|---------|----------|
| `todo add` | POST /api/tasks |
| `todo list` | GET /api/tasks |
| `todo update` | PUT /api/tasks/{id} |
| `todo delete` | DELETE /api/tasks/{id} |
| `todo complete` | PATCH /api/tasks/{id}/complete |

## Success Criteria

### Functional Requirements
- All 5 basic features working in web interface
- User authentication and authorization
- Data persistence in Neon DB
- Responsive design for mobile/desktop
- Real-time updates (optional)

### Technical Requirements
- TypeScript throughout (no any types)
- 100% API test coverage
- Proper error handling
- Security best practices
- Production-ready deployment configuration

### Performance Requirements
- API response time < 200ms
- Page load time < 2 seconds
- Support for 1000+ concurrent users
- Database query optimization

## Integration Points

### To Phase III (AI Chatbot)
- API endpoints become MCP tools
- Task model extends with conversation linking
- JWT authentication shared with chat endpoint
- Database schema extends for chat history

### From Specifications
- speckit.specify: Full-stack feature requirements
- speckit.plan: API and UI architecture
- speckit.tasks: Implementation breakdown by feature