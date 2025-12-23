# Project Constants

## Production URLs

| Service | URL |
|---------|-----|
| Frontend | https://frontend-l0e30jmlq-hamdanprofessionals-projects.vercel.app |
| Backend | https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app |

## AI Configuration

| Setting | Value |
|---------|-------|
| Provider | Groq (Primary) |
| Model | llama-3.1-8b-instant |
| API Base | https://api.groq.com/openai/v1 |
| Free Tier | 14,400 requests/day |
| Fallback | Gemini → OpenAI → Grok |

## Database

| Setting | Value |
|---------|-------|
| Type | PostgreSQL (Neon for prod, local for dev) |
| Schema | SQLModel |
| Migrations | Alembic |
| Latest Migration | 004_fix_message_role_enum_to_varchar |
| Migration Issue | cc82207f4f25 breaks on fresh DB (Better Auth tables) |

## Project Structure

```
Hackathon_2/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   ├── alembic/      # Database migrations
│   └── tests/        # Test files (organized)
├── frontend/         # Next.js frontend
│   ├── app/         # App Router pages
│   ├── components/  # React components
│   └── lib/         # Utilities (api.ts)
├── tests/            # Shared test files
│   ├── test_e2e_functional.py  # E2E test suite
│   ├── test_production_chat.py # Production health test
│   └── test_groq_direct.py     # Direct API tests
├── specs/            # Feature specifications
│   ├── 001-todo-crud/  # Phase I (Complete)
│   ├── 002-web-app/    # Phase II (Complete)
│   ├── 003-ai-chatbot/  # Phase III (Deployed)
│   ├── 004-kubernetes/ # Phase IV (Testing)
│   └── 005-cloud-deployment/ # Phase V (DigitalOcean)
├── helm/             # Kubernetes Helm charts
│   ├── backend/      # Backend deployment
│   └── frontend/     # Frontend deployment
└── .claude/          # Claude configuration
    ├── memory/       # Project memory
    └── settings.local.json
```

## Phase Status (Latest: 2025-12-23)

| Phase | Status | Completion | Notes |
|-------|--------|------------|-------|
| Phase I - Console App | ✅ Complete | 100% | CLI CRUD application working |
| Phase II - Web App | ✅ Complete | 100% | FastAPI + Next.js, JWT auth |
| Phase III - AI Chatbot | ⚠️ Partial | 80% | Deployed, MCP tools not called |
| Phase IV - Kubernetes | ⚠️ Testing | 70% | Minikube running, DB migration issues |
| Phase V - Cloud Deployment | 📋 Spec Ready | 30% | DigitalOcean spec complete |

## E2E Test Results (Production) - 2025-12-23

| Test | Result | Details |
|------|--------|---------|
| Registration/Login | ✅ Pass (3/13) | JWT authentication working |
| Task Create API | ✅ Pass | HTTP POST works |
| Task Read API | ✅ Pass | HTTP GET works |
| Task Delete API | ✅ Pass | HTTP DELETE works |
| Task Update API | ❌ Fail | Returns 400 |
| MCP Tool Invocation | ❌ Fail | Tools NOT called by AI |
| Conversation List | ✅ Pass | 6 conversations found |
| Conversation Details | ❌ Fail | 405 Method Not Allowed |
| AI Text Response | ✅ Pass | AI responds but no tools |

**Success Rate**: 23.1% (3/13 tests passing)

## Critical Issues

1. **MCP Tools Not Invoked**: AI doesn't call get_tasks, create_task, update_task, delete_task
2. **Task Update API**: 400 error on PUT /api/tasks/{id}
3. **Conversation Details**: 405 on GET /api/chat/conversations/{id}
4. **Migration cc82207f4f25**: Tries to drop non-existent Better Auth tables
5. **Local DB Setup**: Fresh database requires manual migration intervention

## Phase III Features Implemented

| Feature | Status | Location |
|---------|--------|----------|
| AI Chat Interface | ✅ | `/chat` page |
| Dashboard Chat Widget | ✅ | ChatWidget component |
| Delete Conversations | ✅ | chat-interface.tsx |
| MCP Tools (Defined) | ⚠️ | mcp_tools.py (5 tools, not called) |
| Stateless Agent | ✅ | agent.py |
| Conversation Persistence | ✅ | conversations/messages tables |

## Test Credentials

| Field | Value |
|-------|-------|
| Email | test1@test.com |
| Password | Test1234 |

## MCP Tools Available (Defined but NOT invoked)

- `add_task` - Create a new task
- `list_tasks` - List all tasks for authenticated user
- `complete_task` - Mark task as complete
- `update_task` - Update task details
- `delete_task` - Delete a task

## Git Branches

| Branch | Purpose |
|--------|---------|
| main | Development branch |
| master | Production PR target |

## Key Files

| File | Purpose |
|------|---------|
| `backend/app/config.py` | AI provider configuration |
| `backend/app/ai/agent.py` | Stateless agent implementation |
| `backend/app/ai/mcp_tools.py` | MCP tool definitions (not invoked) |
| `frontend/components/chat/chat-interface.tsx` | Main chat component |
| `frontend/lib/api.ts` | API client with JWT auth |
| `specs/003-ai-chatbot/spec.md` | Phase III specification |
| `specs/004-kubernetes/spec.md` | Phase IV specification |
| `specs/005-cloud-deployment/spec.md` | Phase V DigitalOcean spec |
| `tests/test_e2e_functional.py` | Comprehensive E2E test suite |

## Development Tools Installed

| Tool | Version | Purpose |
|------|---------|---------|
| kubectl | v1.34.2 | Kubernetes CLI |
| Helm | v3.19.4 | Kubernetes package manager |
| Minikube | v1.37.0 | Local Kubernetes cluster |
| doctl | v1.148.0 | DigitalOcean CLI |
| kubectl-ai | v0.0.28 | AI-powered kubectl |
| Docker Desktop | Latest | Container runtime |
| Python | 3.13 | Backend runtime |
| Node.js | 20.x | Frontend runtime |

## Environment Variables Required

### Backend
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - JWT signing secret (min 32 chars)
- `GROQ_API_KEY` - Groq API key (primary AI)
- `GEMINI_API_KEY` - Gemini API key (fallback)
- `OPENAI_API_KEY` - OpenAI API key (fallback)
- `CORS_ORIGINS` - Allowed frontend origins

### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `BETTER_AUTH_SECRET` - Better Auth secret (if using)

## Testing Standards

### Test-First Development
1. Write test before implementation
2. Run test to verify failure (red)
3. Implement feature
4. Run test to verify pass (green)
5. Commit with tests passing

### Test Coverage Goals
- Unit tests: 80%+ coverage
- Integration tests: All API endpoints
- E2E tests: Critical user paths
- Performance tests: <200ms API response

### Git Commit Standards
After every task:
1. `git status` - Review changes
2. `git add <files>` - Stage changes
3. `git commit -m "<type>(<scope>): <message>"` - Commit
4. `git push` - Push to main
5. Verify: `git log -1`
