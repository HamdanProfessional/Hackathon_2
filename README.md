# Evolution of TODO - AI-Powered Task Management

A modern, full-stack web application showcasing the evolution from a simple CLI todo list to a feature-rich AI-powered task management system with the "Nebula 2025" design aesthetic.

[![Backend CI/CD](https://github.com/YOUR-ORG/YOUR-REPO/actions/workflows/backend-deploy.yml/badge.svg)](https://github.com/YOUR-ORG/YOUR-REPO/actions/workflows/backend-deploy.yml)
[![Notifications CI/CD](https://github.com/YOUR-ORG/YOUR-REPO/actions/workflows/notifications-deploy.yml/badge.svg)](https://github.com/YOUR-ORG/YOUR-REPO/actions/workflows/notifications-deploy.yml)

> **Current Status**: Phase V - DigitalOcean Cloud Deployment ✅
>
> **Live Application**: [Frontend](https://hackathon2.testservers.online) | [Backend API](https://api.testservers.online/docs)

## Features

### Core Task Management
- 🔐 JWT-based user authentication
- 📝 Full CRUD operations for tasks
- 🔍 Real-time search and filtering
- ⚡ Optimistic updates for instant feedback
- 📱 Responsive design (mobile-first)

### AI-Powered Assistant (Phase III)
- 🤖 **AI Chat Interface** - Conversational task management
- 🛠️ **MCP Tools** - AI can perform actions on your behalf:
  - Add tasks
  - List and filter tasks
  - Complete tasks
  - Update task details
  - Delete tasks
- 💬 **Conversation History** - Persistent chat history
- 🗑️ **Delete Conversations** - Manage your chat history
- 🧠 **Stateless Agent** - Scalable architecture with database-backed context
- 🎨 **Dashboard Widget** - Floating AI assistant on dashboard

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
- **Groq API** for AI (llama-3.1-8b-instant model)

## Production URLs

| Service | URL | Docs |
|---------|-----|------|
| Frontend | https://hackathon2.testservers.online | - |
| Backend | https://api.testservers.online | /docs |
| API Docs | https://api.testservers.online/docs | Swagger |

### Alternative Deployment (Vercel)
| Service | URL |
|---------|-----|
| Frontend | https://frontend-l0e30jmlq-hamdanprofessionals-projects.vercel.app |
| Backend | https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app |

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hackathon-2
```

### 2. Environment Configuration

**Backend (.env)**:
```bash
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret-key
GROQ_API_KEY=your-groq-key  # Optional - has fallbacks
```

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC BETTER_AUTH_URL=http://localhost:3000
```

### 3. Start Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
├── frontend/          # Next.js application
│   ├── app/          # App Router pages
│   ├── components/   # React components
│   ├── lib/          # Utilities and API client
│   └── types/        # TypeScript types
├── backend/           # FastAPI application
│   ├── app/          # Application modules
│   │   ├── ai/       # AI agent and MCP tools
│   │   ├── api/      # API endpoints
│   │   ├── config.py # Configuration
│   │   └── models/   # SQLModel database models
│   ├── alembic/      # Database migrations
│   └── requirements.txt
├── tests/            # Shared test files
├── specs/            # Feature specifications
├── .claude/          # Claude AI configuration
└── README.md
```

## API Documentation

### Authentication
All API endpoints (except register and login) require JWT authentication:
```
Authorization: Bearer <jwt_token>
```

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user

#### Tasks
- `GET /api/tasks` - Get all tasks (with filtering/sorting)
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{task_id}` - Get a specific task
- `PUT /api/tasks/{task_id}` - Update a task
- `PATCH /api/tasks/{task_id}/complete` - Toggle task completion
- `DELETE /api/tasks/{task_id}` - Delete a task

#### AI Chat (Phase III)
- `GET /api/conversations` - List all conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations/{id}/messages` - Get conversation history
- `POST /api/chat` - Send message to AI assistant
- `DELETE /api/conversations/{id}` - Delete conversation

### MCP Tools Available

The AI assistant can perform these actions on your behalf:

| Tool | Description |
|------|-------------|
| `add_task` | Create a new task |
| `list_tasks` | List all user tasks |
| `complete_task` | Mark task as complete |
| `update_task` | Update task details |
| `delete_task` | Delete a task |

## AI Configuration

The application uses **Groq API** as the primary AI provider:

- **Model**: llama-3.1-8b-instant
- **Free Tier**: 14,400 requests/day
- **Fallback Chain**: Groq → Gemini → OpenAI → Grok

To configure your own AI provider, set environment variables in `backend/.env`:
```bash
GROQ_API_KEY=gsk_...        # Primary (recommended)
GEMINI_API_KEY=...          # Fallback 1
OPENAI_API_KEY=...          # Fallback 2
```

## The "Nebula 2025" Design System

A dark-mode first aesthetic featuring:
- **Background**: Deep space Zinc-950 (#09090b)
- **Accent**: Electric Violet to Fuchsia gradients
- **Typography**: Clean Inter/Geist Sans fonts
- **Effects**: Glassmorphism with backdrop blur
- **Animations**: Smooth transitions with Framer Motion

## Development Workflow

This project follows **Spec-Driven Development (SDD)**:

1. **Specify** - Define feature requirements in `specs/`
2. **Plan** - Architecture and design decisions
3. **Tasks** - Break down into atomic tasks
4. **Implement** - Code following the specifications

See `specs/003-ai-chatbot/spec.md` for Phase III implementation details.

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

### Phase V - DigitalOcean Cloud (Kubernetes + Dapr)

The application is deployed to DigitalOcean Kubernetes (DOKS) with event-driven architecture using Dapr:

**CI/CD Pipeline**:
- Backend: Automated deployment via GitHub Actions (`.github/workflows/backend-deploy.yml`)
- Notifications: Automated deployment via GitHub Actions (`.github/workflows/notifications-deploy.yml`)
- Frontend: Vercel auto-deployment

**Infrastructure**:
- **Container Registry**: `registry.digitalocean.com/todo-chatbot-reg`
- **Kubernetes Cluster**: `do-fra1-hackathon2h1` (Frankfurt region)
- **Namespace**: `production`
- **Helm Charts**: `helm/backend`, `helm/notifications`
- **Event Bus**: Dapr + Kafka/Redpanda (for pub/sub)

**Manual Deployment**:
```bash
# Build and push image
docker build -t registry.digitalocean.com/todo-chatbot-reg/todo-backend:latest backend/
docker push registry.digitalocean.com/todo-chatbot-reg/todo-backend:latest

# Deploy with Helm
helm upgrade --install todo-backend helm/backend \
  --namespace production \
  --set image.tag=latest \
  --wait
```

See [docs/GITHUB_ACTIONS_SETUP.md](docs/GITHUB_ACTIONS_SETUP.md) for complete CI/CD configuration.

### Phase III - Vercel Deployment

Frontend is deployed on Vercel with auto-deployment:

```bash
# Deploy frontend
cd frontend
vercel --prod
```

Backend is also available on Vercel for API access.

## Contributing

1. Create a feature branch from `main`
2. Follow the spec-driven development workflow
3. Update specifications before implementing
4. Include tests for new features
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

**Phase III of Evolution of TODO - PIAIC Hackathon II**
