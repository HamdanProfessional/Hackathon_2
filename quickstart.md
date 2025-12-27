# QUICKSTART - Evolution of TODO

Get **Evolution of TODO** running in minutes! This guide covers all 5 phases.

## Prerequisites

Choose based on which phase you want to run:

### All Phases
- **Git** - For cloning the repository

### Phase I (Console App)
- **Python 3.13+**
- **UV** (Python package manager)

### Phase II (Web App)
- **Node.js 18+** and **npm**
- **Python 3.13+**
- **Neon Database account** ([neon.tech](https://neon.tech) - Free tier)

### Phase III (AI Chatbot)
- All Phase II prerequisites
- **Groq API key** ([groq.com](https://groq.com) - Free tier: 14,400 requests/day)

### Phase IV (Kubernetes)
- **Docker Desktop** or **Docker**
- **Minikube** (local Kubernetes)
- **kubectl** (Kubernetes CLI)

### Phase V (Cloud Deployment)
- All Phase IV prerequisites
- **DigitalOcean account** ($200 free credit)
- **Helm** (Kubernetes package manager)

---

## Phase I: Console App (5 minutes)

```bash
# Navigate to project
cd hackathon-2

# Run with UV
uv run src/main.py

# Or install with UV and run
uv pip install -e .
python src/main.py
```

**Features:**
- Add, delete, update, list tasks
- Mark tasks as complete
- Rich CLI interface with colors

---

## Phase II: Web Application (10 minutes)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
JWT_SECRET=your-secret-key-here
EOF

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
# New terminal
cd frontend

# Install dependencies
npm install

# Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Start dev server
npm run dev
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Phase III: AI Chatbot (5 minutes)

### Configure AI Provider

**Backend/.env**:
```bash
# Add Groq API key (recommended - free tier)
GROQ_API_KEY=gsk_your_key_here

# Optional fallbacks
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
```

### Test AI Chat

1. Start the backend (from Phase II)
2. Open http://localhost:3000/chat
3. Try commands like:
   - "Add a task to buy groceries"
   - "Show me all my tasks"
   - "Mark task 1 as complete"
   - "Delete the grocery task"

---

## Phase IV: Kubernetes (Local) (15 minutes)

### 1. Start Minikube

```bash
minikube start

# Enable registry for local images
eval $(minikube docker-env)
```

### 2. Build Docker Images

```bash
# Backend
docker build -t todo-backend:latest backend/

# Frontend (if deploying)
docker build -t todo-frontend:latest frontend/
```

### 3. Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace production

# Apply manifests
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/

# Check pods
kubectl get pods -n production
```

### 4. Access Application

```bash
# Port forward backend
kubectl port-forward -n production deployment/todo-backend 8000:8000

# Access at http://localhost:8000
```

---

## Phase V: Cloud Deployment (DigitalOcean) (20 minutes)

### 1. Set Up DigitalOcean Kubernetes

```bash
# Install doctl
curl -sL https://github.com/digitalocean/doctl/releases/download/v1.100.0/doctl-1.100.0-linux-amd64.tar.gz | tar xz
sudo mv doctl /usr/local/bin/

# Authenticate
doctl auth init

# Create cluster (or use existing)
doctl kubernetes cluster create hackathon2 --region fra1 --version 1.28.0-do.0 --size s-2vcpu-4gb --count 2

# Get kubeconfig
doctl kubernetes cluster kubeconfig save hackathon2
```

### 2. Install Dapr

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Verify
dapr status -k
```

### 3. Deploy Email Worker

```bash
# Build and push image
cd services/email-worker
docker build -t registry.digitalocean.com/todo-chatbot-reg/todo-backend:email-worker-v2 .
docker push registry.digitalocean.com/todo-chatbot-reg/todo-backend:email-worker-v2

# Deploy with Helm
helm upgrade --install email-worker ../../helm/email-worker --namespace production --create-namespace

# Verify deployment
kubectl get pods -n production -l app=email-worker
```

### 4. Deploy Backend with Dapr

```bash
# Build and push
cd ../../backend
docker build -t registry.digitalocean.com/todo-chatbot-reg/todo-backend:phase-v .
docker push registry.digitalocean.com/todo-chatbot-reg/todo-backend:phase-v

# Deploy
helm upgrade --install todo-backend ../../helm/backend --namespace production
```

### 5. Test Email Worker

```bash
# Port forward to test locally
kubectl port-forward -n production deployment/email-worker 8003:8003

# Test email endpoint (in another terminal)
curl -X POST http://localhost:8003/test-email
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Check DATABASE_URL format
# Should be: postgresql+asyncpg://user:password@host:port/dbname

# Verify Neon database is active
# Check network connectivity
```

### Port Already in Use

```bash
# Kill process on port 3000
npx kill-port 3000

# Kill process on port 8000
npx kill-port 8000
```

### Minikube Issues

```bash
# Restart Minikube
minikube stop
minikube start

# Clear cache
minikube delete
minikube start
```

### Kubernetes Pod Issues

```bash
# Check pod status
kubectl get pods -n production

# View logs
kubectl logs -n production <pod-name>

# Describe pod for events
kubectl describe pod -n production <pod-name>
```

### Email Worker SMTP Issues

**Note**: DigitalOcean K8s blocks outbound SMTP (ports 25, 587, 465).

**Solutions**:
1. Use email API service (SendGrid, Mailgun, Resend)
2. Test locally with Docker
3. Configure SMTP relay through allowed service

```bash
# Local test (works)
docker run -p 8003:8003 \
  -e MAIL_USERNAME="your@email.com" \
  -e MAIL_PASSWORD="app-password" \
  registry.digitalocean.com/todo-chatbot-reg/todo-backend:email-worker-v2
```

---

## Development Tips

### Backend

- Use Swagger docs at `/docs` for API testing
- Check logs for SQL queries and errors
- Use `pytest` for running tests

### Frontend

- Check browser console for errors
- Use React DevTools for debugging
- Check Network tab for API calls

### Kubernetes

- Use `kubectl get events -n production` to see cluster events
- Port forwarding: `kubectl port-forward -n production deployment/<name> <local-port>:<container-port>`
- Exec into pod: `kubectl exec -it -n production <pod-name> -- /bin/bash`

---

## What's Next?

### Explore the Codebase

- **`specs/`** - Feature specifications for each phase
- **`docs/`** - Additional documentation
- **`history/`** - Prompt history and decisions

### Features to Try

**Phase II (Web App)**:
- ✅ Create, edit, delete tasks
- 🔍 Search and filter tasks
- 🎨 Light/dark theme toggle
- 📱 Mobile responsive design

**Phase III (AI Chatbot)**:
- 🤖 Conversational task management
- 📝 Natural language commands
- 💬 Conversation history
- 🛠️ MCP tool integration

**Phase V (Microservices)**:
- 📨 Email notifications
- 🔄 Recurring tasks
- ⚡ Event-driven architecture
- 🎯 Background job processing

---

**Need Help?**

- Check the main [README.md](./README.md)
- Read specs in `specs/` directory
- Review docs in `docs/` directory
- Open an issue on GitHub

---

**Evolution of TODO - PIAIC Hackathon II**
**From Console to Cloud - The Complete Journey** 🚀
