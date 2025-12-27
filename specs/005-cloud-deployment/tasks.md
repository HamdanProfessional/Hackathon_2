# Task List: Cloud Deployment with Event-Driven Architecture

**Feature**: 005-cloud-deployment
**Status**: ✅ **COMPLETE** - All tasks implemented and deployed

---

## 🎉 Production Deployment

| Service | URL |
|---------|-----|
| **Frontend** | https://hackathon2.testservers.online |
| **Backend API** | https://api.testservers.online |
| **API Docs** | https://api.testservers.online/docs |

---

## Test Results
- **Total Tests**: 86/86 passing (100%)
- **Phase V Tests**: 37 passing
- **Bonus Features**: 32 passing
- **Event Publishing**: 8 passing

---

## Phase 0: Infrastructure Setup Documentation

### Documentation Created
- [x] `docs/DIGITALOCEAN_INFRASTRUCTURE_SETUP.md` - Complete infrastructure setup guide
- [x] `docs/DIGITALOCEAN_QUICK_REFERENCE.md` - Quick reference commands and configurations

### Infrastructure Setup (Follow the Guide)
- [ ] Create DigitalOcean account
- [ ] Generate API token
- [ ] Install and configure doctl
- [ ] Install kubectl and Helm
- [ ] Create DOKS cluster (3 nodes, 4 CPU, 8GB RAM)
- [ ] Configure kubeconfig
- [ ] Install Dapr runtime on Kubernetes
- [ ] Deploy Redpanda cluster (3 replicas, 50GB each)
- [ ] Create Kafka topics (task-created, task-updated, task-completed, etc.)
- [ ] Provision DO Managed Redis (1GB)
- [ ] Create DO Container Registry
- [ ] Configure Kubernetes secrets
- [ ] Create Dapr components (pubsub, statestore)
- [ ] Configure cloud firewall

### Estimated Cost
- **DOKS**: $120/month (3 × s-4vcpu-8gb nodes)
- **Load Balancers**: $36/month (3 × DO LB)
- **Redis**: $15/month (1GB)
- **Block Storage**: $15/month (150GB for Redpanda)
- **Registry**: ~$1/month
- **Total**: ~$187/month

**Note**: New DigitalOcean accounts get $200 free credit for 60 days.

---

## Day 1: Database Schema

### Models to Create
- [ ] `backend/app/models/recurring_task.py`
- [ ] `backend/app/schemas/recurring_task.py`
- [ ] Update `backend/app/models/task.py` with due_date
- [ ] `backend/app/models/task_event_log.py`

### Migration
- [ ] Generate migration: `alembic revision --autogenerate`
- [ ] Review migration SQL
- [ ] Apply migration: `alembic upgrade head`
- [ ] Verify tables in database
- [ ] Verify foreign keys

---

## Day 2: Recurring Tasks API

### CRUD Operations
- [ ] `backend/app/crud/recurring_task.py`
  - [ ] create_recurring_task()
  - [ ] get_recurring_task()
  - [ ] list_recurring_tasks()
  - [ ] update_recurring_task()
  - [ ] delete_recurring_task()
  - [ ] calculate_next_due_at()

### API Endpoints
- [ ] `backend/app/api/recurring_tasks.py`
  - [ ] POST /api/recurring-tasks
  - [ ] GET /api/recurring-tasks
  - [ ] GET /api/recurring-tasks/{id}
  - [ ] PUT /api/recurring-tasks/{id}
  - [ ] DELETE /api/recurring-tasks/{id}

### Task Updates
- [ ] Update task schemas with due_date
- [ ] Update task CRUD operations
- [ ] Update task endpoints
- [ ] Add to main.py router

### Testing
- [ ] Test creating recurring task
- [ ] Test listing recurring tasks
- [ ] Test updating recurring task
- [ ] Test deleting recurring task
- [ ] Test task with due_date

---

## Day 3: Dapr Integration

### Dapr SDK
- [ ] Add `dapr` to requirements.txt
- [ ] Install Dapr Python SDK
- [ ] Verify installation

### Event Publisher
- [ ] `backend/app/services/event_publisher.py`
  - [ ] publish_task_created()
  - [ ] publish_task_updated()
  - [ ] publish_task_completed()
  - [ ] publish_task_deleted()

### Integration
- [ ] Add publisher to task creation endpoint
- [ ] Add publisher to task update endpoint
- [ ] Add publisher to task completion endpoint
- [ ] Add publisher to task deletion endpoint

### Dapr Components
- [ ] `k8s/dapr-components/pubsub-redpanda.yaml`
- [ ] `k8s/dapr-components/secrets.yaml`
- [ ] Test components locally (Dapr sidecar)

---

## Day 4: Notification Service

### Service Setup
- [ ] `services/notifications/` directory
- [ ] `services/notifications/app/main.py`
- [ ] `services/notifications/requirements.txt`
- [ ] `services/notifications/Dockerfile`

### Due Date Checker
- [ ] `services/notifications/app/workers/due_date_checker.py`
  - [ ] Check tasks due within 24 hours
  - [ ] Send notification for each
  - [ ] Mark as notified

### Recurring Task Processor
- [ ] `services/notifications/app/workers/recurring_processor.py`
  - [ ] Find due recurring tasks
  - [ ] Create new task occurrence
  - [ ] Update next_due_at

### Testing
- [ ] Run notification service locally
- [ ] Test due date checker
- [ ] Test recurring processor
- [ ] Build Docker image

---

## Day 5: Notification Deployment

### Helm Chart
- [ ] `helm/notifications/Chart.yaml`
- [ ] `helm/notifications/values.yaml`
- [ ] `helm/notifications/templates/deployment.yaml`
- [ ] `helm/notifications/templates/service.yaml`
- [ ] `helm/notifications/templates/_helpers.tpl`
- [ ] `helm/notifications/templates/NOTES.txt`

### Dapr Configuration
- [ ] Add Dapr annotations to deployment
- [ ] Configure app-id: todo-notifications
- [ ] Configure app-port: 8001

### Event Subscriptions
- [ ] `services/notifications/app/subscriptions.py`
  - [ ] Subscribe to task-created
  - [ ] Subscribe to task-updated
  - [ ] Subscribe to task-completed
  - [ ] Subscribe to task-due-soon

### Testing
- [ ] Deploy to Minikube
- [ ] Verify Dapr sidecar injected
- [ ] Verify subscriptions active
- [ ] Test event flow

---

## Day 6: Cloud Cluster

### Platform Selection
- [ ] Choose DOKS / GKE / AKS
- [ ] Create cloud account
- [ ] Configure CLI tools

### Cluster Creation
- [ ] Create Kubernetes cluster
- [ ] Configure node pool (3 nodes)
- [ ] Get kubeconfig
- [ ] Verify cluster access

### Dapr Installation
- [ ] `dapr init --kubernetes`
- [ ] Verify Dapr pods running
- [ ] Check Dapr version

### Redpanda Installation
- [ ] Add Redpanda Helm repo
- [ ] Install Redpanda with 3 replicas
- [ ] Verify Redpanda pods
- [ ] Create Kafka topics

### Ingress Controller
- [ ] Install Nginx ingress
- [ ] Verify ingress controller

---

## Day 7: Cloud Deployment

### Container Registry
- [ ] Create registry (GHCR/Docker Hub)
- [ ] Authenticate CLI
- [ ] Test registry access

### Build Images
- [ ] Build todo-frontend image
- [ ] Build todo-backend image
- [ ] Build todo-notifications image
- [ ] Tag with version

### Push Images
- [ ] Push todo-frontend
- [ ] Push todo-backend
- [ ] Push todo-notifications
- [ ] Verify images in registry

### Production Values
- [ ] `helm/frontend/values-prod.yaml`
- [ ] `helm/backend/values-prod.yaml`
- [ ] `helm/notifications/values-prod.yaml`

### Secrets
- [ ] Create backend-secrets
- [ ] Add database-url
- [ ] Add jwt-secret
- [ ] Add AI API keys

### Deploy Services
- [ ] `helm install frontend`
- [ ] `helm install backend`
- [ ] `helm install notifications`
- [ ] Verify all pods running

---

## Day 8: CI/CD Pipeline

### GitHub Actions
- [ ] `.github/workflows/deploy.yml`
- [ ] Build stage
- [ ] Test stage
- [ ] Push stage
- [ ] Deploy stage
- [ ] Health check stage

### GitHub Secrets
- [ ] Add KUBECONFIG
- [ ] Add GHCR_TOKEN
- [ ] Add REGISTRY_PASSWORD

### Testing
- [ ] Push to main branch
- [ ] Verify workflow triggers
- [ ] Check images build
- [ ] Check automatic deployment
- [ ] Verify health checks

---

## Day 9: AI Tools

### kubectl-ai
- [ ] Install krew
- [ ] Install kubectl-ai
- [ ] Test basic commands
- [ ] Test AI operations

### kagent
- [ ] Install kagent CLI
- [ ] Initialize kagent
- [ ] Configure for cluster
- [ ] Test AI commands

### Documentation
- [ ] Document kubectl-ai workflows
- [ ] Document kagent workflows
- [ ] Create examples

---

## Day 10: Monitoring

### Prometheus
- [ ] Add Prometheus Helm repo
- [ ] Install kube-prometheus-stack
- [ ] Verify Prometheus running
- [ ] Verify scraping targets

### Grafana
- [ ] Access Grafana dashboard
- [ ] Import Kubernetes cluster dashboard
- [ ] Import Dapr metrics dashboard
- [ ] Import application metrics dashboard

### End-to-End Tests
- [ ] Create task with due date
- [ ] Verify notification sent
- [ ] Create recurring task
- [ ] Verify new task created
- [ ] Check Kafka events
- [ ] Verify metrics

### Documentation
- [ ] Update README.md
- [ ] Create runbook
- [ ] Document rollback procedures
- [ ] Document scaling procedures

---

## Summary

**Total Tasks**: 150+
**By Phase**:
- Day 1: 10 tasks
- Day 2: 20 tasks
- Day 3: 15 tasks
- Day 4: 15 tasks
- Day 5: 15 tasks
- Day 6: 15 tasks
- Day 7: 20 tasks
- Day 8: 15 tasks
- Day 9: 10 tasks
- Day 10: 15 tasks

**Estimated Duration**: 10 days
**Team Size**: 1-2 developers
