# Project Setup - Evolution of TODO Edition

This guide documents the actual project setup patterns used in the Evolution of TODO project.

## Project Structure

```
Hackathon_2/
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings (Pydantic Settings)
│   │   ├── database.py          # Database connection
│   │   ├── models/              # SQLModel models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── api/                 # API routers
│   │   │   ├── deps.py          # Dependencies (get_current_user)
│   │   │   ├── tasks.py         # Task endpoints
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   ├── chat.py          # Chat endpoints (Phase III)
│   │   │   └── email.py         # Email endpoints (Bonus)
│   │   ├── crud/                # Database operations
│   │   ├── services/            # Business logic
│   │   │   ├── event_publisher.py
│   │   │   ├── event_logger.py
│   │   │   └── email_notifier.py
│   │   ├── ai/                  # AI agent (Phase III)
│   │   │   ├── agent.py
│   │   │   ├── tools.py
│   │   │   └── conversation_manager.py
│   │   └── utils/               # Utilities
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Test files
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Container image
│   └── .env                     # Environment variables
│
├── frontend/                     # Next.js frontend
│   ├── app/                     # Next.js App Router
│   │   ├── (auth)/             # Auth route group
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── chat/page.tsx        # AI chat (Phase III)
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Home page
│   ├── components/              # React components
│   │   ├── ui/                  # shadcn/ui components
│   │   └── task/                # Task components
│   ├── lib/                     # Utilities
│   │   ├── api.ts               # API client
│   │   ├── auth.ts              # Auth utilities
│   │   └── types.ts             # TypeScript types
│   ├── hooks/                   # Custom React hooks
│   ├── styles/                  # Global styles
│   ├── public/                  # Static assets
│   │   └── config.json          # Runtime config
│   ├── package.json             # Node dependencies
│   ├── tsconfig.json            # TypeScript config
│   ├── tailwind.config.js       # Tailwind config
│   ├── Dockerfile               # Container image
│   └── .env.local               # Local environment
│
├── k8s/                         # Kubernetes manifests
│   ├── backend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── secrets.yaml
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── ingress.yaml             # Ingress rules
│
├── helm/                        # Helm charts
│   └── todo-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── tests/                       # E2E tests
│   ├── test_chatbot.py
│   └── conftest.py
│
├── specs/                       # Feature specs
│   ├── 001-basic-todo-crud/
│   ├── 002-user-authentication/
│   └── ...
│
├── services/                    # Microservices (Phase V)
│   └── email-worker/
│       ├── app/
│       │   └── main.py
│       └── requirements.txt
│
├── docker-compose.yml           # Local development
├── CLAUDE.md                    # Project instructions
└── README.md                    # Project documentation
```

## Backend Setup (Python 3.13+)

### 1. Initialize Project with UV

```bash
# Install UV
pip install uv

# Create project
uv init --name todo-backend

# Add dependencies
uv add fastapi uvicorn[standard] sqlmodel sqlalchemy asyncpg
uv add pydantic pydantic-settings
uv add python-jose[cryptography] passlib[bcrypt]
uv add alembic
uv add pytest pytest-asyncio httpx
uv add python-multipart email-validator

# Add dev dependencies
uv add --dev ruff mypy pytest-cov

# Install all
uv sync
```

### 2. Project Configuration

```bash
# Create directories
mkdir -p app/{models,schemas,api,crud,services,utils}
mkdir -p tests
mkdir -p alembic/versions

# Create __init__.py files
touch app/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/api/__init__.py
touch app/crud/__init__.py
```

### 3. Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/todo

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI (Phase III)
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIz...
OPENAI_API_KEY=sk-...

# Email (Bonus)
EMAIL_FROM_NAME=Todo App
GMAIL_CREDENTIALS='{"token": "...", "refresh_token": "..."}'

# CORS
CORS_ORIGINS=http://localhost:3000

# App
APP_NAME=Todo CRUD API
DEBUG=false
```

### 4. Alembic Setup

```bash
# Initialize Alembic
alembic init alembic

# Edit alembic.ini to set database URL
# sqlalchemy.url = postgresql+asyncpg://...

# Create first migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Run Development Server

```bash
# With UV
uv run uvicorn app.main:app --reload --port 8000

# Or with pip
uvicorn app.main:app --reload --port 8000
```

## Frontend Setup (Next.js 16+)

### 1. Initialize Next.js Project

```bash
# Create Next.js app
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir

cd frontend

# Install dependencies
npm install axios sonner lucide-react
npm install @radix-ui/react-dialog
npm install @radix-ui/react-select
npm install @radix-ui/react-switch
npm install @radix-ui/react-label
npm install class-variance-authority clsx tailwind-merge

# Install shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add input
npx shadcn-ui@latest add label
npx shadcn-ui@latest add select
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add switch
npx shadcn-ui@latest add toast
```

### 2. Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Runtime Config (public/config.json)

```json
{
  "NEXT_PUBLIC_API_URL": "http://localhost:8000"
}
```

### 4. Run Development Server

```bash
npm run dev
```

## Docker Setup

### 1. Build Images

```bash
# Build backend
docker build -t todo-backend ./backend

# Build frontend
docker build -t todo-frontend ./frontend
```

### 2. Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Kubernetes Setup

### 1. Create Secrets

```bash
kubectl create secret generic todo-backend-secrets \
  --from-literal=database-url='postgresql+asyncpg://...' \
  --from-literal=jwt-secret='your-secret-key' \
  --from-literal=groq-api-key='gsk_...'
```

### 2. Deploy to Kubernetes

```bash
# Apply backend
kubectl apply -f k8s/backend/

# Apply frontend
kubectl apply -f k8s/frontend/

# Apply ingress
kubectl apply -f k8s/ingress.yaml
```

### 3. Check Status

```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

## Helm Setup

```bash
# Install chart
helm install todo-app ./helm/todo-app

# Upgrade chart
helm upgrade todo-app ./helm/todo-app

# Uninstall chart
helm uninstall todo-app
```

## Initial Development Workflow

1. **Backend First**:
   ```bash
   cd backend
   uv run uvicorn app.main:app --reload
   ```

2. **Frontend Second**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Database**:
   ```bash
   # Run migrations
   cd backend
   alembic upgrade head
   ```

4. **Test**:
   ```bash
   # Backend tests
   pytest

   # Frontend tests
   npm test
   ```

## Production Deployment

### Vercel (Frontend)

```bash
cd frontend
npm run build
npx vercel
```

### Railway/Render (Backend)

```bash
# Connect GitHub repo
# Auto-deploy on push to main
# Set environment variables in dashboard
```

### DigitalOcean Kubernetes (Full Stack)

```bash
# Build and push images
docker build -t registry.digitalocean.com/todo-chatbot-reg/todo-backend:latest ./backend
docker push registry.digitalocean.com/todo-chatbot-reg/todo-backend:latest

# Deploy with Helm
helm upgrade todo-app ./helm/todo-app
```

## Key Configuration Files

### pyproject.toml (Backend)

```toml
[project]
name = "todo-backend"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlmodel>=0.0.14",
    "pydantic>=2.0",
    "alembic>=1.12.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]

[tool.ruff]
line-length = 100

[tool.mypy]
python_version = "3.13"
```

### package.json (Frontend)

```json
{
  "name": "todo-frontend",
  "version": "0.1.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "16.0.0",
    "react": "^18.3.0",
    "axios": "^1.6.0",
    "sonner": "^1.2.0",
    "lucide-react": "^0.300.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "@types/node": "^20.10.0"
  }
}
```

## Quick Start Commands

```bash
# Clone and setup
git clone <repo>
cd Hackathon_2

# Backend setup
cd backend
uv sync
alembic upgrade head
uv run uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev

# Or use Docker Compose
docker-compose up -d
```
