---
name: cloud-deployer
description: Comprehensive deployment automation for local development, backend services, and cloud platforms. Use when deploying applications: (1) Local development (Docker Compose, Minikube/k3s), (2) Backend deployment (systemd, PM2, Gunicorn), (3) Cloud deployment (Vercel, Kubernetes/DOKS/GKE/AKS), (4) CI/CD pipelines (GitHub Actions), (5) Container registry management, (6) Infrastructure setup (Helm charts, Terraform). Includes automated scripts for all deployment types, reference documentation, and asset templates.
---

# Cloud Deployer

Comprehensive deployment automation covering local development, backend services, and cloud infrastructure.

## Deployment Types

### Local Development
- **Docker Compose**: Full local stack with containers
- **Minikube/k3s**: Local Kubernetes for testing

### Backend Deployment
- **systemd**: Linux service management
- **PM2**: Process manager with monitoring
- **Gunicorn**: Production WSGI server

### Cloud Deployment
- **Vercel**: Serverless deployment
- **Kubernetes**: DOKS, GKE, AKS
- **Helm Charts**: Package management

### CI/CD
- **GitHub Actions**: Automated pipelines
- **Container Registries**: DO, GCR, ACR

## Quick Reference

| Deployment | Script | Reference |
|------------|--------|-----------|
| Docker Compose | `scripts/local/deploy-docker-compose.sh` | `references/local-deployment.md` |
| Minikube | `scripts/local/deploy-minikube.sh` | `references/local-deployment.md` |
| systemd | `scripts/backend/deploy-systemd.sh` | `references/backend-deployment.md` |
| PM2 | `scripts/backend/deploy-pm2.sh` | `references/backend-deployment.md` |
| Kubernetes | `scripts/cloud/deploy-kubernetes.sh` | `references/cloud-deployment.md` |
| Vercel | `scripts/cloud/deploy-vercel.sh` | `references/cloud-deployment.md` |
| CI/CD | `scripts/cloud/deploy-cicd.sh` | `references/cloud-deployment.md` |

## Deployment Workflows

### 1. Local Development (Docker Compose)

**When to use**: Daily development, testing full stack locally

```bash
# Start all services
./scripts/local/deploy-docker-compose.sh up

# View logs
./scripts/local/deploy-docker-compose.sh logs

# Stop services
./scripts/local/deploy-docker-compose.sh down
```

**Requirements**: Docker, Docker Compose

**Key files**:
- `docker-compose.yml` - Service orchestration
- `.env` - Environment configuration
- `assets/templates/docker-compose.yml` - Template

### 2. Local Kubernetes (Minikube)

**When to use**: Testing K8s manifests before production

```bash
# Start Minikube
./scripts/local/deploy-minikube.sh start

# Deploy to Minikube
./scripts/local/deploy-minikube.sh deploy

# Access via tunnel
./scripts/local/deploy-minikube.sh tunnel
```

**Requirements**: Minikube, kubectl

**See**: `references/local-deployment.md` for Minikube setup and troubleshooting

### 3. Backend Deployment (systemd)

**When to use**: Production Linux servers, VPS deployment

```bash
# Install systemd service
sudo ./scripts/backend/deploy-systemd.sh install

# Start service
sudo ./scripts/backend/deploy-systemd.sh start

# Check status
sudo ./scripts/backend/deploy-systemd.sh status
```

**Requirements**: Linux with systemd, Python 3.13+

**Key variables**:
- `SERVICE_NAME` - Service name (default: todo-backend)
- `WORK_DIR` - Application directory (default: /opt/todo-backend)
- `VENV_DIR` - Virtual environment path

**See**: `references/backend-deployment.md` for systemd configuration and Nginx reverse proxy

### 4. Backend Deployment (PM2)

**When to use**: Node.js environments, need process monitoring

```bash
# Start with PM2
./scripts/backend/deploy-pm2.sh start

# Monitor
./scripts/backend/deploy-pm2.sh monit

# Zero-downtime reload
./scripts/backend/deploy-pm2.sh reload
```

**Requirements**: Node.js, PM2

**See**: `references/backend-deployment.md` for PM2 ecosystem configuration

### 5. Cloud Deployment (Kubernetes)

**When to use**: Production cloud deployment, scalable infrastructure

```bash
# Deploy to cluster
CLUSTER=do-fra1-hackathon2 ./scripts/cloud/deploy-kubernetes.sh deploy

# Check status
CLUSTER=do-fra1-hackathon2 ./scripts/cloud/deploy-kubernetes.sh status

# Rollback
CLUSTER=do-fra1-hackathon2 ./scripts/cloud/deploy-kubernetes.sh rollback 2
```

**Requirements**: kubectl configured for target cluster

**Key variables**:
- `CLUSTER` - Kubernetes cluster context
- `NAMESPACE` - Target namespace (default: default)
- `REGISTRY` - Container registry URL

**See**: `references/cloud-deployment.md` for cluster setup, Helm charts, and troubleshooting

### 6. Cloud Deployment (Vercel)

**When to use**: Serverless deployment, quick prototyping

```bash
# Deploy frontend to production
./scripts/cloud/deploy-vercel.sh frontend prod

# Deploy backend preview
./scripts/cloud/deploy-vercel.sh backend preview

# List deployments
./scripts/cloud/deploy-vercel.sh list
```

**Requirements**: Vercel CLI, Vercel token

**See**: `references/cloud-deployment.md` for Vercel configuration

### 7. CI/CD Setup (GitHub Actions)

**When to use**: Automated testing and deployment

```bash
# Setup workflow
./scripts/cloud/deploy-cicd.sh setup

# Validate workflow
./scripts/cloud/deploy-cicd.sh validate
```

**Creates**: `.github/workflows/ci-cd.yml`

**Required secrets**:
- `DIGITALOCEAN_ACCESS_TOKEN`
- `DOCKER_USERNAME` / `DOCKER_PASSWORD`
- `KUBERNETES_CLUSTER` / `KUBERNETES_NAMESPACE`
- `VERCEL_TOKEN` (optional)

**See**: `references/cloud-deployment.md` for workflow customization

## Deployment Selection Guide

Choose deployment type based on your needs:

| Scenario | Recommended Deployment |
|----------|----------------------|
| Local development | Docker Compose |
| Testing K8s manifests | Minikube |
| Production server | systemd + Gunicorn |
| Need process monitoring | PM2 |
| Cloud production | Kubernetes (Helm) |
| Quick deployment | Vercel |
| Automated pipeline | GitHub Actions |

## Common Patterns

### Multi-Environment Setup

1. **Development**: Docker Compose locally
2. **Staging**: Minikube or small K8s cluster
3. **Production**: Kubernetes with HPA

### Blue-Green Deployment

```bash
# Deploy blue
kubectl apply -f k8s/blue-deployment.yaml

# Test blue
# ... run tests ...

# Switch traffic to blue
kubectl apply -f k8s/service-blue.yaml

# Deploy green
kubectl apply -f k8s/green-deployment.yaml
```

### Canary Deployment

```bash
# Initial deployment (90% old, 10% new)
kubectl apply -f k8s/canary-deployment.yaml

# Gradually increase traffic
kubectl scale deployment/new-version --replicas=2
kubectl scale deployment/old-version --replicas=8
```

## Asset Templates

Use templates in `assets/templates/`:

- **Dockerfile.backend** - Multi-stage FastAPI build
- **Dockerfile.frontend** - Multi-stage Next.js build
- **docker-compose.yml** - Full stack orchestration
- **service.template** - systemd service template
- **k8s-deployment.yaml** - Kubernetes manifest template

## Troubleshooting

### Docker Compose Issues

**Port conflicts**:
```bash
# Check ports
netstat -tulpn | grep :3000
# Change ports in docker-compose.yml
```

**Volume errors**:
```bash
docker-compose down -v
docker volume prune
docker-compose up -d
```

### Backend Service Issues

**Service won't start**:
```bash
sudo systemctl status todo-backend
sudo journalctl -u todo-backend -n 50
```

**Permission errors**:
```bash
sudo chown -R www-data:www-data /opt/todo-backend
```

### Kubernetes Issues

**Pods not starting**:
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**Image pull errors**:
```bash
kubectl get secret registry-pull-secret -o yaml
# Verify credentials
```

**DNS issues**:
```bash
kubectl run debug --image=nicolaka/netshoot -it --rm
# Inside pod: nslookup todo-backend
```

## Best Practices

1. **Always test locally first** - Use Docker Compose before cloud deployment
2. **Use environment variables** - Never hardcode credentials
3. **Secure secrets** - Use Kubernetes secrets or external secret managers
4. **Resource limits** - Set memory/CPU limits in Kubernetes
5. **Health checks** - Always define liveness and readiness probes
6. **Log rotation** - Prevent disk filling with logs
7. **Monitoring** - Set up logging and metrics for production
8. **Rollback plan** - Always know how to rollback quickly

## Environment Variables

Create `.env` file in project root:

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=tododb
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/tododb

# Backend
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
GROQ_API_KEY=your-groq-key
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Deployment
CLUSTER=do-fra1-hackathon2
NAMESPACE=default
REGISTRY=registry.digitalocean.com
```

## Quick Start Commands

```bash
# Local development
docker-compose up -d

# Deploy to local Kubernetes
eval $(minikube docker-env)
kubectl apply -f k8s/

# Deploy to cloud
CLUSTER=do-fra1-hackathon2 ./scripts/cloud/deploy-kubernetes.sh deploy

# Setup CI/CD
./scripts/cloud/deploy-cicd.sh setup
```

## Related Skills

- **cloud-ops**: Infrastructure operations and DevOps automation (merged into this skill)
- **deployment-validator**: Validate deployments before going live
- **dapr-events**: Event-driven architecture for microservices
