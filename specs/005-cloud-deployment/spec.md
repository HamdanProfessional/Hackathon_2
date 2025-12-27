# Feature Specification: Cloud Deployment with Event-Driven Architecture

**Feature Branch**: `005-cloud-deployment`
**Created**: 2025-12-23
**Updated**: 2025-12-27
**Status**: ✅ **COMPLETE**
**Input**: Phase V: Cloud Deployment with Event-Driven Architecture using Dapr, Redpanda, and CI/CD automation on **DigitalOcean**

---

## 🎉 Production Deployment

| Service | URL |
|---------|-----|
| **Frontend** | https://hackathon2.testservers.online |
| **Backend API** | https://api.testservers.online |
| **API Docs** | https://api.testservers.online/docs |

---

## 📋 Implementation Summary

### 🎯 Goal
Deploy the Todo application to **DigitalOcean Kubernetes (DOKS)** with event-driven architecture using Dapr, Redpanda, and CI/CD automation. Transform the monolithic architecture into microservices with event streaming on DigitalOcean's cloud platform.

### 🌊 Why DigitalOcean?

- **Simplicity**: Easy to use, developer-friendly interface
- **Cost-effective**: Competitive pricing for managed Kubernetes
- **All-in-one**: Managed databases (PostgreSQL, Redis), Load Balancers, Spaces
- **Performance**: Fast SSD storage, global data centers
- **Integration**: Native integration with DO services (LoadBalancers, Block Storage)

### ✅ Implemented Features

| Feature | Priority | Status |
|---------|----------|--------|
| Cloud Kubernetes Deployment | P0 | ✅ Complete |
| Dapr Integration | P0 | ✅ Complete |
| Redpanda (Kafka) Cluster | P0 | ✅ Complete |
| Recurring Tasks | P1 | ✅ Complete |
| Task Due Dates | P1 | ✅ Complete |
| Notification Service | P1 | ✅ Complete |
| Event Publishing/Subscription | P0 | ✅ Complete |
| CI/CD Pipeline | P1 | ✅ Complete |
| Prometheus Monitoring | P2 | ✅ Complete |
| Grafana Dashboards | P2 | ✅ Complete |
| kubectl-ai Integration | P2 | ✅ Complete |
| kagent Integration | P2 | ✅ Complete |

---

## User Scenarios & Testing

### User Story 1 - Recurring Tasks

Users can create tasks that repeat on a schedule (daily, weekly, monthly, yearly) without manually creating each occurrence.

**Acceptance Scenarios**:

1. **Given** user wants a daily reminder, **When** they create recurring task for "Take medication" with daily recurrence, **Then** system creates new task each day automatically
2. **Given** user sets weekly team meeting, **When** they create recurring task for "Weekly Standup" every Monday, **Then** task appears every Monday at specified time
3. **Given** user sets end date, **When** creating recurring task with end date, **Then** tasks stop creating after end date

### User Story 2 - Task Due Dates

Users can set due dates on tasks and receive notifications when tasks are due.

**Acceptance Scenarios**:

1. **Given** user creates task with due date, **When** task becomes due, **Then** user receives notification
2. **Given** task is due within 24 hours, **When** checking dashboard, **Then** task is highlighted as due soon
3. **Given** task is overdue, **When** viewing tasks, **Then** it shows as overdue

### User Story 3 - Event-Driven Architecture

Services communicate asynchronously via events, enabling loose coupling and scalability.

**Acceptance Scenarios**:

1. **Given** task is created, **When** creation event is published, **Then** notification service receives event
2. **Given** task is completed, **When** completion event is published, **Then** analytics service can process it
3. **Given** service crashes, **When** it restarts, **Then** it processes missed events from Kafka

---

## Technical Specification

### DigitalOcean Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DigitalOcean Kubernetes (DOKS)                           │
│                    Region: NYC1 / SFO2 / AMS3 / FRA1                       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                   DigitalOcean Load Balancer                           │  │
│  │                   ($12/mo - included with DOKS)                       │  │
│  │  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────────┐   │  │
│  │  │  Frontend SVC   │  │   Backend SVC    │  │  Notification SVC    │   │  │
│  │  │  (DO LB)        │  │  (DO LB)         │  │  (DO LB)             │   │  │
│  │  └────────┬───────┘  └────────┬────────┘  └──────────┬───────────┘   │  │
│  │           │                    │                       │             │  │
│  │  ┌────────▼────────┐  ┌───────▼──────────┐  ┌────────▼───────────┐  │  │
│  │  │ Frontend Pod    │  │  Backend Pod     │  │  Notification Pod   │  │  │
│  │  │ (Next.js 14)    │  │  (FastAPI)       │  │  (FastAPI Worker)   │  │  │
│  │  │ + Dapr Sidecar  │  │  + Dapr Sidecar  │  │  + Dapr Sidecar     │  │  │
│  │  │ Port: 3000      │  │  Port: 8000      │  │  Port: 8001         │  │  │
│  │  └─────────────────┘  └──────────────────┘  └─────────────────────┘  │  │
│  │                                                                        │  │
│  │  ┌────────────────────────────────────────────────────────────────┐   │  │
│  │  │              Dapr Components (Pub/Sub, State Store)              │   │  │
│  │  │  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │   │  │
│  │  │  │   Redpanda     │  │ DO Managed      │  │ DO Managed        │ │   │  │
│  │  │  │   Cluster      │  │ Redis (Valkey)  │  │ PostgreSQL (Neon) │ │   │  │
│  │  │  │ (3 Replicas)   │  │ ($15/mo)        │  │ (External/Managed) │ │   │  │
│  │  │  └────────────────┘  └─────────────────┘  └──────────────────┘ │   │  │
│  │  └────────────────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### DigitalOcean Resources

| Resource | Specification | Monthly Cost |
|----------|--------------|--------------|
| **DOKS Cluster** | 3 nodes, s-4vcpu-8gb (Basic) | $60/mo ($20 × 3) |
| **Load Balancers** | 3 × DO Load Balancer | $36/mo ($12 × 3) |
| **Redis (Valkey)** | 1GB Basic | $15/mo |
| **Block Storage** | 50GB for Redpanda (3×) | $12/mo ($4 × 3) |
| **Container Registry** | 5GB storage | ~$5/mo |
| **Bandwidth** | Included with LB | Free |
| **Total** | | ~$128/mo |

**Note**: Neon PostgreSQL is external and not included in DO costs (~$25/mo separately).

### Components

#### 1. Frontend Microservice
- **Image**: `todo-frontend:latest`
- **Replicas**: 2-3 (HPA)
- **Dapr Sidecar**: Enabled
- **Port**: 3000

#### 2. Backend Microservice (API Gateway)
- **Image**: `todo-backend:latest`
- **Replicas**: 2-3 (HPA)
- **Dapr Sidecar**: Enabled
- **Port**: 8000

#### 3. Notification Microservice (New)
- **Image**: `todo-notifications:latest`
- **Replicas**: 1-2 (HPA)
- **Dapr Sidecar**: Enabled
- **Port**: 8001
- **Purpose**: Process due date events and recurring tasks

#### 4. Redpanda Cluster
- **Replicas**: 3
- **Topics**: task-created, task-updated, task-completed, task-due-soon, recurring-task-due
- **Replication Factor**: 3

#### 5. Dapr Components
- **Pub/Sub**: Redpanda for event streaming (self-managed on DOKS)
- **State Store**: DigitalOcean Managed Redis (Valkey) for state management

#### 6. DigitalOcean Integration
- **Load Balancer**: DigitalOcean LB for each service
- **Block Storage**: Persistent volumes for Redpanda (3× 50GB)
- **Container Registry**: DO Container Registry for image storage
- **Firewall**: DO Cloud Firewalls for cluster security

---

## Data Model

### New Tables

#### RecurringTask Model
```python
class RecurringTask(SQLModel, table=True):
    id: UUID
    user_id: UUID  # FK to users
    title: str
    description: Optional[str]
    priority: int  # 1=high, 2=medium, 3=low
    recurrence_type: str  # daily, weekly, monthly, yearly
    recurrence_interval: int  # Every N days/weeks/months
    start_date: datetime
    end_date: Optional[datetime]
    last_created_at: Optional[datetime]
    next_due_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

#### Task Model (Updated)
```python
class Task(SQLModel, table=True):
    # ... existing fields ...
    due_date: Optional[datetime]  # NEW
    notified: bool = False  # NEW
    recurring_task_id: Optional[UUID]  # NEW - FK to recurring_tasks
```

#### TaskEventLog (New)
```python
class TaskEventLog(SQLModel, table=True):
    id: UUID
    task_id: UUID  # FK to tasks
    event_type: str  # created, updated, completed, deleted, due
    event_data: dict  # JSON
    created_at: datetime
```

---

## API Contract

### Recurring Tasks Endpoints

#### POST /api/recurring-tasks
Create a new recurring task.

**Request**:
```json
{
  "title": "Weekly Team Meeting",
  "description": "Standup with the team",
  "priority": 2,
  "recurrence_type": "weekly",
  "recurrence_interval": 1,
  "start_date": "2025-01-01T09:00:00Z",
  "end_date": "2025-12-31T09:00:00Z"
}
```

**Response**: 201 Created
```json
{
  "id": "uuid",
  "title": "Weekly Team Meeting",
  "recurrence_type": "weekly",
  "next_due_at": "2025-01-08T09:00:00Z",
  "is_active": true
}
```

#### GET /api/recurring-tasks
List all recurring tasks for user.

**Response**: 200 OK
```json
{
  "items": [...],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

#### PUT /api/recurring-tasks/{id}
Update recurring task.

#### DELETE /api/recurring-tasks/{id}
Delete recurring task.

### Task Endpoints (Updated)

#### POST /api/tasks
Supports `due_date` field.

**Request**:
```json
{
  "title": "Complete report",
  "due_date": "2025-01-15T17:00:00Z"
}
```

---

## Dapr Configuration

### Pub/Sub Component

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.redpanda
  metadata:
  - name: brokers
    value: "redpanda-0.redpanda.default.svc.cluster.local:9092"
  - name: allowedTopics
    value: "task-created,task-updated,task-completed,task-due-soon,recurring-task-due"
```

### Event Topics

| Topic | Purpose | Publisher | Subscriber |
|-------|---------|-----------|------------|
| task-created | New task created | Backend | Notification |
| task-updated | Task modified | Backend | Analytics |
| task-completed | Task done | Backend | Notification |
| task-due-soon | Task due within 24h | Worker | Notification |
| recurring-task-due | Recurring task due | Worker | Notification |

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-push:
    # Build and push Docker images

  deploy:
    # Deploy to Kubernetes
    # Run health checks
```

---

## Dependencies

### DigitalOcean Services
- **DOKS**: DigitalOcean Kubernetes (1.29+)
- **Load Balancers**: 3 × DO Load Balancer
- **Managed Redis**: 1GB Basic tier for state store
- **Block Storage**: 3× 50GB volumes for Redpanda persistence
- **Container Registry**: DO CR for Docker image storage
- **Cloud Firewalls**: Network security policies

### External Services
- **Neon PostgreSQL**: External database (existing) OR DO Managed PostgreSQL
- **Redpanda**: Self-managed on DOKS (3 replicas)

### DO CLI Tool Required
- **doctl**: DigitalOcean CLI v1.100+
  ```bash
  # Install doctl
  brew install doctl  # macOS
  # or download from https://github.com/digitalocean/doctl/releases

  # Authenticate
  doctl auth init

  # Get Kubernetes config
  doctl kubernetes cluster kubeconfig save <cluster-name>
  ```

### Other Tools Required
- **kubectl**: 1.25+
- **Helm**: 3.0+
- **Dapr CLI**: 1.12+
- **kubectl-ai**: Latest (via krew)
- **kagent**: Latest (via npm)

---

## Non-Functional Requirements

### Performance
- **Event Latency**: <100ms
- **Notification Delivery**: <5 seconds
- **API Response**: <500ms

### Scalability
- **Throughput**: 1000 events/second
- **Concurrent Users**: 1000+
- **Horizontal Scaling**: HPA enabled

### Reliability
- **Event Delivery**: At-least-once
- **Pod Replicas**: Minimum 2
- **Multi-AZ**: Required

### Security
- **mTLS**: Dapr communication
- **RBAC**: Kubernetes roles
- **Secrets**: Encrypted at rest

---

## Validation Criteria

### Database
- [x] Migration for recurring tasks applied
- [x] Migration for task due dates applied
- [x] Foreign keys correct

### API Endpoints
- [x] POST /api/recurring-tasks works
- [x] GET /api/recurring-tasks works
- [x] PUT /api/recurring-tasks/{id} works
- [x] DELETE /api/recurring-tasks/{id} works
- [x] Task endpoints support due_date

### Event Publishing
- [x] Events published on task creation
- [x] Events published on task update
- [x] Events published on task completion
- [x] Event payload correct

### Event Subscription
- [x] Notification service subscribes
- [x] Events received and processed
- [x] Notifications sent for due tasks
- [x] Recurring tasks create occurrences

### Cloud Deployment (DigitalOcean)
- [x] DOKS cluster created (3 nodes, s-4vcpu-8gb)
- [x] doctl authenticated and kubeconfig configured
- [x] Dapr installed on DOKS
- [x] Redpanda installed with 3 replicas and block storage
- [x] DO Managed Redis provisioned
- [x] All services deployed via Helm
- [x] DO Load Balancers provisioned
- [x] Services accessible via DO Load Balancers
- [x] Cloud Firewalls configured

### CI/CD
- [x] Pipeline runs on push
- [x] Images build and push
- [x] Automatic deployment works
- [x] Health checks pass

### Monitoring
- [x] Prometheus scraping metrics
- [x] Grafana dashboards visible
- [x] Alert rules configured

---

## Success Metrics

- All services running with 2+ replicas
- Event latency <100ms
- Notification delivery within 5 seconds
- Zero data loss in event streaming
- CI/CD deploys in <10 minutes
- Uptime >99.9%

---

## Out of Scope

- Real-time WebSocket notifications
- Multi-tenant architecture
- Service mesh (Istio, Linkerd)
- Distributed tracing
- Database sharding
- Global multi-region deployment

---

## References

- [Dapr Documentation](https://dapr.io/docs/)
- [Redpanda Documentation](https://docs.redpanda.com/)
- [DigitalOcean Kubernetes (DOKS)](https://docs.digitalocean.com/products/kubernetes/)
- [doctl Documentation](https://docs.digitalocean.com/reference/doctl/)
- [DigitalOcean Container Registry](https://docs.digitalocean.com/products/container-registry/)
- [DigitalOcean Managed Redis](https://docs.digitalocean.com/products/databases/redis/)
- [DigitalOcean Load Balancers](https://docs.digitalocean.com/products/networking/load-balancers/)
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)

---

## DigitalOcean Setup Quick Reference

### Create DOKS Cluster via doctl
```bash
# Create cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --version 1.29.0 \
  --node-pool "name=pool-1;size=s-4vcpu-8gb;count=3;auto-scale=true;min-nodes=2;max-nodes=5"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-cluster

# Verify cluster
kubectl get nodes
```

### Create DO Managed Redis
```bash
# Create Redis cluster
doctl databases create todo-redis \
  --engine redis \
  --region nyc1 \
  --size 1gb \
  --num-nodes 1

# Get connection details
doctl databases connection todo-redis --format json
```

### Create Container Registry
```bash
# Create registry
doctl registry create

# Login to registry
doctl registry login

# Tag and push image
docker tag todo-frontend:latest registry.digitalocean.com/todo-app/todo-frontend:latest
docker push registry.digitalocean.com/todo-app/todo-frontend:latest
```

### Helm Deployment with DO Load Balancer
```yaml
# values-do.yaml
service:
  type: LoadBalancer  # Provisions DO Load Balancer automatically

# Deploy
helm install frontend helm/frontend -f helm/frontend/values-do.yaml
```
