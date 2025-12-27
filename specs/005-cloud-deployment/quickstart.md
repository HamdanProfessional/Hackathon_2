# Quick Start: Cloud Deployment with Event-Driven Architecture on DigitalOcean

**Status**: ✅ **IMPLEMENTATION COMPLETE**

This guide helps you get started with Phase V implementation on **DigitalOcean Kubernetes (DOKS)**.

## 🎉 Production Deployment

The application has been successfully deployed to production:

| Service | URL |
|---------|-----|
| **Frontend** | https://hackathon2.testservers.online |
| **Backend API** | https://api.testservers.online |
| **API Docs** | https://api.testservers.online/docs |

All 86 tests passing (100%), including all Phase V E2E tests and bonus features.

---

---

## Prerequisites

### Tools to Install

```bash
# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Helm
brew install helm

# doctl (DigitalOcean CLI)
brew install doctl

# Dapr CLI
brew install dapr/tap/dapr-cli

# kubectl-ai (via krew)
kubectl krew install ai

# kagent
npm install -g @kagent/cli
```

### DigitalOcean Account

1. Create account at [digitalocean.com](https://www.digitalocean.com)
2. Generate API token: Account > API > Generate New Token
3. Save token for doctl authentication

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

## Day 6: DigitalOcean Cluster Setup

### Install and Authenticate doctl

```bash
# Install doctl
brew install doctl

# Authenticate with your API token
doctl auth init

# Verify authentication
doctl account get
```

### Create DOKS Cluster

```bash
# Create cluster with 3 nodes (autoscaling 2-5)
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --version 1.29.0 \
  --node-pool "name=pool-1;size=s-4vcpu-8gb;count=3;auto-scale=true;min-nodes=2;max-nodes=5"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-cluster

# Verify cluster
kubectl get nodes
kubectl cluster-info
```

### Create DO Managed Redis

```bash
# Create Redis database for Dapr state store
doctl databases create todo-redis \
  --engine redis \
  --region nyc1 \
  --size 1gb \
  --num-nodes 1

# Get connection details
doctl databases connection todo-redis --format json > redis-connection.json
cat redis-connection.json | jq '.host, .port, .password'
```

### Create DO Container Registry

```bash
# Create registry
doctl registry create

# Login to registry
doctl registry login
```

### Install Dapr and Redpanda on DOKS

```bash
# Install Dapr
dapr init --kubernetes
kubectl get pods -n dapr-system

# Install Redpanda with DO Block Storage
helm repo add redpanda https://charts.redpanda.com
helm repo update

helm install redpanda redpanda/redpanda \
  --set replicas=3 \
  --set persistence.size=50Gi \
  --set resources.requests.cpu=2 \
  --set resources.requests.memory=4Gi

# Verify Redpanda
kubectl get pods -l app=redpanda
```

---

## Day 7: Deploy to DigitalOcean

### Build and Push Images to DO Registry

```bash
# Build images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
docker build -t todo-notifications:latest ./services/notifications

# Tag for DO registry
docker tag todo-frontend:latest registry.digitalocean.com/todo-app/todo-frontend:latest
docker tag todo-backend:latest registry.digitalocean.com/todo-app/todo-backend:latest
docker tag todo-notifications:latest registry.digitalocean.com/todo-app/todo-notifications:latest

# Push to DO registry
docker push registry.digitalocean.com/todo-app/todo-frontend:latest
docker push registry.digitalocean.com/todo-app/todo-backend:latest
docker push registry.digitalocean.com/todo-app/todo-notifications:latest
```

### Deploy with Helm

```bash
# Create secrets
kubectl create secret generic backend-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=groq-api-key="$GROQ_API_KEY"

# Create Redis secret
kubectl create secret generic redis-secrets \
  --from-literal=redis-host="<REDIS_HOST>" \
  --from-literal=redis-port="<REDIS_PORT>" \
  --from-literal=redis-password="<REDIS_PASSWORD>"

# Install services (provisions DO Load Balancers automatically)
helm install frontend helm/frontend \
  -f helm/frontend/values-do.yaml \
  --namespace production --create-namespace

helm install backend helm/backend \
  -f helm/backend/values-do.yaml \
  --namespace production --create-namespace

helm install notifications helm/notifications \
  -f helm/notifications/values-do.yaml \
  --namespace production --create-namespace
```

### Verify Deployment

```bash
# Check pods
kubectl get pods -n production

# Check Load Balancers
kubectl get svc -n production

# Get Load Balancer IPs
doctl compute load-balancer list
```

---

## Day 8: CI/CD Pipeline with DigitalOcean

### Create GitHub Actions Workflow

File: `.github/workflows/deploy-digitalocean.yml`

```yaml
name: Deploy to DigitalOcean

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Login to DO Registry
      run: docker login registry.digitalocean.com -u ${{ secrets.DO_REGISTRY_TOKEN }} -p ${{ secrets.DO_REGISTRY_TOKEN }}

    - name: Build and push
      run: |
        docker build -t registry.digitalocean.com/todo-app/todo-backend:${{ github.sha }} ./backend
        docker push registry.digitalocean.com/todo-app/todo-backend:${{ github.sha }}

    - name: Install doctl
      uses: digitalocean/action-doctl@v2
      with:
        token: ${{ secrets.DO_ACCESS_TOKEN }}

    - name: Deploy to DOKS
      run: |
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        helm upgrade --install backend helm/backend --set image.tag=${{ github.sha }}
```

### Add GitHub Secrets

1. Go to repository Settings > Secrets > New secret
2. Add `DO_REGISTRY_TOKEN` (from `doctl registry token create`)
3. Add `DO_ACCESS_TOKEN` (from DO dashboard)
4. Add `KUBECONFIG` (base64 encoded kubeconfig)

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
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

### Access Grafana

```bash
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
```

Open http://localhost:3000
- Username: `admin`
- Password: `prom-operator`

---

## Testing

### Create Task with Due Date

```bash
# Get Load Balancer IP
LB_IP=$(kubectl get svc backend -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

curl -X POST http://$LB_IP/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Complete report",
    "due_date": "2025-01-15T17:00:00Z"
  }'
```

### Create Recurring Task

```bash
curl -X POST http://$LB_IP/api/recurring-tasks \
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
helm uninstall frontend backend notifications -n production

# Delete Redpanda
helm uninstall redpanda

# Uninstall Dapr
dapr uninstall --kubernetes

# Delete DO Managed Redis
doctl databases delete todo-redis

# Delete DOKS cluster
doctl kubernetes cluster delete todo-cluster

# Delete DO Container Registry (optional)
doctl registry delete
```

---

## Cost Summary

| DigitalOcean Service | Monthly Cost |
|---------------------|--------------|
| DOKS Cluster (3 nodes) | $60 |
| Load Balancers (3×) | $36 |
| Managed Redis | $15 |
| Block Storage (150GB) | $12 |
| Container Registry | ~$5 |
| **Total** | **~$128/mo** |

---

## Next Steps

- Read full [spec.md](./spec.md) for DigitalOcean architecture details
- Follow [plan.md](./plan.md) for 10-day DigitalOcean implementation
- See [tasks.md](./tasks.md) for complete task list
- Review [research.md](./research.md) for technology decisions
