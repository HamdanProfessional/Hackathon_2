# Implementation Plan: Cloud Deployment with Event-Driven Architecture

**Feature**: 005-cloud-deployment
**Created**: 2025-12-23
**Estimated Duration**: 10 days
**Status**: 📋 Planned

---

## Overview

This plan breaks down Phase V implementation into 10 days of work, covering database changes, API development, Dapr integration, notification service, cloud deployment, and CI/CD automation.

---

## Day 1: Database Schema and Migrations

### Tasks

1. **Create RecurringTask Model**
   - File: `backend/app/models/recurring_task.py`
   - Fields: id, user_id, title, description, priority, recurrence_type, recurrence_interval, start_date, end_date, next_due_at, is_active

2. **Update Task Model**
   - Add `due_date` field
   - Add `notified` field
   - Add `recurring_task_id` foreign key

3. **Create TaskEventLog Model**
   - File: `backend/app/models/task_event_log.py`
   - Fields: id, task_id, event_type, event_data, created_at

4. **Generate Migration**
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add recurring tasks and due dates"
   alembic upgrade head
   ```

**Validation**:
- [ ] Migration applies successfully
- [ ] New tables exist
- [ ] Foreign keys correct

---

## Day 2: Recurring Tasks CRUD API

### Tasks

1. **Create CRUD Operations**
   - File: `backend/app/crud/recurring_task.py`
   - Functions: create, get, list, update, delete

2. **Create Schemas**
   - File: `backend/app/schemas/recurring_task.py`
   - Schemas: RecurringTaskCreate, RecurringTaskUpdate, RecurringTaskResponse

3. **Create API Endpoints**
   - File: `backend/app/api/recurring_tasks.py`
   - Routes: POST, GET, PUT, DELETE

4. **Update Task API**
   - Modify: `backend/app/api/tasks.py`
   - Add support for `due_date` field

**Validation**:
- [ ] Can create recurring task
- [ ] Can list recurring tasks
- [ ] Can update recurring task
- [ ] Can delete recurring task
- [ ] Due date works on tasks

---

## Day 3: Dapr Integration and Event Publishing

### Tasks

1. **Install Dapr Python SDK**
   ```bash
   pip install dapr
   ```

2. **Create Event Publisher Service**
   - File: `backend/app/services/event_publisher.py`
   - Functions: publish_task_created, publish_task_updated, publish_task_completed

3. **Integrate Event Publishing**
   - Modify: `backend/app/api/tasks.py`
   - Publish events on CRUD operations

4. **Create Dapr Component Manifests**
   - File: `k8s/dapr-components/pubsub-redpanda.yaml`
   - File: `k8s/dapr-components/secrets.yaml`

**Validation**:
- [ ] Dapr SDK installed
- [ ] Events publish without errors
- [ ] Event payload correct
- [ ] Dapr components configured

---

## Day 4: Notification Service Development

### Tasks

1. **Create Notification Service Application**
   - Directory: `services/notifications/`
   - File: `services/notifications/app/main.py`
   - File: `services/notifications/requirements.txt`

2. **Create Due Date Checker**
   - File: `services/notifications/app/workers/due_date_checker.py`
   - Check for tasks due within 24 hours
   - Send notifications

3. **Create Recurring Task Processor**
   - File: `services/notifications/app/workers/recurring_processor.py`
   - Create next occurrence when due
   - Update next_due_at

4. **Create Dockerfile**
   - File: `services/notifications/Dockerfile`

**Validation**:
- [ ] Notification service runs locally
- [ ] Due date checker works
- [ ] Recurring processor creates tasks
- [ ] Docker image builds

---

## Day 5: Notification Service Deployment

### Tasks

1. **Create Helm Chart**
   - Directory: `helm/notifications/`
   - Chart.yaml, values.yaml, templates/

2. **Configure Dapr Sidecar**
   - Add Dapr annotations to deployment
   - Configure app-id and app-port

3. **Create Event Subscriptions**
   - Subscribe to: task-created, task-updated, task-due-soon
   - File: `services/notifications/app/subscriptions.py`

4. **Test Event Flow**
   - Deploy to Minikube
   - Verify subscription works
   - Verify events processed

**Validation**:
- [ ] Notification service deploys
- [ ] Dapr sidecar injected
- [ ] Subscribes to topics
- [ ] Receives and processes events

---

## Day 6: Cloud Cluster Setup

### Tasks

1. **Create Cloud Cluster**
   - Choose: DOKS, GKE, or AKS
   - Create cluster with 3 nodes
   - Configure kubectl context

2. **Install Dapr**
   ```bash
   dapr init --kubernetes
   kubectl get pods -n dapr-system
   ```

3. **Install Redpanda**
   ```bash
   helm repo add redpanda https://charts.redpanda.com
   helm install redpanda redpanda/redpanda --set replicas=3
   ```

4. **Install Ingress Controller**
   - Nginx ingress for cloud

**Validation**:
- [ ] Cluster has 3 nodes
- [ ] Dapr pods running
- [ ] Redpanda has 3 replicas
- [ ] Ingress controller running

---

## Day 7: Deploy to Cloud

### Tasks

1. **Build and Push Images**
   - Tag with version
   - Push to registry (GHCR, Docker Hub)

2. **Create Production Values**
   - File: `helm/*/values-prod.yaml`
   - Configure LoadBalancer
   - Configure resource limits

3. **Create Secrets**
   ```bash
   kubectl create secret generic backend-secrets \
     --from-literal=database-url="$DATABASE_URL" \
     --from-literal=jwt-secret="$JWT_SECRET"
   ```

4. **Deploy Services**
   ```bash
   helm install frontend helm/frontend -f helm/frontend/values-prod.yaml
   helm install backend helm/backend -f helm/backend/values-prod.yaml
   helm install notifications helm/notifications -f helm/notifications/values-prod.yaml
   ```

**Validation**:
- [ ] Images pushed
- [ ] Secrets created
- [ ] All pods running
- [ ] Services accessible

---

## Day 8: CI/CD Pipeline

### Tasks

1. **Create GitHub Actions Workflow**
   - File: `.github/workflows/deploy.yml`
   - Stages: Build, Test, Push, Deploy, Health Check

2. **Configure Secrets**
   - Add KUBECONFIG to GitHub secrets
   - Add registry credentials

3. **Test Pipeline**
   - Push to main branch
   - Verify automated deployment
   - Check health checks

**Validation**:
- [ ] Workflow runs on push
- [ ] Images build and push
- [ ] Automatic deployment works
- [ ] Health checks pass

---

## Day 9: kubectl-ai and kagent

### Tasks

1. **Install kubectl-ai**
   ```bash
   kubectl krew install ai
   ```

2. **Install kagent**
   ```bash
   npm install -g @kagent/cli
   kagent init
   ```

3. **Test AI Operations**
   ```bash
   kubectl ai list pods
   kagent "Scale backend to 3 replicas"
   ```

**Validation**:
- [ ] kubectl-ai installed
- [ ] kagent configured
- [ ] Can perform operations with AI
- [ ] Can troubleshoot with AI

---

## Day 10: Monitoring and Documentation

### Tasks

1. **Install Prometheus/Grafana**
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/kube-prometheus-stack
   ```

2. **Create Dashboards**
   - Kubernetes Cluster
   - Dapr Metrics
   - Application Metrics

3. **End-to-End Testing**
   - Create task with due date
   - Create recurring task
   - Verify notifications
   - Check event flow

4. **Documentation**
   - Update README
   - Create runbook
   - Document rollback procedures

**Validation**:
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards visible
- [ ] All E2E tests pass
- [ ] Documentation complete

---

## Rollback Plan

### Helm Rollback
```bash
helm rollback frontend
helm rollback backend
helm rollback notifications
```

### Emergency Disable
```bash
helm uninstall frontend
helm uninstall backend
helm uninstall notifications
```

---

## Success Criteria

Phase V complete when:
- [ ] All services deployed to cloud
- [ ] Dapr sidecars running
- [ ] Redpanda cluster healthy
- [ ] Events publishing/consuming
- [ ] Recurring tasks working
- [ ] Due date notifications working
- [ ] CI/CD automated
- [ ] Monitoring active
- [ ] AI tools functional
- [ ] E2E tests passing
- [ ] Documentation complete

---

## Estimated Timeline

| Phase | Days | Status |
|-------|------|--------|
| Database Changes | 1 | 📋 Planned |
| Recurring Tasks API | 1 | 📋 Planned |
| Dapr Integration | 1 | 📋 Planned |
| Notification Service | 2 | 📋 Planned |
| Cloud Cluster Setup | 1 | 📋 Planned |
| Cloud Deployment | 1 | 📋 Planned |
| CI/CD Pipeline | 1 | 📋 Planned |
| AI Tools Setup | 1 | 📋 Planned |
| Monitoring & Docs | 1 | 📋 Planned |

**Total**: 10 days
