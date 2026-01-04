# DigitalOcean App Platform Examples

This directory contains examples for deploying applications to DigitalOcean App Platform, a serverless Platform-as-a-Service (PaaS) offering.

## What is App Platform?

DigitalOcean App Platform is a fully managed PaaS that makes it easy to build, deploy, and scale apps quickly. It handles:

- Automatic builds from GitHub/GitLab
- Container orchestration
- Load balancing
- SSL certificates
- Auto-scaling
- Log aggregation
- Managed databases

## Examples

### 1. `simple-app.yaml` - Minimal Example
A basic example with:
- Static frontend (HTML/CSS/JS)
- Simple backend API
- Managed PostgreSQL database

**Best for**: Getting started, small projects, prototypes

### 2. `app.yaml` - Full Stack Application
A production-ready example with:
- Frontend (Next.js)
- Backend API (FastAPI)
- Worker service for background jobs
- Managed PostgreSQL with HA
- Redis for caching
- Scheduled cron jobs
- Custom domains
- Auto-scaling
- Health checks
- Alerts

**Best for**: Production applications, full-stack projects

## Prerequisites

1. **DigitalOcean Account**
   ```bash
   # Sign up at https://cloud.digitalocean.com
   ```

2. **doctl CLI**
   ```bash
   # macOS
   brew install doctl

   # Linux
   curl -sL https://github.com/digitalocean/doctl/releases/latest/download/doctl-linux-amd64.tar.gz | tar xz
   sudo mv doctl /usr/local/bin/

   # Windows
   choco install doctl

   # Authenticate
   doctl auth init
   ```

3. **GitHub Repository**
   - Your code must be in a GitHub/GitLab repository
   - App Platform will automatically deploy on push

## Quick Start

### 1. Create Simple App

```bash
# Clone your repository
git clone https://github.com/your-username/simple-app.git
cd simple-app

# Copy the example spec
cp .claude/skills/cloud-deployer/examples/app-platform/simple-app.yaml app.yaml

# Edit app.yaml with your repository details
nano app.yaml

# Create the app
doctl apps create --spec app.yaml

# Get the app URL
doctl apps list
```

### 2. Deploy Full Stack App

```bash
# Clone your repository
git clone https://github.com/your-username/todo-app.git
cd todo-app

# Copy the example spec
cp .claude/skills/cloud-deployer/examples/app-platform/app.yaml app.yaml

# Edit app.yaml with your:
# - GitHub repository URL
# - Branch name
# - Custom domains
# - Environment variables
nano app.yaml

# Deploy the app
doctl apps create --spec app.yaml

# Monitor deployment
doctl apps list
doctl apps deployment-list <app-id>
```

## App Spec Reference

### Core Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Unique name for your app |
| `region` | string | Datacenter region (nyc, sfo, ams, fra, etc.) |
| `domains` | array | Custom domains with SSL |

### Static Sites

```yaml
static_sites:
  - name: frontend
    environment_slug: node-js  # or html, static
    build_command: npm run build
    output_dir: dist
    github:
      repo: your-username/repo
      branch: main
      deploy_on_push: true
    routes:
      - path: /
    env_vars:
      - key: NODE_ENV
        value: production
```

**Supported Static Site Types**:
- `node-js`: Node.js apps (Next.js, Nuxt, etc.)
- `html`: Pure HTML/CSS/JS
- `static`: Static file serving
- `hugo`: Hugo static site generator
- `jekyll`: Jekyll static site generator

### Services

```yaml
services:
  - name: api
    environment_slug: python  # python, node-js, php, ruby, go
    build_command: pip install -r requirements.txt
    run_command: uvicorn main:app --host 0.0.0.0 --port 8080
    http_port: 8080
    instance_size_slug: basic-xxs
    instance_count: 2
    routes:
      - path: /api
    env_vars:
      - key: APP_ENV
        value: production
```

**Supported Service Types**:
- `python`: Python 3.9+
- `node-js`: Node.js 14+
- `php`: PHP 7/8
- `ruby`: Ruby 2.7+
- `go`: Go 1.19+

**Instance Sizes**:
| Size | CPU | RAM | Price |
|------|-----|-----|-------|
| `basic-xxs` | 1 vCPU | 512MB | ~$5/mo |
| `basic-xs` | 1 vCPU | 1GB | ~$12/mo |
| `basic-s` | 1 vCPU | 2GB | ~$24/mo |
| `basic-m` | 2 vCPU | 4GB | ~$48/mo |
| `professional-m` | 4 vCPU | 8GB | ~$96/mo |

### Databases

```yaml
databases:
  - name: db
    engine: PG  # PG, MYSQL, REDIS, MONGODB
    version: "16"
    size: db-s-1vcpu-1gb
    num_nodes: 1
    production: false
```

**Database Engines**:
- `PG`: PostgreSQL (versions: 14, 15, 16)
- `MYSQL`: MySQL (versions: 8)
- `REDIS`: Redis (versions: 6, 7)
- `MONGODB`: MongoDB (versions: 4, 5, 6)

**Database Sizes**:
| Size | CPU | RAM | Storage | Price |
|------|-----|-----|---------|-------|
| `db-s-1vcpu-1gb` | 1 vCPU | 1GB | 10GB | ~$15/mo |
| `db-s-1vcpu-2gb` | 1 vCPU | 2GB | 25GB | ~$30/mo |
| `db-s-2vcpu-4gb` | 2 vCPU | 4GB | 38GB | ~$60/mo |
| `db-s-4vcpu-16gb` | 4 vCPU | 16GB | 115GB | ~$240/mo |

### Workers

```yaml
services:
  - name: worker
    environment_slug: python
    build_command: pip install -r requirements.txt
    run_command: python worker.py
    instance_size_slug: basic-xxs
    instance_count: 1
    # No routes for workers
```

### Cron Jobs

```yaml
crons:
  - name: cleanup
    schedule: "0 */6 * * *"  # Every 6 hours
    command: python -m app.scripts.cleanup
    run_command: python -m app.scripts.cleanup
```

### Auto-scaling

```yaml
services:
  - name: api
    autoscaling:
      min_instance_count: 2
      max_instance_count: 10
      metrics:
        - type: CPU
          target: 70  # Scale when CPU > 70%
        - type: MEMORY
          target: 80  # Scale when memory > 80%
```

## Environment Variables

### Reference Other Components

Use `${component.COMPONENT_VAR}` to reference values from other components:

```yaml
env_vars:
  - key: DATABASE_URL
    value: ${db.DATABASE_HOST}
  - key: REDIS_HOST
    value: ${redis.REDIS_HOST}
```

### Secret Variables

For sensitive data, use app-level secrets:

```bash
# Set via doctl
doctl apps create --spec app.yaml
doctl apps update <app-id> --env JWT_SECRET=your-secret-here

# Or set in dashboard
# https://cloud.digitalocean.com/apps/<app-id>/settings
```

## Custom Domains

### Automatic SSL

```yaml
domains:
  - domain: app.example.com
    type: PRIMARY
    zone: example.com  # Must be managed by DigitalOcean DNS
```

### Manual DNS

If you use external DNS:

```yaml
domains:
  - domain: app.example.com
    type: SPECIFIED
    zone: example.com
```

Then add DNS records:

```
CNAME app.example.com -> <app-url>.ondigitalocean.app
```

## Health Checks

```yaml
services:
  - name: api
    health_check:
      http_path: /health
      initial_delay_seconds: 30
      period_seconds: 10
      timeout_seconds: 5
      success_threshold: 1
      failure_threshold: 3
```

## Alerts

```yaml
alerts:
  - rule: HIGH_CPU_90
    operator: GREATER_THAN
    threshold: 90
    window: "5m"
    count: 3

  - rule: HIGH_MEMORY_90
    operator: GREATER_THAN
    threshold: 90
    window: "5m"
    count: 3
```

**Available Alert Rules**:
- `HIGH_CPU_90`: CPU > 90%
- `HIGH_MEMORY_90`: Memory > 90%
- `HIGH_RESTART_COUNT`: Too many restarts
- `LOW_INSTANCE_COUNT`: Too few instances
- `DEPLOYMENT_FAILED`: Deployment failed
- `DOMAIN_FAILED`: Domain validation failed

## Deployment Strategies

### Deploy on Push

```yaml
github:
  repo: your-username/repo
  branch: main
  deploy_on_push: true
```

### Manual Deployment

```bash
# Trigger deployment
doctl apps create-deployment <app-id>

# From specific branch
doctl apps create-deployment <app-id> --force-rebuild
```

### Zero-Downtime Deployments

App Platform automatically performs rolling deployments with zero downtime for:
- Services with `instance_count > 1`
- All static sites

## Local Development

### Test Locally

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Use doctl

```bash
# List apps
doctl apps list

# Get app info
doctl apps get <app-id>

# Get deployment logs
doctl apps logs <app-id> --type deploy

# Get running logs
doctl apps logs <app-id> --type run --follow

# SSH into container
doctl apps ssh <app-id> --component backend
```

## Monitoring

### View Metrics

```bash
# Get deployment history
doctl apps deployment-list <app-id>

# View logs
doctl apps logs <app-id> --follow

# Get app metrics
doctl apps metrics <app-id>
```

### Dashboard Access

Visit https://cloud.digitalocean.com/apps to view:
- Deployment status
- Resource usage
- Error logs
- Response times
- Custom metrics

## Troubleshooting

### Build Failures

```bash
# View build logs
doctl apps logs <app-id> --type deploy --tail 100

# Common issues:
# - Missing dependencies in requirements.txt/package.json
# - Incorrect build command
# - Port mismatch (http_port must match app port)
```

### Runtime Errors

```bash
# View runtime logs
doctl apps logs <app-id> --type run --follow

# Check health check endpoint
curl https://<app-url>/health
```

### Database Connection Issues

```bash
# Verify database credentials
doctl apps get <app-id>

# Check database is accessible
doctl databases list

# Test connection from app
doctl apps ssh <app-id> --component backend
```

## Cost Optimization

### Reduce Costs

1. **Use smaller instances** for development
   ```yaml
   instance_size_slug: basic-xxs  # $5/mo
   ```

2. **Scale to zero** when not in use
   ```yaml
   # Not directly supported, but use:
   instance_count: 1
   ```

3. **Use dev databases** for non-production
   ```yaml
   production: false
   num_nodes: 1
   ```

4. **Remove unused services**

5. **Set resource limits**
   ```yaml
   resources:
     memory: "512Mi"
     cpu: "500m"
   ```

### Cost Estimation

**Simple App** (1x basic-xxs + dev database):
- Frontend: Free (static sites on basic plan)
- Backend: $5/mo
- Database: $15/mo
- **Total**: ~$20/mo

**Full Stack** (2x basic-xs + HA database + Redis):
- Frontend: Free
- Backend (2 instances): $24/mo
- Worker (1 instance): $12/mo
- Database (HA): $60/mo
- Redis: $15/mo
- **Total**: ~$111/mo

## Best Practices

### 1. Always Use Specific Versions

```yaml
# Bad
environment_slug: python

# Good
environment_slug: python-3.11

# Bad
version: "16"

# Good
version: "16.3"
```

### 2. Set Resource Limits

```yaml
services:
  - name: api
    instance_size_slug: basic-xs
    # Always set minimum
    instance_count: 2  # For HA
```

### 3. Use Health Checks

```yaml
services:
  - name: api
    health_check:
      http_path: /health
      failure_threshold: 3
```

### 4. Configure Auto-scaling

```yaml
services:
  - name: api
    autoscaling:
      min_instance_count: 2  # Always have 2
      max_instance_count: 10  # But no more than 10
```

### 5. Enable Alerts

```yaml
alerts:
  - rule: HIGH_CPU_90
    disabled: false
```

### 6. Use Environment-Specific Configs

```yaml
# Development
databases:
  - name: db
    production: false
    num_nodes: 1

# Production
databases:
  - name: db
    production: true
    num_nodes: 3
```

### 7. Implement Health Checks

```python
# FastAPI
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Node.js/Express
app.get('/health', (req, res) => {
    res.json({ status: 'healthy' });
});
```

### 8. Use CDN for Static Assets

```yaml
static_sites:
  - name: frontend
    cache:
      paths:
        - /static/*
        - /images/*
      default_ttl: 3600
```

### 9. Secure Secrets

```bash
# Never commit secrets
# Use environment variables instead
doctl apps update <app-id> --env API_KEY=xxx
```

### 10. Monitor Deployments

```bash
# Watch deployment progress
doctl apps logs <app-id> --type deploy --follow
```

## Advanced Topics

### Multiple Environments

```bash
# Create dev app
doctl apps create --spec app-dev.yaml

# Create production app
doctl apps create --spec app-prod.yaml
```

### Blue-Green Deployments

```yaml
services:
  - name: api-blue
    routes:
      - path: /api

  - name: api-green
    routes:
      - path: /api
```

### Custom Buildpacks

```yaml
services:
  - name: api
    buildpack: heroku/buildpacks:20
```

### Log Destinations

```yaml
log_destinations:
  - name: datadog
    type: datadog
    datadog:
      api_key: ${datadog.API_KEY}
```

## Migration Guides

### From Docker

If you have a Dockerfile, App Platform can build from it:

```yaml
services:
  - name: api
    dockerfile_path: Dockerfile
    # No build_command needed
```

### From Kubernetes

Key differences:
- App Platform is simpler (no YAML manifests)
- Auto-scaling is built-in
- No need for ingress controllers
- No need for service discovery

### From Heroku

App Platform is very similar to Heroku:

| Heroku | App Platform |
|--------|--------------|
| `Procfile` | `run_command` in app.yaml |
| `heroku ps:scale` | `instance_count` in app.yaml |
| `heroku config:set` | `doctl apps update --env` |
| `heroku addons` | `databases` in app.yaml |

## Further Reading

- [Official App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [App Platform Pricing](https://www.digitalocean.com/pricing/app-platform)
- [doctl Apps Reference](https://docs.digitalocean.com/reference/doctl/reference/apps/)
- [Buildpacks Documentation](https://buildpacks.io/docs/)

## Support

- DigitalOcean Community: https://www.digitalocean.com/community
- App Platform Tutorials: https://docs.digitalocean.com/products/app-platform/how-to/
- doctl GitHub: https://github.com/digitalocean/doctl

## Example Project Structures

### Full Stack Todo App

```
todo-app/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── pages/
│   ├── package.json
│   └── next.config.js
├── worker/
│   ├── app/
│   └── requirements.txt
├── app.yaml
└── README.md
```

### Simple Static Site

```
site/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── app.js
└── app.yaml
```

### Python API Only

```
api/
├── app/
│   └── main.py
├── requirements.txt
└── app.yaml
```
