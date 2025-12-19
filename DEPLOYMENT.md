# Deployment Guide - Phase III: AI-Powered Todo App

This guide covers deploying the complete Phase III application with AI chatbot functionality to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup (Neon)](#database-setup-neon)
3. [Backend Deployment (Railway)](#backend-deployment-railway)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

### Required Accounts
- ✅ **GitHub**: Code repository hosting
- ✅ **Neon**: PostgreSQL database (https://neon.tech)
- ✅ **Railway** or **Render**: Backend hosting (https://railway.app or https://render.com)
- ✅ **Vercel**: Frontend hosting (https://vercel.com)
- ✅ **OpenAI**: API access for GPT-4 (https://platform.openai.com)

### Required API Keys
- ✅ OpenAI API key (starts with `sk-`)
- ✅ JWT secret key (generate with `openssl rand -hex 32`)

### Code Requirements
- ✅ All code pushed to GitHub repository
- ✅ All migrations created and tested locally
- ✅ Environment variable templates (`.env.example`) up to date

---

## Database Setup (Neon)

### 1. Create Neon Project

1. Sign up or log in to https://neon.tech
2. Click **"New Project"**
3. Configure:
   - **Name**: `todo-ai-production`
   - **Region**: Choose closest to your users (e.g., US East, EU West)
   - **Compute size**: Scale to zero (free tier) or dedicated
4. Click **"Create Project"**

### 2. Get Connection String

1. Navigate to **Connection Details** in your Neon dashboard
2. Copy the **Connection String** (looks like):
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
3. Save this for backend deployment

### 3. Verify Database Access

Test locally:
```bash
cd backend
export DATABASE_URL="postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require"
alembic upgrade head
```

Expected output: Migration succeeds with no errors.

---

## Backend Deployment (Railway)

### Option A: Railway (Recommended)

#### 1. Create Railway Project

1. Sign up or log in to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select your repository: `<username>/todo-ai-app`

#### 2. Configure Build Settings

1. In Railway project settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 3. Set Environment Variables

In Railway project → **Variables**, add:

```env
# Database
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require

# Authentication
JWT_SECRET_KEY=<your-generated-secret-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (update after frontend deployment)
CORS_ORIGINS=https://your-frontend.vercel.app

# Phase III: AI Agent
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4
MAX_TOKENS_PER_DAY=50000
```

#### 4. Run Database Migrations

In Railway project → **Settings** → **Deployments**:

1. Click on latest deployment
2. Open **"Deploy Logs"**
3. Click **"Run Command"**
4. Execute:
   ```bash
   alembic upgrade head
   ```

#### 5. Get Backend URL

1. Navigate to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Copy the URL (e.g., `https://your-backend.railway.app`)
4. Save for frontend configuration

---

### Option B: Render

#### 1. Create Web Service

1. Sign up or log in to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repository
4. Configure:
   - **Name**: `todo-ai-backend`
   - **Environment**: Python 3
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 2. Set Environment Variables

Same as Railway (see above).

#### 3. Deploy and Run Migrations

1. Wait for initial deployment to complete
2. In Render dashboard → **Shell**:
   ```bash
   cd backend
   alembic upgrade head
   ```

---

## Frontend Deployment (Vercel)

### 1. Create Vercel Project

1. Sign up or log in to https://vercel.com
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 2. Set Environment Variables

In Vercel project → **Settings** → **Environment Variables**, add:

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

**Important**: Replace with your actual backend URL from Railway/Render.

### 3. Deploy

1. Click **"Deploy"**
2. Wait for build to complete (~2-3 minutes)
3. Copy the production URL (e.g., `https://your-frontend.vercel.app`)

### 4. Update Backend CORS

1. Go back to Railway/Render
2. Update `CORS_ORIGINS` environment variable:
   ```env
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```
3. Redeploy backend

---

## Post-Deployment Verification

### 1. Smoke Test Registration

1. Navigate to `https://your-frontend.vercel.app`
2. Click **"Register"**
3. Create test account:
   - Email: `test@example.com`
   - Password: `TestPassword123!`
4. Verify auto-login to dashboard

### 2. Test Task CRUD

1. **Create**: Add new task "Buy groceries"
2. **Read**: Verify task appears in list
3. **Update**: Edit task title to "Buy organic groceries"
4. **Complete**: Toggle completion checkbox
5. **Delete**: Delete task with confirmation

### 3. Test AI Chat (Phase III)

1. Click **"AI Chat"** button in navigation
2. Send message: `"Add buy milk to my list"`
3. Verify response: Agent confirms task creation
4. Send message: `"Show me my tasks"`
5. Verify response: Agent lists tasks with checkboxes
6. Test conversation persistence:
   - Refresh page
   - Verify conversation history loads
7. Test conversation switching:
   - Click "New Chat"
   - Start new conversation
   - Switch between conversations in sidebar

### 4. Verify Mobile Responsiveness

1. Open Chrome DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test on iPhone SE, iPad, and Desktop viewports
4. Verify:
   - Chat sidebar toggles on mobile
   - Navigation is readable
   - Input fields are usable

---

## Monitoring & Maintenance

### Backend Monitoring

#### Railway Dashboard

- **Metrics**: CPU, memory, network usage
- **Logs**: Real-time application logs
- **Alerts**: Set up for high error rates

#### OpenAI Usage

1. Visit https://platform.openai.com/usage
2. Monitor daily token consumption
3. Adjust `MAX_TOKENS_PER_DAY` if needed
4. Set up billing alerts to avoid overages

### Frontend Monitoring

#### Vercel Analytics

1. Enable Vercel Analytics in project settings
2. Monitor:
   - Page views
   - Load times
   - Core Web Vitals
   - Error rates

### Database Monitoring

#### Neon Dashboard

1. Monitor **Metrics**:
   - Connections
   - Query performance
   - Storage usage
2. Enable autoscaling if traffic increases
3. Set up automated backups

---

## Troubleshooting

### Backend Issues

#### Migration Errors

**Problem**: `alembic upgrade head` fails

**Solution**:
```bash
# Check current migration state
alembic current

# Rollback one step if needed
alembic downgrade -1

# Re-run upgrade
alembic upgrade head
```

#### CORS Errors

**Problem**: Frontend shows CORS policy errors

**Solution**:
1. Verify `CORS_ORIGINS` in backend includes frontend URL (no trailing slash)
2. Redeploy backend after changes
3. Clear browser cache

#### OpenAI API Errors

**Problem**: Chat returns "Failed to process message"

**Solution**:
1. Check backend logs for OpenAI error details
2. Verify `OPENAI_API_KEY` is correct
3. Check OpenAI account status and billing
4. Verify `OPENAI_MODEL` is available (try `gpt-3.5-turbo` if GPT-4 unavailable)

#### Database Connection Issues

**Problem**: Backend logs show database connection errors

**Solution**:
1. Verify `DATABASE_URL` includes `?sslmode=require`
2. Check Neon project is active (not suspended)
3. Verify database credentials haven't expired

### Frontend Issues

#### API Connection Failed

**Problem**: Frontend shows "Failed to send message"

**Solution**:
1. Verify `NEXT_PUBLIC_API_URL` is correct
2. Check backend is running and accessible
3. Open Network tab in DevTools to see exact error
4. Verify JWT token is present in localStorage

#### Conversation Not Loading

**Problem**: Chat page shows no conversations

**Solution**:
1. Open browser console for errors
2. Verify backend `/api/chat/conversations` endpoint works
3. Clear localStorage and re-login
4. Check backend logs for authentication errors

---

## Cost Optimization

### Free Tier Limits (as of 2025)

- **Neon**: 10 GB storage, autoscaling compute
- **Railway**: $5 free credit/month
- **Vercel**: 100 GB bandwidth, unlimited deployments
- **OpenAI**: Pay-per-use (GPT-4: ~$0.03/1K tokens)

### Reducing OpenAI Costs

1. Use `gpt-3.5-turbo` instead of `gpt-4` for testing
2. Lower `MAX_TOKENS_PER_DAY` to limit daily usage
3. Implement token counting in agent service
4. Add rate limiting to chat endpoint

---

## Security Checklist

Before going live:

- [ ] JWT secret is strong (32+ random characters)
- [ ] OpenAI API key is never exposed to frontend
- [ ] CORS origins are restricted to production domain
- [ ] Environment variables are not committed to Git
- [ ] HTTPS is enabled (automatic on Vercel/Railway)
- [ ] Input validation is active on all endpoints
- [ ] Database has automated backups enabled

---

## Rollback Procedure

If deployment has critical issues:

### Backend Rollback

**Railway**:
1. Go to **Deployments**
2. Find previous working deployment
3. Click **"Redeploy"**

**Render**:
1. Go to **Deployments**
2. Click on previous successful deployment
3. Click **"Redeploy"**

### Frontend Rollback

**Vercel**:
1. Go to **Deployments**
2. Find previous working deployment
3. Click **"⋯"** → **"Promote to Production"**

### Database Rollback

**Caution**: Only if schema change caused issues

```bash
# Check current migration
alembic current

# Rollback to specific revision
alembic downgrade <revision_id>
```

---

## Next Steps

After successful deployment:

1. **Set up monitoring alerts**: Configure email/Slack notifications for errors
2. **Enable analytics**: Track user behavior and performance
3. **Implement rate limiting**: Protect against abuse
4. **Add automated testing**: Set up CI/CD pipeline
5. **Plan Phase IV**: Kubernetes deployment for advanced scaling

---

## Support Resources

- **Neon Docs**: https://neon.tech/docs
- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Next.js Deployment**: https://nextjs.org/docs/deployment
- **OpenAI Platform**: https://platform.openai.com/docs

---

**Deployment Guide Version**: 1.0.0 (Phase III)
**Last Updated**: 2025-12-14
