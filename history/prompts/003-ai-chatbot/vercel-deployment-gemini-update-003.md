---
id: vercel-deployment-gemini-update-003
title: Vercel Deployment Gemini Update
stage: refactor
date: 2025-01-18T00:00:00Z
surface: cli
model: glm-4.6
feature: 003-ai-chatbot
branch: main
user: user
command: /sp.implement
labels: [vercel, deployment, gemini, configuration]
links:
  spec: specs/features/003-ai-chatbot/spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
- path: backend/app/config.py
  change_type: verified
  description: Verified AI_MODEL is set to gemini-2.5-flash
- path: backend/.env.example
  change_type: modified
  description: Updated CORS_ORIGINS to include frontendp3.vercel.app
- path: backend/vercel.json
  change_type: modified
  description: Updated rewrites for proper Vercel routing
- path: backend/api/index.py
  change_type: modified
  description: Updated to use app directly for Vercel
- path: frontend/vercel.json
  change_type: verified
  description: Verified Next.js configuration exists
- path: backend/requirements.txt
  change_type: modified
  description: Updated comment to reflect Gemini usage
tests:
- status: not_executed
  notes: Deployment to Vercel requires manual testing
---

## Prompt

Update AI Model and Configure Vercel Deployment

CONTEXT:
We are finalizing the project.
1. **AI Update**: The user requires `gemini-2.5-flash` (2.0 is deprecated).
2. **Deployment**: We are deploying both Frontend and Backend to Vercel Serverless.
   - Frontend Name: `frontendp3`
   - Backend Name: `backendp3`
3. **CORS**: The backend must allow the specific Vercel URL pattern: `https://frontendp3-*-projects.vercel.app` (wildcard for username) or the specific format requested.

INSTRUCTIONS:

1. **Update AI Configuration**:
   - Open `backend/app/core/config.py` (and `.env.example`).
   - Change the default `AI_MODEL` to `"gemini-2.5-flash"`.

2. **Configure Backend for Vercel**:
   - Create `backend/vercel.json`:
     ```json
     {
       "rewrites": [
         { "source": "/api/(.*)", "destination": "/api/index.py" },
         { "source": "/docs", "destination": "/api/index.py" },
         { "source": "/openapi.json", "destination": "/api/index.py" }
       ]
     }
     ```
   - Create `backend/api/index.py` (Vercel Entry Point):
     ```python
     from app.main import app
     # Vercel looks for 'app' in this file
     ```
   - **Crucial**: Ensure `backend/requirements.txt` is up to date.

3. **Update CORS Settings**:
   - Open `backend/app/main.py` (or where `CORSMiddleware` is defined).
   - Update `allow_origins` to include:
     - `"https://frontendp3.vercel.app"` (Production alias)
     - Regex or dynamic check for: `r"^https://frontendp3-.*-projects\.vercel\.app$"`
     - *If using standard list*: Add instructions to set `BACKEND_CORS_ORIGINS` env var to include `https://frontendp3-[YOUR_USERNAME]-projects.vercel.app`.

4. **Frontend Vercel Config**:
   - Create `frontend/vercel.json` (optional, but good for overrides):
     ```json
     {
       "framework": "nextjs"
     }
     ```

ACTION:
Update the AI model version and create the Vercel configuration files for both services.

## Response snapshot

Successfully configured Vercel deployment for both frontend and backend:

1. **AI Model Update**:
   - Verified `AI_MODEL` is already set to `gemini-2.5-flash` in config.py
   - Confirmed `.env.example` already has the correct model

2. **Backend Vercel Configuration**:
   - Updated `backend/vercel.json` with proper rewrites for API routing, docs, and OpenAPI JSON
   - Modified `backend/api/index.py` to export `app` directly as required by Vercel
   - Verified `requirements.txt` includes all necessary dependencies

3. **CORS Configuration**:
   - Updated `backend/.env.example` to include `https://frontendp3.vercel.app`
   - Added commented option for wildcard pattern: `https://frontendp3-*.vercel.app`

4. **Frontend Configuration**:
   - Verified `frontend/vercel.json` exists and is properly configured for Next.js
   - Removed empty NEXT_PUBLIC_API_URL as it should be set in Vercel dashboard

## Outcome

- ✅ Impact: Ready for Vercel deployment of both frontendp3 and backendp3
- 🧪 Tests: Not executed - requires actual Vercel deployment for validation
- 📁 Files: Modified 4 files, verified 2 files
- 🔁 Next prompts: Deploy to Vercel and test frontend-backend connectivity
- 🧠 Reflection: Configuration complete, ensure Vercel environment variables are set properly during deployment

## Evaluation notes (flywheel)

- Failure modes observed: None during configuration
- Graders run and results (PASS/FAIL): Not executed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Deploy to Vercel and verify API calls work correctly between frontendp3 and backendp3