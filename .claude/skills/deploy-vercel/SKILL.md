---
name: deploy-vercel
description: Deploy frontend (Next.js) and backend (FastAPI) applications to Vercel with automatic environment variable configuration, build optimization, and production deployment. Use when Claude needs to: (1) Deploy a Next.js frontend to Vercel, (2) Deploy a FastAPI backend to Vercel, (3) Configure environment variables for production, (4) Handle both initial deployment and updates to existing deployments, (5) Troubleshoot common Vercel deployment issues
---

# Vercel Deployment Skill

Automated deployment of Next.js and FastAPI applications to Vercel production.

## Quick Start

```bash
# Frontend deployment
cd frontend && vercel --prod

# Backend deployment
cd backend && vercel --prod
```

## Deployment Patterns

### Frontend (Next.js)

**Environment Variables Required**:
```bash
NEXT_PUBLIC_API_URL=https://your-backend.vercel.app
```

**Common Issues**:
- Build failures: Check for missing env vars
- Runtime errors: Verify API_URL is correct
- Static generation issues: Check `next.config.js`

### Backend (FastAPI)

**Environment Variables Required**:
```bash
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret-key
AI_MODEL=llama-3.1-8b-instant
```

**Common Issues**:
- Worker timeout: Keep functions under 10s execution
- Cold starts: Use `--min-workers` for always-on
- Database connection: Use connection pooling

## Scripts

### `scripts/deploy-frontend.sh`
Automated frontend deployment with env var setup.

### `scripts/deploy-backend.sh`
Automated backend deployment with health check.

## Troubleshooting

See [references/vercel-issues.md](references/vercel-issues.md) for common problems and solutions.

## Post-Deployment Checklist

- [ ] Verify deployment URL is accessible
- [ ] Test critical user flows
- [ ] Check environment variables are set
- [ ] Monitor error logs (Vercel Dashboard)
- [ ] Update production URLs in project docs
