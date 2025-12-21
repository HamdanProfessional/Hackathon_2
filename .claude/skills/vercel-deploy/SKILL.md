---
name: vercel-deploy
description: Comprehensive Vercel deployment automation for frontend and backend applications with production optimization, error handling, validation, and rollback capabilities. Use when Claude needs to: (1) Deploy Next.js frontend applications to Vercel, (2) Deploy FastAPI/Python backend APIs to Vercel serverless functions, (3) Handle environment variable configuration and secrets management, (4) Optimize build processes and caching strategies, (5) Validate deployment readiness and troubleshoot deployment issues, (6) Perform rollback operations for failed deployments
---

# Vercel Deployment Skill

## Quick Start

Deploy frontend to Vercel production:
```bash
cd frontend && vercel --prod
```

Deploy backend to Vercel production:
```bash
cd backend && vercel --prod
```

## Deployment Validation

Before deploying, always validate project readiness:

### Frontend Validation
- Check `package.json` for build scripts
- Verify Next.js configuration
- Validate environment variables
- Ensure production build works locally

### Backend Validation
- Check `vercel.json` configuration
- Validate serverless function entry point
- Verify database connectivity
- Test API endpoints locally

## Frontend Deployment (Next.js)

### Prerequisites
- Next.js 14+ with App Router recommended
- `package.json` with build script
- `next.config.js` (if custom configuration needed)

### Environment Setup
```bash
# Set production environment variables
vercel env add NEXT_PUBLIC_API_URL
vercel env add DATABASE_URL
vercel env add JWT_SECRET
```

### Deployment Commands
```bash
# Development deployment
vercel

# Production deployment
vercel --prod

# Deploy with specific configuration
vercel --prod --debug
```

### Common Frontend Issues & Solutions

#### Build Failures
```bash
# Check build logs
vercel logs [deployment-url]

# Common fixes:
# 1. Update dependencies
npm update

# 2. Clear build cache
rm -rf .next && vercel --prod
```

#### Environment Variables Not Available
```bash
# Verify variable names and scopes
vercel env ls

# Add missing variables with correct scope
vercel env add VAR_NAME --scope production
```

## Backend Deployment (FastAPI/Python)

### Prerequisites
- FastAPI application with proper entry point
- `vercel.json` configuration file
- `requirements.txt` or `pyproject.toml`

### Serverless Function Setup
```python
# api/index.py (Vercel entry point)
from app.main import app
handler = app
```

### Vercel Configuration
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

### Python Dependencies
```bash
# requirements.txt or pyproject.toml
# Ensure production-ready versions
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
```

## Advanced Deployment Strategies

### Multi-Environment Deployments
```bash
# Development
vercel --env development

# Staging
vercel --env staging

# Production
vercel --prod
```

### Custom Domains
```bash
# Add custom domain
vercel domains add yourdomain.com

# Verify domain setup
vercel domains ls
```

### Build Optimization
```javascript
// next.config.js
module.exports = {
  // Enable turbopack for faster builds
  experimental: {
    turbo: {
      loaders: {
        '.svg': ['@svgr/webpack'],
      },
    },
  },

  // Optimize images
  images: {
    domains: ['your-api-domain.com'],
    format: ['image/webp', 'image/avif'],
  },

  // Compress responses
  compress: true,

  // Enable SWC minification
  swcMinify: true,
};
```

## Environment Variables Management

### Frontend Variables
```bash
# Public variables (available in browser)
vercel env add NEXT_PUBLIC_API_URL --scope production

# Backend-only variables
vercel env add API_SECRET_KEY --scope production
```

### Backend Variables
```bash
# Database configuration
vercel env add DATABASE_URL --scope production

# Authentication
vercel env add JWT_SECRET --scope production
vercel env add AI_API_KEY --scope production

# External services
vercel env add REDIS_URL --scope production
```

## Monitoring and Health Checks

### Deployment Health Check
```bash
# Check deployment status
vercel inspect [deployment-url]

# View real-time logs
vercel logs [deployment-url] --follow

# Health endpoint test
curl https://your-app.vercel.app/health
```

### Performance Monitoring
```bash
# View deployment analytics
vercel analytics

# Check build performance
vercel build --debug
```

## Rollback Procedures

### Emergency Rollback
```bash
# List recent deployments
vercel ls

# Rollback to previous deployment
vercel rollback [deployment-id]

# Promote previous deployment to production
vercel promote [deployment-id] --scope production
```

### Rollback Validation
```bash
# Test critical functionality
curl -X POST https://your-app.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'

# Verify database connectivity
curl https://your-app.vercel.app/health
```

## Troubleshooting Guide

### Common Deployment Errors

#### 1. Build Timeout
```bash
# Solution: Optimize build process
# - Reduce dependencies
# - Use build caching
# - Split large applications
```

#### 2. Memory Issues
```bash
# Check memory usage
vercel logs [deployment-url] | grep "Memory"

# Solution: Optimize memory usage
# - Reduce bundle size
# - Implement lazy loading
# - Optimize database queries
```

#### 3. Database Connection Issues
```bash
# Test database connection
curl https://your-app.vercel.app/test-db

# Common solutions:
# - Check connection string format
# - Verify SSL configuration
# - Ensure database allows Vercel IP addresses
```

#### 4. CORS Issues
```bash
# Test CORS configuration
curl -H "Origin: https://your-frontend.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://your-backend.vercel.app/api/test

# Solution: Update CORS middleware
```

## Production Optimization

### Frontend Optimization
- Enable Next.js Image optimization
- Implement code splitting
- Use ISR for static content
- Configure CDN caching
- Optimize bundle size

### Backend Optimization
- Implement request caching
- Use connection pooling
- Optimize database queries
- Enable serverless function warmup
- Configure proper timeouts

### Security Best Practices
- Use HTTPS everywhere
- Implement rate limiting
- Sanitize user inputs
- Use environment variables for secrets
- Enable security headers

## Deployment Scripts

### Automated Frontend Deployment
```bash
#!/bin/bash
# deploy-frontend.sh

echo "🚀 Deploying frontend to Vercel..."

# Validate build
npm run build
if [ $? -eq 0 ]; then
    echo "✅ Build successful"
    vercel --prod
    echo "🎉 Frontend deployed successfully!"
else
    echo "❌ Build failed"
    exit 1
fi
```

### Automated Backend Deployment
```bash
#!/bin/bash
# deploy-backend.sh

echo "🚀 Deploying backend to Vercel..."

# Test locally first
python -m pytest
if [ $? -eq 0 ]; then
    echo "✅ Tests passed"
    vercel --prod
    echo "🎉 Backend deployed successfully!"
else
    echo "❌ Tests failed"
    exit 1
fi
```

## Post-Deployment Checklist

- [ ] Test user registration/login
- [ ] Verify API endpoints respond correctly
- [ ] Check database connectivity
- [ ] Validate environment variables
- [ ] Test frontend-backend communication
- [ ] Monitor error logs
- [ ] Verify custom domains work
- [ ] Test critical user workflows
- [ ] Check performance metrics
- [ ] Set up monitoring alerts

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          scope: ${{ secrets.VERCEL_SCOPE }}
```