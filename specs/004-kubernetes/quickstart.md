# Quick Start: Kubernetes Deployment

This guide will help you deploy the Todo application to Kubernetes in under 30 minutes.

---

## Prerequisites

Install these tools first:

```bash
# Docker
docker --version

# kubectl
kubectl version --client

# Helm
helm version

# Minikube (for local testing)
minikube version
```

---

## Local Development (Docker Compose)

### 1. Start All Services

```bash
docker-compose up
```

### 2. Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Stop Services

```bash
docker-compose down
```

---

## Minikube Deployment

### 1. Start Minikube

```bash
minikube start --cpus=4 --memory=8192
```

### 2. Build and Load Images

```bash
# Build images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# Load into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
```

### 3. Install Services

```bash
# Install backend
helm install backend helm/backend

# Install frontend
helm install frontend helm/frontend
```

### 4. Access Application

```bash
# Option 1: Minikube service
minikube service frontend

# Option 2: Tunnel (separate terminal)
minikube tunnel
# Access at localhost:30001
```

### 5. Verify Deployment

```bash
# Check pods
kubectl get pods

# Check services
kubectl get svc

# View logs
kubectl logs -l app.kubernetes.io/name=frontend --tail=50 -f
```

---

## Clean Up

```bash
# Uninstall Helm charts
helm uninstall frontend
helm uninstall backend

# Stop Minikube
minikube stop

# Or delete cluster
minikube delete
```

---

## Troubleshooting

### Pods Not Starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Images Not Found

```bash
minikube image ls
minikube image load todo-frontend:latest
```

### Services Not Accessible

```bash
minikube ip
kubectl get svc
```

---

## Next Steps

- Read [MINIKUBE_DEPLOYMENT_GUIDE.md](../../docs/MINIKUBE_DEPLOYMENT_GUIDE.md) for detailed deployment
- See [KUBERNETES_QUICK_REFERENCE.md](../../docs/KUBERNETES_QUICK_REFERENCE.md) for common commands
- Check [plan.md](./plan.md) for full implementation details
