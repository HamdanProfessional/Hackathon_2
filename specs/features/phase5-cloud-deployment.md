# Feature: Phase V - Cloud Deployment with Event-Driven Architecture

## Overview
Deploy the Todo application to a production cloud Kubernetes cluster with event-driven architecture using Dapr, Kafka/Redpanda, and CI/CD automation. This phase transforms the monolithic architecture into microservices with event streaming, enabling horizontal scaling, fault tolerance, and advanced features like recurring tasks and due dates.

## User Stories
- **US-1**: As a developer, I want to deploy to cloud Kubernetes (DOKS/GKE/AKS), so that I can have a production-ready scalable application
- **US-2**: As a developer, I want to implement event-driven architecture with Dapr and Kafka, so that services can communicate asynchronously
- **US-3**: As a user, I want to set recurring tasks and due dates, so that I can manage my tasks more effectively
- **US-4**: As a developer, I want automated CI/CD pipelines, so that deployments are reliable and repeatable
- **US-5**: As an operator, I want to use kubectl-ai and kagent for cluster management, so that I can leverage AI assistance

## Acceptance Criteria
- [ ] **AC-1**: Application deployed to cloud Kubernetes (DOKS/GKE/AKS)
- [ ] **AC-2**: Dapr sidecar injected into all pods
- [ ] **AC-3**: Kafka/Redpanda cluster running and accessible
- [ ] **AC-4**: Event publishing working from backend services
- [ ] **AC-5**: Event subscriptions receiving and processing events
- [ ] **AC-6**: Recurring tasks feature implemented and working
- [ ] **AC-7**: Due dates feature implemented with notifications
- [ ] **AC-8**: CI/CD pipeline automated (GitHub Actions)
- [ ] **AC-9**: kubectl-ai configured and functional
- [ ] **AC-10**: kagent configured and functional for operations
- [ ] **AC-11**: Application passes all health checks in production
- [ ] **AC-12**: Monitoring and logging configured (Prometheus/Grafana)

## Architecture

### Microservices Architecture Overview
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Production Cloud Kubernetes                          │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                          Ingress Controller (NGINX)                    │  │
│  │  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────────┐   │  │
│  │  │  Frontend SVC   │  │   API Gateway    │  │  Notification SVC    │   │  │
│  │  │  (LoadBalancer) │  │  (LoadBalancer)  │  │  (LoadBalancer)      │   │  │
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
│  │  │  │   Kafka/       │  │   Redis         │  │   PostgreSQL     │ │   │  │
│  │  │  │   Redpanda     │  │   (State)       │  │   (External)     │ │   │  │
│  │  │  │   Cluster      │  │                 │  │                  │ │   │  │
│  │  │  └────────────────┘  └─────────────────┘  └──────────────────┘ │   │  │
│  │  └────────────────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    CI/CD Pipeline (GitHub Actions)                  │    │
│  │  Build → Test → Push → Deploy to K8s → Health Check → Notify        │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

Legend:
- SVC: Kubernetes Service (LoadBalancer for cloud)
- Pod: Container instance(s) with Dapr sidecar
- Dapr Sidecar: /dapr HTTP and gRPC endpoints
- External Database: Neon PostgreSQL (cloud-hosted)
```

### Component Breakdown

#### 1. Frontend Microservice
- **Base Image**: `todo-frontend:latest`
- **Framework**: Next.js 14 with App Router
- **Runtime**: Standalone Node.js server
- **Port**: 3000
- **Dapr Sidecar**: HTTP port 3500, gRPC port 50001
- **Replicas**: 2-3 (Horizontal scaling)

#### 2. Backend Microservice (API Gateway)
- **Base Image**: `todo-backend:latest`
- **Framework**: FastAPI with Uvicorn
- **Runtime**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Port**: 8000
- **Dapr Sidecar**: HTTP port 3500, gRPC port 50001
- **Replicas**: 2-3 (Horizontal scaling)

#### 3. Notification Microservice (New)
- **Base Image**: `todo-notifications:latest`
- **Framework**: FastAPI with Background Tasks
- **Purpose**: Process task due date events and send notifications
- **Runtime**: `uvicorn app.notification:app --host 0.0.0.0 --port 8001`
- **Port**: 8001
- **Dapr Sidecar**: HTTP port 3500, gRPC port 50001
- **Replicas**: 1-2

#### 4. Kafka/Redpanda Cluster
- **Implementation**: Redpanda (Kafka-compatible, simpler)
- **Purpose**: Event streaming for task operations
- **Topics**:
  - `task-created`: Trigger notification service
  - `task-updated`: Update analytics
  - `task-completed`: Record completion metrics
  - `task-due-soon`: Trigger due date notifications
  - `recurring-task-due`: Create next occurrence
- **Replication Factor**: 3
- **Partitions**: 3 per topic

#### 5. Dapr Components
- **Pub/Sub**: Redpanda for event streaming
- **State Store**: Redis for caching (optional)
- **Secrets**: Kubernetes secrets
- **Configuration**: Kubernetes ConfigMaps

## Data Model

### New Tables/Models Required

#### Recurring Task Model
```python
class RecurringTask(SQLModel, table=True):
    """Recurring task configuration."""
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    title: str
    description: Optional[str] = None
    priority: int = Field(default=2)  # 1=high, 2=medium, 3=low
    recurrence_type: str  # 'daily', 'weekly', 'monthly', 'yearly'
    recurrence_interval: int = Field(default=1)  # Every N days/weeks/months
    start_date: datetime
    end_date: Optional[datetime] = None  # Optional end date
    last_created_at: Optional[datetime] = None  # Last time a task was created
    next_due_at: datetime  # Next occurrence
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Task Model (Updated)
```python
class Task(SQLModel, table=True):
    """Task model with due date support."""
    # ... existing fields ...
    due_date: Optional[datetime] = None  # NEW: Due date for task
    notified: bool = Field(default=False)  # NEW: Whether user was notified
    recurring_task_id: Optional[uuid.UUID] = Field(foreign_key="recurringtask.id")  # NEW
```

#### Task Event Log (New - for audit)
```python
class TaskEventLog(SQLModel, table=True):
    """Audit log for task events."""
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    task_id: uuid.UUID = Field(foreign_key="task.id")
    event_type: str  # 'created', 'updated', 'completed', 'deleted', 'due'
    event_data: dict  # JSON event payload
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Database Migration
```bash
# Create migration for recurring tasks
alembic revision --autogenerate -m "Add recurring tasks and due dates"
alembic upgrade head
```

## API Endpoints

### Recurring Tasks Endpoints

#### 1. Create Recurring Task
- **Method**: POST
- **Path**: `/api/recurring-tasks`
- **Auth**: Required (JWT Bearer token)
- **Request Body**:
  ```json
  {
    "title": "Weekly Team Meeting",
    "description": "Standup meeting with the team",
    "priority": 2,
    "recurrence_type": "weekly",
    "recurrence_interval": 1,
    "start_date": "2025-01-01T09:00:00Z",
    "end_date": "2025-12-31T09:00:00Z"
  }
  ```
- **Response (201)**:
  ```json
  {
    "id": "uuid",
    "user_id": "uuid",
    "title": "Weekly Team Meeting",
    "description": "Standup meeting with the team",
    "priority": 2,
    "recurrence_type": "weekly",
    "recurrence_interval": 1,
    "start_date": "2025-01-01T09:00:00Z",
    "end_date": "2025-12-31T09:00:00Z",
    "next_due_at": "2025-01-08T09:00:00Z",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  }
  ```

#### 2. List Recurring Tasks
- **Method**: GET
- **Path**: `/api/recurring-tasks`
- **Auth**: Required
- **Response (200)**:
  ```json
  {
    "items": [
      {
        "id": "uuid",
        "title": "Weekly Team Meeting",
        "recurrence_type": "weekly",
        "next_due_at": "2025-01-08T09:00:00Z",
        "is_active": true
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
  ```

#### 3. Update Recurring Task
- **Method**: PUT
- **Path**: `/api/recurring-tasks/{recurring_task_id}`
- **Auth**: Required
- **Request Body**:
  ```json
  {
    "title": "Updated Title",
    "is_active": false
  }
  ```
- **Response (200)**: Updated recurring task

#### 4. Delete Recurring Task
- **Method**: DELETE
- **Path**: `/api/recurring-tasks/{recurring_task_id}`
- **Auth**: Required
- **Response (204)**: No content

### Task Endpoints (Updated)

#### Update Task with Due Date
- **Method**: PUT
- **Path**: `/api/tasks/{task_id}`
- **Request Body**:
  ```json
  {
    "title": "Updated Task",
    "due_date": "2025-01-15T17:00:00Z"
  }
  ```

## Dapr Configuration

### Dapr Components (Kubernetes)

#### 1. Pub/Sub Component (Redpanda)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
  namespace: default
spec:
  type: pubsub.redpanda
  version: v1
  metadata:
  - name: brokers
    value: "redpanda-0.redpanda.default.svc.cluster.local:9092"
  - name: authRequired
    value: "false"
  - name: allowedTopics
    value: "task-created,task-updated,task-completed,task-due-soon,recurring-task-due"
```

#### 2. State Store Component (Redis - Optional)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-state
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis-secrets
      key: password
```

### Dapr Sidecar Configuration

#### Backend Deployment with Dapr
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"
        - name: DAPR_GRPC_PORT
          value: "50001"
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "debug"
```

## Event-Driven Architecture

### Event Publishing (Backend)

#### Publish Event on Task Creation
```python
from dapr.clients import DaprClient

async def publish_task_created_event(task: Task):
    """Publish task-created event to Dapr pub/sub."""
    with DaprClient() as dapr:
        event_data = {
            "task_id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "timestamp": datetime.utcnow().isoformat()
        }
        dapr.publish_event(
            pubsub_name="todo-pubsub",
            topic_name="task-created",
            data=json.dumps(event_data),
            data_content_type="application/json"
        )
```

### Event Subscription (Notification Service)

#### Subscribe to Task Events
```python
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="todo-pubsub", topic="task-created")
def handle_task_created_event(event_data: dict):
    """Handle task-created event."""
    task_id = event_data.get("task_id")
    due_date = event_data.get("due_date")

    if due_date:
        # Schedule notification for due date
        schedule_notification(task_id, due_date)

    # Log event
    log_task_event(task_id, "task-created", event_data)
```

## CI/CD Pipeline

### GitHub Actions Workflow

#### .github/workflows/deploy.yml
```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  FRONTEND_IMAGE: todo-frontend
  BACKEND_IMAGE: todo-backend

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push Frontend
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}:latest,${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Build and push Backend
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}:latest,${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up kubectl
      uses: azure/setup-kubectl@v3

    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

    - name: Update Helm charts
      run: |
        helm upgrade --install frontend helm/frontend \
          --set image.repository=${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }} \
          --set image.tag=${{ github.sha }} \
          --namespace todo --create-namespace

        helm upgrade --install backend helm/backend \
          --set image.repository=${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }} \
          --set image.tag=${{ github.sha }} \
          --namespace todo --create-namespace

    - name: Verify deployment
      run: |
        kubectl rollout status deployment/frontend -n todo
        kubectl rollout status deployment/backend -n todo

    - name: Health check
      run: |
        kubectl run -it --rm health-check --image=curlimages/curl --restart=Never \
          -- curl -f http://backend-service:8000/health
```

## Cloud Platform Setup

### DigitalOcean Kubernetes (DOKS)

#### 1. Create Cluster
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

# Verify
kubectl get nodes
```

#### 2. Install Dapr
```bash
# Install Dapr to Kubernetes cluster
dapr init --kubernetes --namespace dapr-system

# Verify Dapr installation
kubectl get pods -n dapr-system
```

#### 3. Install Redpanda
```bash
# Add Redpanda Helm repo
helm repo add redpanda https://charts.redpanda.com
helm repo update

# Install Redpanda
helm install redpanda redpanda/redpanda --set replicas=3

# Verify Redpanda
kubectl get pods -l app=redpanda
```

#### 4. Install Nginx Ingress
```bash
# Install ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/do/deploy.yaml

# Verify
kubectl get pods -n ingress-nginx
```

### Google Kubernetes Engine (GKE)

#### 1. Create Cluster
```bash
# Set project
gcloud config set project todo-app-project

# Create cluster
gcloud container clusters create todo-cluster \
  --region=us-central1 \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=5

# Get credentials
gcloud container clusters get-credentials todo-cluster --region=us-central1
```

#### 2. Install Dapr (same as DOKS)

#### 3. Install Redpanda (same as DOKS)

### Azure Kubernetes Service (AKS)

#### 1. Create Cluster
```bash
# Create resource group
az group create --name todo-app-rg --location eastus

# Create cluster
az aks create \
  --resource-group todo-app-rg \
  --name todo-cluster \
  --node-count 3 \
  --node-vm-size Standard_B4ms \
  --enable-managed-identity \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 5

# Get credentials
az aks get-credentials --resource-group todo-app-rg --name todo-cluster
```

## Monitoring and Logging

### Prometheus Monitoring

#### 1. Install Prometheus Operator
```bash
# Add Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack
```

#### 2. Configure ServiceMonitors
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backend-monitor
spec:
  selector:
    matchLabels:
      app: todo-backend
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### Grafana Dashboards

#### Import Pre-built Dashboards
```bash
# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80

# Default credentials: admin / prom-operator
# Import dashboards for:
# - Node Exporter
# - Kubernetes Cluster
# - Dapr Metrics
```

## kubectl-ai Integration

### Installation and Usage
```bash
# Install kubectl-ai via krew
kubectl krew install ai

# List all pods with AI assistance
kubectl ai list pods

# Scale deployment with AI
kubectl ai scale deployment backend --replicas=3

# Generate deployment manifest
kubectl ai generate deployment todo-notifications --image=todo-notifications:latest --port=8001

# Troubleshoot issues
kubectl ai troubleshoot pod/backend-xxx
```

## kagent Integration

### Installation and Usage
```bash
# Install kagent
npm install -g @kagent/cli

# Initialize
kagent init

# Interactive commands
kagent "Deploy the backend service with 3 replicas"
kagent "Check the status of all Redpanda pods"
kagent "Create a new Dapr component for Redis"
kagent "Scale up the frontend for high traffic"
kagent "Show me the error logs from backend service"
```

## Implementation Phases

### Phase 1: Database Schema Updates (Day 1)
1. **Create Recurring Task Model**:
   - Add `RecurringTask` model to `backend/app/models/recurring_task.py`
   - Update `Task` model with `due_date` and `recurring_task_id` fields
   - Create migration with Alembic

2. **Run Migration**:
   ```bash
   alembic revision --autogenerate -m "Add recurring tasks and due dates"
   alembic upgrade head
   ```

### Phase 2: Backend API Development (Days 2-3)
1. **Create Recurring Tasks CRUD**:
   - `backend/app/crud/recurring_task.py`
   - `backend/app/schemas/recurring_task.py`
   - `backend/app/api/recurring_tasks.py`

2. **Update Task API**:
   - Add `due_date` field to task schemas
   - Update task creation and update endpoints

3. **Implement Dapr Event Publishing**:
   - Install Dapr Python SDK: `pip install dapr`
   - Create `backend/app/services/event_publisher.py`
   - Publish events on task CRUD operations

### Phase 3: Notification Service (Days 4-5)
1. **Create Notification Service**:
   - `backend/app/services/notification.py`
   - Background task for checking due dates
   - Process recurring task occurrences

2. **Create Notification Dockerfile**:
   - `services/notifications/Dockerfile`
   - `services/notifications/app/main.py`

3. **Dapr Event Subscriptions**:
   - Subscribe to `task-created`, `task-updated` topics
   - Subscribe to `task-due-soon` topic

### Phase 4: Kubernetes Cloud Deployment (Days 6-7)
1. **Create Cloud Cluster**:
   - Choose platform (DOKS/GKE/AKS)
   - Create cluster with appropriate sizing
   - Configure kubectl context

2. **Install Dapr**:
   ```bash
   dapr init --kubernetes
   kubectl get pods -n dapr-system
   ```

3. **Install Redpanda**:
   ```bash
   helm repo add redpanda https://charts.redpanda.com
   helm install redpanda redpanda/redpanda --set replicas=3
   ```

4. **Create Dapr Components**:
   - Apply `k8s/dapr-components/` manifests
   - Configure pub/sub component for Redpanda

5. **Deploy Services**:
   - Build and push Docker images
   - Update Helm charts for cloud
   - Install with production values

### Phase 5: CI/CD Pipeline (Day 8)
1. **Create GitHub Actions Workflow**:
   - `.github/workflows/deploy.yml`
   - Build and push images
   - Deploy to Kubernetes
   - Health checks

2. **Configure Secrets**:
   - Add `KUBECONFIG` to GitHub secrets
   - Add registry credentials

3. **Test Pipeline**:
   - Push to main branch
   - Verify automated deployment

### Phase 6: kubectl-ai and kagent (Day 9)
1. **Install kubectl-ai**:
   ```bash
   kubectl krew install ai
   kubectl ai --help
   ```

2. **Install kagent**:
   ```bash
   npm install -g @kagent/cli
   kagent init
   ```

3. **Test AI Operations**:
   - Use `kubectl ai` for common operations
   - Use `kagent` for complex workflows

### Phase 7: Monitoring and Validation (Day 10)
1. **Install Prometheus/Grafana**:
   ```bash
   helm install prometheus prometheus-community/kube-prometheus-stack
   ```

2. **Configure Monitoring**:
   - ServiceMonitors for services
   - Grafana dashboards
   - Alert rules

3. **End-to-End Testing**:
   - Create task with due date
   - Create recurring task
   - Verify event publishing
   - Verify notification delivery
   - Test scaling

## Dependencies & Integration

### Existing Features
- **Phase I**: Console app (not affected)
- **Phase II**: Web app with FastAPI + Next.js
- **Phase III**: AI Chatbot with Groq/Gemini
- **Phase IV**: Kubernetes deployment (foundation for Phase V)

### New Features
- **Recurring Tasks**: Automated task creation based on schedule
- **Due Dates**: Tasks can have due dates with notifications
- **Event-Driven**: Async communication via Dapr + Kafka
- **Notification Service**: Background worker for notifications

### External Services
- **Neon PostgreSQL**: External database (existing)
- **Redpanda**: Kafka-compatible event streaming (new)
- **Redis**: Optional state store for Dapr (new)
- **Dapr**: Distributed application runtime (new)

## Non-Functional Requirements

### Performance
- **Event Latency**: <100ms for event publishing
- **Notification Delivery**: <5 seconds after due date
- **Pod Startup Time**: <30 seconds
- **API Response Time**: <500ms

### Scalability
- **Horizontal Scaling**: HPA enabled for all services
- **Event Throughput**: 1000 events/second per partition
- **Concurrent Users**: 1000+ concurrent users

### Reliability
- **Event Delivery**: At-least-once delivery guarantee
- **Retry Logic**: Exponential backoff for failed events
- **Pod Replicas**: Minimum 2 replicas per service
- **Cluster HA**: Multi-AZ deployment

### Security
- **mTLS**: Dapr sidecar communication encrypted
- **RBAC**: Kubernetes role-based access control
- **Secrets Management**: Kubernetes secrets for sensitive data
- **Network Policies**: Restrict pod-to-pod communication

## Testing

### Unit Tests
```bash
# Test recurring task logic
pytest tests/test_recurring_task.py

# Test event publishing
pytest tests/test_event_publisher.py
```

### Integration Tests
```bash
# Test event flow
pytest tests/test_event_flow.py

# Test Dapr integration
pytest tests/test_dapr_integration.py
```

### End-to-End Tests
```bash
# Create recurring task
curl -X POST https://api.example.com/api/recurring-tasks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Daily Standup","recurrence_type":"daily"}'

# Verify task created
curl https://api.example.com/api/tasks?user_id=$USER_ID

# Wait for next occurrence (or trigger manually)
# Verify new task created
```

## Out of Scope
- Mobile application (separate project)
- Real-time WebSocket notifications (can add later)
- Multi-tenant architecture (single-tenant for now)
- Advanced monitoring (distributed tracing)
- Service mesh (Istio, Linkerd)
- Database sharding
- Global multi-region deployment

## Bonus Opportunities

### Automation (+100 points)
- **Automated Testing**: Comprehensive test suite
- **Automated Backups**: Database backup automation
- **Auto-Scaling**: Cluster autoscaler based on load
- **Self-Healing**: Automatic pod restart on failure

### Advanced Features (+150 points)
- **Recurring Task Patterns**: Complex patterns (every 2 weeks, 3rd Monday)
- **Task Dependencies**: Task B depends on Task A completion
- **Task Reminders**: Multiple reminders before due date
- **Task Templates**: Predefined recurring task templates

### AI-Enhanced Operations (+200 points)
- **kubectl-ai**: Comprehensive usage for cluster management
- **kagent**: Advanced workflows for deployment and troubleshooting
- **Predictive Scaling**: AI forecasts resource needs
- **Anomaly Detection**: AI-powered monitoring alerts

### Security Hardening (+100 points)
- **Pod Security Policies**: Restrict container capabilities
- **Secret Encryption**: Encrypt Kubernetes secrets at rest
- **Network Policies**: Restrict all inter-pod communication
- **Security Scanning**: Container image scanning

## Validation Checklist

### Database Schema
- [ ] RecurringTask model created
- [ ] Task model updated with due_date
- [ ] Migration created and applied
- [ ] Foreign keys established
- [ ] Indexes created for performance

### API Endpoints
- [ ] POST /api/recurring-tasks creates recurring task
- [ ] GET /api/recurring-tasks lists recurring tasks
- [ ] PUT /api/recurring-tasks/{id} updates recurring task
- [ ] DELETE /api/recurring-tasks/{id} deletes recurring task
- [ ] Task endpoints support due_date field

### Event Publishing
- [ ] Events published on task creation
- [ ] Events published on task update
- [ ] Events published on task completion
- [ ] Event payload contains all required data

### Event Subscription
- [ ] Notification service subscribes to topics
- [ ] Events received and processed correctly
- [ ] Notifications sent for due tasks
- [ ] Recurring tasks create new occurrences

### Cloud Deployment
- [ ] Kubernetes cluster created
- [ ] Dapr installed and running
- [ ] Redpanda installed with 3 replicas
- [ ] All services deployed with Dapr sidecars
- [ ] Services accessible via LoadBalancer

### CI/CD Pipeline
- [ ] GitHub Actions workflow created
- [ ] Images build and push on commit
- [ ] Automatic deployment to Kubernetes
- [ ] Health checks pass after deployment

### Monitoring
- [ ] Prometheus installed and scraping metrics
- [ ] Grafana dashboards configured
- [ ] Alert rules configured
- [ ] Logs aggregated and searchable

## Success Metrics
- All services running with 2+ replicas
- Event latency <100ms
- API response time <500ms
- Notification delivery within 5 seconds
- Zero data loss in event streaming
- CI/CD pipeline deploys in <10 minutes
- Uptime >99.9%

## References
- Dapr Documentation: https://dapr.io/docs/
- Redpanda Documentation: https://docs.redpanda.com/
- DigitalOcean Kubernetes: https://docs.digitalocean.com/products/kubernetes/
- Google Kubernetes Engine: https://cloud.google.com/kubernetes-engine
- Azure Kubernetes Service: https://docs.microsoft.com/en-us/azure/aks/
- Prometheus: https://prometheus.io/docs/
- Grafana: https://grafana.com/docs/
