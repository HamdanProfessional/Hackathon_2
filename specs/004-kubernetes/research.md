# Research: Kubernetes Deployment

**Feature**: 004-kubernetes
**Status**: Complete
**Last Updated**: 2025-12-25

---

## Table of Contents

1. [Technology Choices](#technology-choices)
2. [Kubernetes Providers Comparison](#kubernetes-providers-comparison)
3. [Container Registry Options](#container-registry-options)
4. [Ingress and Load Balancing](#ingress-and-load-balancing)
5. [Monitoring and Logging Solutions](#monitoring-and-logging-solutions)
6. [CI/CD Integration](#cicd-integration)
7. [Security Considerations](#security-considerations)
8. [Cost Optimization](#cost-optimization)
9. [Backup and Disaster Recovery](#backup-and-disaster-recovery)
10. [References](#references)

---

## Technology Choices

### Why Kubernetes?

Kubernetes was chosen for container orchestration because:

1. **Scalability**: Automatic horizontal pod autoscaling based on CPU/memory
2. **High Availability**: Self-healing, automatic restarts, and replica management
3. **Portability**: Works across different cloud providers (avoid vendor lock-in)
4. **Ecosystem**: Rich ecosystem of tools and extensions
5. **Declarative Configuration**: Infrastructure as Code with YAML
6. **Service Discovery**: Built-in service discovery and load balancing

### Why Helm?

Helm was chosen for package management because:

1. **Templating**: Reusable charts for different environments
2. **Versioning**: Track and rollback chart versions
3. **Ecosystem**: Large library of community charts
4. **Upgrades**: Automated upgrade and rollback capabilities
5. **Values Files**: Environment-specific configuration

### Why NodePort?

For local development (Minikube), NodePort was chosen because:

1. **Simplicity**: Easy to set up for local testing
2. **No External Dependencies**: Doesn't require ingress controller
3. **Direct Access**: Services accessible via `minikube service` or port-forwarding

**Note**: For production, use LoadBalancer or Ingress controllers.

---

## Kubernetes Providers Comparison

### Local Development

| Provider | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| **Minikube** | Easy setup, cross-platform, good for learning | Single-node, resource-intensive | ✅ Recommended |
| **Kind** | Fast, uses Docker containers, multi-node | More complex setup | Good for CI/CD |
| **K3d** | Lightweight, fast | Limited features | Good for quick tests |
| **Docker Desktop** | Built-in, easy GUI | Limited Kubernetes features | Good for beginners |

### Cloud Providers

| Provider | Pros | Cons | Cost (Starting) |
|----------|------|------|-----------------|
| **DigitalOcean (DOKS)** | Simple, affordable, good docs | Fewer features | $10/month |
| **Google Cloud (GKE)** | Auto-upgrades, managed, excellent | More expensive | $74/month |
| **AWS (EKS)** | AWS integration, mature | Complex, expensive | $72/month |
| **Azure (AKS)** | Azure integration, good UI | Learning curve | $60/month |

### Recommendation for This Project

**Development**: Minikube (already in use)
**Production**: DigitalOcean DOKS (best balance of cost/features)

---

## Container Registry Options

### Public Registries

| Registry | Pros | Cons |
|----------|------|------|
| **Docker Hub** | Largest public registry, free tier | Rate limits on pulls |
| **GitHub Container Registry** | Integrated with GitHub, free | Newer, smaller ecosystem |
| **Quay.io** | Security scanning, good UI | No free tier for private |

### Cloud Provider Registries

| Registry | Provider | Notes |
|----------|----------|-------|
| **Container Registry** | DigitalOcean | Included with DOKS |
| **Artifact Registry** | Google Cloud | Integrated with GCP services |
| **ECR** | AWS | IAM integration |
| **ACR** | Azure | Azure AD integration |

### Recommendation

For this project:
- **Development**: Build directly in Minikube (no registry needed)
- **Production**: DigitalOcean Container Registry (included with DOKS)

---

## Ingress and Load Balancing

### Ingress Controllers

| Controller | Pros | Cons |
|------------|------|------|
| **NGINX Ingress** | Popular, well-documented, features | Configuration complexity |
| **Traefik** | Auto-discovery, simple config | Less mature |
| **HAProxy Ingress** | Performance, stability | Steeper learning curve |
| **AWS ALB Ingress** | AWS native | AWS only |

### Load Balancer Types

| Type | Use Case | Notes |
|------|----------|-------|
| **NodePort** | Local development | Port 30000-32767 |
| **LoadBalancer** | Production cloud | Cloud provider LB |
| **Ingress** | Production with HTTP routing | Layer 7 routing |

### Sample Ingress Configuration

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - todo.example.com
    secretName: todo-tls
  rules:
  - host: todo.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: todo-backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-frontend
            port:
              number: 3000
```

---

## Monitoring and Logging Solutions

### Monitoring

| Tool | Type | Pros | Cons |
|------|------|------|------|
| **Prometheus + Grafana** | Metrics | Industry standard, scalable | Complex setup |
| **Kubernetes Dashboard** | UI | Simple, built-in | Limited features |
| **Lens** | IDE | Full-cluster view | Desktop app only |
| **DigitalOcean Monitoring** | Managed | Easy, integrated | DO only |

### Logging

| Tool | Type | Pros | Cons |
|------|------|------|------|
| **ELK Stack** | Centralized logs | Powerful, flexible | Complex, resource-heavy |
| **Loki** | Lightweight logs | Simple, Prometheus-like | Less mature |
| **Fluentd** | Log collector | Rich plugins | Config complexity |
| **Cloud Logs** | Managed | No maintenance | Vendor lock-in |

### Recommendation for This Project

**Development**: Kubernetes Dashboard + kubectl logs
**Production**: Prometheus + Grafana + Loki (or cloud provider's solution)

### Health Check Endpoints

| Endpoint | Method | Response |
|----------|--------|----------|
| `/health` | GET | `{"status": "healthy"}` |
| `/api/health` | GET | `{"status": "database connected"}` |

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Build Frontend
      run: |
        docker build -t todo-frontend:${{ github.sha }} ./frontend
        docker push registry.todo.com/todo-frontend:${{ github.sha }}

    - name: Build Backend
      run: |
        docker build -t todo-backend:${{ github.sha }} ./backend
        docker push registry.todo.com/todo-backend:${{ github.sha }}

    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/todo-frontend frontend=todo-frontend:${{ github.sha }}
        kubectl set image deployment/todo-backend backend=todo-backend:${{ github.sha }}
```

### CI/CD Best Practices

1. **Build on every commit**: Ensure images build successfully
2. **Run tests**: Automated tests before deployment
3. **Tag images**: Use git SHA or semantic versioning
4. **Rollback capability**: Keep previous image versions
5. **Blue-green deployment**: Zero-downtime deployments

---

## Security Considerations

### Image Security

```bash
# Scan images for vulnerabilities
trivy image todo-backend:latest

# Use non-root user
USER appuser

# Use minimal base images
FROM python:3.13-slim
```

### Kubernetes Security

1. **RBAC**: Role-based access control
2. **Network Policies**: Restrict pod-to-pod communication
3. **Pod Security Standards**: Define security contexts
4. **Secrets Encryption**: Enable at-rest encryption

### Sample Security Context

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: backend
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
```

### Secrets Management

| Approach | Pros | Cons |
|----------|------|------|
| **Kubernetes Secrets** | Built-in, simple | Base64 encoded (not encrypted by default) |
| **Sealed Secrets** | GitOps friendly, encrypted | Additional tooling |
| **External Secrets** | Integration with vaults | More complex |
| **Cloud KMS** | Managed, secure | Vendor lock-in |

---

## Cost Optimization

### Right-Sizing Resources

```bash
# Analyze resource usage
kubectl top nodes
kubectl top pods

# Recommendations based on usage:
# - If CPU < 50% consistently: Reduce requests
# - If hitting limits frequently: Increase limits
```

### Cost-Saving Strategies

1. **Use spot instances** for non-critical workloads
2. **Auto-scale pods**: Scale to zero when not in use
3. **Cluster autoscaler**: Add/remove nodes based on demand
4. **Use appropriate instance types**: Don't over-provision
5. **Multi-AZ vs single-AZ**: Single-AZ is cheaper

### DigitalOcean Cost Estimate

| Resources | Monthly Cost |
|-----------|--------------|
| DOKS Cluster (basic) | $10 |
| Load Balancer | $10 |
| 2x Frontend Pods (1GB RAM) | $12 |
| 2x Backend Pods (2GB RAM) | $24 |
| Block Storage (20GB) | $4 |
| **Total** | **~$60/month** |

---

## Backup and Disaster Recovery

### Backup Strategy

1. **Database Backups**:
   ```bash
   # Automated daily backups
   kubectl exec postgres-0 -- pg_dump -U postgres tododb | gzip > backup-$(date +%Y%m%d).sql.gz
   ```

2. **Persistent Volume Snapshots** (cloud providers)

3. **Helm Release Backups**:
   ```bash
   helm list
   helm get values backend > backend-values.yaml
   ```

4. **Cluster Backup**:
   - Use Velero for full cluster backups
   - Store backups in cloud storage (S3, Spaces)

### Disaster Recovery Checklist

- [ ] Database backup schedule configured
- [ ] Backups stored off-site
- [ ] Restore procedure tested
- [ ] Documentation up-to-date
- [ ] Team trained on recovery

---

## Performance Tuning

### Resource Limits

Based on testing:

```yaml
# Frontend (Next.js)
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"

# Backend (FastAPI)
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Database Connection Pooling

```python
# In backend/app/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,      # For production
    max_overflow=40,   # Additional connections
    pool_pre_ping=True,
)
```

### Caching Strategy

1. **Response caching**: Cache API responses
2. **Database query caching**: Use SQLAlchemy caching
3. **CDN**: Serve static assets via CDN

---

## Troubleshooting Guide

### Common Issues

#### Pod Won't Start

```bash
# Check pod status
kubectl get pods
kubectl describe pod <pod-name>

# Common causes:
# - Image pull error: Check image name and registry
# - CrashLoopBackOff: Check logs for application errors
# - OOMKilled: Increase memory limits
```

#### Service Not Accessible

```bash
# Check service
kubectl get svc
kubectl describe svc <service-name>

# Test from within cluster
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never
curl http://todo-backend:8000/health
```

#### Database Connection Failed

```bash
# Check database service
kubectl get svc postgres

# Test connection
kubectl exec -it backend-xxx -- psql $DATABASE_URL

# Common causes:
# - Wrong service name: Use postgres-service (not postgres)
# - Wrong credentials: Check secrets
# - Network policy blocking: Check network policies
```

---

## References

### Official Documentation

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

### Tools and Utilities

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [helm](https://helm.sh/docs/helm/helm/)
- [k9s](https://k9scli.io/) - Terminal UI for Kubernetes
- [Lens](https://k8slens.dev/) - Kubernetes IDE
- [Tilt](https://tilt.dev/) - Local development workflow

### Community Resources

- [Kubernetes Community](https://kubernetes.io/community/)
- [CNCF](https://www.cncf.io/)
- [DigitalOcean Kubernetes Tutorials](https://docs.digitalocean.com/tutorials/kubernetes)

### Articles and Best Practices

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Production Readiness Checklist](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/production-readiness.md)

---

## Decision Record

### Technology Choices

| Decision | Reason | Date |
|----------|--------|------|
| Kubernetes | Container orchestration standard | 2025-12-20 |
| Helm | Package management and templating | 2025-12-20 |
| Minikube | Local development | 2025-12-20 |
| NodePort | Local testing simplicity | 2025-12-20 |
| PostgreSQL | Relational database, ACID compliance | From Phase I |
| Docker | Container runtime | From Phase I |

### Future Considerations

- [ ] Evaluate service mesh (Istio, Linkerd)
- [ ] Implement GitOps (ArgoCD, Flux)
- [ ] Add comprehensive observability (Jaeger, Zipkin)
- [ ] Implement chaos engineering (Chaos Monkey, Litmus)
- [ ] Evaluate Knative for serverless workloads
