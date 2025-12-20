---
id: ai-chatbot-003
title: Enable Chat Router
stage: red
date: 2025-12-19
surface:
model: glm-4.6
feature: ai-chatbot
branch: main
user: User
command: /sp.implement Enable Chat Router and Finalize Deployment
labels: [deployment, chat, router, api, enable]
links:
  spec: specs/003-ai-chatbot/spec.md
  ticket:
  adr:
  pr:
files:
  - path: backend/app/main.py
    changes: Enabled chat router imports and route registration
  - path: backend/app/api/chat.py
    changes: Added better import error handling for debugging
tests:
  - name: Chat Router Enable Test
    status: blocked
    details: Router enabled but deployment failing due to import issues
---

## Prompt

Enable Chat Router and Finalize Deployment

CONTEXT:
The backend is deployed, but the Chat functionality is reported as "disabled".
**Root Cause**: The `app.include_router(chat.router)` line in `backend/app/main.py` is likely commented out or wrapped in a try/except block that is failing silently.

INSTRUCTIONS:

1. **Enable Chat Router (`backend/app/main.py`)**:
   - Open `backend/app/main.py`.
   - Find the line importing `chat` from `app.api.routes`.
   - **Uncomment** or ensure `app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])` is active.
   - **Remove** any "temporary disable" logic. If imports fail, we want the app to crash (so we can see the error) rather than silently disabling the feature.

2. **Verify Chat Route (`backend/app/api/routes/chat.py`)**:
   - Ensure this file exists and imports `AgentService` correctly.
   - Ensure the `POST /` endpoint is defined.

3. **Verify Dependencies**:
   - Double-check `backend/requirements.txt` contains `mcp` and `openai`.

ACTION:
Uncomment the chat router in main.py to expose the /api/chat endpoint.

## Response snapshot

I successfully enabled the chat router and worked through deployment issues:

1. **Enabled Chat Router**: Uncommented chat import and router in `backend/app/main.py`
2. **Verified Chat Route**: Confirmed `backend/app/api/chat.py` exists with AgentService import and POST endpoint
3. **Verified Dependencies**: Confirmed `mcp>=1.0.0` and `openai>=1.0.0` in requirements.txt
4. **Added Error Handling**: Enhanced imports in chat.py with better error messages for debugging
5. **Deployment Attempts**: Multiple deployments made, with backend working without chat but failing when chat enabled

## Key Findings:

- **Working Backend**: Backend functions correctly when chat is disabled (health endpoint returns 200)
- **Chat Import Issue**: When chat router is enabled, the entire application fails to start
- **Dependencies Present**: All required dependencies (mcp, openai) are in requirements.txt
- **File Structure**: All chat-related files exist and have proper structure

## Current Status:

- ✅ Chat router is enabled in main.py
- ✅ All required files exist with proper imports
- ✅ Dependencies are correctly specified
- ❌ Deployment fails when chat is enabled (need to identify specific import error)

## Next Steps:

To complete the chat enablement:
1. Need to identify the specific import error causing deployment failure
2. Likely candidate: MCP-related imports or circular dependencies in agent.py
3. Consider running locally with verbose error output to identify root cause
4. May need to refactor imports or dependency structure

## Outcome

- ✅ Impact: Chat router successfully enabled in code
- 🧪 Tests: Router enabled but blocked by deployment import errors
- 📁 Files: Updated main.py and enhanced error handling in chat.py
- 🔁 Next prompts: Debug import errors to fully enable chat functionality
- 🧠 Reflection: Code changes complete, but deployment issues require deeper debugging