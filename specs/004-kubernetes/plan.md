# Implementation Plan: Kubernetes Deployment

**Feature**: 004-kubernetes
**Created**: 2025-12-23
**Estimated Duration**: 5-7 days
**Status**: 🚧 In Progress

---

## Overview

This plan breaks down the implementation of Kubernetes deployment for the Todo application into manageable phases.

---

## Phase 1: Docker Image Creation (Days 1-2)

### Frontend Dockerfile

**File**: `frontend/Dockerfile`

**Steps**:
1. Create multi-stage Dockerfile
2. Configure Next.js 14 standalone output
3. Add health checks
4. Test locally

**Commands**:
```bash
cd frontend
docker build -t todo-frontend:latest .
docker run -p 3000:3000 todo-frontend:latest
```

**Validation**:
- [ ] Image builds without errors
- [ ] Container starts successfully
- [ ] Application accessible at http://localhost:3000
- [ ] No console errors in browser

### Backend Dockerfile

**File**: `backend/Dockerfile`

**Steps**:
1. Create Dockerfile with Python 3.13
2. Add system dependencies (gcc, postgresql-client, curl)
3. Configure health check endpoint
4. Create non-root user

**Commands**:
```bash
cd backend
docker build -t todo-backend:latest .
docker run -p 8000:8000 todo-backend:latest
curl http://localhost:8000/health
```

**Validation**:
- [ ] Image builds without errors
- [ ] Health check responds
- [ ] API endpoints accessible
- [ ] Database connectivity works

### .dockerignore Files

**Files**:
- `frontend/.dockerignore`
- `backend/.dockerignore`

**Purpose**: Exclude unnecessary files from build context

**Validation**:
- [ ] Build context is smaller
- [ ] No sensitive files included
- [ ] Build speed improved

---

## Phase 2: Docker Compose (Day 2)

### docker-compose.yml

**File**: `docker-compose.yml`

**Services**:
- **frontend**: Next.js on port 3000
- **backend**: FastAPI on port 8000
- **postgres**: PostgreSQL 16 on port 5432

**Commands**:
```bash
docker-compose up
```

**Validation**:
- [ ] All services start
- [ ] Frontend accessible
- [ ] Backend API working
- [ ] Database connectivity

---

## Phase 3: Helm Charts Creation (Days 3-4)

### Frontend Helm Chart

**Directory**: `helm/frontend/`

**Files**:
- `Chart.yaml`: Chart metadata
- `values.yaml`: Default configuration
- `templates/deployment.yaml`: Pod deployment
- `templates/service.yaml`: Service definition
- `templates/ingress.yaml`: Ingress (optional)
- `templates/configmap.yaml`: Environment variables
- `templates/hpa.yaml`: Horizontal Pod Autoscaler
- `templates/_helpers.tpl`: Template helpers
- `templates/NOTES.txt`: Post-install notes

**Commands**:
```bash
helm lint helm/frontend
helm template helm/frontend --debug
helm install --dry-run --debug frontend helm/frontend
```

### Backend Helm Chart

**Directory**: `helm/backend/`

**Files**:
- `Chart.yaml`: Chart metadata
- `values.yaml`: Default configuration
- `templates/deployment.yaml`: Pod deployment
- `templates/service.yaml`: Service definition
- `templates/ingress.yaml`: Ingress (optional)
- `templates/secrets.yaml`: Sensitive data
- `templates/configmap.yaml`: Environment variables
- `templates/hpa.yaml`: Horizontal Pod Autoscaler
- `templates/_helpers.tpl`: Template helpers
- `templates/NOTES.txt`: Post-install notes

**Commands**:
```bash
helm lint helm/backend
helm template helm/backend --debug
helm install --dry-run --debug backend helm/backend
```

**Validation**:
- [ ] Charts pass linting
- [ ] Templates render correctly
- [ ] Dry-run install succeeds
- [ ] NOTES.txt displays helpful info

---

## Phase 4: Minikube Deployment (Days 5-6)

### Minikube Setup

**Commands**:
```bash
# Install Minikube (if not installed)
# Windows: choco install minikube

# Start Minikube
minikube start --cpus=4 --memory=8192

# Enable ingress (optional)
minikube addons enable ingress

# Verify
kubectl cluster-info
kubectl get nodes
```

### Build and Load Images

**Commands**:
```bash
# Build images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# Load into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Verify
minikube image ls | grep todo
```

### Install Helm Charts

**Commands**:
```bash
# Install backend
helm install backend helm/backend

# Install frontend
helm install frontend helm/frontend

# Verify
kubectl get pods
kubectl get svc
```

### Test Deployment

**Commands**:
```bash
# Check pods
kubectl get pods -w

# Access services
minikube service backend --url
minikube service frontend --url

# Or use tunnel
minikube tunnel
# Access at localhost:30001 (frontend) and localhost:30002 (backend)
```

**Validation**:
- [ ] All pods Running (2/2)
- [ ] Services accessible
- [ ] Frontend loads without errors
- [ ] Backend API responds
- [ ] Database connectivity works

---

## Phase 5: Documentation (Day 7)

### Create Documentation Files

**Files**:
- `docs/MINIKUBE_DEPLOYMENT_GUIDE.md`: Complete deployment guide
- `docs/KUBERNETES_QUICK_REFERENCE.md`: kubectl/Helm commands cheat sheet

**Content**:
- Prerequisites and installation
- Step-by-step deployment
- Troubleshooting guide
- Common commands
- YAML examples

---

## Rollback Plan

If any step fails:

1. **Docker Build Fails**:
   - Check Dockerfile syntax
   - Verify dependencies in requirements.txt/package.json
   - Check for missing files

2. **Helm Chart Fails**:
   - Run `helm lint` for syntax errors
   - Check template rendering with `helm template`
   - Review values.yaml configuration

3. **Minikube Deployment Fails**:
   - Check pod status: `kubectl describe pod <name>`
   - View logs: `kubectl logs <pod-name>`
   - Delete and reinstall: `helm uninstall <release>`

---

## Success Criteria

Phase 4 is complete when:
- [ ] Docker images build and run locally
- [ ] Docker Compose starts all services
- [ ] Helm charts pass all lint checks
- [ ] Application deploys to Minikube
- [ ] All services accessible and functional
- [ ] Documentation complete

---

## Next Steps

After Phase 4 completion:
1. **Phase 5**: Cloud deployment (DOKS/GKE/AKS)
2. **Phase 5**: CI/CD pipeline setup
3. **Phase 5**: Monitoring and logging
4. **Phase 5**: Advanced features
