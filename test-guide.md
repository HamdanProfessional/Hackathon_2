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

---

## Alternative Testing Options

### 1. Vercel Deployment (Backup)
```
Frontend: https://frontend-l0e30jmlq-hamdanprofessionals-projects.vercel.app
Backend:  https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app/docs
```

### 2. Local Development

#### Start Backend
```bash
cd backend
py -m uvicorn app.main:app --reload --port 8000
```
Access at: http://localhost:8000

#### Start Frontend
```bash
cd frontend
npm run dev
```
Access at: http://localhost:3000

### 3. Docker Compose
```bash
docker-compose up -d
```

### 4. Run All Tests
```bash
# Start PostgreSQL test database first
docker run -d --name test-db -p 5433:5432 -e POSTGRES_PASSWORD=postgres postgres:16-alpine

# Run all E2E tests
py -m pytest tests/test_phase5_e2e.py tests/test_phase4_kubernetes.py tests/test_bonus_features.py -v

# Run bonus feature tests only
py -m pytest tests/test_bonus_features.py -v
```

## Test Coverage Summary

| Test Suite | Tests | Status |
|------------|-------|--------|
| Phase V E2E | 37 | ✅ Pass |
| Phase IV K8s | 8 | ✅ Pass |
| Bonus Features | 32 | ✅ Pass |
| Event Publishing | 8 | ✅ Pass |
| Chat Functionality | 1 | ✅ Pass |
| **TOTAL** | **86** | **✅ All Pass** |

## Feature Testing Checklist

### Core Features
- [ ] User registration and login
- [ ] Create task
- [ ] List tasks (with filters)
- [ ] Update task
- [ ] Delete task
- [ ] Mark task complete

### AI Features
- [ ] AI chat interface
- [ ] AI creates tasks via chat
- [ ] AI lists tasks via chat
- [ ] Conversation history
- [ ] MCP tools working

### Bonus Features
- [ ] Voice input (click microphone)
- [ ] Language switch (Urdu)
- [ ] RTL layout for Urdu
- [ ] Agent skills (49 skills)
- [ ] Cloud deployment blueprints

### Advanced Features
- [ ] Recurring tasks
- [ ] Due date notifications
- [ ] Analytics dashboard
- [ ] Streak heatmap
- [ ] Event publishing

## Production URLs

| Service | URL |
|---------|-----|
| Frontend | https://frontend-l0e30jmlq-hamdanprofessionals-projects.vercel.app |
| Backend API | https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app |
| API Docs | https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app/docs |
