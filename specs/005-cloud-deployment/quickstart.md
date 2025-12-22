# Quick Start: Cloud Deployment with Event-Driven Architecture

This guide helps you get started with Phase V implementation.

---

## Prerequisites

### Tools to Install

```bash
# kubectl
kubectl version --client

# Helm
helm version

# Dapr CLI
dapr version

# kubectl-ai (via krew)
kubectl krew install ai

# kagent
npm install -g @kagent/cli
```

### Cloud Account

Choose one:
- **DigitalOcean**: Create account at digitalocean.com
- **Google Cloud**: Create project at console.cloud.google.com
- **Azure**: Create account at portal.azure.com

---

## Day 1: Database Setup

### Run Migration

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Add recurring tasks and due dates"

# Apply migration
alembic upgrade head

# Verify
psql $DATABASE_URL -c "\dt"
```

You should see new tables: `recurringtask`, `taskeventlog`.

---

## Day 2: API Development

### Install Dependencies

```bash
cd backend
pip install dapr
```

### Test Recurring Tasks API

```bash
# Start backend
uvicorn app.main:app --reload

# Create recurring task (in another terminal)
curl -X POST http://localhost:8000/api/recurring-tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily Standup",
    "recurrence_type": "daily",
    "start_date": "2025-01-01T09:00:00Z"
  }'
```

---

## Day 3: Dapr Setup

### Initialize Dapr

```bash
# Install Dapr to Kubernetes cluster
dapr init --kubernetes

# Verify
kubectl get pods -n dapr-system
```

### Create Dapr Components

```bash
kubectl apply -f k8s/dapr-components/
```

---

## Day 4-5: Notification Service

### Build and Run Locally

```bash
cd services/notifications

# Install dependencies
pip install -r requirements.txt

# Run worker
python -m app.main
```

### Build Docker Image

```bash
docker build -t todo-notifications:latest .
```

---

## Day 6: Cloud Cluster Setup

### DigitalOcean (DOKS)

```bash
# Install doctl
brew install doctl

# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --node-pool "name=pool-1;size=s-4vcpu-8gb;count=3"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-cluster
```

### Google Cloud (GKE)

```bash
# Create cluster
gcloud container clusters create todo-cluster \
  --region=us-central1 \
  --num-nodes=3

# Get credentials
gcloud container clusters get-credentials todo-cluster --region=us-central1
```

### Azure (AKS)

```bash
# Create cluster
az aks create \
  --resource-group todo-rg \
  --name todo-cluster \
  --node-count 3

# Get credentials
az aks get-credentials --resource-group todo-rg --name todo-cluster
```

---

## Day 7: Deploy to Cloud

### Push Images

```bash
# Tag for registry
docker tag todo-frontend:latest ghcr.io/username/todo-frontend:latest
docker tag todo-backend:latest ghcr.io/username/todo-backend:latest
docker tag todo-notifications:latest ghcr.io/username/todo-notifications:latest

# Push
docker push ghcr.io/username/todo-frontend:latest
docker push ghcr.io/username/todo-backend:latest
docker push ghcr.io/username/todo-notifications:latest
```

### Deploy with Helm

```bash
# Create secrets
kubectl create secret generic backend-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=jwt-secret="$JWT_SECRET"

# Install services
helm install frontend helm/frontend \
  --set image.repository=ghcr.io/username/todo-frontend

helm install backend helm/backend \
  --set image.repository=ghcr.io/username/todo-backend

helm install notifications helm/notifications \
  --set image.repository=ghcr.io/username/todo-notifications
```

---

## Day 8: CI/CD Pipeline

### Create GitHub Actions Workflow

File: `.github/workflows/deploy.yml`

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build images
      run: |
        docker build -t ghcr.io/todo-backend ./backend
        docker push ghcr.io/todo-backend
```

### Add GitHub Secrets

1. Go to repository Settings > Secrets
2. Add `KUBECONFIG` (base64 encoded)
3. Add `GHCR_TOKEN`

---

## Day 9: AI Tools

### kubectl-ai

```bash
# List pods with AI
kubectl ai list pods

# Scale with AI
kubectl ai scale deployment backend --replicas=3

# Troubleshoot
kubectl ai troubleshoot pod/backend-xxx
```

### kagent

```bash
# Initialize
kagent init

# Use AI assistant
kagent "Show me the backend logs"
kagent "Create a Dapr component for Redis"
kagent "Scale the frontend for high traffic"
```

---

## Day 10: Monitoring

### Install Prometheus

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack
```

### Access Grafana

```bash
kubectl port-forward svc/prometheus-grafana 3000:80
```

Open http://localhost:3000
- Username: `admin`
- Password: `prom-operator`

---

## Testing

### Create Task with Due Date

```bash
curl -X POST $API_URL/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Complete report",
    "due_date": "2025-01-15T17:00:00Z"
  }'
```

### Create Recurring Task

```bash
curl -X POST $API_URL/api/recurring-tasks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Daily Standup",
    "recurrence_type": "daily",
    "start_date": "2025-01-01T09:00:00Z"
  }'
```

### Verify Events

```bash
# Check Redpanda topics
kubectl exec -it redpanda-0 -- rpk topic list

# Consume events
kubectl exec -it redpanda-0 -- rpk topic consume task-created
```

---

## Clean Up

```bash
# Uninstall services
helm uninstall frontend backend notifications

# Delete Redpanda
helm uninstall redpanda

# Uninstall Dapr
dapr uninstall --kubernetes

# Delete cluster (DOKS)
doctl kubernetes cluster delete todo-cluster
```

---

## Next Steps

- Read full [spec.md](./spec.md) for details
- Follow [plan.md](./plan.md) for 10-day implementation
- See [tasks.md](./tasks.md) for complete task list
