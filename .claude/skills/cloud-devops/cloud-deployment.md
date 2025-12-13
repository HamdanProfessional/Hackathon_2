# Cloud Deployment Skill

**Type**: Agent Skill
**Category**: Cloud & DevOps
**Phases**: Phase V

---

## Purpose

This skill handles advanced cloud deployment for the Evolution of TODO project, including event-driven architecture with Kafka, Dapr integration, and multi-cloud Kubernetes deployment.

---

## Skill Invocation

```
/skill cloud-deployment provider=digitalocean
```

Or via Claude Code Task tool:
```python
Task(
    subagent_type="cloud-deployment",
    description="Deploy to cloud with Kafka and Dapr",
    prompt="Deploy Evolution of TODO to DigitalOcean Kubernetes with Kafka event streaming and Dapr"
)
```

---

## What This Skill Does

1. **Cloud Infrastructure Setup**
   - Provisions Kubernetes cluster
   - Configures networking
   - Sets up load balancers
   - Manages DNS/domains

2. **Kafka Integration**
   - Deploys Kafka cluster (Strimzi) or connects to Redpanda Cloud
   - Creates topics (task-events, reminders, task-updates)
   - Configures producers/consumers
   - Sets up monitoring

3. **Dapr Integration**
   - Installs Dapr runtime
   - Configures building blocks (Pub/Sub, State, Bindings, Secrets)
   - Creates Dapr components
   - Adds sidecar annotations

4. **Event-Driven Architecture**
   - Implements event sourcing
   - Sets up CQRS pattern
   - Creates event handlers
   - Configures dead-letter queues

5. **CI/CD Pipeline**
   - GitHub Actions workflows
   - Automated testing
   - Container building
   - Kubernetes deployment
   - Rollback strategy

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Cloud Kubernetes Cluster                         │
│                       (DigitalOcean DOKS / GKE / AKS)                   │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                      Ingress Controller                        │    │
│  │                  (nginx-ingress / LoadBalancer)                │    │
│  └──────────────────────────┬─────────────────────────────────────┘    │
│                             │                                          │
│        ┌────────────────────┼────────────────────┐                     │
│        │                    │                    │                     │
│  ┌─────▼──────┐    ┌───────▼──────┐    ┌───────▼──────┐               │
│  │ Frontend   │    │  Chat API    │    │ Notification │               │
│  │ (Next.js)  │    │  (FastAPI)   │    │  Service     │               │
│  │            │    │              │    │              │               │
│  │ + Dapr     │    │ + Dapr       │    │ + Dapr       │               │
│  │ Sidecar    │    │ Sidecar      │    │ Sidecar      │               │
│  └────────────┘    └──────┬───────┘    └──────┬───────┘               │
│                           │                   │                        │
│                           │                   │                        │
│  ┌────────────────────────┼───────────────────┼────────────────────┐   │
│  │              Dapr Control Plane             │                   │   │
│  │  ┌──────────────────────────────────────────────────────────┐  │   │
│  │  │  Pub/Sub Component (Kafka)                               │  │   │
│  │  ├──────────────────────────────────────────────────────────┤  │   │
│  │  │  State Store Component (PostgreSQL)                      │  │   │
│  │  ├──────────────────────────────────────────────────────────┤  │   │
│  │  │  Bindings Component (Cron for reminders)                 │  │   │
│  │  ├──────────────────────────────────────────────────────────┤  │   │
│  │  │  Secrets Component (Kubernetes Secrets)                  │  │   │
│  │  └──────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────┬────────────────────────────────────────┘   │
│                            │                                           │
│  ┌─────────────────────────▼────────────────────────────────────────┐   │
│  │                  Kafka Cluster (Strimzi Operator)                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │   │
│  │  │ task-events  │  │  reminders   │  │ task-updates │           │   │
│  │  │   Topic      │  │   Topic      │  │   Topic      │           │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │                External Services                                  │   │
│  │  - Neon PostgreSQL (Database)                                     │   │
│  │  - Redpanda Cloud (Optional Kafka alternative)                    │   │
│  │  - OpenAI API                                                     │   │
│  └───────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Generated Files

### 1. Cloud Provider Setup

#### DigitalOcean (`cloud/digitalocean/terraform/main.tf`)
```hcl
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

variable "do_token" {}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_kubernetes_cluster" "todo_cluster" {
  name    = "evolution-of-todo"
  region  = "nyc1"
  version = "1.28.2-do.0"

  node_pool {
    name       = "worker-pool"
    size       = "s-4vcpu-8gb"
    auto_scale = true
    min_nodes  = 3
    max_nodes  = 10
  }

  tags = ["hackathon", "phase-v"]
}

output "cluster_id" {
  value = digitalocean_kubernetes_cluster.todo_cluster.id
}

output "kubeconfig" {
  value     = digitalocean_kubernetes_cluster.todo_cluster.kube_config[0].raw_config
  sensitive = true
}
```

---

### 2. Kafka Setup

#### Strimzi Operator (`kafka/strimzi-operator.yaml`)
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: evolution-todo-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
    storage:
      type: persistent-claim
      size: 10Gi
      class: do-block-storage
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 5Gi
      class: do-block-storage
  entityOperator:
    topicOperator: {}
    userOperator: {}
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: evolution-todo-kafka
spec:
  partitions: 6
  replicas: 3
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: evolution-todo-kafka
spec:
  partitions: 3
  replicas: 3
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: evolution-todo-kafka
spec:
  partitions: 6
  replicas: 3
```

---

### 3. Dapr Components

#### Pub/Sub Component (`dapr/pubsub.yaml`)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-production
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "evolution-todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
  - name: consumerGroup
    value: "todo-service"
  - name: authType
    value: "none"
  - name: maxMessageBytes
    value: 1024000
scopes:
- backend-service
- notification-service
- recurring-task-service
```

#### State Store Component (`dapr/statestore.yaml`)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-production
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: database-secret
      key: url
  - name: tableName
    value: "dapr_state"
  - name: keyPrefix
    value: "todo"
scopes:
- backend-service
- notification-service
```

#### Cron Binding Component (`dapr/cron-binding.yaml`)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-scheduler
  namespace: todo-production
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "*/5 * * * *"  # Every 5 minutes
  - name: direction
    value: "input"
scopes:
- notification-service
```

#### Secrets Component (`dapr/secrets.yaml`)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: todo-production
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
scopes:
- backend-service
```

---

### 4. Event-Driven Backend

#### Kafka Producer (`backend/services/event_publisher.py`)
```python
"""
Event Publisher Service
Publishes task events to Kafka via Dapr
"""
import httpx
from typing import Dict, Any

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"

async def publish_event(topic: str, event_type: str, data: Dict[str, Any]) -> None:
    """
    Publish event to Kafka via Dapr Pub/Sub.

    Args:
        topic: Kafka topic name (task-events, reminders, task-updates)
        event_type: Event type (created, updated, completed, deleted)
        data: Event payload
    """
    event = {
        "event_type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}",
            json=event
        )
        response.raise_for_status()

# Usage in FastAPI endpoints
@app.post("/api/{user_id}/tasks")
async def create_task(user_id: str, task: TaskCreate):
    # Create task in database
    new_task = await create_task_in_db(user_id, task)

    # Publish event
    await publish_event(
        topic="task-events",
        event_type="created",
        data={
            "task_id": new_task.id,
            "user_id": user_id,
            "title": new_task.title,
            "description": new_task.description
        }
    )

    return new_task
```

#### Kafka Consumer (`backend/services/event_handlers.py`)
```python
"""
Event Handler Service
Subscribes to Kafka topics via Dapr
"""
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/dapr/subscribe")
async def subscribe():
    """Tell Dapr which topics to subscribe to."""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task-events"
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/events/reminders"
        }
    ]

@app.post("/events/task-events")
async def handle_task_event(request: Request):
    """Handle task events from Kafka."""
    event = await request.json()
    event_type = event.get("event_type")
    data = event.get("data")

    if event_type == "created" and data.get("recurring"):
        # Schedule next occurrence for recurring tasks
        await schedule_recurring_task(data)

    # Log to audit trail
    await log_audit_event(event_type, data)

    return {"status": "SUCCESS"}

@app.post("/events/reminders")
async def handle_reminder(request: Request):
    """Handle reminder events from Kafka."""
    event = await request.json()

    # Send notification via email/push
    await send_notification(
        user_id=event["data"]["user_id"],
        message=f"Reminder: {event['data']['title']}"
    )

    return {"status": "SUCCESS"}
```

---

### 5. CI/CD Pipeline

#### GitHub Actions (`.github/workflows/deploy.yml`)
```yaml
name: Deploy to Cloud

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push Frontend image
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-frontend:${{ github.sha }}

    - name: Build and push Backend image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Install doctl
      uses: digitalocean/action-doctl@v2
      with:
        token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

    - name: Save kubeconfig
      run: doctl kubernetes cluster kubeconfig save evolution-of-todo

    - name: Deploy with Helm
      run: |
        helm upgrade --install evolution-of-todo ./helm-chart \
          --namespace todo-production \
          --create-namespace \
          --set frontend.image.tag=${{ github.sha }} \
          --set backend.image.tag=${{ github.sha }} \
          --set dapr.enabled=true \
          --set kafka.enabled=true \
          --wait

    - name: Verify deployment
      run: |
        kubectl rollout status deployment/frontend -n todo-production
        kubectl rollout status deployment/backend -n todo-production
```

---

## Deployment Steps

### Step 1: Provision Cloud Infrastructure
```bash
# DigitalOcean
cd cloud/digitalocean/terraform
terraform init
terraform apply -var="do_token=$DO_TOKEN"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save evolution-of-todo
```

### Step 2: Install Kafka
```bash
# Install Strimzi operator
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka

# Deploy Kafka cluster
kubectl apply -f kafka/strimzi-operator.yaml

# Wait for Kafka to be ready
kubectl wait kafka/evolution-todo-kafka --for=condition=Ready --timeout=300s -n kafka
```

### Step 3: Install Dapr
```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes
dapr init -k

# Deploy Dapr components
kubectl apply -f dapr/
```

### Step 4: Deploy Application
```bash
# Deploy with Helm
helm upgrade --install evolution-of-todo ./helm-chart \
  --namespace todo-production \
  --create-namespace \
  --set dapr.enabled=true \
  --set kafka.enabled=true \
  --wait
```

### Step 5: Configure DNS
```bash
# Get LoadBalancer IP
kubectl get svc ingress-nginx-controller -n ingress-nginx

# Add DNS A record pointing to LoadBalancer IP
# todo-app.yourdomain.com → <LoadBalancer-IP>
```

---

## Success Criteria

Cloud deployment is successful when:

1. ✅ Kubernetes cluster provisioned
2. ✅ Kafka cluster running (3 brokers)
3. ✅ Dapr installed and components configured
4. ✅ All pods Running and healthy
5. ✅ Events flowing through Kafka
6. ✅ Dapr Pub/Sub working
7. ✅ CI/CD pipeline deploying
8. ✅ App accessible via public URL

---

## Deliverables

When this skill completes, you'll have:

1. ✅ Cloud infrastructure (Terraform)
2. ✅ Kafka cluster (Strimzi)
3. ✅ Dapr components configured
4. ✅ Event-driven backend
5. ✅ CI/CD pipeline (GitHub Actions)
6. ✅ Monitoring & logging
7. ✅ Production-ready deployment

---

**Skill Version**: 1.0.0
**Created**: 2025-12-13
**Hackathon Points**: Contributes to Phase V (300 pts) and +200 bonus (Cloud-Native Blueprints)
**Phase**: V
