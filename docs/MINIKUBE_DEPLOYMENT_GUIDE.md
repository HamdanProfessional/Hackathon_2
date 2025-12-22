# Minikube Deployment Guide - Phase IV

This guide walks through deploying the Todo App to Minikube using the Helm charts created for Phase IV.

## Prerequisites

### 1. Install Required Tools

```bash
# Install Minikube
# Windows: Download from https://minikube.sigs.k8s.io/docs/start/
# chocolatey install minikube

# Install kubectl
# Windows: choco install kubernetes-cli

# Install Helm
# Windows: choco install kubernetes-helm

# Verify installations
minikube version
kubectl version --client
helm version
```

### 2. Start Minikube

```bash
# Start Minikube with adequate resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable ingress (optional, for domain routing)
minikube addons enable ingress

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

## Phase 1: Build Docker Images

### Option A: Build and Load to Minikube (Recommended for Local)

```bash
# Navigate to project root
cd C:\Users\User\Desktop\PIAIC_HACKATHON_1\Hackathon_2

# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Build backend image
docker build -t todo-backend:latest ./backend

# Load images into Minikube
minikube image load todo-frontend:latest
minikube image load todo-backend:latest

# Verify images in Minikube
minikube image ls
```

### Option B: Push to Registry (For Production)

```bash
# Tag images for registry
docker tag todo-frontend:latest your-registry/todo-frontend:v1.0.0
docker tag todo-backend:latest your-registry/todo-backend:v1.0.0

# Push to registry
docker push your-registry/todo-frontend:v1.0.0
docker push your-registry/todo-backend:v1.0.0

# Update Helm values with registry images
# Edit helm/frontend/values.yaml and helm/backend/values.yaml
```

## Phase 2: Configure Environment

### Create Production Secrets

```bash
# Create a secrets file for backend
cat > helm/backend/values-prod.yaml << 'EOF'
secrets:
  databaseUrl: "postgresql+asyncpg://neondb_owner:password@ep-xxx.aws.neon.tech/neondb?sslmode=require"
  jwtSecret: "your-production-jwt-secret-min-32-chars"
  groqApiKey: "gsk_xxx..."
  geminiApiKey: "AIzaSyxxx..."
  openaiApiKey: "sk-xxx..."

image:
  tag: "latest"

service:
  type: NodePort
  nodePort: 30002
EOF

# Create production values for frontend
cat > helm/frontend/values-prod.yaml << 'EOF'
image:
  tag: "latest"

service:
  type: NodePort
  nodePort: 30001

env:
  NEXT_PUBLIC_API_URL: "http://backend-service:8000"
EOF
```

## Phase 3: Install Helm Charts

### Install Backend

```bash
# Lint the chart first
helm lint helm/backend

# Install with production values
helm install backend helm/backend -f helm/backend/values-prod.yaml

# Check deployment
kubectl get pods -l app.kubernetes.io/name=backend
kubectl get svc backend
```

### Install Frontend

```bash
# Lint the chart first
helm lint helm/frontend

# Install with production values
helm install frontend helm/frontend -f helm/frontend/values-prod.yaml

# Check deployment
kubectl get pods -l app.kubernetes.io/name=frontend
kubectl get svc frontend
```

## Phase 4: Access the Application

### Option A: Minikube Tunnel (Recommended)

```bash
# Start tunnel in a separate terminal
minikube tunnel

# Access via NodePort
# Frontend: http://localhost:30001
# Backend API: http://localhost:30002
```

### Option B: Minikube Service

```bash
# Open frontend in browser
minikube service frontend

# Open backend API in browser
minikube service backend
```

### Option C: Port Forwarding

```bash
# Forward frontend port
kubectl port-forward svc/frontend 3000:3000

# Forward backend port
kubectl port-forward svc/backend 8000:8000

# Access at http://localhost:3000 and http://localhost:8000
```

## Phase 5: Verify Deployment

### Check Pod Status

```bash
# Get all pods
kubectl get pods

# Describe pod for details
kubectl describe pod <pod-name>

# View logs
kubectl logs -l app.kubernetes.io/name=frontend --tail=50 -f
kubectl logs -l app.kubernetes.io/name=backend --tail=50 -f
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:30002/health

# Test frontend-backend communication
# Open http://localhost:30001 in browser
```

## Phase 6: Enable Horizontal Pod Autoscaling (Optional)

```bash
# Enable HPA for frontend
helm upgrade frontend helm/frontend -f helm/frontend/values-prod.yaml --set autoscaling.enabled=true

# Enable HPA for backend
helm upgrade backend helm/backend -f helm/backend/values-prod.yaml --set autoscaling.enabled=true

# Check HPA status
kubectl get hpa
```

## Troubleshooting

### Common Issues

**Pods not starting:**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**Image pull errors:**
```bash
# Verify image is in Minikube
minikube image ls | grep todo

# Load image again
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
```

**Service not accessible:**
```bash
# Check service type
kubectl get svc

# For NodePort, get the node IP
minikube ip

# Access via <minikube-ip>:<nodeport>
```

**Database connection issues:**
```bash
# Verify database URL in secrets
kubectl get secret backend-secrets -o yaml

# Check pod environment
kubectl exec -it <backend-pod> -- env | grep DATABASE_URL
```

### Restart Services

```bash
# Restart backend
kubectl rollout restart deployment/backend

# Restart frontend
kubectl rollout restart deployment/frontend
```

### Uninstall Helm Charts

```bash
# Uninstall frontend
helm uninstall frontend

# Uninstall backend
helm uninstall backend

# Verify cleanup
kubectl get all
```

## Clean Up

```bash
# Stop Minikube
minikube stop

# Delete Minikube cluster (reset everything)
minikube delete

# Remove Docker images
docker rmi todo-frontend:latest todo-backend:latest
```

## Next Steps

After successful Minikube deployment, you can:

1. **Deploy to Cloud**: Update `values-prod.yaml` with cloud-specific settings
2. **Set up Ingress**: Configure Ingress for domain routing with TLS
3. **Enable Monitoring**: Add Prometheus and Grafana for monitoring
4. **CI/CD Pipeline**: Automate builds and deployments with GitHub Actions
5. **kubectl-ai Integration**: Use `kubectl ai` for AI-assisted operations

## Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Phase IV Specification](../specs/features/phase4-kubernetes.md)
