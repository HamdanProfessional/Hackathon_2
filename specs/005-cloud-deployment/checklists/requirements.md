# Validation Checklist: Cloud Deployment with Event-Driven Architecture

**Feature**: 005-cloud-deployment
**Status**: 📋 Planned

---

## Database Schema

### Migrations
- [ ] Migration file created: `005_add_recurring_tasks.py`
- [ ] `recurringtask` table created
- [ ] `taskeventlog` table created
- [ ] `tasks.due_date` column added
- [ ] `tasks.notified` column added
- [ ] `tasks.recurring_task_id` column added
- [ ] Foreign keys created correctly
- [ ] Indexes created
- [ ] Migration applies: `alembic upgrade head`
- [ ] Migration can rollback: `alembic downgrade -1`

### Schema Validation
- [ ] Can create recurring task via SQL
- [ ] Can create task with due_date via SQL
- [ ] Foreign key constraints work
- [ ] Indexes improve query performance

---

## API Endpoints

### Recurring Tasks CRUD
- [ ] POST /api/recurring-tasks creates recurring task
- [ ] GET /api/recurring-tasks lists recurring tasks
- [ ] GET /api/recurring-tasks/{id} returns one recurring task
- [ ] PUT /api/recurring-tasks/{id} updates recurring task
- [ ] DELETE /api/recurring-tasks/{id} deletes recurring task
- [ ] Pagination works on list endpoint
- [ ] User isolation works (only own tasks)

### Task Endpoints (Updated)
- [ ] POST /api/tasks accepts due_date
- [ ] PUT /api/tasks accepts due_date
- [ ] Task response includes due_date
- [ ] Task response includes notified status
- [ ] Tasks can be filtered by due_date

---

## Dapr Integration

### Dapr Installation
- [ ] Dapr CLI installed
- [ ] `dapr init --kubernetes` completed
- [ ] Dapr pods running in dapr-system namespace
- [ ] `dapr list` shows sidecars

### Dapr Components
- [ ] Pub/sub component configured
- [ ] Pub/sub component applied: `kubectl apply -f k8s/dapr-components/`
- [ ] Component status: `dapr components -k`

### Event Publishing
- [ ] Event published on task creation
- [ ] Event published on task update
- [ ] Event published on task completion
- [ ] Event published on task deletion
- [ ] Event payload contains all required fields
- [ ] Event published to correct topic

---

## Notification Service

### Service Implementation
- [ ] `services/notifications/app/main.py` exists
- [ ] `services/notifications/requirements.txt` exists
- [ ] `services/notifications/Dockerfile` exists
- [ ] Due date checker implemented
- [ ] Recurring task processor implemented
- [ ] Event subscriptions configured
- [ ] Docker image builds

### Event Subscriptions
- [ ] Subscribes to task-created topic
- [ ] Subscribes to task-updated topic
- [ ] Subscribes to task-completed topic
- [ ] Subscribes to task-due-soon topic
- [ ] Subscribes to recurring-task-due topic
- [ ] Events received from Kafka
- [ ] Events processed correctly

### Notification Logic
- [ ] Due date checker finds tasks due within 24h
- [ ] Notifications sent for due tasks
- [ ] Tasks marked as notified
- [ ] Recurring processor creates new tasks
- [ ] next_due_at updated after creation

---

## Redpanda (Kafka)

### Installation
- [ ] Redpanda Helm repo added
- [ ] Redpanda installed with 3 replicas
- [ ] All Redpanda pods Running
- [ ] Cluster is healthy

### Topics
- [ ] task-created topic exists
- [ ] task-updated topic exists
- [ ] task-completed topic exists
- [ ] task-due-soon topic exists
- [ ] recurring-task-due topic exists
- [ ] Each topic has 3 partitions
- [ ] Replication factor is 3

### Testing
- [ ] Can produce events to topic
- [ ] Can consume events from topic
- [ ] Events persist correctly
- [ ] Consumer groups work

---

## Cloud Deployment

### Cluster Setup
- [ ] Cloud account created (DOKS/GKE/AKS)
- [ ] Kubernetes cluster created
- [ ] Cluster has 3+ nodes
- [ ] kubectl configured for cluster
- [ ] `kubectl get nodes` shows Ready

### Dapr on Cluster
- [ ] Dapr installed on cluster
- [ ] Dapr system pods running
- [ ] Dapr version compatible

### Redpanda on Cluster
- [ ] Redpanda installed on cluster
- [ ] Redpanda cluster healthy
- [ ] Topics created
- [ ] Accessible from services

### Container Registry
- [ ] Registry created/configured
- [ ] Can authenticate to registry
- [ ] Images can be pushed
- [ ] Images can be pulled

### Service Deployment
- [ ] todo-frontend image built
- [ ] todo-backend image built
- [ ] todo-notifications image built
- [ ] All images pushed to registry
- [ ] Frontend deployed: `helm install frontend`
- [ ] Backend deployed: `helm install backend`
- [ ] Notifications deployed: `helm install notifications`
- [ ] All pods Running (2/2 or more)
- [ ] All services accessible

---

## CI/CD Pipeline

### GitHub Actions
- [ ] `.github/workflows/deploy.yml` exists
- [ ] Workflow triggers on push to main
- [ ] Build stage works
- [ ] Test stage works
- [ ] Push stage works
- [ ] Deploy stage works
- [ ] Health check stage works

### Secrets
- [ ] KUBECONFIG secret added
- [ ] Registry credentials added
- [ ] API keys added (if needed)

### Automation
- [ ] Push to main triggers workflow
- [ ] Images build automatically
- [ ] Images pushed automatically
- [ ] Deployment runs automatically
- [ ] Health checks pass
- [ ] Rollback on failure

---

## Monitoring

### Prometheus
- [ ] Prometheus installed
- [ ] Prometheus scraping metrics
- [ ] ServiceMonitors configured
- [ ] Metrics accessible

### Grafana
- [ ] Grafana installed
- [ ] Grafana accessible
- [ ] Dashboards imported
- [ ] Dashboards show data

### Alerts
- [ ] Alert rules configured
- [ ] Alerts trigger on issues
- [ ] Notifications work

---

## kubectl-ai

### Installation
- [ ] krew installed
- [ ] kubectl-ai installed via krew
- [ ] `kubectl ai --help` works

### Functionality
- [ ] Can list resources with AI
- [ ] Can get resources with AI
- [ ] Can describe resources with AI
- [ ] Can troubleshoot with AI
- [ ] Can generate manifests with AI

---

## kagent

### Installation
- [ ] kagent CLI installed
- [ ] `kagent init` completed
- [ ] Configuration file created

### Functionality
- [ ] Can execute commands via AI
- [ ] Can scale deployments with AI
- [ ] Can diagnose issues with AI
- [ ] Can create resources with AI
- [ ] Can query cluster status with AI

---

## End-to-End Tests

### Recurring Tasks
- [ ] Create daily recurring task
- [ ] Verify next_due_at calculated correctly
- [ ] Wait for next occurrence (or trigger manually)
- [ ] Verify new task created
- [ ] Verify next_due_at updated
- [ ] Stop recurring task
- [ ] Verify no more tasks created

### Due Dates
- [ ] Create task with due date
- [ ] Task appears in due list
- [ ] Notification sent when due
- [ ] Task marked as notified
- [ ] Complete task
- [ ] Task removed from due list

### Event Flow
- [ ] Create task via API
- [ ] Verify event in Kafka
- [ ] Verify notification service receives event
- [ ] Verify appropriate action taken

### Performance
- [ ] API response time <500ms
- [ ] Event latency <100ms
- [ ] Notification delivery <5 seconds
- [ ] No memory leaks
- [ ] No database connection issues

---

## Documentation

### Spec Files
- [ ] `specs/005-cloud-deployment/spec.md` complete
- [ ] `specs/005-cloud-deployment/plan.md` complete
- [ ] `specs/005-cloud-deployment/quickstart.md` complete
- [ ] `specs/005-cloud-deployment/tasks.md` complete
- [ ] `specs/005-cloud-deployment/data-model.md` complete

### Runbooks
- [ ] Deployment runbook created
- [ ] Rollback runbook created
- [ ] Troubleshooting guide created
- [ ] Scaling procedures documented

---

## Security

### Dapr Security
- [ ] mTLS enabled for Dapr
- [ ] Dapr API tokens configured
- [ ] App IDs unique

### Kubernetes Security
- [ ] RBAC configured
- [ ] Service accounts created
- [ ] Secrets encrypted at rest
- [ ] Network policies (optional)

### Application Security
- [ ] All services run as non-root
- [ ] No privileged containers
- [ ] Resource limits enforced
- [ ] Security contexts configured

---

## Success Criteria

Phase V is complete when:
- [ ] All database migrations applied
- [ ] All API endpoints functional
- [ ] Dapr sidecars running on all pods
- [ ] Events publishing correctly
- [ ] Events consuming correctly
- [ ] Recurring tasks working
- [ ] Due date notifications working
- [ ] Application deployed to cloud
- [ ] CI/CD pipeline automated
- [ ] Monitoring and logging active
- [ ] kubectl-ai functional
- [ ] kagent functional
- [ ] All E2E tests passing
- [ ] Documentation complete

---

## Sign-off

**Developer**: _________________ **Date**: _______

**Reviewer**: _________________ **Date**: _______

**DevOps**: _________________ **Date**: _______
