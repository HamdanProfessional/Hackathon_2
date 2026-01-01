# Evolution of TODO - AI-Powered Task Management

A modern, full-stack web application showcasing the complete evolution from a simple CLI todo list to a feature-rich AI-powered task management system with event-driven microservices architecture.

> **Current Status**: ✅ **ALL PHASES COMPLETE** - Including Bonus Features
>
> **Live Application**: [hackathon2.testservers.online](https://hackathon2.testservers.online)
>
> **Final Score**: **1,700 / 1,600** points (All core + all bonus features)

---

## Project Evolution

This project demonstrates the complete evolution of a software application through 5 phases with bonus features:

| Phase | Description | Points | Status |
|-------|-------------|--------|--------|
| **Phase I** | Python Console App | 100 | ✅ Complete |
| **Phase II** | Full-Stack Web App | 150 | ✅ Complete |
| **Phase III** | AI Chatbot Integration | 200 | ✅ Complete |
| **Phase IV** | Kubernetes Deployment | 250 | ✅ Complete |
| **Phase V** | Cloud Microservices | 300 | ✅ Complete |
| **Bonus** | Reusable Intelligence (44 Agent Skills) | +200 | ✅ Complete |
| **Bonus** | Cloud-Native Blueprints | +200 | ✅ Complete |
| **Bonus** | Multi-language (Urdu) | +100 | ✅ Complete |
| **Bonus** | Voice Commands | +200 | ✅ Complete |
| **Total** | | **1,700** | **100%** |

---

## Features

### Core Task Management
- 🔐 JWT-based user authentication with Better Auth
- 📝 Full CRUD operations for tasks
- 🔍 Real-time search and filtering
- ⚡ Optimistic updates for instant feedback
- 📱 Responsive design (mobile-first)
- 📧 Email notifications for all task events (created/completed/updated/deleted)

### AI-Powered Assistant (Phase III)
- 🤖 **AI Chat Interface** - Conversational task management via OpenAI ChatKit
- 🛠️ **MCP Tools** - AI can perform actions:
  - Add, list, complete, update, and delete tasks
- 💬 **Conversation History** - Persistent chat with database-backed context
- 🧠 **Stateless Agent** - Scalable architecture
- 🎨 **Dashboard Widget** - Floating AI assistant

### Event-Driven Architecture (Phase V)
- ⚡ **Direct Email Notifications** - Task CRUD events trigger emails
- 📨 **Custom Email API** - Bearer token authentication
- 🔄 **Async Processing** - FastAPI BackgroundTasks
- 📊 **Event Logging** - TaskEventLog for audit trail

### Bonus Features

#### 🌍 Multi-language Support (Urdu)
- 📝 English/Urdu bilingual interface
- 🔄 RTL (Right-to-Left) layout for Urdu
- 🎨 Noto Nastaliq Urdu typography
- 🔤 Language switcher component

#### 🎤 Voice Commands
- 🎙️ Web Speech API integration
- 🗣️ Voice input for task creation
- 🎯 Speech-to-text for all text inputs

#### 🧠 Reusable Intelligence (44 Agent Skills)
- Complete Spec-Kit Plus workflow
- Architecture planning agents
- Code quality analyzers
- Test generation specialists
- Deployment automation
- 21 skills + 23 agents for comprehensive development support

#### ☁️ Cloud-Native Blueprints
- Docker containerization
- Kubernetes manifests
- Helm charts
- Dapr integration
- CI/CD workflows

---

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

### Infrastructure
- **DigitalOcean Kubernetes** (DOKS) for production
- **Minikube** for local development
- **Dapr** for microservices coordination
- **Kafka/Redpanda** for event streaming (attempted, bypassed with direct API)
- **Helm** for package management
- **Docker** for containerization

### Email Service
- **Custom Email API**: `https://email.testservers.online/api/send`
- **Authentication**: Bearer token
- **Features**: HTML templates, status badges, responsive design

---

## Production URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | https://hackathon2.testservers.online | Next.js application |
| Backend | https://api.testservers.online | FastAPI with AI & email |
| API Docs | https://api.testservers.online/docs | Swagger UI |

---

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.13+
- Docker and Docker Compose (optional)
- Kubernetes (Minikube for local, DOKS for cloud)

### Local Development

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Open http://localhost:8000/docs
```

---

## Project Structure

```
├── frontend/              # Next.js 16+ application
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   └── types/            # TypeScript types
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── ai/           # AI agent and MCP tools
│   │   ├── api/          # API endpoints
│   │   ├── utils/        # Email notification utility
│   │   ├── services/     # Business logic
│   │   └── models/       # SQLModel database models
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── services/             # Microservices
│   └── email-worker/     # Email notification service (Phase V)
├── helm/                 # Kubernetes Helm charts
├── k8s/                  # Kubernetes manifests
├── specs/                # Feature specifications
│   ├── 001-todo-crud/    # Phase I
│   ├── 002-phase2-webapp/ # Phase II
│   ├── 003-ai-chatbot/   # Phase III
│   ├── 004-kubernetes/   # Phase IV
│   ├── 005-cloud-deployment/ # Phase V
│   └── 006-fix-email/    # Email notification fix
├── tests/                # Shared test files
└── .claude/              # Claude Code skills and configuration
```

---

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
- `POST /api/tasks` - Create task → **Sends email notification**
- `PUT /api/tasks/{id}` - Update task → **Sends email notification**
- `DELETE /api/tasks/{id}` - Delete task → **Sends email notification**
- `PATCH /api/tasks/{id}/complete` - Toggle completion → **Sends email when completed**

#### AI Chat (Phase III)
- `GET /api/conversations` - List conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations/{id}/messages` - Get history
- `POST /api/chat` - Send message to AI
- `DELETE /api/conversations/{id}` - Delete conversation

---

## Email Notifications

### Event Types
Email notifications are sent for:
1. **Task Created** - Confirmation when task is created
2. **Task Completed** - Congratulatory email when task is marked complete
3. **Task Updated** - Notification when task details change
4. **Task Deleted** - Confirmation when task is deleted

### Email Template Features
- HTML format with responsive design
- Color-coded status badges (green, yellow, blue, red)
- Purple gradient header
- Task details included
- Link to application

### Configuration
- **API**: `https://email.testservers.online/api/send`
- **Method**: HTTP POST with Bearer token authentication
- **Implementation**: FastAPI BackgroundTasks (non-blocking)
- **Error Handling**: Failures logged but don't block task operations

---

## AI Configuration

**Primary Provider**: Groq API (llama-3.1-8b-instant)
- Free tier: 14,400 requests/day
- Fast inference (sub-second response times)

**Fallback Chain**: Groq → Gemini → OpenAI → Grok

**Environment Variables**:
```bash
GROQ_API_KEY=gsk_...        # Primary
GEMINI_API_KEY=...          # Fallback 1
OPENAI_API_KEY=...          # Fallback 2
```

---

## MCP Tools

The AI assistant can perform the following actions:

| Tool | Description |
|------|-------------|
| `get_tasks` | List user tasks with filters |
| `create_task` | Create new task |
| `update_task` | Update task details |
| `complete_task` | Mark task complete |
| `delete_task` | Delete a task |

---

## Deployment

### Production (DigitalOcean)

**Backend**:
```bash
# Build and push Docker image
docker build -t todo-backend:latest backend/
docker tag todo-backend:latest registry.digitalocean.com/todo-chatbot-reg/todo-backend:latest
docker push registry.digitalocean.com/todo-chatbot-reg/todo-backend:latest

# Deploy to Kubernetes
kubectl set image deployment/todo-backend todo-backend=registry.digitalocean.com/todo-chatbot-reg/todo-backend:latest -n default
kubectl rollout status deployment/todo-backend -n default
```

**Frontend (Vercel)**:
```bash
cd frontend
vercel --prod
```

### Local Development (Minikube)

```bash
# Start Minikube
minikube start

# Build and deploy
eval $(minikube docker-env)
docker build -t todo-backend:latest backend/
kubectl apply -f k8s/
```

---

## Development Workflow

This project follows **Spec-Kit Plus (Spec-Driven Development)**:

1. **Specify** (`/sp.specify`) - Create feature specification with user stories
2. **Plan** (`/sp.plan`) - Architecture decisions and technical design
3. **Tasks** (`/sp.tasks`) - Generate actionable, dependency-ordered tasks
4. **Implement** (`/sp.implement`) - Execute implementation following specs

See `specs/006-fix-email/` for a complete example.

---

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### E2E Tests
```bash
pytest tests/test_e2e.py -v
```

### Email Testing
```bash
# Get JWT token
TOKEN=$(curl -X POST "https://api.testservers.online/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' | jq -r '.access_token')

# Create task (triggers email)
curl -X POST "https://api.testservers.online/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Email","description":"Testing notifications"}'
```

---

## Monitoring

### Kubernetes Logs
```bash
# Backend logs
kubectl logs -n default deployment/todo-backend -f

# Check for email sending
kubectl logs -n default deployment/todo-backend | grep EMAIL
```

### Expected Log Output
```
[EMAIL] Scheduling background task for email notification
[EMAIL] Background task scheduled
[EMAIL] Sending created email to user@example.com for task 123
[EMAIL] Successfully sent created email to user@example.com
```

---

## Contributing

1. Create feature branch from `main`
2. Follow Spec-Kit Plus workflow (`/sp.specify`, `/sp.plan`, `/sp.tasks`, `/sp.implement`)
3. Update specifications before implementing
4. Include tests for new features
5. Submit pull request

---

## License

MIT License - see LICENSE file for details.

---

**Evolution of TODO - PIAIC Hackathon II**

**Final Score**: 1,700 / 1,600 points 🏆

**Status**: All phases complete, all bonus features implemented, production deployed 🚀
