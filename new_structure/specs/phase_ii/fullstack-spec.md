# Phase II: Full-Stack Web Application Specification

## Overview
Transform the Phase I console todo application into a modern multi-user web application with persistent storage using Next.js, FastAPI, SQLModel, and Neon Serverless PostgreSQL database.

## Technology Stack

### Frontend
- **Framework**: Next.js 16+ with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI (Python)
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT (issued by Better Auth)
- **Documentation**: Automatic OpenAPI/Swagger

### Development
- **Package Manager**: npm (frontend) / pip (backend)
- **Code Quality**: ESLint, Prettier, Black, mypy
- **Testing**: Jest (frontend) / pytest (backend)
- **Type Safety**: End-to-end TypeScript

## Core Requirements

### Basic Level Features (All Required)
1. **User Authentication**
   - Sign up with email/password
   - Login with existing account
   - JWT token management
   - Protected routes

2. **Task Management CRUD**
   - Create task with title and optional description
   - View all user's tasks
   - Update task title and/or description
   - Delete tasks with confirmation
   - Mark tasks as complete/incomplete

3. **Multi-User Support**
   - Each user sees only their tasks
   - User isolation at database level
   - Secure API endpoints

### User Stories

#### User Authentication
- As a new user, I want to sign up with my email and password
- As a returning user, I want to log in to access my tasks
- As a logged-in user, I want to stay logged in between sessions
- As a user, I want to log out securely

#### Task Management
- As a user, I want to add tasks from a web interface
- As a user, I want to see all my tasks in a clean list
- As a user, I want to edit task details inline or via form
- As a user, I want to delete tasks I no longer need
- As a user, I want to mark tasks as complete with a click
- As a user, I want my tasks to be saved automatically

## Technical Specifications

### Database Schema

#### Users Table (Managed by Better Auth)
```sql
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Tasks Table
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### API Endpoints

#### Authentication (Handled by Better Auth)
- `POST /api/auth/sign-up` - Create new user account
- `POST /api/auth/sign-in` - Authenticate user
- `POST /api/auth/sign-out` - End session
- `GET /api/auth/session` - Get current session info

#### Task Management
```typescript
// Task model
interface Task {
  id: number;
  title: string;           // 1-200 characters
  description?: string;    // Optional, max 1000 characters
  completed: boolean;
  created_at: string;      // ISO 8601 timestamp
  updated_at: string;      // ISO 8601 timestamp
}
```

##### GET /api/tasks
List all tasks for authenticated user.

**Query Parameters:**
- `status`: "all" | "pending" | "completed" (default: "all")
- `sort`: "created" | "title" | "updated" (default: "created")
- `order`: "asc" | "desc" (default: "desc")

**Response:**
```typescript
{
  "tasks": Task[],
  "total": number,
  "completed": number,
  "pending": number
}
```

##### POST /api/tasks
Create a new task.

**Request Body:**
```typescript
{
  "title": string,          // Required, 1-200 chars
  "description?: string     // Optional, max 1000 chars
}
```

**Response:** Created Task object

##### GET /api/tasks/{id}
Get specific task details.

**Response:** Task object

**Errors:**
- 404: Task not found
- 403: Task belongs to different user

##### PUT /api/tasks/{id}
Update a task.

**Request Body:**
```typescript
{
  "title?: string,          // Optional, 1-200 chars
  "description?: string     // Optional, max 1000 chars
}
```

**Response:** Updated Task object

##### DELETE /api/tasks/{id}
Delete a task.

**Response:** 204 No Content

##### PATCH /api/tasks/{id}/complete
Toggle task completion status.

**Response:** Updated Task object

### Frontend Components

#### Page Structure
```
app/
├── (auth)/                  # Auth route group
│   ├── login/              # Login page
│   └── signup/             # Signup page
├── dashboard/              # Main dashboard
│   └── page.tsx           # Task list and management
├── api/                   # API routes
│   └── tasks/             # Task API proxy (if needed)
├── layout.tsx            # Root layout
├── globals.css           # Global styles
└── loading.tsx          # Loading UI
```

#### Component Hierarchy
```typescript
// Main dashboard page
export default function Dashboard() {
  return (
    <DashboardLayout>
      <TaskHeader />
      <TaskForm onAdd={handleAdd} />
      <TaskList
        tasks={tasks}
        onUpdate={handleUpdate}
        onDelete={handleDelete}
        onComplete={handleComplete}
      />
      <TaskStats stats={stats} />
    </DashboardLayout>
  );
}
```

#### UI Components

##### TaskItem
```typescript
interface TaskItemProps {
  task: Task;
  onUpdate: (id: number, updates: Partial<Task>) => void;
  onDelete: (id: number) => void;
  onComplete: (id: number) => void;
}
```

##### TaskForm
```typescript
interface TaskFormProps {
  onSubmit: (task: Omit<Task, 'id' | 'created_at' | 'updated_at'>) => void;
  initialData?: Partial<Task>;
}
```

##### TaskStats
```typescript
interface TaskStatsProps {
  total: number;
  completed: number;
  pending: number;
}
```

### Authentication Flow

#### Better Auth Configuration
```typescript
// auth.ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  database: {
    provider: "postgresql",
    url: process.env.DATABASE_URL,
  },
  emailAndPassword: {
    enabled: true,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
});
```

#### JWT Integration
```typescript
// JWT token issued by Better Auth
{
  "sub": "user_id",
  "email": "user@example.com",
  "name": "User Name",
  "iat": 1234567890,
  "exp": 1234567890
}
```

#### API Middleware
```python
# FastAPI JWT middleware
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = decode_jwt(token.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token")
        return user_id
    except:
        raise HTTPException(401, "Invalid token")
```

### Styling Requirements

#### Tailwind CSS Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
        }
      }
    },
  },
  plugins: [],
}
```

#### Design System
- **Primary Color**: Blue (#3b82f6)
- **Success Color**: Green (#10b981)
- **Error Color**: Red (#ef4444)
- **Warning Color**: Yellow (#f59e0b)
- **Font**: Inter UI (system fonts)
- **Spacing**: 4px base unit
- **Border Radius**: 6px default

### Responsive Design
- **Mobile**: 320px - 640px (single column)
- **Tablet**: 640px - 1024px (two columns)
- **Desktop**: 1024px+ (full layout)

### Error Handling

#### Backend Errors
```typescript
// Standard error response format
interface ErrorResponse {
  error: {
    code: string;          // "TASK_NOT_FOUND"
    message: string;       // "Task with ID 123 not found"
    details?: any;         // Additional error details
  };
}
```

#### Error Codes
- `TASK_NOT_FOUND`: Task does not exist
- `TASK_ACCESS_DENIED`: User cannot access task
- `INVALID_TITLE`: Title validation failed
- `INVALID_DESCRIPTION`: Description validation failed
- `UNAUTHORIZED`: No valid JWT token
- `FORBIDDEN`: Insufficient permissions

### Testing Requirements

#### Backend Tests
```python
# pytest example
def test_create_task(client, auth_headers):
    response = client.post(
        "/api/tasks",
        json={"title": "Test task"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test task"
```

#### Frontend Tests
```typescript
// Jest + React Testing Library
test("should create a new task", async () => {
  render(<Dashboard />);

  const input = screen.getByPlaceholderText("Add a new task");
  const button = screen.getByText("Add Task");

  await userEvent.type(input, "Test task");
  await userEvent.click(button);

  expect(screen.getByText("Test task")).toBeInTheDocument();
});
```

### Performance Requirements
- API response time: < 200ms (95th percentile)
- First Contentful Paint: < 1.5 seconds
- Largest Contentful Paint: < 2.5 seconds
- Time to Interactive: < 3.5 seconds
- Bundle size: < 100KB (gzipped)

### Security Requirements
- All API endpoints require JWT authentication
- HTTPS in production
- SQL injection prevention (SQLModel)
- XSS prevention (React auto-escapes)
- CSRF protection (SameSite cookies)
- Rate limiting on API endpoints

## Acceptance Criteria

### Functional Requirements
1. Users can sign up and log in
2. Logged-in users can manage their tasks
3. Tasks are persisted in database
4. Users see only their own tasks
5. All CRUD operations work correctly

### Non-Functional Requirements
1. Application is responsive on mobile devices
2. API responses are fast and reliable
3. User data is secure and isolated
4. Application handles errors gracefully
5. UI follows consistent design patterns

## Deliverables

### Code Structure
```
todo-fullstack/
├── frontend/              # Next.js app
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
├── backend/               # FastAPI app
│   ├── app/
│   ├── alembic/
│   └── tests/
├── shared/                # Shared types
└── docs/                  # Documentation
```

### Documentation
- API documentation (auto-generated)
- Component documentation
- Deployment guide
- Migration guide from Phase I

### Migration Path for Phase III
- Task model ready for AI chatbot integration
- API endpoints ready for MCP tool conversion
- Authentication shared with chat features
- Database schema ready for conversation tables

## Deployment Requirements

### Frontend (Vercel)
- Automatic deployments from main branch
- Environment variables for API URL
- Custom domain (optional)

### Backend (Render/Heroku)
- Container-based deployment
- Environment variables for database
- Health check endpoint
- SSL certificate

### Database (Neon)
- Serverless PostgreSQL
- Connection pooling
- Automated backups
- Branch for development