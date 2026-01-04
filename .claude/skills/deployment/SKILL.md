---
name: deployment
description: Create multi-stage Dockerfiles (FROM python:alpine AS builder → FROM python:slim), write Kubernetes manifests: deployment.yaml with replicas/containers/resources, service.yaml with LoadBalancer/NodePort, configmap.yaml for env vars, and secrets.yaml for sensitive data. Generate Helm charts with Chart.yaml, templates/, values.yaml for environment configs. Deploy Next.js to Vercel via vercel --prod. Use when containerizing FastAPI/Next.js, deploying to DOKS/GKE/AKS, or setting up production infrastructure.
---

# Deployment Skill

Comprehensive deployment automation and validation.

## File Structure

```
k8s/
├── backend/
│   ├── deployment.yaml    # Backend deployment spec
│   ├── service.yaml        # Backend service
│   ├── configmap.yaml      # Environment variables
│   └── secrets.yaml        # Sensitive data
├── frontend/
│   ├── deployment.yaml    # Frontend deployment
│   └── service.yaml        # Frontend service
└── ingress.yaml            # Ingress routing

helm/
└── backend/
    ├── Chart.yaml          # Helm chart metadata
    ├── values.yaml         # Default values
    └── templates/          # Kubernetes templates
```

## Quick Commands

```bash
# Build and push Docker images
docker build -t registry.com/backend:latest -f backend/Dockerfile backend
docker push registry.com/backend:latest

# Deploy to Kubernetes
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/

# Check deployment status
kubectl get pods -l app=backend
kubectl get services
kubectl describe deployment backend

# View logs
kubectl logs -l app=backend --tail=50 -f

# Deploy with Helm
helm install backend ./helm/backend --values helm/backend/values-prod.yaml

# Rollback deployment
kubectl rollout undo deployment/backend

# Vercel deployment
cd frontend
vercel --prod
```

## Common Issues & Troubleshooting

| Issue | Error Message | Root Cause | Fix Command |
|-------|---------------|------------|-------------|
| ImagePullBackOff | `Failed to pull image` | Wrong registry/secret | `kubectl create secret docker-registry regcred --docker-server=... --username=... --password=...` |
| CrashLoopBackOff | `Pod crashed 5 times` | Missing env vars / app crash | `kubectl logs <pod>` then add env vars to deployment.yaml |
| Pod not ready | `Readiness probe failed` | Wrong health check path | Update `failureThreshold: 30` and `periodSeconds: 10` |
| 502 Bad Gateway | `Service not responding` | Service not exposing port | Check `targetPort` matches `containerPort` |
| OOMKilled | `Pod was killed due to OOM` | Memory limit too low | Increase `resources.limits.memory` in deployment |

---

## Kubernetes Deployment

### Deployment Manifest

**File: `k8s/backend/deployment.yaml`**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  labels:
    app: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: registry.com/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: backend-config
              key: database-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**Apply with**:
```bash
kubectl apply -f k8s/backend/deployment.yaml
kubectl rollout status deployment/backend
```
