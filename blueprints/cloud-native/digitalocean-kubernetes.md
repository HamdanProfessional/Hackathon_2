# DigitalOcean Kubernetes (DOKS) Deployment Blueprint

Production-ready deployment blueprint for Todo Application on DigitalOcean Kubernetes.

## Overview

- **Cluster**: DigitalOcean Kubernetes (DOKS)
- **Node Pools**: 3 nodes (Standard: 2x4GB, Premium: 1x8GB)
- **Region**: NYC1 (or nearest to users)
- **Services**: Frontend (Next.js), Backend (FastAPI), Notifications (Python)
- **Infrastructure**: Redpanda (Kafka), PostgreSQL (managed), Dapr

## 1. Cluster Setup

### 1.1 Create DOKS Cluster

```bash
# Install doctl CLI
curl -sL https://github.com/digitalocean/doctl/releases/download/v1.100.0/doctl-1.100.0-windows-amd64.zip -o doctl.zip
unzip doctl.zip
mv doctl.exe /usr/local/bin/

# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create todo-app-cluster \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --node-pool "name=worker-pool;count=3;size=s-4vcpu-8gb" \
  --auto-upgrade=true \
  --maintenance-window "wednesday=03:00" \
  --ha=true

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-app-cluster

# Verify
kubectl get nodes
```

### 1.2 Install Cluster Add-ons

```bash
# Install DigitalOcean CSI (for storage)
kubectl apply -f "https://raw.githubusercontent.com/digitalocean/csi-digitalocean/master/deploy/kubernetes/releases/csi-digitalocean-v1.28.0.yaml"

# Install metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.6.4/components.yaml

# Verify
kubectl get pods -n kube-system
```

## 2. Infrastructure Services

### 2.1 PostgreSQL Database

```bash
# Create DigitalOcean database
doctl databases create todo-app-db \
  --engine pg \
  --version 15 \
  --num-nodes 1 \
  --size db-s-2vcpu-4gb \
  --region nyc1

# Get connection string
doctl databases get todo-app-db --format Connection

# Create Kubernetes secret
kubectl create secret generic db-credentials \
  --from-literal=DATABASE_URL="postgresql://user:pass@host/db"

# Or use Terraform
resource "digitalocean_database_cluster" "todo_app_db" {
  name       = "todo-app-db"
  engine     = "pg"
  version    = "15"
  size       = "db-s-2vcpu-4gb"
  region     = "nyc1"
  node_count = 1
}
```

### 2.2 Redpanda (Kafka)

```bash
# Add Redpanda Helm repo
helm repo add redpanda https://charts.redpanda.com
helm repo update

# Create namespace
kubectl create namespace redpanda

# Install Redpanda
helm install redpanda redpanda/redpanda \
  --namespace redpanda \
  --set replicas=3 \
  --set resources.limits.cpu=4 \
  --set resources.limits.memory=8Gi \
  --set resources.requests.cpu=2 \
  --set resources.requests.memory=4Gi \
  --set persistence.storage=100Gi

# Create topics
kubectl exec -n redpanda redpanda-0 -- rpk topic create task-created
kubectl exec -n redpanda redpanda-0 -- rpk topic create task-updated
kubectl exec -n redpanda redpanda-0 -- rpk topic create task-completed
kubectl exec -n redpanda redpanda-0 -- rpk topic create task-deleted
kubectl exec -n redpanda redpanda-0 -- rpk topic create task-due-soon
kubectl exec -n redpanda redpanda-0 -- rpk topic create recurring-task-due
```

### 2.3 Dapr Installation

```bash
# Initialize Dapr on Kubernetes
dapr init --kubernetes --wait

# Verify Dapr system pods
kubectl get pods -n dapr-system

# Install Dapr with HA
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --set global.ha.enabled=true \
  --set global.ha.replicaCount=3 \
  --set dapr_placement.replicaCount=3 \
  --set dapr_sidecar_injector.replicaCount=3 \
  --set dapr_sentry.replicaCount=3 \
  --set dapr_operator.replicaCount=3
```

## 3. Application Deployment

### 3.1 Build and Push Container Images

```bash
# Set environment variables
export REGISTRY="registry.digitalocean.com/todo-app"
export VERSION=$(git rev-parse --short HEAD)

# Build and push images
docker build -t ${REGISTRY}/backend:${VERSION} backend/
docker build -t ${REGISTRY}/frontend:${VERSION} frontend/
docker build -t ${REGISTRY}/notifications:${VERSION} services/notifications/

doctl registry repository create todo-app-backend
doctl registry repository create todo-app-frontend
doctl registry repository create todo-app-notifications

docker push ${REGISTRY}/backend:${VERSION}
docker push ${REGISTRY}/frontend:${VERSION}
docker push ${REGISTRY}/notifications:${VERSION}
```

### 3.2 Deploy Backend

```bash
# Create namespace
kubectl create namespace todo-app

# Create secrets
kubectl create secret generic jwt-secret \
  --from-literal=JWT_SECRET_KEY="your-secret-key-here"

kubectl create secret generic ai-credentials \
  --from-literal=AI_API_KEY="your-groq-api-key"

kubectl create secret generic dapr-config \
  --from-literal=DAPR_ENABLED="true"

# Install backend
helm install backend helm/backend \
  --namespace todo-app \
  --set image.repository=${REGISTRY}/backend \
  --set image.tag=${VERSION} \
  --set image.pullSecrets[0].name=registry-credentials \
  --set replicaCount=3 \
  --set resources.limits.cpu=1000m \
  --set resources.limits.memory=1Gi \
  --set resources.requests.cpu=500m \
  --set resources.requests.memory=512Mi \
  --set env.DATABASE_URL="postgresql://user:pass@dohost/db" \
  --set env.REDPANDA_BROKERS="redpanda.redpanda.svc.cluster.local:9092" \
  --set dapr.enabled=true \
  --set dapr.appId="todo-backend" \
  --set dapr.appPort=8000
```

### 3.3 Deploy Frontend

```bash
# Install frontend
helm install frontend helm/frontend \
  --namespace todo-app \
  --set image.repository=${REGISTRY}/frontend \
  --set image.tag=${VERSION} \
  --set image.pullSecrets[0].name=registry-credentials \
  --set replicaCount=2 \
  --set resources.limits.cpu=500m \
  --set resources.limits.memory=512Mi \
  --set resources.requests.cpu=250m \
  --set resources.requests.memory=256Mi \
  --set env.NEXT_PUBLIC_API_URL="https://api.todo-app.com" \
  --set ingress.enabled=true \
  --set ingress.host="todo-app.com"
```

### 3.4 Deploy Notifications Service

```bash
# Install notifications
helm install notifications helm/notifications \
  --namespace todo-app \
  --set image.repository=${REGISTRY}/notifications \
  --set image.tag=${VERSION} \
  --set image.pullSecrets[0].name=registry-credentials \
  --set replicaCount=2 \
  --set resources.limits.cpu=500m \
  --set resources.limits.memory=512Mi \
  --set dapr.enabled=true \
  --set dapr.appId="todo-notifications" \
  --set dapr.subscriptions="all"
```

## 4. Monitoring & Logging

### 4.1 Prometheus and Grafana

```bash
# Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --create-namespace \
  --set server.persistentVolume.enabled=true

# Install Grafana
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set persistence.enabled=true \
  --set adminPassword="admin123"

# Get Grafana URL
kubectl get svc -n monitoring grafana
```

### 4.2 Loki (Log Aggregation)

```bash
# Install Loki
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set loki.persistence.enabled=true \
  --set promtail.enabled=true
```

## 5. CI/CD Pipeline

### 5.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy-doks.yml
name: Deploy to DigitalOcean Kubernetes

on:
  push:
    branches: [main]

env:
  REGISTRY: registry.digitalocean.com/todo-app
  CLUSTER: todo-app-cluster

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_TOKEN }}

      - name: Build and push images
        run: |
          VERSION=${{ github.sha }}
          docker build -t ${REGISTRY}/backend:${VERSION} backend/
          docker build -t ${REGISTRY}/frontend:${VERSION} frontend/
          docker push ${REGISTRY}/backend:${VERSION}
          docker push ${REGISTRY}/frontend:${VERSION}

      - name: Update kubeconfig
        run: doctl kubernetes cluster kubeconfig save ${CLUSTER}

      - name: Deploy to Kubernetes
        run: |
          VERSION=${{ github.sha }}
          helm upgrade --install backend helm/backend \
            --set image.tag=${VERSION}
          helm upgrade --install frontend helm/frontend \
            --set image.tag=${VERSION}
```

## 6. Security Hardening

### 6.1 Network Policies

```yaml
# Network policy to restrict traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: todo-app-network-policy
  namespace: todo-app
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: todo-app
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: redpanda
    ports:
    - protocol: TCP
      port: 9092
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### 6.2 Pod Security

```yaml
# Pod security context
apiVersion: v1
kind: Pod
metadata:
  name: backend
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: backend
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
```

## 7. Disaster Recovery

### 7.1 Backup Strategy

```bash
# PostgreSQL backup
doctl databases backup-list todo-app-db

# Restore backup
doctl databases backup restore <backup-id> todo-app-db

# Velero for cluster backup
velero install --provider digitalocean --bucket todo-app-backups
velero backup create todo-app-backup --include-namespaces todo-app
```

### 7.2 Rollback Procedure

```bash
# Helm rollback
helm rollback backend
helm rollback frontend

# Or rollback to specific revision
helm rollback backend 2
```

## 8. Scaling

### 8.1 Horizontal Pod Autoscaler

```bash
# Enable HPA on backend
kubectl autoscale deployment backend \
  --namespace todo-app \
  --cpu-percent=70 \
  --min=3 \
  --max=10

# Enable HPA on frontend
kubectl autoscale deployment frontend \
  --namespace todo-app \
  --cpu-percent=70 \
  --min=2 \
  --max=5
```

### 8.2 Cluster Autoscaler

```bash
# Enable cluster autoscaler on DOKS
doctl kubernetes cluster update todo-app-cluster \
  --auto-upgrade=true \
  --node-pools "worker-pool:auto-scale=3..10;min-nodes=3;max-nodes=10"
```

## 9. Cost Optimization

- Use spot instances for non-critical workloads
- Enable cluster autoscaler
- Set resource requests/limits appropriately
- Use DigitalOcean's reserved pricing for 12-month commitment
- Monitor and optimize with Cost Analysis

## 10. Troubleshooting

### 10.1 Common Issues

```bash
# Check pod status
kubectl get pods -n todo-app

# View logs
kubectl logs -n todo-app deployment/backend -f

# Describe pod
kubectl describe pod -n todo-app backend-xxx

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Port forward to local
kubectl port-forward -n todo-app svc/backend 8000:80

# Test API locally
curl http://localhost:8000/api/health
```

### 10.2 Performance Tuning

```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n todo-app

# Adjust resources
kubectl set resources deployment backend \
  --limits=cpu=2000m,memory=2Gi \
  --requests=cpu=1000m,memory=1Gi \
  -n todo-app
```

## Conclusion

This blueprint provides a production-ready deployment of the Todo Application on DigitalOcean Kubernetes with:
- High availability (3+ replicas)
- Auto-scaling (HPA + cluster autoscaler)
- Monitoring (Prometheus + Grafana)
- Logging (Loki)
- CI/CD automation
- Security hardening
- Disaster recovery

Total estimated cost: $300-500/month depending on traffic and scaling needs.
