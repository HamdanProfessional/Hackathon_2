# Cloud Deployment Reference

## Kubernetes (DOKS/GKE/AKS)

### Cluster Setup

#### DigitalOcean Kubernetes (DOKS)

```bash
# Install doctl
brew install doctl  # macOS
curl -sL https://github.com/digitalocean/doctl/releases/latest/download/doctl-linux-amd64.tar.gz | tar xz
sudo mv doctl /usr/local/bin

# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create hackathon2 \
  --region fra1 \
  --version 1.29.1 \
  --node-pool "name=pool-1;size=s-4vcpu-8gb;count=2"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save hackathon2

# Verify
kubectl get nodes
```

#### Google Kubernetes Engine (GKE)

```bash
# Install gcloud
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Create cluster
gcloud container clusters create hackathon2 \
  --region=us-central1 \
  --num-nodes=2 \
  --machine-type=e2-medium

# Get credentials
gcloud container clusters get-credentials hackathon2 --region=us-central1
```

#### Azure Kubernetes Service (AKS)

```bash
# Install az CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Create cluster
az aks create --resource-group hackathon2-rg \
  --name hackathon2 \
  --location eastus \
  --node-count 2 \
  --node-vm-size Standard_B2s

# Get credentials
az aks get-credentials --resource-group hackathon2-rg --name hackathon2
```

### Deployment Manifests

#### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
```

#### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-backend-config
data:
  cors-origins: "https://hackathon2.testservers.online,https://api.testservers.online"
  app-name: "Todo CRUD API"
  debug: "false"
  jwt-algorithm: "HS256"
  jwt-access-token-expire-minutes: "1440"
```

#### Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-backend-secrets
type: Opaque
stringData:
  database-url: "postgresql+asyncpg://user:pass@host:5432/db"
  jwt-secret: "your-secret-key-min-32-chars"
  groq-api-key: "your-api-key"
```

#### Backend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: backend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: backend
    spec:
      imagePullSecrets:
      - name: registry-pull-secret
      containers:
      - name: backend
        image: registry.digitalocean.com/todo-backend:latest
        ports:
        - name: http
          containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-backend-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 5
```

#### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: http
  selector:
    app.kubernetes.io/name: backend
```

#### Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://hackathon2.testservers.online"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.testservers.online
    secretName: todo-tls
  rules:
  - host: api.testservers.online
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-backend
            port:
              number: 8000
```

### Container Registry Setup

#### DigitalOcean Container Registry

```bash
# Create registry
doctl registry create

# Login
doctl registry login

# Build and tag
docker build -t registry.digitalocean.com/todo-backend:latest -f backend/Dockerfile backend/

# Push
docker push registry.digitalocean.com/todo-backend:latest

# Create registry secret for Kubernetes
doctl kubernetes cluster registry create hackathon2

# Or manually
kubectl create secret docker-registry registry-pull-secret \
  --docker-server=registry.digitalocean.com \
  --docker-username=<token> \
  --docker-password=<token>
```

#### Google Artifact Registry

```bash
# Enable APIs
gcloud services enable artifactregistry.googleapis.com

# Create repository
gcloud artifacts repositories create todo-repo \
  --repository-format=docker \
  --location=us-central1

# Configure authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push
docker build -t us-central1-docker.pkg.dev/my-project/todo-repo/backend:latest .
docker push us-central1-docker.pkg.dev/my-project/todo-repo/backend:latest
```

#### Azure Container Registry

```bash
# Create registry
az acr create --resource-group hackathon2-rg \
  --name hackathon2acr \
  --sku Basic

# Login
az acr login --name hackathon2acr

# Build and push
az acr build -t hackathon2acr.azurecr.io/backend:latest -f backend/Dockerfile backend/
```

### Deployment Commands

```bash
# Apply all manifests
kubectl apply -f k8s/

# Apply specific resources
kubectl apply -f k8s/backend/deployment.yaml
kubectl apply -f k8s/backend/service.yaml
kubectl apply -f k8s/backend/ingress.yaml

# Check rollout status
kubectl rollout status deployment/todo-backend

# Scale deployment
kubectl scale deployment/todo-backend --replicas=3

# Update image
kubectl set image deployment/todo-backend backend=registry.digitalocean.com/todo-backend:v1.0.0

# Rollback
kubectl rollout undo deployment/todo-backend
kubectl rollout history deployment/todo-backend

# Get logs
kubectl logs -f deployment/todo-backend

# Exec into container
kubectl exec -it deployment/todo-backend -- /bin/bash

# Port forward for local testing
kubectl port-forward deployment/todo-backend 8000:8000
```

### Helm Charts

#### Create Helm Chart

```bash
helm create todo-chart
cd todo-chart
```

#### values.yaml

```yaml
replicaCount: 2

image:
  repository: registry.digitalocean.com/todo-backend
  pullPolicy: IfNotPresent
  tag: "latest"

imagePullSecrets:
  - name: registry-pull-secret

service:
  type: ClusterIP
  port: 8000

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: api.testservers.online
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: todo-tls
      hosts:
        - api.testservers.online

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 200m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

#### Deploy with Helm

```bash
# Install
helm install todo-app ./todo-chart

# Upgrade
helm upgrade todo-app ./todo-chart

# Uninstall
helm uninstall todo-app

# Lint
helm lint ./todo-chart

# Dry run
helm install todo-app ./todo-chart --dry-run --debug
```

## Vercel Deployment

### Setup

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login
```

### vercel.json Configuration

```json
{
  "version": 2,
  "name": "todo-backend",
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/app/main.py"
    }
  ],
  "env": {
    "DATABASE_URL": "@database-url",
    "JWT_SECRET_KEY": "@jwt-secret"
  }
}
```

### Deploy

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Set environment variables
vercel env add DATABASE_URL production
vercel env add JWT_SECRET_KEY production

# List deployments
vercel ls

# View logs
vercel logs
```

### Backend on Vercel

For FastAPI backends, use `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/app/main.py"
    }
  ]
}
```

Create `api/index.py`:

```python
from app.main import app

# Vercel entry point
handler = app
```

## GitHub Actions CI/CD

### Workflow Structure

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: registry.digitalocean.com
  IMAGE_NAME: todo-app

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Configure kubectl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Deploy to Kubernetes
        run: |
          doctl kubernetes cluster kubeconfig save ${{ secrets.KUBERNETES_CLUSTER }}
          kubectl set image deployment/todo-backend backend=${{ needs.build.outputs.image-tag }}
          kubectl rollout status deployment/todo-backend
```

## Monitoring and Logging

### Prometheus + Grafana

```yaml
# Prometheus ServiceMonitor
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: todo-backend
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: backend
  endpoints:
  - port: http
    interval: 30s
```

### Sentry Integration

```python
# In FastAPI app
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://...",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### Health Checks

```python
# health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "database": await check_database()
    }
```

## Security Best Practices

1. **Network policies**: Restrict pod-to-pod communication
2. **RBAC**: Use role-based access control
3. **Secrets management**: Use sealed-secrets or external secret managers
4. **Image scanning**: Scan for vulnerabilities (Trivy, Snyk)
5. **TLS/SSL**: Always use HTTPS in production
6. **Resource limits**: Prevent resource exhaustion
7. **Pod security policies**: Restrict privileged containers
8. **Regular updates**: Keep cluster and images updated

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Image pull errors
```bash
kubectl get secret registry-pull-secret -o yaml
# Verify secret has correct credentials
```

### DNS issues
```bash
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never
# Inside pod:
nslookup todo-backend
```

### CrashLoopBackOff
```bash
kubectl logs <pod-name> --previous
kubectl describe pod <pod-name>
```
