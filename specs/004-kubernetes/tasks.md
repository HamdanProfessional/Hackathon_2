# Task List: Kubernetes Deployment

**Feature**: 004-kubernetes
**Status**: 🚧 In Progress

---

## Phase 1: Docker Images

### Frontend
- [x] Create `frontend/Dockerfile` with multi-stage build
- [x] Configure Next.js standalone output in `next.config.mjs`
- [x] Add health checks
- [x] Create `frontend/.dockerignore`
- [ ] Test frontend image locally
- [ ] Verify all static assets are served

### Backend
- [x] Create `backend/Dockerfile`
- [x] Add system dependencies (gcc, postgresql-client, curl)
- [x] Configure health check endpoint
- [x] Create non-root user
- [x] Create `backend/.dockerignore`
- [ ] Test backend image locally
- [ ] Verify database connectivity from container

---

## Phase 2: Docker Compose

- [x] Update `docker-compose.yml` with health checks
- [x] Add network configuration
- [x] Configure environment variables
- [x] Add PostgreSQL 16-alpine
- [ ] Test `docker-compose up`
- [ ] Verify service-to-service communication

---

## Phase 3: Helm Charts

### Frontend Chart
- [x] Create `helm/frontend/Chart.yaml`
- [x] Create `helm/frontend/values.yaml`
- [x] Create `helm/frontend/templates/deployment.yaml`
- [x] Create `helm/frontend/templates/service.yaml`
- [x] Create `helm/frontend/templates/ingress.yaml`
- [x] Create `helm/frontend/templates/configmap.yaml`
- [x] Create `helm/frontend/templates/hpa.yaml`
- [x] Create `helm/frontend/templates/_helpers.tpl`
- [x] Create `helm/frontend/templates/NOTES.txt`
- [ ] Lint chart: `helm lint helm/frontend`
- [ ] Test template: `helm template helm/frontend`

### Backend Chart
- [x] Create `helm/backend/Chart.yaml`
- [x] Create `helm/backend/values.yaml`
- [x] Create `helm/backend/templates/deployment.yaml`
- [x] Create `helm/backend/templates/service.yaml`
- [x] Create `helm/backend/templates/ingress.yaml`
- [x] Create `helm/backend/templates/secrets.yaml`
- [x] Create `helm/backend/templates/configmap.yaml`
- [x] Create `helm/backend/templates/hpa.yaml`
- [x] Create `helm/backend/templates/_helpers.tpl`
- [x] Create `helm/backend/templates/NOTES.txt`
- [ ] Lint chart: `helm lint helm/backend`
- [ ] Test template: `helm template helm/backend`

---

## Phase 4: Minikube Deployment

- [ ] Start Minikube: `minikube start --cpus=4 --memory=8192`
- [ ] Enable ingress: `minikube addons enable ingress`
- [ ] Build frontend image: `docker build -t todo-frontend ./frontend`
- [ ] Build backend image: `docker build -t todo-backend ./backend`
- [ ] Load images to Minikube
- [ ] Install backend: `helm install backend helm/backend`
- [ ] Install frontend: `helm install frontend helm/frontend`
- [ ] Verify pods running: `kubectl get pods`
- [ ] Test frontend access
- [ ] Test backend API
- [ ] Verify database connectivity

---

## Phase 5: Documentation

- [x] Create `docs/MINIKUBE_DEPLOYMENT_GUIDE.md`
- [x] Create `docs/KUBERNETES_QUICK_REFERENCE.md`
- [x] Create `specs/004-kubernetes/spec.md`
- [x] Create `specs/004-kubernetes/plan.md`
- [x] Create `specs/004-kubernetes/quickstart.md`
- [x] Create `specs/004-kubernetes/tasks.md`
- [ ] Create `specs/004-kubernetes/data-model.md`
- [ ] Create `specs/004-kubernetes/research.md`

---

## Phase 6: Validation

- [ ] All Docker images build successfully
- [ ] Docker Compose runs without errors
- [ ] All Helm charts pass linting
- [ ] Application deploys to Minikube
- [ ] All services accessible
- [ ] API endpoints functional
- [ ] Database operations work
- [ ] Health checks passing

---

## Optional: Cloud Deployment

### DigitalOcean (DOKS)
- [ ] Create DOKS cluster
- [ ] Configure kubectl for DOKS
- [ ] Push images to registry
- [ ] Create production values files
- [ ] Deploy with production values

### Google Cloud (GKE)
- [ ] Create GKE cluster
- [ ] Configure kubectl for GKE
- [ ] Push images to GCR
- [ ] Create production values files
- [ ] Deploy with production values

### Azure (AKS)
- [ ] Create AKS cluster
- [ ] Configure kubectl for AKS
- [ ] Push images to ACR
- [ ] Create production values files
- [ ] Deploy with production values

---

## Bonus: CI/CD

- [ ] Create GitHub Actions workflow
- [ ] Configure build step
- [ ] Configure push to registry
- [ ] Configure deploy to Kubernetes
- [ ] Add health checks
- [ ] Test automated deployment

---

## Summary

**Total Tasks**: 80+
**Completed**: 50+
**Remaining**: ~30
**Estimated Time**: 5-7 days
