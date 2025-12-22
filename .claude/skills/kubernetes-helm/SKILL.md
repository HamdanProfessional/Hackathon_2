---
name: kubernetes-helm
description: Kubernetes deployment and Helm chart management skills. Use when deploying applications to Kubernetes (Minikube/DOKS/GKE/AKS), creating or updating Helm charts, managing Kubernetes resources, or troubleshooting deployment issues. Includes multi-stage Docker builds, Helm 3 chart structure, Kubernetes manifests, and cloud deployment automation for the Todo App phases IV and V.
---

# Kubernetes & Helm Deployment

This skill provides comprehensive guidance for containerizing and deploying applications to Kubernetes using Helm charts.

## When to Use This Skill

Use this skill when:
- Creating Docker images (Dockerfile, multi-stage builds)
- Building or updating Helm charts
- Deploying to Kubernetes (Minikube, DOKS, GKE, AKS)
- Troubleshooting Kubernetes deployments
- Configuring Kubernetes resources (Deployments, Services, Ingress, etc.)
- Setting up cloud Kubernetes clusters

## Quick Reference

### Docker Commands

```bash
# Build image
docker build -t image-name:tag ./path

# Build multi-stage
docker build --target builder -t image-name:tag ./path

# Run locally
docker run -p 8080:8080 image-name:tag

# Push to registry
docker push registry/namespace/image:tag

# Load into Minikube
minikube image load image-name:tag
```

### Helm Commands

```bash
# Lint chart
helm lint chart-name

# Template rendering
helm template chart-name

# Dry run install
helm install --dry-run --debug release-name chart-name

# Install
helm install release-name chart-name

# Install with values
helm install release-name chart-name -f values.yaml

# Upgrade
helm upgrade release-name chart-name

# Rollback
helm rollback release-name [revision]

# Uninstall
helm uninstall release-name

# List releases
helm list

# Get values
helm get values release-name

# Get manifest
helm get manifest release-name
```

### kubectl Commands

```bash
# Get resources
kubectl get pods,services,deployments

# Describe pod
kubectl describe pod pod-name

# View logs
kubectl logs pod-name --tail=50 -f

# Exec into container
kubectl exec -it pod-name -- sh

# Port forward
kubectl port-forward svc/service-name 8080:80

# Apply manifest
kubectl apply -f manifest.yaml

# Delete resource
kubectl delete pod pod-name
```

### Minikube Commands

```bash
# Start
minikube start --cpus=4 --memory=8192

# Stop
minikube stop

# Delete
minikube delete

# Service URL
minikube service service-name --url

# Tunnel (for LoadBalancer)
minikube tunnel

# Image load
minikube image load image-name:tag

# Dashboard
minikube dashboard
```

## Dockerfile Patterns

### Multi-Stage Next.js Dockerfile

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder /app/node_modules ./node_modules
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

### FastAPI Dockerfile

```dockerfile
FROM python:3.13-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc postgresql-client curl \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m -u 1001 appuser && chown -R appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Helm Chart Structure

```
chart-name/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── secrets.yaml
    ├── hpa.yaml
    ├── _helpers.tpl
    └── NOTES.txt
```

### Chart.yaml

```yaml
apiVersion: v2
name: chart-name
description: Chart description
type: application
version: 1.0.0
appVersion: "1.0.0"
```

### Values Template

```yaml
replicaCount: 2

image:
  repository: image-name
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: NodePort
  port: 8080
  nodePort: 30001

ingress:
  enabled: false
  className: nginx
  annotations: {}
  hosts: []
  tls: []

resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

nodeSelector: {}
tolerations: []
affinity: {}
```

## Kubernetes Resources

### Deployment Template

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "chart.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "chart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "chart.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: {{ .Values.service.port }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
```

### Service Template

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "chart.fullname" . }}
spec:
  type: {{ .Values.service.type }}
  ports:
  - port: {{ .Values.service.port }}
    targetPort: http
    protocol: TCP
  selector:
    {{- include "chart.selectorLabels" . | nindent 4 }}
```

## Cloud Deployment

### DigitalOcean (DOKS)

```bash
# Install doctl
brew install doctl

# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create cluster-name \
  --region nyc1 \
  --version 1.29.0 \
  --node-pool "name=pool-1;size=s-4vcpu-8gb;count=3"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save cluster-name
```

### Google Cloud (GKE)

```bash
# Set project
gcloud config set project project-id

# Create cluster
gcloud container clusters create cluster-name \
  --region=us-central1 \
  --num-nodes=3 \
  --machine-type=e2-medium

# Get credentials
gcloud container clusters get-credentials cluster-name \
  --region=us-central1
```

### Azure (AKS)

```bash
# Create resource group
az group create --name rg-name --location eastus

# Create cluster
az aks create \
  --resource-group rg-name \
  --name cluster-name \
  --node-count 3 \
  --node-vm-size Standard_B4ms \
  --enable-managed-identity

# Get credentials
az aks get-credentials \
  --resource-group rg-name \
  --name cluster-name
```

## Troubleshooting

### Pod Issues

```bash
# Check pod status
kubectl get pods

# Describe pod for events
kubectl describe pod pod-name

# View logs
kubectl logs pod-name

# Previous container logs
kubectl logs pod-name --previous
```

### Image Issues

```bash
# ImagePullBackOff - verify image
kubectl describe pod pod-name | grep Image

# Load image to Minikube
minikube image load image-name:tag

# Verify image in registry
docker pull registry/image:tag
```

### Service Issues

```bash
# Check service endpoints
kubectl get endpoints

# Check service
kubectl describe svc service-name

# Port forward for testing
kubectl port-forward svc/service-name 8080:80
```

## Health Checks

### Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 15
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Readiness Probe

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

## For More Information

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
