# Frontend Helm Chart

Helm chart for deploying the Todo App frontend (Next.js 14) to Kubernetes.

## Prerequisites

- Kubernetes cluster (Minikube, DOKS, GKE, AKS, etc.)
- Helm 3.x installed
- kubectl configured for your cluster

## Quick Start

### Minikube

```bash
# Start Minikube
minikube start

# Build and load image
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend

# Install Helm chart
helm install todo-frontend helm/frontend

# Get URL
minikube service todo-frontend --url
```

### Cloud Kubernetes (DOKS, GKE, AKS)

```bash
# Push image to registry
docker tag todo-frontend:latest your-registry/todo-frontend:latest
docker push your-registry/todo-frontend:latest

# Update values.yaml with your registry
# image.repository = your-registry/todo-frontend

# Install Helm chart
helm install todo-frontend helm/frontend \
  --set image.repository=your-registry/todo-frontend \
  --set image.tag=latest \
  --set service.type=LoadBalancer
```

## Configuration

### Required Values

```yaml
image:
  repository: todo-frontend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: NodePort  # Use LoadBalancer for cloud
  port: 3000
```

### Optional Values

```yaml
replicaCount: 2

resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"

ingress:
  enabled: false
  className: "nginx"
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: frontend-tls
      hosts:
        - app.example.com

env:
  NEXT_PUBLIC_API_URL: "http://backend-service:8000"
```

## Install Commands

```bash
# Lint the chart
helm lint helm/frontend

# Dry run
helm install todo-frontend helm/frontend --dry-run --debug

# Install with default values
helm install todo-frontend helm/frontend

# Install with custom values
helm install todo-frontend helm/frontend -f custom-values.yaml

# Upgrade
helm upgrade todo-frontend helm/frontend

# Uninstall
helm uninstall todo-frontend
```

## Accessing the Application

### Minikube (NodePort)

```bash
# Get URL
minikube service todo-frontend --url

# Or access via node IP
kubectl get nodes -o wide
# Access at http://<NODE-IP>:30001
```

### Cloud (LoadBalancer)

```bash
# Get external IP
kubectl get svc todo-frontend

# Access at http://<EXTERNAL-IP>:3000
```

## Troubleshooting

```bash
# Check pod status
kubectl get pods -l app=todo-frontend

# View logs
kubectl logs -l app=todo-frontend

# Describe service
kubectl describe svc todo-frontend

# Port forward to local
kubectl port-forward svc/todo-frontend 3000:3000
```

## Values Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `2` |
| `image.repository` | Docker image repository | `todo-frontend` |
| `image.tag` | Docker image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Kubernetes service type | `NodePort` |
| `service.port` | Container port | `3000` |
| `service.nodePort` | NodePort for Minikube | `30001` |
| `resources.requests.memory` | Memory request | `128Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `ingress.enabled` | Enable ingress | `false` |
| `env.NEXT_PUBLIC_API_URL` | Backend API URL | `http://backend-service:8000` |
