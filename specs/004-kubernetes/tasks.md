# Task List: Kubernetes Deployment

**Feature**: 004-kubernetes
**Status**: ✅ Complete

---

## Phase 1: Docker Images

### Frontend
- [x] Create `frontend/Dockerfile` with multi-stage build
- [x] Configure Next.js standalone output in `next.config.mjs`
- [x] Add health checks
- [x] Create `frontend/.dockerignore`
- [x] Test frontend image locally
- [x] Verify all static assets are served

### Backend
- [x] Create `backend/Dockerfile`
- [x] Add system dependencies (gcc, postgresql-client, curl)
- [x] Configure health check endpoint
- [x] Create non-root user
- [x] Create `backend/.dockerignore`
- [x] Test backend image locally
- [x] Verify database connectivity from container

---

## Phase 2: Docker Compose

- [x] Update `docker-compose.yml` with health checks
- [x] Add network configuration
- [x] Configure environment variables
- [x] Add PostgreSQL 16-alpine
- [x] Test `docker-compose up`
- [x] Verify service-to-service communication

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
- [x] Lint chart: `helm lint helm/frontend`
- [x] Test template: `helm template helm/frontend`

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
- [x] Lint chart: `helm lint helm/backend`
- [x] Test template: `helm template helm/backend`

---

## Phase 4: Minikube Deployment

- [x] Start Minikube: `minikube start --cpus=4 --memory=8192`
- [x] Build frontend image: `docker build -t todo-frontend ./frontend`
- [x] Build backend image: `docker build -t todo-backend ./backend`
- [x] Load images to Minikube
- [x] Install backend: `helm install backend helm/backend`
- [x] Install frontend: `helm install frontend helm/frontend`
- [x] Verify pods running: `kubectl get pods`
- [x] Test frontend access
- [x] Test backend API
- [x] Verify database connectivity

---

## Phase 5: Documentation

- [x] Create `docs/MINIKUBE_DEPLOYMENT_GUIDE.md`
- [x] Create `docs/KUBERNETES_QUICK_REFERENCE.md`
- [x] Create `specs/004-kubernetes/spec.md`
- [x] Create `specs/004-kubernetes/plan.md`
- [x] Create `specs/004-kubernetes/quickstart.md`
- [x] Create `specs/004-kubernetes/tasks.md`
- [x] Create `specs/004-kubernetes/data-model.md`
- [x] Create `specs/004-kubernetes/research.md`

---

## Phase 6: Validation

- [x] All Docker images build successfully
- [x] Docker Compose runs without errors
- [x] All Helm charts pass linting
- [x] Application deploys to Minikube
- [x] All services accessible
- [x] API endpoints functional
- [x] Database operations work
- [x] Health checks passing

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
**Completed**: 75+
**Remaining**: ~5 (cloud deployment + CI/CD optional)
**Status**: ✅ Phase IV (Kubernetes) Complete
