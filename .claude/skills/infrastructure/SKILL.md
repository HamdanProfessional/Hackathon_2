---
name: kubernetes-setup
description: Set up complete Kubernetes environment for TODO app supporting both local Minikube development and cloud deployment (DigitalOcean DOKS, GKE, AKS). Use when Claude needs to create Kubernetes manifests, Helm charts, configure services, deploy containerized applications, or integrate AI DevOps tools like kubectl-ai and kagent.
license: Complete terms in LICENSE.txt
---

# Kubernetes Setup

Sets up K8s for TODO app locally or in cloud.

## Quick Start

Local development:
```bash
/skill kubernetes-setup environment=local
```

Cloud deployment:
```bash
/skill kubernetes-setup environment=cloud provider=digitalocean
```

## Environment Options

- `local` - Minikube for development
- `cloud` - Production cluster
  - `digitalocean` - DOKS
  - `gke` - Google Kubernetes Engine
  - `aks` - Azure Kubernetes Service

## Implementation Steps

### 1. Prerequisites Check
Verify tools installed:
```bash
# Required for all environments
docker --version
kubectl version

# Local only
minikube version

# Cloud only
doctl version  # DigitalOcean
gcloud version # GKE
az version      # AKS
```

### 2. Create Kubernetes Manifests
Generate deployment YAMLs:
- Frontend (Next.js) deployment
- Backend (FastAPI) deployment with Dapr sidecar
- Services for networking
- ConfigMaps for configuration
- Secrets for credentials

Example deployment structure:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: todo-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    spec:
      containers:
      - name: fastapi
        image: todo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
```

### 3. Generate Helm Chart
Create reusable deployment package:
```
helm-chart/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default values
└── templates/
    ├── deployment.yaml # Pod templates
    ├── service.yaml    # Service definitions
    ├── configmap.yaml  # Configuration
    └── ingress.yaml    # External access
```

### 4. Setup Infrastructure

#### Local (Minikube)
```bash
# Start cluster
minikube start --cpus=4 --memory=8192

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Build images locally
eval $(minikube docker-env)
docker build -t todo-backend:latest ./backend
```

#### Cloud
```bash
# DigitalOcean
doctl kubernetes cluster kubeconfig save todo-cluster

# Deploy with Helm
helm upgrade --install evolution-of-todo ./helm-chart \
  --namespace todo-production \
  --create-namespace
```

### 5. Configure Services
- **Frontend**: NodePort/LoadBalancer on port 3000
- **Backend**: ClusterIP on port 8000
- **Database**: External Neon connection
- **Ingress**: nginx controller for HTTP routing

### 6. AI DevOps Integration
Install AI-powered tools:
- `kubectl-ai` - Natural language kubectl commands
- `kagent` - Kubernetes optimization agent
- `Docker AI (Gordon)` - Container optimization

## Generated Files

```
k8s/
├── namespace.yaml         # App namespace
├── configmap.yaml         # App configuration
├── secrets.yaml            # Credentials
├── frontend-deployment.yaml
├── backend-deployment.yaml
├── frontend-service.yaml
├── backend-service.yaml
└── ingress.yaml            # External access

helm-chart/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── configmap.yaml
    └── ingress.yaml

scripts/
├── setup-local.sh          # Minikube setup
└── setup-cloud.sh          # Cloud deployment
```

## Configuration

### Environment Variables
Create secrets for:
- `DATABASE_URL` - PostgreSQL connection
- `GEMINI_API_KEY` - AI service
- `JWT_SECRET_KEY` - Authentication

### Values Override
Customize deployment with values.yaml:
```yaml
frontend:
  replicaCount: 3
  image:
    tag: v1.2.0

backend:
  replicaCount: 5
  resources:
    limits:
      cpu: 1000m
      memory: 2Gi

ingress:
  enabled: true
  host: todo-app.yourdomain.com
```

## Success Criteria

Setup complete when:
- [ ] Cluster running and accessible
- [ ] All pods in Running state
- [ ] Services responding to health checks
- [ ] Application accessible via URL
- [ ] Helm chart installs successfully
- [ ] AI tools integrated

## Troubleshooting

### Pods Not Starting
```bash
kubectl describe pod <name> -n todo-app
kubectl logs <pod-name> -n todo-app
```

### Image Pull Issues
```bash
# For local development
eval $(minikube docker-env)
docker build -t todo-backend:latest .

# For cloud
kubectl create secret docker-registry regcred \
  --docker-server=<registry-url> \
  --docker-username=<username> \
  --docker-password=<password>
```

### Access Issues
```bash
# Check services
kubectl get svc -n todo-app

# Port forward for testing
kubectl port-forward svc/backend 8000:8000 -n todo-app
```