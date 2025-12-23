# Backend Helm Chart

Helm chart for deploying the Todo App backend (FastAPI) to Kubernetes.

## Prerequisites

- Kubernetes cluster (Minikube, DOKS, GKE, AKS, etc.)
- Helm 3.x installed
- kubectl configured for your cluster
- PostgreSQL database (Neon or self-hosted)

## Quick Start

### Minikube

```bash
# Start Minikube
minikube start

# Create secrets
kubectl create secret generic backend-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=groq-api-key="$GROQ_API_KEY"

# Build and load image
eval $(minikube docker-env)
docker build -t todo-backend:latest ./backend

# Install Helm chart
helm install todo-backend helm/backend

# Get URL
minikube service todo-backend --url
```

### Cloud Kubernetes (DOKS, GKE, AKS)

```bash
# Push image to registry
docker tag todo-backend:latest your-registry/todo-backend:latest
docker push your-registry/todo-backend:latest

# Update values.yaml with your registry
# image.repository = your-registry/todo-backend

# Install Helm chart
helm install todo-backend helm/backend \
  --set image.repository=your-registry/todo-backend \
  --set image.tag=latest \
  --set service.type=LoadBalancer \
  --set secrets.databaseURL="$DATABASE_URL" \
  --set secrets.jwtSecret="$JWT_SECRET"
```

## Configuration

### Required Secrets

The following secrets MUST be provided:

```bash
kubectl create secret generic backend-secrets \
  --from-literal=database-url="postgresql+asyncpg://user:pass@host:5432/db" \
  --from-literal=jwt-secret="your-production-secret-min-32-chars"
```

### Optional Secrets (AI Features)

```bash
kubectl create secret generic backend-secrets \
  --from-literal=groq-api-key="gsk_xxx..." \
  --from-literal=gemini-api-key="AIzaSyxxx..." \
  --from-literal=openai-api-key="sk-xxx..."
```

### Values Reference

```yaml
replicaCount: 2

image:
  repository: todo-backend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: NodePort  # Use LoadBalancer for cloud
  port: 8000

secrets:
  databaseURL: ""  # Required: PostgreSQL connection string
  jwtSecret: ""    # Required: JWT signing secret (min 32 chars)
  groqApiKey: ""   # Optional: Groq API key for AI
  geminiApiKey: "" # Optional: Gemini API key fallback
  openaiApiKey: "" # Optional: OpenAI API key fallback

config:
  corsOrigins: "http://localhost:3000,https://yourdomain.com"
  appName: "Todo CRUD API"
  debug: "false"
  jwtAlgorithm: "HS256"
  jwtAccessTokenExpireMinutes: "1440"

resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "1000m"

ingress:
  enabled: false
  className: "nginx"
  hosts:
    - host: api.example.com
      paths:
        - path: /api
          pathType: Prefix
  tls:
    - secretName: backend-tls
      hosts:
        - api.example.com
```

## Install Commands

```bash
# Lint the chart
helm lint helm/backend

# Dry run
helm install todo-backend helm/backend --dry-run --debug

# Install with secrets
kubectl create secret generic backend-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=jwt-secret="$JWT_SECRET"

helm install todo-backend helm/backend

# Install with custom values
helm install todo-backend helm/backend -f custom-values.yaml

# Upgrade
helm upgrade todo-backend helm/backend

# Uninstall
helm uninstall todo-backend
```

## Accessing the Application

### Minikube (NodePort)

```bash
# Get URL
minikube service todo-backend --url

# Or access via node IP
kubectl get nodes -o wide
# Access at http://<NODE-IP>:30002
```

### Cloud (LoadBalancer)

```bash
# Get external IP
kubectl get svc todo-backend

# Access at http://<EXTERNAL-IP>:8000
```

## Health Check

The backend exposes a `/health` endpoint:

```bash
# Check health
curl http://$(minikube service todo-backend --url)/health

# Expected response
{"status": "healthy", "database": "connected"}
```

## Troubleshooting

```bash
# Check pod status
kubectl get pods -l app=todo-backend

# View logs
kubectl logs -l app=todo-backend

# Check secrets
kubectl get secret backend-secrets -o yaml

# Describe service
kubectlubectl describe svc todo-backend

# Port forward to local
kubectl port-forward svc/todo-backend 8000:8000
```

## Database Setup

### Neon (Recommended)

```bash
# Get connection string from Neon console
export DATABASE_URL="postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require"

# Create secret
kubectl create secret generic backend-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=jwt-secret="your-production-jwt-secret-min-32-chars"
```

### Self-Hosted PostgreSQL

```bash
# Install PostgreSQL (if needed)
helm install postgres bitnami/postgresql \
  --set auth.password=postgres \
  --set auth.database=todoapp

# Get connection string
export POSTGRES_HOST=$(kubectl get svc postgres-postgresql -o jsonpath='{.spec.clusterIP}')

# Create secret
kubectl create secret generic backend-secrets \
  --from-literal=database-url="postgresql+asyncpg://postgres:postgres@${POSTGRES_HOST}:5432/todoapp" \
  --from-literal=jwt-secret="your-production-jwt-secret-min-32-chars"
```

## Security Notes

1. **Never commit secrets to git** - Always use Kubernetes Secrets
2. **Use strong JWT secrets** - Minimum 32 characters, randomly generated
3. **Rotate secrets regularly** - Update secrets and restart pods
4. **Use HTTPS** - Enable ingress with TLS for production
5. **Limit resource usage** - Set appropriate resource requests/limits

## Scaling

### Manual Scaling

```bash
# Scale to 5 replicas
kubectl scale deployment todo-backend --replicas=5

# Or via Helm upgrade
helm upgrade todo-backend helm/backend --set replicaCount=5
```

### Horizontal Pod Autoscaler

```bash
# Enable HPA (if template includes it)
kubectl autoscale deployment todo-backend \
  --min=2 --max=10 \
  --cpu-percent=80 \
  --memory-percent=80
```
