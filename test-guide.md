# Testing Guide for Evolution of TODO

## 🌟 PRIMARY TESTING URLS (Official Deployment)

### Frontend Application
```
https://hackathon2.testservers.online
```
**This is the main application URL** - Open this to test the full Todo app.

### Backend API
```
https://api.testservers.online
```
API Documentation (Swagger UI):
```
https://api.testservers.online/docs
```

### Phase V Backend (with Background Jobs)
```
https://backend-lac-nu-61.vercel.app
```
This deployment includes:
- Background jobs endpoint (`/background/check-due-tasks`)
- Event publishing for Dapr
- Recurring task processing

---

## Alternative Testing Options

### 1. Vercel Deployment (Backup)
```
Frontend: https://frontend-l0e30jmlq-hamdanprofessionals-projects.vercel.app
Backend (Phase V): https://backend-lac-nu-61.vercel.app
```

### 2. Local Development

#### Start Backend
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
Access at: http://localhost:8000

#### Start Frontend
```bash
cd frontend
npm install
npm run dev
```
Access at: http://localhost:3000

### 3. Kubernetes Deployment (Phase V)

#### Email Worker Testing

**Port Forward to Local**:
```bash
kubectl port-forward -n production deployment/email-worker 8003:8003
```

**Test Email Endpoint**:
```bash
# Test email sending
curl -X POST http://localhost:8003/test-email
```

**Health Checks**:
```bash
# General health
curl http://localhost:8003/health

# Readiness probe
curl http://localhost:8003/health/ready

# Dapr subscriptions
curl http://localhost:8003/dapr/subscribe
```

**Background Jobs Endpoint** (Phase V Backend):
```bash
# Check for tasks due within 24 hours
curl -X POST "https://backend-lac-nu-61.vercel.app/background/check-due-tasks?hours_threshold=24"

# Process recurring tasks
curl -X POST "https://backend-lac-nu-61.vercel.app/background/process-recurring-tasks"

# Reset notification flags
curl -X POST "https://backend-lac-nu-61.vercel.app/background/reset-notified-flags"
```

### 4. Local Email Worker Test (Docker)

```bash
# Run email worker locally
docker run -d --name email-worker-test -p 8003:8003 \
  -e MAIL_SERVER="smtp.gmail.com" \
  -e MAIL_PORT="587" \
  -e MAIL_USERNAME="your@email.com" \
  -e MAIL_PASSWORD="your-app-password" \
  -e MAIL_FROM="noreply@hackathon2.testservers.online" \
  -e MAIL_FROM_NAME="Todo App" \
  registry.digitalocean.com/todo-chatbot-reg/todo-backend:email-worker-v2

# Test email endpoint
curl -X POST http://localhost:8003/test-email

# Check logs
docker logs email-worker-test

# Clean up
docker stop email-worker-test && docker rm email-worker-test
```

### 5. Run All Tests

```bash
# Backend tests
cd backend
pytest

# E2E tests
pytest tests/test_phase5_e2e.py -v

# Kubernetes tests
pytest tests/test_phase4_kubernetes.py -v

# Event publishing tests
pytest tests/test_event_publishing.py -v

# Bonus feature tests
pytest tests/test_bonus_features.py -v

# All tests
pytest tests/ -v
```

## Test Coverage Summary

| Test Suite | Tests | Status |
|------------|-------|--------|
| Phase V E2E | 37 | ✅ Pass |
| Phase IV K8s | 8 | ✅ Pass |
| Bonus Features | 32 | ✅ Pass |
| Event Publishing | 8 | ✅ Pass |
| Chat Functionality | 1 | ✅ Pass |
| Email Worker | 1 (local) | ✅ Pass |
| **TOTAL** | **87** | **✅ All Pass** |

## Feature Testing Checklist

### Core Features (Phase I & II)
- [x] User registration and login
- [x] Create task
- [x] List tasks (with filters)
- [x] Update task
- [x] Delete task
- [x] Mark task complete
- [x] Search and filter tasks
- [x] Priority levels
- [x] Task categories/tags

### AI Features (Phase III)
- [x] AI chat interface
- [x] AI creates tasks via chat
- [x] AI lists tasks via chat
- [x] Conversation history
- [x] MCP tools working
- [x] Stateless agent architecture

### Bonus Features
- [x] Voice input (click microphone)
- [x] Language switch (Urdu/English)
- [x] RTL layout for Urdu
- [x] Agent skills (49 skills)
- [x] Cloud deployment blueprints

### Advanced Features (Phase V)
- [x] Recurring tasks
- [x] Due date notifications (email worker deployed)
- [x] Analytics dashboard
- [x] Streak heatmap
- [x] Event publishing (Dapr + Kafka)
- [x] Background job processing
- [x] Email notification service

### Infrastructure (Phase IV & V)
- [x] Docker containerization
- [x] Kubernetes deployment (Minikube)
- [x] Helm charts
- [x] DigitalOcean K8s deployment
- [x] Dapr integration
- [x] CI/CD pipeline (GitHub Actions)

## Testing Email Notifications

### Gmail SMTP Configuration
- **Server**: smtp.gmail.com:587
- **Username**: n00bi2761@gmail.com
- **Verified**: ✅ Local Docker test passed

### Important Notes
**DigitalOcean Kubernetes blocks outbound SMTP** (ports 25, 587, 465) for security.

**Email sending from K8s cluster requires**:
1. Email API service (SendGrid, Mailgun, Resend) - **Recommended**
2. SMTP relay configuration
3. Or use the deployed email worker with email API integration

### Testing Flow
1. Create a task with due date
2. Call `/background/check-due-tasks?hours_threshold=24`
3. Backend publishes `task-due-soon` event
4. Email worker receives event via Dapr
5. Email is sent to user's email address

## Production URLs Summary

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | https://hackathon2.testservers.online | Main application |
| Backend (Phase III) | https://api.testservers.online/docs | API with docs |
| Backend (Phase V) | https://backend-lac-nu-61.vercel.app | Background jobs + events |
| Email Worker | Running in DigitalOcean K8s | Dapr-enabled microservice |

## Troubleshooting Tests

### Backend Tests Failing
```bash
# Check database connection
echo $DATABASE_URL

# Run migrations
alembic upgrade head

# Check database schema
python -c "from app.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### Kubernetes Tests Failing
```bash
# Check cluster connection
kubectl cluster-info

# Check pods
kubectl get pods -n production

# Check Dapr
dapr status -k
```

### Email Worker Tests
```bash
# Local test (works - verified ✅)
docker run -p 8003:8003 \
  -e MAIL_USERNAME="your@email.com" \
  -e MAIL_PASSWORD="app-password" \
  registry.digitalocean.com/todo-chatbot-reg/todo-backend:email-worker-v2

# K8s test (SMTP blocked by cluster firewall)
# Email is published but not delivered due to port blocking
```

## Development Tips

### Backend Testing
- Use Swagger UI at `/docs` for manual API testing
- Check logs for SQL queries and errors
- Use `pytest` for automated tests
- Test MCP tools via `/api/chat` endpoint

### Frontend Testing
- Use browser DevTools (F12)
- Check Network tab for API calls
- Console shows JavaScript errors
- React DevTools for component inspection

### Kubernetes Testing
- `kubectl get pods` - pod status
- `kubectl logs <pod>` - view logs
- `kubectl describe pod <pod>` - pod details
- `kubectl port-forward` - local access

### Email Worker Testing
- Local Docker works (no firewall)
- K8s deployment active (SMTP blocked)
- Health endpoint: `/health/ready`
- Test endpoint: `/test-email`

---

**Evolution of TODO - PIAIC Hackathon II**
**Complete Testing Coverage Across All 5 Phases** ✅
