# Kubernetes Setup Skill

**Type**: Agent Skill
**Category**: Infrastructure
**Phases**: Phase IV & V

---

## Purpose

This skill sets up a complete Kubernetes environment for the Evolution of TODO project, supporting both local development (Minikube) and cloud deployment (DigitalOcean DOKS, GKE, AKS).

---

## Skill Invocation

```
/skill kubernetes-setup environment=local
```

Or via Claude Code Task tool:
```python
Task(
    subagent_type="kubernetes-setup",
    description="Setup Kubernetes environment",
    prompt="Set up Minikube for local development with all required services"
)
```

---

## What This Skill Does

1. **Validates Prerequisites**
   - Checks Docker installation
   - Verifies kubectl installed
   - Confirms Minikube/cloud CLI available
   - Validates system resources

2. **Creates Kubernetes Manifests**
   - Deployment YAMLs for each service
   - Service definitions (ClusterIP, LoadBalancer)
   - ConfigMaps for configuration
   - Secrets for credentials
   - PersistentVolumeClaims if needed

3. **Generates Helm Charts**
   - Chart.yaml with metadata
   - values.yaml with configurable parameters
   - Templates for all resources
   - Helpers for common patterns
   - README with usage

4. **Sets Up Infrastructure**
   - Starts Minikube (local) or connects to cloud
   - Creates namespaces
   - Applies manifests
   - Configures networking
   - Sets up ingress

5. **Integrates AI DevOps Tools**
   - Installs kubectl-ai
   - Configures kagent
   - Sets up Docker AI (Gordon)
   - Documents AI-assisted workflows

---

## Architecture

### Local Development (Minikube)

```
┌──────────────────────────────────────────────────┐
│              Minikube Cluster                     │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │  Namespace: todo-app                       │  │
│  │                                            │  │
│  │  ┌──────────────┐  ┌──────────────┐       │  │
│  │  │  Frontend    │  │  Backend     │       │  │
│  │  │  (Next.js)   │  │  (FastAPI)   │       │  │
│  │  │  Deployment  │  │  Deployment  │       │  │
│  │  │  + Service   │  │  + Service   │       │  │
│  │  └──────────────┘  └──────────────┘       │  │
│  │                                            │  │
│  │  ┌──────────────┐  ┌──────────────┐       │  │
│  │  │  MCP Server  │  │  Neon DB     │       │  │
│  │  │  Deployment  │  │  (External)  │       │  │
│  │  │  + Service   │  │  ConfigMap   │       │  │
│  │  └──────────────┘  └──────────────┘       │  │
│  │                                            │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │  ConfigMaps                          │ │  │
│  │  │  - app-config                        │ │  │
│  │  │  - feature-flags                     │ │  │
│  │  └──────────────────────────────────────┘ │  │
│  │                                            │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │  Secrets                             │ │  │
│  │  │  - openai-api-key                    │ │  │
│  │  │  - database-url                      │ │  │
│  │  │  - jwt-secret                        │ │  │
│  │  └──────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

### Cloud Deployment (DOKS/GKE/AKS)

```
┌──────────────────────────────────────────────────┐
│         Cloud Kubernetes Cluster                  │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │  Namespace: todo-production                │  │
│  │                                            │  │
│  │  ┌──────────────┐                         │  │
│  │  │  Ingress     │ (LoadBalancer)          │  │
│  │  │  Controller  │                         │  │
│  │  └──────┬───────┘                         │  │
│  │         │                                  │  │
│  │    ┌────┴──────────────┐                  │  │
│  │    │                   │                  │  │
│  │  ┌─▼────────┐   ┌─────▼──────┐           │  │
│  │  │ Frontend │   │  Backend   │           │  │
│  │  │ (3 pods) │   │  (3 pods)  │           │  │
│  │  └──────────┘   └────────────┘           │  │
│  │                                            │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │  Kafka Cluster (Strimzi)             │ │  │
│  │  │  - 3 brokers                         │ │  │
│  │  │  - 3 zookeepers                      │ │  │
│  │  └──────────────────────────────────────┘ │  │
│  │                                            │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │  Dapr Components                     │ │  │
│  │  │  - Pub/Sub (Kafka)                   │ │  │
│  │  │  - State Store (PostgreSQL)          │ │  │
│  │  │  - Secrets (Kubernetes)              │ │  │
│  │  └──────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

---

## Generated Files

### 1. Kubernetes Manifests (`k8s/`)

#### `k8s/namespace.yaml`
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
  labels:
    app: evolution-of-todo
    environment: development
```

#### `k8s/frontend-deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: todo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: nextjs
        image: todo-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: api_url
        - name: NEXT_PUBLIC_OPENAI_DOMAIN_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: domain_key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### `k8s/backend-deployment.yaml`
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
    metadata:
      labels:
        app: backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
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
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api_key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

#### `k8s/configmap.yaml`
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: todo-app
data:
  api_url: "http://backend-service:8000"
  environment: "production"
  log_level: "info"
```

#### `k8s/secrets.yaml`
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openai-secret
  namespace: todo-app
type: Opaque
stringData:
  api_key: "${OPENAI_API_KEY}"
  domain_key: "${OPENAI_DOMAIN_KEY}"
---
apiVersion: v1
kind: Secret
metadata:
  name: database-secret
  namespace: todo-app
type: Opaque
stringData:
  url: "${DATABASE_URL}"
```

---

### 2. Helm Chart (`helm-chart/`)

#### `helm-chart/Chart.yaml`
```yaml
apiVersion: v2
name: evolution-of-todo
description: A Helm chart for Evolution of TODO application
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - todo
  - ai
  - mcp
  - spec-driven
maintainers:
  - name: PIAIC Hackathon Team
```

#### `helm-chart/values.yaml`
```yaml
# Default values for evolution-of-todo

frontend:
  replicaCount: 2
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 3000
  resources:
    requests:
      memory: 256Mi
      cpu: 250m
    limits:
      memory: 512Mi
      cpu: 500m

backend:
  replicaCount: 3
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      memory: 512Mi
      cpu: 500m
    limits:
      memory: 1Gi
      cpu: 1000m

database:
  host: "${NEON_HOST}"
  port: 5432
  name: todo_db

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: todo-app.local
      paths:
        - path: /
          pathType: Prefix

dapr:
  enabled: false  # Enable for Phase V

kafka:
  enabled: false  # Enable for Phase V
```

#### `helm-chart/templates/deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo.fullname" . }}-frontend
  labels:
    {{- include "todo.labels" . | nindent 4 }}
    component: frontend
spec:
  replicas: {{ .Values.frontend.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo.selectorLabels" . | nindent 6 }}
      component: frontend
  template:
    metadata:
      labels:
        {{- include "todo.selectorLabels" . | nindent 8 }}
        component: frontend
    spec:
      containers:
      - name: nextjs
        image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
        imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 3000
          protocol: TCP
        resources:
          {{- toYaml .Values.frontend.resources | nindent 12 }}
```

---

### 3. Setup Scripts

#### `k8s/setup-local.sh` (Minikube)
```bash
#!/bin/bash
set -e

echo "🚀 Setting up Minikube for Evolution of TODO..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker not found. Install Docker first."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "kubectl not found. Installing..."; }
command -v minikube >/dev/null 2>&1 || { echo "Minikube not found. Installing..."; }

# Start Minikube
echo "📦 Starting Minikube..."
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable addons
echo "🔌 Enabling addons..."
minikube addons enable ingress
minikube addons enable metrics-server

# Create namespace
echo "📁 Creating namespace..."
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -

# Create secrets
echo "🔐 Creating secrets..."
kubectl create secret generic database-secret \
  --from-literal=url="$DATABASE_URL" \
  --namespace=todo-app \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic openai-secret \
  --from-literal=api_key="$OPENAI_API_KEY" \
  --from-literal=domain_key="$OPENAI_DOMAIN_KEY" \
  --namespace=todo-app \
  --dry-run=client -o yaml | kubectl apply -f -

# Apply manifests
echo "📋 Applying manifests..."
kubectl apply -f k8s/

# Wait for deployments
echo "⏳ Waiting for deployments..."
kubectl wait --for=condition=available --timeout=300s \
  deployment/frontend deployment/backend -n todo-app

echo "✅ Setup complete!"
echo "🌐 Access the app: minikube service frontend -n todo-app"
```

#### `k8s/setup-cloud.sh` (Cloud K8s)
```bash
#!/bin/bash
set -e

CLOUD_PROVIDER=${1:-digitalocean}  # digitalocean, gke, or aks

echo "🚀 Setting up $CLOUD_PROVIDER Kubernetes..."

case $CLOUD_PROVIDER in
  digitalocean)
    doctl kubernetes cluster kubeconfig save todo-cluster
    ;;
  gke)
    gcloud container clusters get-credentials todo-cluster --region=us-central1
    ;;
  aks)
    az aks get-credentials --resource-group todo-rg --name todo-cluster
    ;;
esac

# Install Helm if not present
command -v helm >/dev/null 2>&1 || { echo "Installing Helm..."; }

# Deploy with Helm
echo "📦 Deploying with Helm..."
helm upgrade --install evolution-of-todo ./helm-chart \
  --namespace todo-production \
  --create-namespace \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=5 \
  --set ingress.enabled=true

echo "✅ Cloud deployment complete!"
```

---

## AI DevOps Integration

### kubectl-ai Setup
```bash
# Install kubectl-ai
curl -sSL https://get.kubectl.ai | bash

# Usage examples
kubectl-ai "deploy the frontend with 3 replicas"
kubectl-ai "scale the backend to handle more load"
kubectl-ai "check why the pods are failing"
kubectl-ai "show me the logs for backend service"
```

### kagent Setup
```bash
# Install kagent
pip install kubernetes-agent

# Usage examples
kagent "analyze cluster health"
kagent "optimize resource allocation for todo-app"
kagent "suggest improvements for deployment manifests"
```

### Docker AI (Gordon) Setup
```bash
# Enable in Docker Desktop settings
# Settings > Beta features > Toggle Docker AI

# Usage examples
docker ai "What can you do?"
docker ai "Build an optimized image for Python FastAPI app"
docker ai "Why is my container using so much memory?"
```

---

## Success Criteria

Kubernetes setup is successful when:

1. ✅ Cluster running (Minikube or cloud)
2. ✅ All pods in Running state
3. ✅ Services accessible
4. ✅ Health checks passing
5. ✅ Secrets configured
6. ✅ Helm chart deployable
7. ✅ kubectl-ai/kagent working

---

## Troubleshooting

### Minikube won't start
```bash
# Check Docker is running
docker ps

# Clean start
minikube delete
minikube start --driver=docker
```

### Pods stuck in Pending
```bash
# Check events
kubectl describe pod <pod-name> -n todo-app

# Check resources
kubectl top nodes
```

### Cannot pull images
```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build images locally
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
```

---

## Deliverables

When this skill completes, you'll have:

1. ✅ Kubernetes manifests (`k8s/`)
2. ✅ Helm chart (`helm-chart/`)
3. ✅ Setup scripts (local & cloud)
4. ✅ ConfigMaps and Secrets
5. ✅ Health checks configured
6. ✅ kubectl-ai/kagent installed
7. ✅ Documentation (README)

---

**Skill Version**: 1.0.0
**Created**: 2025-12-13
**Hackathon Points**: Contributes to Phase IV (250 pts) and +200 bonus (Cloud-Native Blueprints)
**Phase**: IV & V
