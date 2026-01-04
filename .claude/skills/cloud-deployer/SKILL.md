---
name: cloud-deployer
description: Deploy and manage applications on DigitalOcean DOKS with Docker, Kubernetes, Helm, Dapr, Kafka, and monitoring. Use when containerizing applications, creating Kubernetes manifests, deploying with Helm charts, integrating Dapr sidecars for event-driven architecture, deploying Kafka/Redpanda for pub/sub, setting up monitoring with Prometheus/Grafana, or using AIOps tools (kubectl-ai, kagent, Docker AI). Complete DigitalOcean-focused deployment patterns for production workloads.
---

# Cloud Deployer

Deploy and manage applications across container platforms, Kubernetes clusters, and DigitalOcean cloud services.

## When to Use This Skill

| User Request | Action | Deployment Type |
|--------------|--------|------------------|
| "Deploy this to production" | Choose deployment target based on requirements | Multi-environment |
| "Containerize the application" | Create Dockerfile and docker-compose.yml | Docker |
| "Set up Kubernetes cluster" | Configure DOKS with doctl or Minikube locally | Kubernetes |
| "Package as Helm chart" | Create Chart.yaml, values.yaml, templates/ | Helm |
| "Add event-driven architecture" | Integrate Dapr sidecars and pub/sub | Dapr |
| "Set up message queue" | Deploy Kafka/Redpanda for pub/sub | Event Streaming |
| "Add monitoring" | Install Prometheus, Grafana, Loki | Observability |
| "Use AI for deployment" | Configure kubectl-ai, kagent, Docker AI | AIOps |

## Common Scenarios

### Scenario 1: Containerize and Deploy Full-Stack Application
**User Request**: "Containerize the todo app and deploy it"

**Workflow**:
```bash
# 1. Create Dockerfile for backend
# File: backend/Dockerfile
FROM python:3.13-alpine AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# 2. Create Dockerfile for frontend
# File: frontend/Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]

# 3. Create docker-compose.yml for local testing
docker-compose up -d

# 4. Build and tag for registry
docker build -t myregistry/todo-backend:latest ./backend
docker build -t myregistry/todo-frontend:latest ./frontend

# 5. Push to registry
docker push myregistry/todo-backend:latest
docker push myregistry/todo-frontend:latest
```

### Scenario 2: Deploy to DigitalOcean Kubernetes (DOKS)
**User Request**: "Deploy to production on DigitalOcean"

**Commands**:
```bash
# 1. Install doctl
brew install doctl  # macOS
curl -sL https://github.com/digitalocean/doctl/releases/latest/download/doctl-linux-amd64.tar.gz | tar xz
sudo mv doctl /usr/local/bin

# 2. Authenticate
doctl auth init

# 3. Create cluster
doctl kubernetes cluster create todo-prod \
  --region fra1 \
  --version 1.29.1 \
  --node-pool "name=pool-1;size=s-4vcpu-8gb;count=2"

# 4. Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-prod

# 5. Create namespace
kubectl create namespace todo-app

# 6. Apply secrets
kubectl apply -f k8s/backend/secrets.yaml -n todo-app

# 7. Apply configmap
kubectl apply -f k8s/backend/configmap.yaml -n todo-app

# 8. Deploy backend
kubectl apply -f k8s/backend/deployment.yaml -n todo-app

# 9. Expose with service
kubectl apply -f k8s/backend/service.yaml -n todo-app

# 10. Setup ingress
kubectl apply -f k8s/ingress.yaml -n todo-app

# 11. Verify
kubectl get pods -n todo-app
kubectl get services -n todo-app
```

### Scenario 3: Package Application as Helm Chart
**User Request**: "Create a Helm chart for the application"

**Commands**:
```bash
# 1. Create chart structure
helm create todo-app
cd todo-app

# 2. Edit Chart.yaml
# 3. Configure values.yaml
# 4. Customize templates/

# 5. Lint chart
helm lint todo-app

# 6. Install chart
helm install todo-backend todo-app/ -n todo-app --create-namespace

# 7. Install with custom values
helm install todo-backend todo-app/ -n todo-app \
  --values todo-app/values-prod.yaml \
  --set image.tag=v1.0.0

# 8. Test the chart
helm test todo-backend -n todo-app

# 9. Get manifest (dry-run)
helm template todo-backend todo-app/
```

### Scenario 4: Add Dapr Sidecars for Event-Driven Architecture
**User Request**: "Make the application event-driven with Dapr"

**Commands**:
```bash
# 1. Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# 2. Initialize Dapr on cluster
dapr init -k

# 3. Verify Dapr installation
kubectl get pods -n dapr-system

# 4. Add Dapr annotations to deployment
# Edit k8s/backend/deployment.yaml:
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "todo-backend"
    dapr.io/app-port: "8000"

# 5. Create pub/sub component
kubectl apply -f k8s/dapr/pubsub.yaml -n todo-app

# 6. Create state store component
kubectl apply -f k8s/dapr/statestore.yaml -n todo-app

# 7. Deploy updated application
kubectl apply -f k8s/backend/deployment.yaml -n todo-app

# 8. Verify Dapr sidecar is running
kubectl get pods -n todo-app -l app=todos-backend
```

### Scenario 5: Deploy Kafka for Event Streaming
**User Request**: "Set up Kafka for task events"

**Commands**:
```bash
# 1. Install Strimzi operator
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka

# 2. Deploy Kafka cluster
kubectl apply -f k8s/kafka/kafka-cluster.yaml

# 3. Create topics
kubectl apply -f k8s/kafka/topics.yaml

# 4. Verify Kafka installation
kubectl get pods -n kafka
kubectl get kafkatopics -n kafka

# 5. Test Kafka (optional)
kubectl exec -it todo-kafka-kafka-0 -n kafka -- bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 --list
```

### Scenario 6: Set Up Monitoring with Prometheus and Grafana
**User Request**: "Add monitoring and dashboards"

**Commands**:
```bash
# 1. Add Prometheus Community Helm repo
helm repo add prometheus-community \
  https://prometheus-community.github.io/helm-charts
helm repo update

# 2. Install Prometheus Operator
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace

# 3. Create ServiceMonitor for application
kubectl apply -f k8s/monitoring/servicemonitor.yaml -n todo-app

# 4. Expose FastAPI metrics in backend
# Add to backend/app/main.py:
from prometheus_client import Counter, Histogram
task_created = Counter('tasks_created_total', 'Total tasks created')

# 5. Port forward Grafana
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring

# 6. Access Grafana: http://localhost:3000
#    Default: admin / prom-operator

# 7. Import dashboards (IDs: 10826, 11412, 6417, 13327)
```

---

## Quick Templates

### Kubernetes Deployment Manifest

**File**: `k8s/backend/deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  namespace: todo-app
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
      containers:
      - name: backend
        image: todo-backend:latest
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
          periodSeconds: 5
```

### Helm Chart Structure

```
helm/todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration
├── values-prod.yaml        # Production overrides
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── secret.yaml
    └── _helpers.tpl
```

### Dapr Sidecar Annotation

```yaml
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "todo-backend"
    dapr.io/app-port: "8000"
    dapr.io/config: "todo-app-config"
```

### Dapr Pub/Sub Component

**File**: `k8s/dapr/pubsub.yaml`
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "todo-kafka-kafka-bootstrap.kafka.svc:9092"
    - name: consumerGroup
      value: "todo-service"
```

### Kafka Topic

**File**: `k8s/kafka/topics.yaml`
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
```

---

## Implementation Procedures

### Procedure 1: Local Development with Docker Compose

**Use When**: Quick local testing, development environment setup

**Steps**:
1. Create `docker-compose.yml` with all services
2. Define health checks for dependencies
3. Use named volumes for data persistence
4. Run `docker-compose up -d`
5. View logs with `docker-compose logs -f`
6. Stop with `docker-compose down`

### Procedure 2: Containerization

**Use When**: Preparing application for Kubernetes deployment

**Steps**:
1. Create multi-stage Dockerfile (builder → runtime)
2. Minimize image size (use alpine/slim variants)
3. Copy only necessary files
4. Set appropriate user permissions
5. Expose only required ports
6. Define health check endpoints

### Procedure 3: Kubernetes Deployment

**Use When**: Production deployment, orchestration needs

**Steps**:
1. Create namespace for isolation
2. Create ConfigMap for environment variables
3. Create Secret for sensitive data
4. Write Deployment with replicas and resource limits
5. Create Service (ClusterIP/LB/NodePort)
6. Configure Ingress for external access
7. Add probes (liveness, readiness, startup)
8. Apply with `kubectl apply -f k8s/`

### Procedure 4: Helm Chart Packaging

**Use When**: Complex applications, multi-environment deployments

**Steps**:
1. Run `helm create chart-name` to scaffold
2. Edit `Chart.yaml` with metadata
3. Configure `values.yaml` with defaults
4. Customize templates in `templates/`
5. Add helper templates in `_helpers.tpl`
6. Lint with `helm lint chart-name`
7. Test with `helm test chart-name`
8. Install with `helm install release chart-name`

### Procedure 5: Dapr Integration

**Use When**: Event-driven architecture, pub/sub, state management

**Steps**:
1. Install Dapr on cluster: `dapr init -k`
2. Add `dapr.io/enabled` annotation to deployment
3. Configure Dapr components (pubsub, state, secrets)
4. Update application to use Dapr HTTP API
5. Publish events: `POST http://localhost:3500/v1.0/publish/pubsub/topic`
6. Subscribe to topics with Subscription CRD
7. Test end-to-end event flow

### Procedure 6: Kafka Deployment

**Use When**: Event streaming, message queuing

**Self-hosted (Strimzi)**:
1. Install Strimzi operator
2. Create Kafka cluster resource
3. Create topics with partitions
4. Configure Dapr pubsub component
5. Deploy applications with Kafka clients

**Managed (Redpanda Cloud)**:
1. Sign up at redpanda.com/cloud
2. Create cluster and topics
3. Copy bootstrap servers and credentials
4. Update application with connection details
5. Test with producer/consumer

### Procedure 7: Monitoring Setup

**Use When**: Production observability, alerting

**Steps**:
1. Install Prometheus Operator: `helm install prometheus prometheus-community/kube-prometheus-stack`
2. Create ServiceMonitor for application
3. Add `/metrics` endpoint to FastAPI
4. Install Loki for logs: `helm install loki grafana/loki-stack`
5. Configure Fluent Bit for log forwarding
6. Create Grafana dashboards
7. Set up alert rules (PrometheusRule)
8. Test alerts with failure scenarios

### Procedure 8: AIOps Configuration

**Use When**: Natural language infrastructure operations

**kubectl-ai**:
1. Install: `go install github.com/kubectl-ai/kubectl-ai@latest`
2. Configure OpenAI API key
3. Use: `kubectl-ai "deploy with 3 replicas"`

**kagent**:
1. Install: `curl -sSL https://raw.githubusercontent.com/kagent-ai/kagent/main/install.sh | bash`
2. Initialize: `kagent init`
3. Use: `kagent "optimize resource allocation"`

**Docker AI (Gordon)**:
1. Enable in Docker Desktop Settings
2. Use: `docker ai "optimize Dockerfile"`
3. Get troubleshooting suggestions

---

## Decision Guide

**Choose Docker Compose when**:
- Local development and testing
- Simple stack with few services
- Quick setup required
- No scaling needed

**Choose Kubernetes when**:
- Multi-service orchestration
- Horizontal scaling requirements
- Production workloads
- Need for self-healing

**Choose Helm when**:
- Complex Kubernetes applications
- Multi-environment deployments (dev/staging/prod)
- Need for versioning and rollbacks
- Template reuse across services

**Choose Dapr when**:
- Event-driven architecture
- Pub/sub messaging needed
- State management abstraction
- Service-to-service communication

**Choose Kafka when**:
- Event streaming at scale
- Message queuing with durability
- Multiple consumers for topics
- Event sourcing patterns

**Choose Prometheus/Grafana when**:
- Metrics collection and visualization
- Alerting on metrics
- Historical data analysis
- Dashboard requirements

**Choose AIOps tools when**:
- Team learning Kubernetes
- Natural language interface preferred
- Quick troubleshooting needed
- Resource optimization required

---

## Quick Reference Commands

| Action | Command |
|--------|---------|
| **Docker** | `docker-compose up -d` |
| **Minikube** | `minikube start --driver=docker` |
| **DOKS Create** | `doctl kubernetes cluster create` |
| **Kubeconfig** | `doctl kubernetes cluster kubeconfig save` |
| **Deploy** | `kubectl apply -f k8s/` |
| **Get pods** | `kubectl get pods -n namespace` |
| **Logs** | `kubectl logs -f deployment/name -n namespace` |
| **Port forward** | `kubectl port-forward svc/name 8080:80` |
| **Helm Install** | `helm install release chart/` |
| **Helm Upgrade** | `helm upgrade release chart/` |
| **Dapr Init** | `dapr init -k` |
| **Dapr List** | `dapr list -k` |
| **Prometheus Install** | `helm install prometheus prometheus-community/kube-prometheus-stack` |
| **Grafana Port Forward** | `kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring` |

---

## Troubleshooting

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| ImagePullBackOff | Wrong image/tag or secret missing | `kubectl create secret docker-registry regcred` |
| CrashLoopBackOff | App crashes on startup | Check logs: `kubectl logs pod-name` |
| OOMKilled | Memory limit too low | Increase `resources.limits.memory` |
| Pod Pending | No available nodes | Scale node pool or check resources |
| 502/503 errors | Service not ready | Check readiness probe, service selector |

### Debug Commands

```bash
# Describe pod for detailed info
kubectl describe pod pod-name -n namespace

# Get logs from crashed container
kubectl logs pod-name --previous -n namespace

# Exec into container
kubectl exec -it pod-name -n namespace -- /bin/bash

# Check events
kubectl get events -n namespace --sort-by='.lastTimestamp'

# Verify DNS resolution
kubectl run test-pod --image=busybox --rm -it -- nslookup service-name

# Check resource usage
kubectl top pods -n namespace
kubectl top nodes
```

---

## DigitalOcean Quick Start

### DOKS (Kubernetes)
```bash
doctl kubernetes cluster create my-cluster \
  --region fra1 \
  --node-pool "name=pool-1;size=s-4vcpu-8gb;count=2"
```

### App Platform
```bash
doctl apps create --spec app.yaml
```

### Spaces (S3-compatible)
```bash
doctl spaces create my-assets --region nyc3
aws s3 sync ./build s3://my-assets \
  --endpoint=https://nyc3.digitaloceanspaces.com
```
