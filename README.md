# The Evolution of Todo - Phase II (Completed)

A modern, full-stack web application showcasing the evolution from a simple CLI todo list to a feature-rich task management system with authentication, persistence, and the "Nebula 2025" design aesthetic.

> **Status**: Phase II is complete. See [PHASE_2_REPORT.md](./PHASE_2_REPORT.md) for detailed completion summary.
>
> **Current Phase**: [Phase III - AI-Powered Chatbot](./specs/003-ai-chatbot/) - In Progress

## Tech Stack

### Frontend
- **Next.js 16+** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** with custom "Nebula 2025" theme
- **Framer Motion** for animations
- **Better Auth** for authentication
- **Axios** for API communication

### Backend
- **FastAPI** for REST API
- **Python 3.13+** with type hints
- **SQLModel** for database ORM
- **Neon PostgreSQL** for serverless database
- **JWT** for stateless authentication
- **Alembic** for database migrations

## Features

- 🔐 User authentication with JWT
- 📝 Full CRUD operations for tasks
- 🎨 "Nebula 2025" dark mode UI with glassmorphism
- 📱 Responsive design (mobile-first)
- 🔍 Real-time search and filtering
- ⚡ Optimistic updates for instant feedback
- 🐳 Docker support for local development

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hackathon-2
```

### 2. Environment Configuration

Copy the environment template and fill in your values:

```bash
cp .env.example .env
```

Required environment variables:

- `DATABASE_URL` - Get from your Neon console (Connection string)
- `JWT_SECRET` - Generate a secure random string: `openssl rand -base64 32`
- `BETTER_AUTH_SECRET` - Use the same value as JWT_SECRET
- `BETTER_AUTH_URL` - Your app URL (http://localhost:3000 for development)
- `NEXT_PUBLIC_API_URL` - Backend API URL (http://localhost:8000 for development)

### 3. Start Development

Using Docker Compose (recommended):

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Setup (Alternative)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
├── frontend/          # Next.js application
│   ├── app/          # App Router pages
│   ├── components/   # React components
│   ├── lib/          # Utilities and API client
│   └── types/        # TypeScript types
├── backend/           # FastAPI application
│   ├── app/          # Application modules
│   ├── alembic/      # Database migrations
│   └── tests/        # Test files
├── specs/            # Feature specifications
├── history/          # Prompt history and ADRs
├── docker-compose.yml
└── README.md
```

## Development Workflow

This project follows **Spec-Driven Development (SDD)**:

1. **Specify** - Define feature requirements
2. **Plan** - Architecture and design decisions
3. **Tasks** - Break down into atomic tasks
4. **Implement** - Code following the specifications

All documentation is kept in the `specs/` directory with full traceability from user stories to implementation.

## The "Nebula 2025" Design System

A dark-mode first aesthetic featuring:
- **Background**: Deep space Zinc-950 (#09090b)
- **Accent**: Electric Violet to Fuchsia gradients
- **Typography**: Clean Inter/Geist Sans fonts
- **Effects**: Glassmorphism with backdrop blur
- **Animations**: Smooth transitions with Framer Motion

## API Documentation

### Base URL
- Development: `http://localhost:8000`
- Production: `https://your-app-domain.com`

### Authentication
All API endpoints (except register and login) require JWT authentication in the header:
```
Authorization: Bearer <jwt_token>
```

### API Endpoints

#### Authentication
- `POST /api/auth/register` - Register a new user
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
  Response: `201 Created` with JWT token

- `POST /api/auth/login` - Login user
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
  Response: `200 OK` with JWT token

#### Tasks
- `GET /api/tasks` - Get all tasks for authenticated user
  - Query Parameters:
    - `search`: Filter by title or description
    - `status`: Filter by status ("completed" or "pending")
    - `priority`: Filter by priority ("low", "medium", or "high")
    - `sort_by`: Sort field ("created_at", "due_date", "priority", "title")
    - `sort_order`: Sort direction ("asc" or "desc")
    - `limit`: Number of tasks to return (default: 20, max: 100)
    - `offset`: Number of tasks to skip (for pagination)

- `POST /api/tasks` - Create a new task
  ```json
  {
    "title": "Task title",
    "description": "Optional description",
    "priority": "low|medium|high",
    "due_date": "2024-12-31"
  }
  ```
  Response: `201 Created`

- `GET /api/tasks/{task_id}` - Get a specific task
  Response: `200 OK`

- `PUT /api/tasks/{task_id}` - Update a task
  ```json
  {
    "title": "Updated title",
    "description": "Updated description",
    "priority": "low|medium|high",
    "due_date": "2024-12-31"
  }
  ```
  Response: `200 OK`

- `PATCH /api/tasks/{task_id}/complete` - Toggle task completion
  Response: `200 OK`

- `DELETE /api/tasks/{task_id}` - Delete a task
  Response: `204 No Content`

#### User Management
- `GET /api/users/me` - Get current user profile
  Response: `200 OK` with user data and preferences

- `PATCH /api/users/me/preferences` - Update user preferences
  ```json
  {
    "preferences": {
      "showCompleted": true,
      "compactView": false
    }
  }
  ```
  Response: `200 OK`

- `GET /api/users/me/export` - Export all user data
  Response: JSON file download with all tasks and preferences

#### Chat (Phase III)
- `POST /api/chat` - Send message to AI assistant
  ```json
  {
    "message": "Help me organize my tasks"
  }
  ```
  Response: `200 OK` with AI response

### Response Format
All responses follow consistent format:
- Success: Returns data with appropriate HTTP status
- Error: Returns JSON with error details
  ```json
  {
    "detail": "Error message description"
  }
  ```

### Rate Limiting
- Authentication endpoints: 5 requests per minute
- Other endpoints: No current limit (may be added for production)

### CORS Configuration
The API supports CORS for these origins in development:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

For interactive API documentation, visit `/docs` when the backend is running.

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Contributing

1. Create a feature branch from `main`
2. Follow the spec-driven development workflow
3. Update specifications before implementing
4. Include tests for new features
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

**Phase II of Evolution of Todo - PIAIC Hackathon II**