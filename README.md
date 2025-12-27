# Evolution of TODO - AI-Powered Task Management

A modern, full-stack web application showcasing the evolution from a simple CLI todo list to a feature-rich AI-powered task management system with event-driven microservices architecture.

[![Backend CI/CD](https://github.com/YOUR-ORG/YOUR-REPO/actions/workflows/backend-deploy.yml/badge.svg)](https://github.com/YOUR-ORG/YOUR-REPO/actions/workflows/backend-deploy.yml)
[![Email Worker CI/CD](https://github.com/YOUR-ORG/YOUR-REPO/actions/workflows/notifications-deploy.yml/badge.svg)](https://github.com/YOUR-ORG/YOUR-REPO/actions/workflows/notifications-deploy.yml)

> **Current Status**: Phase V - Event-Driven Microservices Architecture ✅
>
> **Live Application**: [Frontend](https://hackathon2.testservers.online) | [Backend API](https://api.testservers.online/docs)

## Project Evolution

This project demonstrates the complete evolution of a software application through 5 phases:

| Phase | Description | Status | Tech Stack |
|-------|-------------|--------|------------|
| **Phase I** | Python Console App | ✅ Complete | Python 3.13+, Rich CLI |
| **Phase II** | Full-Stack Web App | ✅ Complete | Next.js 16+, FastAPI, Neon DB |
| **Phase III** | AI Chatbot Integration | ✅ Complete | OpenAI ChatKit, MCP Tools, Groq API |
| **Phase IV** | Kubernetes Deployment | ✅ Complete | Docker, Minikube, Helm Charts |
| **Phase V** | Cloud Microservices | ✅ Complete | Dapr, Kafka, DigitalOcean K8s |

## Features

### Core Task Management
- 🔐 JWT-based user authentication with Better Auth
- 📝 Full CRUD operations for tasks
- 🔍 Real-time search and filtering
- ⚡ Optimistic updates for instant feedback
- 📱 Responsive design (mobile-first)

### AI-Powered Assistant (Phase III)
- 🤖 **AI Chat Interface** - Conversational task management via OpenAI ChatKit
- 🛠️ **MCP Tools** - AI can perform actions:
  - Add, list, complete, update, and delete tasks
- 💬 **Conversation History** - Persistent chat with database-backed context
- 🧠 **Stateless Agent** - Scalable architecture
- 🎨 **Dashboard Widget** - Floating AI assistant

### Event-Driven Architecture (Phase V)
- ⚡ **Dapr Integration** - Distributed application runtime
- 📨 **Email Notifications** - Task reminder service
- 🔄 **Recurring Tasks** - Auto-scheduling system
- 📊 **Event Publishing** - Kafka-based pub/sub
- 🎯 **Background Jobs** - Scheduled task processing

## Tech Stack

### Frontend
- **Next.js 16+** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** with "Nebula 2025" theme
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
- **Groq API** (llama-3.1-8b-instant) with fallbacks

### Infrastructure (Phase V)
- **DigitalOcean Kubernetes** (DOKS)
- **Dapr** for microservices coordination
- **Kafka/Redpanda** for event streaming
- **Helm** for package management
- **GitHub Actions** for CI/CD

## Production URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | https://hackathon2.testservers.online | Next.js application |
| Backend (Phase V) | https://backend-lac-nu-61.vercel.app | FastAPI with background jobs |
| API Docs | https://api.testservers.online/docs | Swagger UI |
| Email Worker | Running in DigitalOcean K8s | Dapr-enabled microservice |

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.13+
- Docker and Docker Compose (optional)
- Kubernetes (Minikube for local, DOKS for cloud)

### Option 1: Using Vercel (Fastest)

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Kubernetes (Phase V)

```bash
# Start Minikube
minikube start

# Install Dapr
dapr init -k

# Deploy with Helm
helm upgrade --install todo-backend ./helm/backend --namespace production --create-namespace
helm upgrade --install email-worker ./helm/email-worker --namespace production
```

## Project Structure

```
├── frontend/              # Next.js 16+ application
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   └── types/            # TypeScript types
├── backend/              # FastAPI application
│   ├── app/              # Application modules
│   │   ├── ai/           # AI agent and MCP tools
│   │   ├── api/          # API endpoints
│   │   ├── services/     # Business logic
│   │   └── models/       # SQLModel database models
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── services/             # Phase V microservices
│   └── email-worker/     # Email notification service
├── helm/                 # Kubernetes Helm charts
│   ├── backend/
│   └── email-worker/
├── k8s/                  # Kubernetes manifests
├── specs/                # Feature specifications
│   ├── 001-todo-crud/
│   ├── 002-phase2-webapp/
│   ├── 003-ai-chatbot/
│   ├── 004-kubernetes/
│   └── 005-cloud-deployment/
├── tests/                # Shared test files
└── docs/                 # Additional documentation
```

## API Documentation

### Authentication
All endpoints require JWT authentication:
```
Authorization: Bearer <jwt_token>
```

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

#### Tasks
- `GET /api/tasks` - List tasks (filter/sort supported)
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle completion

#### AI Chat (Phase III)
- `GET /api/conversations` - List conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations/{id}/messages` - Get history
- `POST /api/chat` - Send message to AI
- `DELETE /api/conversations/{id}` - Delete conversation

#### Background Jobs (Phase V)
- `POST /background/check-due-tasks` - Check for due tasks
- `POST /background/process-recurring-tasks` - Process recurring tasks
- `POST /background/reset-notified-flags` - Reset notification flags

### MCP Tools

| Tool | Description |
|------|-------------|
| `get_tasks` | List user tasks |
| `create_task` | Create new task |
| `update_task` | Update task details |
| `complete_task` | Mark task complete |
| `delete_task` | Delete a task |

## AI Configuration

**Primary Provider**: Groq API (llama-3.1-8b-instant)
- Free tier: 14,400 requests/day
- Fallback chain: Groq → Gemini → OpenAI → Grok

**Environment Variables**:
```bash
GROQ_API_KEY=gsk_...        # Primary
GEMINI_API_KEY=...          # Fallback 1
OPENAI_API_KEY=...          # Fallback 2
```

## Email Configuration (Phase V)

**Email Worker** handles notifications via Dapr events:

**Topics**:
- `task-due-soon` - Triggered when task due date approaches
- `recurring-task-due` - Triggered for recurring task instances

**SMTP Settings** (Gmail):
- Server: smtp.gmail.com:587
- Username: n00bi2761@gmail.com
- Verified via local Docker test ✅

**Note**: DigitalOcean K8s blocks outbound SMTP. Use email API service (SendGrid, Mailgun, Resend) for production emails.

## Deployment

### Vercel Deployment (Frontend + Backend)

```bash
# Frontend
cd frontend
vercel --prod

# Backend
cd backend
vercel --prod
```

### Kubernetes Deployment (Phase V)

**DigitalOcean**:
```bash
# Configure kubectl for DOKS
doctl kubernetes cluster kubeconfig save <cluster-id>

# Deploy
helm upgrade --install todo-backend ./helm/backend --namespace production --create-namespace
helm upgrade --install email-worker ./helm/email-worker --namespace production
```

**Minikube (Local)**:
```bash
minikube start
eval $(minikube docker-env)
docker build -t todo-backend:latest backend/
kubectl apply -f k8s/
```

## Development Workflow

This project follows **Spec-Driven Development (SDD)**:

1. **Specify** - Define requirements in `specs/`
2. **Plan** - Architecture decisions in plan.md
3. **Tasks** - Atomic tasks in tasks.md
4. **Implement** - Code following specifications

See `specs/005-cloud-deployment/spec.md` for Phase V details.

## Testing

```bash
# Backend tests
cd backend
pytest

# E2E tests
pytest tests/test_phase5_e2e.py

# Email worker test (local)
docker run -p 8003:8003 \
  -e MAIL_USERNAME="your@email.com" \
  -e MAIL_PASSWORD="app-password" \
  registry.digitalocean.com/todo-chatbot-reg/todo-backend:email-worker-v2
```

## CI/CD Pipeline

**GitHub Actions** (`.github/workflows/`):
- `backend-deploy.yml` - Automated backend deployment
- `notifications-deploy.yml` - Email worker deployment

**Triggers**:
- Push to `main` branch
- Pull request to `main`
- Manual workflow dispatch

## Monitoring

**Kubernetes**:
```bash
# Check pod status
kubectl get pods -n production

# View logs
kubectl logs -n production -l app=email-worker -f

# Port forward for local testing
kubectl port-forward -n production deployment/email-worker 8003:8003
```

## Contributing

1. Create feature branch from `main`
2. Follow spec-driven development workflow
3. Update specifications before implementing
4. Include tests for new features
5. Submit pull request

## License

MIT License - see LICENSE file for details.

---

**Evolution of TODO - PIAIC Hackathon II**
**Phase V Complete: Event-Driven Microservices Architecture** 🚀
