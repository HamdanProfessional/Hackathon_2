# Feature Specification: Kubernetes Deployment

**Feature Branch**: `004-kubernetes`
**Created**: 2025-12-23
**Updated**: 2025-12-23
**Status**: ✅ Complete - All Validation Tests Passed
**Input**: Phase IV: Kubernetes Deployment - Containerize and deploy to Kubernetes using Minikube for local development and production-ready Helm charts

---

## 📋 Implementation Summary

### 🎯 Goal
Transform the monolithic Vercel deployment into a containerized architecture suitable for scalable cloud deployment on platforms like DigitalOcean Kubernetes (DOKS), Google Kubernetes Engine (GKE), or Azure Kubernetes Service (AKS).

### ✅ Completed Features

| Feature | Status | Notes |
|---------|--------|-------|
| Frontend Dockerfile | ✅ Complete | Multi-stage Next.js 14 build |
| Backend Dockerfile | ✅ Complete | Production FastAPI with health checks |
| Docker Compose | ✅ Complete | Local development setup |
| Frontend Helm Chart | ✅ Complete | Deployment, Service, Ingress, HPA |
| Backend Helm Chart | ✅ Complete | Deployment, Service, Ingress, Secrets |
| .dockerignore Files | ✅ Complete | Build optimization |
| Deployment Guides | ✅ Complete | Minikube and Kubernetes quick reference |

### 🔧 Technical Implementation

| Component | Technology | Status |
|-----------|------------|--------|
| **Frontend Image** | node:20-alpine | ✅ Complete |
| **Backend Image** | python:3.13-slim | ✅ Complete |
| **Helm Charts** | Helm 3 | ✅ Complete |
| **Service Type** | NodePort (Minikube) | ✅ Configured |
| **Ingress** | Nginx (Optional) | ✅ Template ready |

---

## User Scenarios & Testing

### User Story 1 - Containerized Local Development

Developers can run the entire application stack locally using Docker Compose, ensuring parity between development and production environments.

**Acceptance Scenarios**:

1. **Given** developer clones repository, **When** they run `docker-compose up`, **Then** all services (frontend, backend, postgres) start successfully
2. **Given** services are running, **When** accessing http://localhost:3000, **Then** frontend loads without errors
3. **Given** frontend is loaded, **When** creating a task, **Then** it persists to PostgreSQL database

### User Story 2 - Minikube Deployment

Developers can deploy the application to Minikube for Kubernetes testing before cloud deployment.

**Acceptance Scenarios**:

1. **Given** Minikube is running, **When** building and loading images, **Then** images are available in Minikube
2. **Given** images are loaded, **When** installing Helm charts, **Then** pods reach Running state
3. **Given** pods are running, **When** accessing via Minikube tunnel, **Then** application is functional

### User Story 3 - Production Cloud Deployment

Developers can deploy to cloud Kubernetes (DOKS/GKE/AKS) using production Helm charts.

**Acceptance Scenarios**:

1. **Given** cloud cluster is ready, **When** pushing images to registry, **Then** images are accessible
2. **Given** images are available, **When** installing with production values, **Then** services deploy successfully
3. **Given** services are deployed, **When** accessing via LoadBalancer IP, **Then** application responds correctly

---

## Technical Specification

### Frontend Docker Image

**Base**: `node:20-alpine`
**Stages**:
1. **deps**: Install dependencies with `npm ci`
2. **builder**: Production build with `npm run build`
3. **runner**: Standalone Next.js server

**Configuration**:
- **Port**: 3000
- **User**: nextjs (UID 1001)
- **Output**: Standalone mode
- **Health Check**: HTTP GET /

### Backend Docker Image

**Base**: `python:3.13-slim`
**Stages**:
1. **system**: Install gcc, postgresql-client, curl
2. **python**: Install Python dependencies
3. **app**: Copy application code

**Configuration**:
- **Port**: 8000
- **User**: appuser (UID 1001)
- **Health Check**: HTTP GET /health
- **Runtime**: uvicorn app.main:app

### Helm Charts

#### Frontend Chart (`helm/frontend/`)

**Templates**:
- `deployment.yaml`: 2 replicas, resource limits, security context
- `service.yaml`: NodePort 30001 (or LoadBalancer for cloud)
- `ingress.yaml`: Optional ingress for domain routing
- `configmap.yaml`: NEXT_PUBLIC_API_URL configuration
- `hpa.yaml`: Horizontal Pod Autoscaler (optional)

**Resources**:
- Requests: 128Mi memory, 100m CPU
- Limits: 512Mi memory, 500m CPU

#### Backend Chart (`helm/backend/`)

**Templates**:
- `deployment.yaml`: 2 replicas, resource limits, security context
- `service.yaml`: NodePort 30002 (or LoadBalancer for cloud)
- `ingress.yaml`: Optional ingress for API routing
- `secrets.yaml`: Database URL, JWT, AI keys
- `configmap.yaml`: CORS, app settings
- `hpa.yaml`: Horizontal Pod Autoscaler (optional)

**Resources**:
- Requests: 256Mi memory, 200m CPU
- Limits: 1Gi memory, 1000m CPU

### Docker Compose

**Services**:
- `frontend`: Next.js on port 3000
- `backend`: FastAPI on port 8000
- `postgres`: PostgreSQL 16 on port 5432

**Network**: `todo-network` (bridge)

**Health Checks**:
- Backend: `/health` endpoint
- Postgres: `pg_isready`

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                     Ingress Controller (Nginx)                   │  │
│  │  ┌────────────────┐  ┌─────────────────┐                      │  │
│  │  │  Frontend SVC   │  │   Backend SVC    │                      │  │
│  │  │  (NodePort/CLB) │  │  (NodePort/CLB)  │                      │  │
│  │  └────────┬───────┘  └────────┬────────┘                      │  │
│  │           │                    │                               │  │
│  │  ┌────────▼────────┐  ┌───────▼──────────┐                    │  │
│  │  │ Frontend Pod    │  │   Backend Pod     │                    │  │
│  │  │ (Next.js 14)    │  │   (FastAPI)       │                    │  │
│  │  │ Port: 3000      │  │   Port: 8000      │                    │  │
│  │  └─────────────────┘  └──────────────────┘                    │  │
│  │                                                                │  │
│  │  ┌────────────────────────────────────────────────────────┐   │  │
│  │  │              Neon PostgreSQL (External)                     │   │  │
│  │  │         postgresql+asyncpg://neon-db...                │   │  │
│  │  └────────────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Model

**No new database tables** - This phase is deployment-focused only.

Existing tables from Phases I-III remain unchanged.

---

## API Contract

**No new API endpoints** - Existing Phase II/III APIs remain unchanged.

Frontend communicates with backend using existing REST API:
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `POST /api/chat` - Chat with AI (Phase III)

---

## Dependencies

### External Services
- **Neon PostgreSQL**: External database (existing)
- **Container Registry**: Docker Hub / GHCR (new)

### Tools Required
- **Docker**: 20.10+
- **Helm**: 3.0+
- **Minikube**: 1.25+ (for local testing)
- **kubectl**: 1.25+

---

## Non-Functional Requirements

### Performance
- **Pod Startup**: <30 seconds
- **API Response**: <500ms
- **Resource Limits**: As specified in Helm charts

### Security
- **Non-root User**: All containers run as non-root
- **Secrets Management**: Kubernetes Secrets for sensitive data
- **Network Policies**: Restrict pod communication (optional)

### Reliability
- **Replicas**: Minimum 2 per service
- **Health Checks**: Liveness and readiness probes
- **Resource Limits**: Prevent memory/CPU exhaustion

### Scalability
- **HPA**: Horizontal Pod Autoscaler (optional)
- **Cluster Autoscaler**: Add nodes on pressure (cloud)
- **Load Balancing**: Service (LoadBalancer) distributes traffic

---

## Validation Criteria

### Docker Images
- [x] Frontend image builds: `docker build -t todo-frontend ./frontend`
- [x] Backend image builds: `docker build -t todo-backend ./backend`
- [x] Frontend runs: `docker run -p 3000:3000 todo-frontend`
- [x] Backend runs: `docker run -p 8000:8000 todo-backend`

### Docker Compose
- [x] `docker-compose up` starts all services
- [x] Frontend accessible at http://localhost:3000
- [x] Backend accessible at http://localhost:8000
- [x] Database connectivity works

### Helm Charts
- [x] Charts pass linting: `helm lint helm/frontend helm/backend`
- [x] Templates render: `helm template helm/frontend`
- [x] Frontend installs: `helm install frontend helm/frontend`
- [x] Backend installs: `helm install backend helm/backend`

### Minikube Deployment
- [x] Minikube starts successfully
- [x] Images load into Minikube
- [x] Pods reach Running state (2/2 each)
- [x] Services accessible via NodePort

---

### ✅ Validation Test Results (2025-12-23)

**Test Suite**: `tests/test_phase4_kubernetes.py`
**Total Tests**: 8 categories
**Passed**: 8 (100%)
**Failed**: 0

| Test Category | Result | Details |
|---------------|--------|---------|
| Dockerfiles | ✅ Pass | Frontend & Backend Dockerfiles exist with proper base images |
| .dockerignore Files | ✅ Pass | Both frontend and backend exclude build artifacts |
| Docker Compose | ✅ Pass | Complete compose file with frontend, backend, postgres |
| Helm Charts Structure | ✅ Pass | Frontend (5 templates) & Backend (6 templates) |
| Helm Chart Validity | ✅ Pass | Both charts pass `helm lint` |
| Helm Values Configuration | ✅ Pass | Image, service, secrets properly configured |
| Deployment Guides | ✅ Pass | README.md files for both charts |
| Security Hardening | ✅ Pass | Non-root user, security context, resource limits |

**Security Features Verified**:
- ✅ `runAsNonRoot: true` in both charts
- ✅ `runAsUser: 1001` (non-root UID)
- ✅ `allowPrivilegeEscalation: false`
- ✅ `capabilities.drop: [ALL]`
- ✅ Resource requests and limits defined
- ✅ Liveness and readiness probes configured

---

## Success Metrics

- All pods running with 2/2 status
- Services respond within 500ms
- Application accessible via Minikube tunnel
- Docker Compose runs locally without errors
- Helm charts pass all lint checks

---

## Out of Scope

- StatefulSets (not needed for stateless app)
- PersistentVolumes (database is external)
- Service Mesh (Istio, Linkerd) - Phase V
- CI/CD pipelines - Phase V
- Dapr integration - Phase V
- Event-driven architecture - Phase V
- Multi-environment deployments (dev/staging/prod)

---

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
