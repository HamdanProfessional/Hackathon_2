# Feature: Phase IV - Kubernetes Deployment (Container Orchestration)

## Overview
Containerize the Todo application and deploy to Kubernetes using Minikube for local development and production-ready Helm charts. This phase transforms the monolithic Vercel deployment into a containerized architecture suitable for scalable cloud deployment on platforms like DigitalOcean Kubernetes (DOKS), Google Kubernetes Engine (GKE), or Azure Kubernetes Service (AKS). The deployment integrates kubectl-ai and kagent for AI-assisted Kubernetes operations.

## User Stories
- **US-1**: As a developer, I want to containerize frontend and backend applications, so that I can deploy them consistently across environments
- **US-2**: As a developer, I want to deploy to Minikube for local testing, so that I can validate Kubernetes manifests before production deployment
- **US-3**: As a developer, I want to use Helm charts for deployment, so that I can manage releases and upgrades efficiently
- **US-4**: As a developer, I want to use kubectl-ai and kagent for Kubernetes operations, so that I can leverage AI assistance for cluster management
- **US-5**: As a developer, I want production-ready Kubernetes configurations, so that I can deploy to cloud platforms (DOKS/GKE/AKS) with confidence

## Acceptance Criteria
- [ ] **AC-1**: Frontend Docker image built with multi-stage build (Next.js 14 production build)
- [ ] **AC-2**: Backend Docker image built with production FastAPI server (Uvicorn)
- [ ] **AC-3**: Helm chart created for frontend deployment with service and ingress
- [ ] **AC-4**: Helm chart created for backend deployment with service and ingress
- [ ] **AC-5**: Application deploys successfully to Minikube with `kubectl apply`
- [ ] **AC-6**: kubectl-ai is configured and functional for cluster management
- [ **AC-7**: kagent is configured and functional for AI-assisted operations
- [ ] **AC-8**: Services are accessible via Minikube tunnel or NodePort
- [ ] **AC-9**: Environment variables and secrets are properly configured in Kubernetes
- [ ] **AC-10**: Database connection works from Kubernetes pods to Neon PostgreSQL

## Architecture

### Kubernetes Architecture Overview
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

Legend:
- SVC: Kubernetes Service (NodePort for Minikube, LoadBalancer for cloud)
- Pod: Container instance(s)
- External Database: Neon PostgreSQL (cloud-hosted, not in cluster)
```

### Component Breakdown

#### 1. Frontend Container
- **Base Image**: `node:20-alpine` (or `node:22-alpine`)
- **Framework**: Next.js 14 with App Router
- **Build Process**:
  - Stage 1: `npm ci` (install dependencies)
  - Stage 2: `npm run build` (production build)
  - Stage 3: Copy build artifacts to nginx image
- **Runtime**: nginx (serves static files) or standalone Node.js
- **Port**: 3000
- **Replicas**: 2-3 (Horizontal scaling)

#### 2. Backend Container
- **Base Image**: `python:3.13-slim`
- **Framework**: FastAPI with Uvicorn
- **Dependencies**: Defined in requirements.txt
- **Runtime**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Port**: 8000
- **Replicas**: 2-3 (Horizontal scaling)

#### 3. Helm Charts
**Frontend Helm Chart** (`helm/frontend/`):
- `Chart.yaml`: Chart metadata
- `values.yaml`: Default configuration
- `templates/deployment.yaml`: Pod deployment spec
- `templates/service.yaml`: Service (NodePort/LoadBalancer)
- `templates/ingress.yaml`: Ingress for domain routing
- `templates/configmap.yaml`: Environment variables

**Backend Helm Chart** (`helm/backend/`):
- `Chart.yaml`: Chart metadata
- `values.yaml`: Default configuration
- `templates/deployment.yaml`: Pod deployment spec
- `templates/service.yaml`: Service (NodePort/LoadBalancer)
- `templates/ingress.yaml`: Ingress for API routing
- `templates/secret.yaml`: Database credentials, JWT secrets
- `templates/configmap.yaml`: Environment variables

## Data Model

### No New Database Tables Required
This phase is deployment-focused and does not introduce new data models. Existing tables from Phase I-III remain unchanged.

### Environment Variables Configuration

#### Frontend Environment Variables (ConfigMap)
```yaml
env:
  NEXT_PUBLIC_API_URL: "http://backend-service:8000"
  # Production: Override with Ingress host
  NEXT_PUBLIC_API_URL: "https://api.yourdomain.com"

  # Better Auth
  BETTER_AUTH_SECRET: "<from Kubernetes Secret>"

  # ChatKit (Phase III)
  NEXT_PUBLIC_OPENAI_DOMAIN_KEY: ""
```

#### Backend Environment Variables (Secret)
```yaml
env:
  # Database
  DATABASE_URL: "postgresql+asyncpg://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb"

  # JWT
  JWT_SECRET_KEY: "<from Kubernetes Secret>"
  JWT_ALGORITHM: "HS256"
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "1440"

  # AI (Phase III)
  GROQ_API_KEY: "<from Kubernetes Secret>"
  GEMINI_API_KEY: "<from Kubernetes Secret>"
  OPENAI_API_KEY: "<from Kubernetes Secret>"

  # CORS
  CORS_ORIGINS: "http://localhost:3000,https://yourdomain.com"

  # Application
  APP_NAME: "Todo CRUD API"
  DEBUG: "false"
```

## Kubernetes Resources

### 1. Frontend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  labels:
    app: todo-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
    spec:
      containers:
      - name: frontend
        image: todo-frontend:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          valueFrom:
            configMapKeyRef:
              name: frontend-config
              key: NEXT_PUBLIC_API_URL
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort  # Use LoadBalancer for cloud
  selector:
    app: todo-frontend
  ports:
  - port: 3000
    targetPort: 3000
    nodePort: 30001  # For Minikube access
  selector:
    app: todo-frontend
```

### 2. Backend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  labels:
    app: todo-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: database-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: NodePort  # Use LoadBalancer for cloud
  selector:
    app: todo-backend
  ports:
  - port: 8000
    targetPort: 8000
    nodePort: 30002  # For Minikube access
```

### 3. Ingress (Optional - for domain routing)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  rules:
  - host: app.yourdomain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 3000
  tls:
  - hosts:
    - app.yourdomain.com
    secretName: todo-tls
```

### 4. Kubernetes Secrets
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
type: Opaque
stringData:
  database-url: "postgresql+asyncpg://user:pass@ep-xxx..."
  jwt-secret: "your-production-jwt-secret-min-32-chars"
  groq-api-key: "gsk_xxx..."
  gemini-api-key: "AIzaSyxxx..."
---
apiVersion: v1
kind: Secret
metadata:
  name: frontend-secrets
type: Opaque
stringData:
  better-auth-secret: "your-production-jwt-secret-min-32-chars"
```

## Docker Images

### 1. Frontend Dockerfile
**Location**: `frontend/Dockerfile`

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Production Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

USER nextjs
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

### 2. Backend Dockerfile
**Location**: `backend/Dockerfile`

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1001 appuser && \
    chown -R appuser /app
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "--port", "8000"]
```

### 3. Docker Compose (Local Development)
**Location**: `docker-compose.yml` (root level)

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
    depends_on:
      - postgres

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=tododb
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Helm Charts Structure

### Frontend Helm Chart
**Directory**: `helm/frontend/`

```
helm/frontend/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── secrets.yaml
    └── hpa.yaml (HorizontalPodAutoscaler)
```

**values.yaml** (Default configuration):
```yaml
replicaCount: 2

image:
  repository: todo-frontend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: NodePort
  port: 3000
  nodePort: 30001

ingress:
  enabled: false
  className: nginx
  annotations: {}
  hosts:
    - host: chart-example.local
      paths:
      - path: /
        pathType: Prefix
  tls: []

resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

env:
  NEXT_PUBLIC_API_URL: "http://backend-service:8000"
```

### Backend Helm Chart
**Directory**: `helm/backend/`

```
helm/backend/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── secrets.yaml
    ├── configmap.yaml
    └── hpa.yaml
```

**values.yaml** (Default configuration):
```yaml
replicaCount: 2

image:
  repository: todo-backend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: NodePort
  port: 8000
  nodePort: 30002

ingress:
  enabled: false
  className: nginx
  annotations: {}
  hosts:
    - host: api.chart-example.local
      paths:
      - path: /api
        pathType: Prefix
  tls: []

secrets:
  databaseUrl: "postgresql+asyncpg://user:pass@..."
  jwtSecret: "change-this-in-production"
  groqApiKey: ""
  geminiApiKey: ""
  openaiApiKey: ""

resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "1000m"

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

env:
  CORS_ORIGINS: "http://localhost:3000,https://yourdomain.com"
  APP_NAME: "Todo CRUD API"
  DEBUG: "false"
```

## kubectl-ai Integration

### Installation and Setup
```bash
# Install kubectl-ai via krew
kubectl krew index add kubectl-ai https://github.com/akuity/kubectl-ai.git
kubectl krew install kubectl-ai

# Verify installation
kubectl ai --help
```

### Usage Examples
```bash
# List all pods
kubectl ai list pods

# Get pod details
kubectl ai get pod frontend-xxx

# Describe a pod
kubectl ai describe deployment backend

# Get logs from a pod
kubectl ai logs deployment/backend --tail=50

# Execute command in pod
kubectl ai exec deployment/frontend -- ls -la /app

# Scale deployment
kubectl ai scale deployment backend --replicas=3

# Apply manifest with AI assistance
kubectl ai apply -f helm/frontend/templates/deployment.yaml

# Get cluster info
kubectl ai cluster info

# Troubleshoot pod issues
kubectl ai troubleshoot pod/backend-xxx

# Generate deployment manifest
kubectl ai generate deployment todo-backend --image=todo-backend:latest --port=8000
```

## kagent Integration

### Installation and Setup
```bash
# Install kagent (AI-powered Kubernetes assistant)
# Refer to: https://github.com/yourusername/kagent
npm install -g @kagent/cli

# Or via Python
pip install kagent

# Initialize kagent
kagent init
```

### Usage Examples
```bash
# Interactive mode
kagent

# Direct commands
kagent "Scale the backend deployment to 3 replicas"
kagent "Check the status of frontend pods"
kagent "Get the logs from the backend service"
kagent "Apply the frontend Helm chart with values-dev.yaml"
kagent "Troubleshoot why the backend pods are crashing"
kagent "Show me the resource usage for all pods"
kagent "Create an Ingress for domain app.example.com"
```

## Implementation Phases

### Phase 1: Docker Image Creation (Days 1-2)
1. **Frontend Dockerfile**:
   - Create multi-stage Dockerfile in `frontend/`
   - Configure Next.js 14 production build
   - Test locally with `docker build -t todo-frontend .`
   - Verify image runs: `docker run -p 3000:3000 todo-frontend`

2. **Backend Dockerfile**:
   - Create Dockerfile in `backend/`
   - Configure Python dependencies and FastAPI/Uvicorn
   - Test locally: `docker build -t todo-backend .`
   - Verify image runs: `docker run -p 8000:8000 todo-backend`

3. **Docker Compose** (for local dev):
   - Create `docker-compose.yml` in project root
   - Test locally: `docker-compose up`
   - Verify frontend-backend communication

### Phase 2: Helm Charts Creation (Days 3-4)
1. **Frontend Helm Chart**:
   - Initialize chart: `helm create helm/frontend`
   - Configure `values.yaml` with defaults
   - Create templates for deployment, service, ingress
   - Add ConfigMap for environment variables
   - Add Secret for sensitive data

2. **Backend Helm Chart**:
   - Initialize chart: `helm create helm/backend`
   - Configure `values.yaml` with defaults
   - Create templates for deployment, service, ingress
   - Add Secret for database/JWT/AI keys
   - Add ConfigMap for CORS and app settings

3. **Chart Testing**:
   - Lint charts: `helm lint helm/frontend helm/backend`
   - Test templates: `helm template helm/frontend --debug`
   - Dry-run install: `helm install --dry-run --debug frontend helm/frontend`

### Phase 3: Minikube Deployment (Days 5-6)
1. **Minikube Setup**:
   - Install Minikube
   - Start cluster: `minikube start`
   - Enable ingress: `minikube addons enable ingress`
   - Verify cluster: `kubectl cluster-info`

2. **Build and Push Images**:
   - For local: Load images into Minikube: `minikube image load todo-frontend`
   - For cloud: Push to registry (Docker Hub, GitHub Container Registry)

3. **Install Helm Charts**:
   - Install frontend: `helm install frontend helm/frontend`
   - Install backend: `helm install backend helm/backend`
   - Verify pods: `kubectl get pods`
   - Verify services: `kubectl get svc`

4. **Test Deployment**:
   - Access frontend: `minikube service frontend --url`
   - Test backend API: `curl http://<minikube-ip>:30002/health`
   - Test frontend-backend communication
   - Verify database connectivity

### Phase 4: kubectl-ai and kagent Setup (Days 7)
1. **Install kubectl-ai**:
   - Install via krew
   - Verify with `kubectl ai --help`
   - Test basic commands

2. **Install kagent**:
   - Install via npm or pip
   - Initialize configuration
   - Test with simple queries

3. **AI-Assisted Operations**:
   - Use `kubectl ai` for common operations
   - Use `kagent` for complex workflows
   - Create AI-powered deployment scripts

### Phase 5: Production Preparation (Days 8-9)
1. **Container Registry**:
   - Set up GitHub Container Registry or Docker Hub
   - Tag and push images
   - Update Helm charts with production image references

2. **Cloud Platform Setup**:
   - Create Kubernetes cluster (DOKS/GKE/AKS)
   - Configure kubectl context
   - Set up Ingress controller (nginx/cert-manager)
   - Configure DNS for custom domains

3. **Environment Configuration**:
   - Create production secrets (database, JWT, AI keys)
   - Configure `values-prod.yaml` for cloud deployment
   - Set up monitoring/logging (Prometheus, Grafana)

### Phase 6: Production Deployment (Day 10)
1. **Deploy to Cloud**:
   - Install frontend: `helm install frontend helm/frontend -f helm/frontend/values-prod.yaml`
   - Install backend: `helm install backend helm/backend -f helm/backend/values-prod.yaml`
   - Configure Ingress for HTTPS

2. **Validation**:
   - Test all endpoints
   - Verify database connectivity
   - Check pod health and resource usage
   - Test scaling with HorizontalPodAutoscaler

3. **Documentation**:
   - Document deployment process
   - Create runbooks for common operations
   - Document kubectl-ai/kagent workflows

## Dependencies & Integration

### Existing Features
- **Phase I**: Console app (not affected)
- **Phase II**: Web app with FastAPI + Next.js (containerized)
- **Phase III**: AI Chatbot with Groq/Gemini (containerized with backend)

### Database Connectivity
- **Neon PostgreSQL**: External cloud database
- **Connection String**: Configured via Kubernetes Secret
- **Firewall**: Allow Kubernetes cluster IP ranges in Neon console

### Authentication
- **JWT Secret**: Stored in Kubernetes Secret
- **Better Auth**: Configured via environment variables
- **CORS**: Configured for Kubernetes service domain

### Service Discovery
- **Frontend → Backend**: Kubernetes service DNS (`backend-service`)
- **Backend → Database**: External Neon endpoint (DNS)
- **Ingress**: Optional single-domain routing with path-based routing

## Non-Functional Requirements

### Performance
- **Pod Startup Time**: <30 seconds for all pods
- **API Response Time**: <500ms for healthy pods (same as Vercel)
- **Resource Requests**: Appropriate for workloads (see resource specs)
- **Resource Limits**: Prevent resource exhaustion
- **Horizontal Scaling**: HPA for auto-scaling based on CPU/memory

### Security
- **Secrets Management**: Kubernetes Secrets for sensitive data
- **RBAC**: Role-based access control for cluster operations
- **Network Policies**: Restrict pod-to-pod communication
- **Image Scanning**: Scan for vulnerabilities (Trivy, etc.)
- **Non-Root User**: Containers run as non-root user
- **TLS**: HTTPS for Ingress (cert-manager + Let's Encrypt)

### Reliability
- **Health Checks**: Liveness and readiness probes configured
- **Restart Policy**: Always restart on failure
- **Replicas**: Minimum 2 replicas per service
- **Resource Limits**: Prevent memory/CPU exhaustion
- **Pod Disruption Budgets**: Minimum availability during updates

### Scalability
- **Horizontal Pod Autoscaler**: Scale based on CPU/memory (70-80%)
- **Cluster Autoscaler**: Add nodes on resource pressure
- **Load Balancing**: Service (LoadBalancer) distributes traffic
- **Session Affinity**: Not required (stateless JWT auth)

### Monitoring
- **Metrics**: Prometheus-compatible metrics (optional)
- **Logging**: Structured logs to stdout/stderr
- **Tracing**: Distributed tracing (optional, Phase V)
- **Alerts**: Prometheus AlertManager (optional)

### Testing
- **Container Testing**: Test Docker images locally
- **Helm Chart Testing**: Use `helm test` on charts
- **Integration Tests**: Test service-to-service communication
- **E2E Tests**: Test full user flows through ingress
- **Load Tests**: k6 or Locust for performance testing

## Out of Scope
- StatefulSets (not needed for stateless app)
- PersistentVolumes (database is external Neon)
- Service Mesh (Istio, Linkerd) - can add in Phase V
- Advanced monitoring (Grafana dashboards) - optional
- CI/CD pipelines (GitHub Actions, GitLab CI) - bonus
- Multiple environment Kubernetes clusters (dev/staging/prod)
- Database migrations in Kubernetes (Job/CronJob) - handled separately
- Dapr integration (Phase V event-driven architecture)

## Bonus Opportunities

### Kubernetes Automation (+100 points)
- **GitHub Actions**: Automated build and deploy on push
- **Automated Testing**: Run tests in pipeline before deploy
- **Rollback Strategy**: Automatic rollback on failed deployments
- **Blue-Green Deployments**: Zero-downtime updates

### Advanced Features (+150 points)
- **Horizontal Pod Autoscaler**: Auto-scale based on CPU/memory
- **Cluster Autoscaler**: Auto-scale nodes based on resource pressure
- **Network Policies**: Restrict pod-to-pod communication
- **Resource Quotas**: Limit namespace resource usage

### AI-Enhanced Operations (+200 points)
- **kubectl-ai**: Comprehensive usage for cluster management
- **kagent**: Advanced workflows for deployment and troubleshooting
- **AI-Powered Monitoring**: Automated anomaly detection
- **Predictive Scaling**: AI forecasts resource needs

### Security Hardening (+100 points)
- **Pod Security Policies**: Restrict container capabilities
- **Secret Encryption**: Encrypt Kubernetes secrets at rest
- **Image Signing**: Verify image provenance
- **Admission Controllers**: Validate pod configurations

## Validation Checklist

### Docker Images
- [ ] Frontend Dockerfile exists in `frontend/Dockerfile`
- [ ] Frontend image builds successfully: `docker build -t todo-frontend .`
- [ ] Frontend container runs on port 3000
- [ ] Backend Dockerfile exists in `backend/Dockerfile`
- [ ] Backend image builds successfully: `docker build -t todo-backend .`
- [ ] Backend container runs on port 8000
- [ ] `docker-compose.yml` exists for local development

### Helm Charts
- [ ] `helm/frontend/` directory exists with Chart.yaml
- [ ] `helm/backend/` directory exists with Chart.yaml
- [ ] Both charts have `values.yaml` with defaults
- [ ] Both charts have deployment templates
- [ ] Both charts have service templates
- [ ] Both charts have ConfigMap/Secret templates
- [ ] Charts pass linting: `helm lint helm/frontend helm/backend`

### Minikube Deployment
- [ ] Minikube starts successfully
- [ ] Images load into Minikube: `minikube image load todo-frontend`
- [ ] Frontend installs: `helm install frontend helm/frontend`
- [ ] Backend installs: `helm install backend helm/backend`
- [ ] Pods are running: `kubectl get pods` shows 2/2 for each
- [ ] Services are accessible: `kubectl get svc`
- [ ] Frontend accessible via Minikube tunnel
- [ ] Backend API responds to health check
- [ ] Frontend can call backend API

### kubectl-ai Integration
- [ ] kubectl-ai installed via krew
- [ ] `kubectl ai --help` works
- [ ] Can list/get/describe resources
- [ ] Can troubleshoot issues
- [ ] Can generate deployment manifests

### kagent Integration
- [ ] kagent installed
- [ ] kagent initialized
- [ ] Can execute common commands
- [ ] Can scale deployments
- [ ] Can diagnose issues

### Production Readiness
- [ ] Docker images pushed to registry
- [ ] Production values files configured
- [ ] Cloud Kubernetes cluster created
- [ ] kubectl configured for cloud cluster
- [ ] Ingress controller installed
- [ ] TLS certificates configured
- [ ] Database connectivity verified from pods

## Success Metrics
- All pods running with 2/2 status in Minikube
- Services respond within 500ms
- Application accessible via Minikube tunnel
- kubectl-ai successfully manages cluster resources
- kagent successfully executes deployment workflows
- Production deployment passes all health checks
- Horizontal scaling works with HPA (if configured)

## References
- Kubernetes Documentation: https://kubernetes.io/docs/home/
- Helm Documentation: https://helm.sh/docs/
- Minikube Documentation: https://minikube.sigs.k8s.io/docs/
- kubectl-ai GitHub: https://github.com/akuity/kubectl-ai
- Dockerfile Best Practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Next.js Deployment: https://nextjs.org/docs/deployment
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/
- PostgreSQL on Neon: https://neon.tech/docs/integrations
- DigitalOcean Kubernetes: https://www.digitalocean.com/products/kubernetes/
- Google Kubernetes Engine: https://cloud.google.com/kubernetes-engine
- Azure Kubernetes Service: https://azure.microsoft.com/en-us/services/kubernetes-service
