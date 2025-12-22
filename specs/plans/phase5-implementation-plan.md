# Phase V Implementation Plan

## Overview
This document provides a step-by-step implementation plan for Phase V - Cloud Deployment with Event-Driven Architecture.

## Implementation Timeline: 10 Days

### Day 1: Database Schema and Migrations

**Tasks:**
1. Create `RecurringTask` model in `backend/app/models/recurring_task.py`
2. Update `Task` model with `due_date` and `notified` fields
3. Create `TaskEventLog` model for event audit
4. Generate and run Alembic migration
5. Test database changes locally

**Files to Create:**
- `backend/app/models/recurring_task.py`
- `backend/app/schemas/recurring_task.py`

**Files to Modify:**
- `backend/app/models/task.py`
- `backend/app/schemas/task.py`

**Commands:**
```bash
cd backend
alembic revision --autogenerate -m "Add recurring tasks and due dates"
alembic upgrade head
```

**Validation:**
- [ ] Migration applies successfully
- [ ] New tables exist in database
- [ ] Foreign keys are correct
- [ ] Indexes created

---

### Day 2: Recurring Tasks CRUD API

**Tasks:**
1. Create CRUD operations for recurring tasks
2. Create API endpoints for recurring tasks
3. Update task endpoints to support due_date
4. Write unit tests for recurring task logic

**Files to Create:**
- `backend/app/crud/recurring_task.py`
- `backend/app/api/recurring_tasks.py`

**Files to Modify:**
- `backend/app/api/tasks.py`
- `backend/app/main.py` (add recurring tasks router)

**API Endpoints:**
- `POST /api/recurring-tasks` - Create recurring task
- `GET /api/recurring-tasks` - List recurring tasks
- `GET /api/recurring-tasks/{id}` - Get recurring task
- `PUT /api/recurring-tasks/{id}` - Update recurring task
- `DELETE /api/recurring-tasks/{id}` - Delete recurring task

**Validation:**
- [ ] Can create recurring task via API
- [ ] Can list recurring tasks
- [ ] Can update recurring task
- [ ] Can delete recurring task
- [ ] Due date works on tasks

---

### Day 3: Dapr Integration and Event Publishing

**Tasks:**
1. Install Dapr Python SDK
2. Create event publisher service
3. Integrate event publishing into task CRUD
4. Create Dapr component manifests
5. Test local Dapr with Docker

**Files to Create:**
- `backend/app/services/event_publisher.py`
- `k8s/dapr-components/pubsub-redpanda.yaml`
- `k8s/dapr-components/secrets.yaml`

**Files to Modify:**
- `backend/requirements.txt` (add dapr)
- `backend/app/api/tasks.py` (publish events)

**Dependencies:**
```bash
pip install dapr
```

**Events to Publish:**
- `task-created` - When task is created
- `task-updated` - When task is updated
- `task-completed` - When task is completed
- `task-deleted` - When task is deleted

**Validation:**
- [ ] Dapr SDK installed
- [ ] Events publish without errors
- [ ] Event payload is correct
- [ ] Dapr components configured

---

### Day 4: Notification Service

**Tasks:**
1. Create notification service application
2. Implement due date checker
3. Implement recurring task processor
4. Create Dockerfile for notification service
5. Test notification logic locally

**Files to Create:**
- `services/notifications/Dockerfile`
- `services/notifications/app/main.py`
- `services/notifications/app/worker.py`
- `services/notifications/requirements.txt`
- `services/notifications/app/services/due_date_checker.py`
- `services/notifications/app/services/recurring_processor.py`

**Features:**
- Check for tasks due within 24 hours
- Send notifications for due tasks
- Create new tasks from recurring schedules
- Process events from Kafka topics

**Validation:**
- [ ] Notification service runs locally
- [ ] Due date checker finds tasks
- [ ] Recurring processor creates tasks
- [ ] Docker image builds

---

### Day 5: Notification Service Deployment

**Tasks:**
1. Create Helm chart for notification service
2. Configure Dapr sidecar for notification service
3. Test event subscription
4. Deploy to local Minikube

**Files to Create:**
- `helm/notifications/Chart.yaml`
- `helm/notifications/values.yaml`
- `helm/notifications/templates/deployment.yaml`
- `helm/notifications/templates/service.yaml`
- `helm/notifications/templates/_helpers.tpl`

**Dapr Annotations:**
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "todo-notifications"
  dapr.io/app-port: "8001"
```

**Validation:**
- [ ] Notification service deploys
- [ ] Dapr sidecar injected
- [ ] Subscribes to Kafka topics
- [ ] Receives and processes events

---

### Day 6: Cloud Cluster Setup

**Tasks:**
1. Create cloud Kubernetes cluster (DOKS/GKE/AKS)
2. Configure kubectl context
3. Install Dapr to cluster
4. Install Redpanda to cluster
5. Install Nginx Ingress Controller

**Platform Choice:** Select one of:
- **DigitalOcean (DOKS)** - Easiest, good documentation
- **Google Cloud (GKE)** - More features, managed
- **Azure (AKS)** - Enterprise features

**Commands (DOKS Example):**
```bash
# Install doctl
brew install doctl

# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --version 1.29.0 \
  --node-pool "name=pool-1;size=s-4vcpu-8gb;count=3"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-cluster

# Install Dapr
dapr init --kubernetes

# Install Redpanda
helm repo add redpanda https://charts.redpanda.com
helm install redpanda redpanda/redpanda --set replicas=3

# Install Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/do/deploy.yaml
```

**Validation:**
- [ ] Cluster has 3 nodes running
- [ ] Dapr pods running in dapr-system namespace
- [ ] Redpanda pods running with 3 replicas
- [ ] Ingress controller running
- [ ] kubectl configured for cluster

---

### Day 7: Deploy to Cloud

**Tasks:**
1. Build and push Docker images to registry
2. Create production values files
3. Create Kubernetes secrets
4. Install Dapr components
5. Deploy all services with Helm

**Files to Create:**
- `helm/frontend/values-prod.yaml`
- `helm/backend/values-prod.yaml`
- `helm/notifications/values-prod.yaml`

**Commands:**
```bash
# Build and push images
docker build -t ghcr.io/hamdanprofessionals/todo-frontend:latest ./frontend
docker build -t ghcr.io/hamdanprofessionals/todo-backend:latest ./backend
docker build -t ghcr.io/hamdanprofessionals/todo-notifications:latest ./services/notifications

docker push ghcr.io/hamdanprofessionals/todo-frontend:latest
docker push ghcr.io/hamdanprofessionals/todo-backend:latest
docker push ghcr.io/hamdanprofessionals/todo-notifications:latest

# Create secrets
kubectl create secret generic backend-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=groq-api-key="$GROQ_API_KEY"

# Install Dapr components
kubectl apply -f k8s/dapr-components/

# Install services
helm install frontend helm/frontend -f helm/frontend/values-prod.yaml
helm install backend helm/backend -f helm/backend/values-prod.yaml
helm install notifications helm/notifications -f helm/notifications/values-prod.yaml
```

**Validation:**
- [ ] Images pushed to registry
- [ ] Secrets created
- [ ] Dapr components installed
- [ ] All pods running
- [ ] Services accessible

---

### Day 8: CI/CD Pipeline

**Tasks:**
1. Create GitHub Actions workflow
2. Configure secrets in GitHub
3. Test build pipeline
4. Test deployment pipeline
5. Verify automated deployment

**Files to Create:**
- `.github/workflows/deploy.yml`

**GitHub Secrets Required:**
- `KUBECONFIG` - Base64 encoded kubeconfig file
- `GITHUB_TOKEN` - Automatically provided
- `REGISTRY_PASSWORD` - If using private registry

**Pipeline Stages:**
1. Build Docker images on push
2. Run tests
3. Push images to registry
4. Deploy to Kubernetes (on main branch only)
5. Run health checks

**Validation:**
- [ ] Workflow runs on push
- [ ] Images build successfully
- [ ] Tests pass
- [ ] Images pushed to registry
- [ ] Automatic deployment works

---

### Day 9: kubectl-ai and kagent Setup

**Tasks:**
1. Install kubectl-ai via krew
2. Install kagent CLI
3. Configure kagent for cluster
4. Test AI-assisted operations
5. Document AI workflows

**Commands:**
```bash
# Install kubectl-ai
kubectl krew install ai

# Test kubectl-ai
kubectl ai list pods
kubectl ai get deployment backend

# Install kagent
npm install -g @kagent/cli
kagent init

# Test kagent
kagent "Scale the backend deployment to 3 replicas"
kagent "Show me the logs from the notification service"
kagent "Create a new Dapr component for Redis state store"
```

**Validation:**
- [ ] kubectl-ai installed and working
- [ ] kagent installed and configured
- [ ] Can perform operations with AI
- [ ] Can troubleshoot with AI
- [ ] Can generate manifests with AI

---

### Day 10: Monitoring, Testing, and Documentation

**Tasks:**
1. Install Prometheus and Grafana
2. Configure service monitors
3. Create Grafana dashboards
4. Run end-to-end tests
5. Document deployment procedures
6. Create runbook for operations

**Commands:**
```bash
# Install Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80

# Import dashboards for:
# - Kubernetes Cluster
# - Node Exporter
# - Dapr Metrics
```

**End-to-End Tests:**
1. Create task with due date
2. Verify notification sent
3. Create recurring task
4. Verify new tasks created
5. Check event flow in Kafka
6. Verify all metrics in Grafana

**Documentation:**
- Update README with cloud deployment info
- Create runbook for common operations
- Document rollback procedures
- Document scaling procedures

**Validation:**
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards visible
- [ ] All E2E tests pass
- [ ] Documentation complete
- [ ] Runbook created

---

## Rollback Plan

If deployment fails at any stage:

1. **Helm Rollback:**
   ```bash
   helm rollback frontend
   helm rollback backend
   helm rollback notifications
   ```

2. **Previous Version:**
   ```bash
   helm list
   helm history frontend
   helm rollback frontend <revision>
   ```

3. **Emergency Disable:**
   ```bash
   helm uninstall frontend
   helm uninstall backend
   helm uninstall notifications
   ```

---

## Success Criteria

### Phase 5 Complete When:
- [ ] All services deployed to cloud Kubernetes
- [ ] Dapr sidecars running on all pods
- [ ] Redpanda cluster healthy
- [ ] Events publishing and consuming
- [ ] Recurring tasks creating occurrences
- [ ] Due date notifications working
- [ ] CI/CD pipeline automated
- [ ] Monitoring and logging active
- [ ] kubectl-ai functional
- [ ] kagent functional
- [ ] E2E tests passing
- [ ] Documentation complete

---

## Next Steps After Phase V

After Phase V completion, consider:
1. Add WebSocket support for real-time notifications
2. Implement distributed tracing with OpenTelemetry
3. Add service mesh with Istio or Linkerd
4. Implement multi-tenant architecture
5. Add mobile application (React Native / Flutter)
6. Implement advanced analytics
7. Add GraphQL API layer
