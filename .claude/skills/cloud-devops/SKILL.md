---
name: cloud-deployment
description: Deploy Evolution of TODO to production cloud Kubernetes with event-driven architecture using Kafka, Dapr integration, and CI/CD pipelines. Use when Claude needs to set up cloud infrastructure on DigitalOcean/GKE/AKS, configure Kafka event streaming, implement Dapr building blocks, or create automated deployment pipelines for microservices.
license: Complete terms in LICENSE.txt
---

# Cloud Deployment

Deploys TODO app to cloud with Kafka and Dapr event streaming.

## Quick Start

Deploy to cloud:
```bash
/skill cloud-deployment provider=digitalocean
```

## Provider Selection

Supports multiple cloud providers:
- `digitalocean` - DigitalOcean Kubernetes (DOKS)
- `gcp` - Google Kubernetes Engine (GKE)
- `azure` - Azure Kubernetes Service (AKS)

## Implementation Steps

### 1. Provision Infrastructure
Create Kubernetes cluster with Terraform:
```hcl
# DigitalOcean example
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
}
```

### 2. Install Kafka
Deploy Strimzi Kafka operator:
```bash
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka
```

Create Kafka topics:
- `task-events` - Task CRUD events
- `reminders` - Due date notifications
- `task-updates` - State change events

### 3. Configure Dapr
Install Dapr runtime and components:
- Pub/Sub component for Kafka
- State store for PostgreSQL
- Cron bindings for reminders
- Secret management

### 4. Event-Driven Backend
Update backend services:
- Add event publishers for task operations
- Implement Kafka consumers via Dapr
- Configure event sourcing patterns

### 5. Setup CI/CD
Create GitHub Actions workflow:
- Build container images
- Deploy with Helm charts
- Automated rollback on failure

## Architecture Components

### Event Flow
```
User Action → API → Dapr Pub/Sub → Kafka → Event Handlers
                                      ↓
                               State Store (PostgreSQL)
                                      ↓
                               Notifications (Email/Push)
```

### Dapr Building Blocks
- **Pub/Sub**: Kafka integration for event streaming
- **State**: Distributed caching and session state
- **Bindings**: Cron triggers for recurring tasks
- **Secret**: Secure credential management

## Generated Files

```
cloud/
├── digitalocean/terraform/    # Infrastructure code
├── gcp/terraform/             # GCP resources
├── azure/terraform/           # Azure resources
kafka/
├── strimzi-operator.yaml     # Kafka cluster
└── topics/                    # Event topics
dapr/
├── pubsub.yaml               # Pub/Sub component
├── statestore.yaml           # State component
├── cron-binding.yaml         # Reminder scheduler
└── secrets.yaml              # Secret store
.github/workflows/
└── deploy.yml                # CI/CD pipeline
```

## Success Criteria

Deployment successful when:
- [ ] Kubernetes cluster running (3+ nodes)
- [ ] Kafka cluster healthy (3 brokers)
- [ ] Dapr components configured
- [ ] All services deployed and healthy
- [ ] Events flowing through topics
- [ ] CI/CD pipeline functional
- [ ] App accessible via HTTPS

## Monitoring

Set up observability:
- Prometheus metrics
- Grafana dashboards
- ELK stack for logs
- Jaeger for tracing

## Scaling Configuration

- Horizontal Pod Autoscaler
- Cluster autoscaling
- Kafka partition scaling
- Database connection pooling