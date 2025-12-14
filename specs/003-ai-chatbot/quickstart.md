# Quickstart Guide: Phase III AI Chatbot Development

**Date**: 2025-12-13
**Prerequisites**: Phase II complete and running (backend + frontend + database)

This guide walks through setting up Phase III AI chatbot functionality on top of your existing Phase II application.

---

## 1. Prerequisites Check

Before starting Phase III development, ensure you have:

- ✅ Phase II backend running (FastAPI on port 8000)
- ✅ Phase II frontend running (Next.js on port 3000)
- ✅ Neon PostgreSQL database accessible
- ✅ User authentication working (can register/login)
- ✅ Task CRUD working via web UI
- ✅ Python 3.13+ installed
- ✅ Node.js 18+ installed

**Verify Phase II**:
```bash
# Backend
curl http://localhost:8000/api/tasks  # Should return 401 (auth required)

# Frontend
open http://localhost:3000  # Should show login page
```

---

## 2. Obtain OpenAI API Key

Phase III requires an OpenAI API key for AI agent functionality.

**Steps**:
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create new secret key
5. Copy key (starts with `sk-...`)
6. Save securely - you won't see it again!

**Pricing Note**: GPT-4 costs ~$0.03 per 1K tokens. Expect ~$0.01-0.05 per conversation turn.

---

## 3. Install New Dependencies

### Backend Dependencies

Add to `backend/requirements.txt`:
```txt
openai>=1.0.0
mcp>=1.0.0
```

Install:
```bash
cd backend
pip install -r requirements.txt
```

**Verify installation**:
```bash
python -c "import openai; import mcp; print('✅ Dependencies installed')"
```

### Frontend Dependencies

Install ChatKit:
```bash
cd frontend
npm install @openai/chatkit
```

**Verify installation**:
```bash
npm list @openai/chatkit  # Should show installed version
```

---

## 4. Configure Environment Variables

### Backend Environment (`.env`)

Add to `backend/.env`:
```env
# Existing Phase II variables (keep these)
DATABASE_URL=postgresql://user:pass@your-neon-host/dbname
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000

# NEW Phase III variables
OPENAI_API_KEY=sk-...  # Your OpenAI API key
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo for lower cost
MAX_TOKENS_PER_DAY=50000  # Daily token budget per user
```

**Security Note**: Never commit `.env` to version control. Add to `.gitignore`.

### Frontend Environment (`.env.local`)

Add to `frontend/.env.local`:
```env
# Existing Phase II variable
NEXT_PUBLIC_API_URL=http://localhost:8000

# NEW Phase III variables
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=  # Leave empty for localhost development
```

---

## 5. Run Database Migrations

Phase III adds two new tables: `conversations` and `messages`.

**Generate migration** (if not already created):
```bash
cd backend
alembic revision --autogenerate -m "Add conversations and messages tables"
```

**Apply migration**:
```bash
alembic upgrade head
```

**Verify migration**:
```bash
# Connect to your Neon database
psql $DATABASE_URL

# Check tables exist
\dt
# Should see: users, tasks, conversations, messages, alembic_version

# Check conversation schema
\d conversations
# Should show: id, user_id, created_at, updated_at

# Check messages schema
\d messages
# Should show: id, conversation_id, role, content, created_at
```

---

## 6. Test MCP Tools Independently

Before integrating with the agent, test each MCP tool individually.

**Create test file** `backend/test_mcp_manual.py`:
```python
import asyncio
from app.mcp.tools import add_task, list_tasks, complete_task

async def test_tools():
    user_id = 1  # Replace with your test user ID

    # Test add_task
    result = await add_task(user_id=user_id, title="Test task", description="Testing MCP")
    print(f"✅ Created task: {result}")
    task_id = result["task_id"]

    # Test list_tasks
    tasks = await list_tasks(user_id=user_id, status="all")
    print(f"✅ Listed {tasks['count']} tasks")

    # Test complete_task
    complete_result = await complete_task(user_id=user_id, task_id=task_id)
    print(f"✅ Completed task: {complete_result}")

asyncio.run(test_tools())
```

**Run test**:
```bash
cd backend
python test_mcp_manual.py
```

**Expected output**:
```
✅ Created task: {'task_id': 42, 'status': 'created', 'title': 'Test task'}
✅ Listed 1 tasks
✅ Completed task: {'task_id': 42, 'status': 'completed', 'title': 'Test task'}
```

---

## 7. Test Chat API Endpoint

Once MCP tools work, test the chat endpoint with sample conversations.

**Start backend**:
```bash
cd backend
uvicorn app.main:app --reload
```

**Test with curl** (in new terminal):
```bash
# Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com", "password":"password123"}' \
  | jq -r '.access_token')

# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add buy groceries to my list"}' \
  | jq
```

**Expected response**:
```json
{
  "conversation_id": 1,
  "response": "I've added 'Buy groceries' to your task list.",
  "tool_calls": [
    {"tool": "add_task", "parameters": {"title": "Buy groceries"}}
  ]
}
```

**Test multi-turn conversation**:
```bash
# Second message in same conversation
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": 1, "message": "What did I just add?"}' \
  | jq
```

---

## 8. Configure ChatKit Domain Allowlist (Production Only)

**For localhost development**: Skip this step. ChatKit works on localhost without domain allowlist.

**For production deployment**:

1. Deploy frontend to Vercel:
   ```bash
   cd frontend
   vercel --prod
   ```

2. Note the production URL (e.g., `https://your-app.vercel.app`)

3. Add to OpenAI domain allowlist:
   - Go to https://platform.openai.com/settings/organization/security/domain-allowlist
   - Click "Add domain"
   - Enter: `your-app.vercel.app`
   - Save

4. Copy domain key provided by OpenAI

5. Update frontend environment:
   ```env
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here
   ```

6. Redeploy frontend

---

## 9. Run Frontend Chat Interface

**Start frontend** (if not already running):
```bash
cd frontend
npm run dev
```

**Access chat interface**:
1. Open http://localhost:3000
2. Login with test account
3. Navigate to `/chat` (or click "Chat" link in nav)
4. Type a message: "Add buy groceries to my list"
5. See AI response and task creation confirmation

**Test features**:
- Create task via chat: "Add finish report to my tasks"
- List tasks: "What's on my todo list?"
- Mark complete: "I finished the report"
- Update task: "Change groceries task to include fruits"
- Delete task: "Remove the old meeting notes"

---

## 10. Debugging Agent Behavior

### View Agent Logs

**Backend logs**:
```bash
cd backend
uvicorn app.main:app --reload --log-level debug
```

Look for:
- `[AGENT]` - Agent decision logs
- `[MCP]` - Tool invocation logs
- `[DB]` - Database query logs

### View Tool Calls in Response

Chat API response includes `tool_calls` array showing which tools agent invoked:

```json
{
  "tool_calls": [
    {"tool": "add_task", "parameters": {"title": "Buy groceries", "description": ""}}
  ]
}
```

### Test Specific Scenarios

**Ambiguous input**:
```
User: "Add something about meeting"
Expected: Agent asks "What would you like to add about the meeting?"
```

**Multi-step operation**:
```
User: "Add task X and mark task 3 as done"
Expected: Agent calls add_task, then complete_task
```

**Out of scope request**:
```
User: "What's the weather?"
Expected: "I'm here to help with your todo list. Would you like to add, view, or manage tasks?"
```

---

## 11. Common Issues & Solutions

### Issue: "OpenAI API key not found"
**Solution**: Check `backend/.env` has `OPENAI_API_KEY=sk-...`

### Issue: "conversations table does not exist"
**Solution**: Run `alembic upgrade head` to apply migrations

### Issue: "ChatKit domain not allowlisted"
**Solution**: Only affects production. For localhost, ignore this. For production, add domain to OpenAI platform.

### Issue: "Agent not understanding commands"
**Solution**: Check system prompt in `agent_service.py`. Ensure prompt clearly defines tool usage patterns.

### Issue: "Token budget exceeded"
**Solution**: Increase `MAX_TOKENS_PER_DAY` in `.env` or wait 24 hours for reset.

### Issue: "Conversation history not loading"
**Solution**: Check database indexes exist: `CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);`

---

## 12. Development Workflow

**Typical development cycle**:

1. **Make changes** to agent service or MCP tools
2. **Restart backend**: `uvicorn app.main:app --reload` (auto-reloads on file changes)
3. **Test via curl**: Send chat messages, check responses
4. **Test via UI**: Open frontend, try conversation
5. **Check logs**: View backend logs for debugging
6. **Iterate**: Adjust prompt, tool implementations, or schemas

**Best practices**:
- Test MCP tools in isolation before integrating with agent
- Use clear, specific prompts for deterministic agent behavior
- Log all tool calls for debugging
- Monitor token usage to control costs
- Test multi-turn conversations to verify context preservation

---

## 13. Next Steps

After quickstart setup complete:

1. **Run `/sp.tasks`** to generate detailed task breakdown
2. **Implement tasks** in recommended order (database → tools → agent → frontend)
3. **Write tests** for each component (unit, integration, E2E)
4. **Deploy to staging** for user testing
5. **Monitor token usage** and adjust budgets as needed

---

## References

- OpenAI Agents SDK: https://platform.openai.com/docs/guides/agents
- OpenAI ChatKit: https://platform.openai.com/docs/guides/chatkit
- MCP Protocol: https://github.com/modelcontextprotocol/specification
- Phase III Spec: [spec.md](./spec.md)
- Phase III Plan: [plan.md](./plan.md)
- MCP Tool Contracts: [contracts/](./contracts/)

---

**Support**: If you encounter issues not covered here, check backend logs, review agent prompt, and verify all environment variables are set correctly.
