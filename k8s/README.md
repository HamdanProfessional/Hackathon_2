# Kubernetes Manifests for Local/Minikube Development

This directory contains Kubernetes manifests for deploying the Todo application to a local Minikube cluster. These configurations are **separate from production** and will NOT affect Digital Ocean deployments.

## Production vs Local Development

| Environment | Location | Deployment Method |
|-------------|----------|-------------------|
| **Production** | Digital Ocean DOKS | Helm Charts (`helm/` directory) |
| **Local/Dev** | Minikube | Direct K8s Manifests (`k8s/` directory) |

## Prerequisites

1. **Minikube** installed and running:
   ```bash
   minikube start
   ```

2. **kubectl** configured to use Minikube:
   ```bash
   kubectl config use-context minikube
   ```

3. **Docker images** built locally:
   ```bash
   # From project root
   docker build -t todo-backend:latest ./backend
   docker build -t todo-frontend:latest ./frontend

   # Load images into Minikube
   minikube image load todo-backend:latest
   minikube image load todo-frontend:latest
   ```

## Quick Start

### Option 1: Deploy Backend Only

```bash
# Apply backend manifests
kubectl apply -f k8s/backend/configmap.yaml
kubectl apply -f k8s/backend/secrets.yaml
kubectl apply -f k8s/backend/deployment.yaml
kubectl apply -f k8s/backend/service.yaml
kubectl apply -f k8s/backend/ingress.yaml

# Check status
kubectl get pods -l app.kubernetes.io/name=backend
kubectl get svc todo-backend
```

### Option 2: Deploy Frontend Only

```bash
# Apply frontend manifests
kubectl apply -f k8s/frontend/deployment.yaml
kubectl apply -f k8s/frontend/service.yaml
kubectl apply -f k8s/frontend/ingress.yaml

# Check status
kubectl get pods -l app.kubernetes.io/name=frontend
kubectl get svc todo-frontend
```

### Option 3: Deploy All (Using Script)

```bash
bash k8s/deploy-local.sh
```

## Kafka Deployment (Optional)

For event-driven architecture with Dapr:

```bash
# Deploy Kafka to kafka namespace
bash k8s/kafka/deploy-kafka-local.sh

# Verify Kafka is running
kubectl get pods -n kafka
kubectl get svc -n kafka
```

## Accessing the Application

### Via NodePort

```bash
# Get Minikube URL for backend
minikube service todo-backend --url

# Get Minikube URL for frontend
minikube service todo-frontend --url
```

### Via Ingress (Recommended)

Add entries to `/etc/hosts`:

```
<minikube-ip> todo-backend.local
<minikube-ip> todo.local
```

Get Minikube IP:
```bash
minikube ip
```

Then access:
- Backend: http://todo-backend.local
- Frontend: http://todo.local

## Configuration

### Backend Secrets

Edit `k8s/backend/secrets.yaml` before deploying:

```yaml
stringData:
  database-url: "postgresql+asyncpg://user:pass@host:5432/db"
  jwt-secret: "your-secret-key-min-32-chars"
  groq-api-key: "your-groq-key"  # Optional
  gemini-api-key: "your-gemini-key"  # Optional
  openai-api-key: "your-openai-key"  # Optional
```

For better security, create secrets using kubectl:

```bash
kubectl create secret generic todo-backend-secrets \
  --from-literal=database-url='your-db-url' \
  --from-literal=jwt-secret='your-secret' \
  --from-literal=groq-api-key='your-key' \
  -n default
```

### Backend ConfigMap

Edit `k8s/backend/configmap.yaml` to adjust settings:

```yaml
data:
  cors-origins: "http://localhost:3000,http://frontend:3000"
  app-name: "Todo CRUD API"
  debug: "true"
  jwt-algorithm: "HS256"
  jwt-access-token-expire-minutes: "1440"
```

### Frontend Environment

Edit `k8s/frontend/deployment.yaml` to set API URL:

```yaml
env:
  - name: NEXT_PUBLIC_API_URL
    value: "http://todo-backend:8000"
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod for errors
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name> -f
```

### Images Not Found

Make sure to load images into Minikube:

```bash
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

### Ingress Not Working

Enable NGINX Ingress Controller in Minikube:

```bash
minikube addons enable ingress
```

### Database Connection Issues

For local development, you can:
1. Use a local PostgreSQL instance
2. Use Neon (production) for testing (not recommended for dev)
3. Deploy PostgreSQL in the cluster

Example PostgreSQL deployment:

```bash
kubectl apply -f https://raw.githubusercontent.com/bitnami/charts/main/bitnami/postgresql/templates/svc.yaml
```

## Cleaning Up

```bash
# Delete all resources
kubectl delete -f k8s/backend/
kubectl delete -f k8s/frontend/

# Delete Kafka (if deployed)
kubectl delete -f k8s/kafka/kafka-local.yaml
kubectl delete namespace kafka

# Delete Dapr components
kubectl delete -f k8s/dapr-components/
```

## Production Deployment

For production deployment on Digital Ocean, use the Helm charts:

```bash
# Backend
helm install todo-backend helm/backend/ -f helm/backend/values-prod.yaml

# Frontend
helm install todo-frontend helm/frontend/ -f helm/frontend/values-prod.yaml
```

## Namespaces

| Environment | Namespace | Purpose |
|-------------|-----------|---------|
| Local/Dev | `default` | Local development |
| Production | `production` | Production deployment on DOKS |

**Important**: The manifests in this directory use the `default` namespace to avoid conflicts with production.
