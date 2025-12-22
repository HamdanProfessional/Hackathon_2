# Validation Checklist: Kubernetes Deployment

**Feature**: 004-kubernetes
**Status**: 🚧 In Progress

---

## Docker Images

### Frontend Image
- [ ] `frontend/Dockerfile` exists
- [ ] Multi-stage build configured
- [ ] Next.js standalone output enabled in `next.config.mjs`
- [ ] `.dockerignore` created
- [ ] Image builds: `docker build -t todo-frontend ./frontend`
- [ ] Container runs: `docker run -p 3000:3000 todo-frontend`
- [ ] Application accessible at http://localhost:3000
- [ ] No console errors in browser
- [ ] Static assets served correctly

### Backend Image
- [ ] `backend/Dockerfile` exists
- [ ] Python 3.13-slim base image
- [ ] Health check configured
- [ ] Non-root user created
- [ ] `.dockerignore` created
- [ ] Image builds: `docker build -t todo-backend ./backend`
- [ ] Container runs: `docker run -p 8000:8000 todo-backend`
- [ ] Health check responds: `curl http://localhost:8000/health`
- [ ] API endpoints accessible
- [ ] Database connectivity works

---

## Docker Compose

### Configuration
- [ ] `docker-compose.yml` exists
- [ ] Frontend service configured
- [ ] Backend service configured
- [ ] PostgreSQL service configured
- [ ] Network configured (todo-network)
- [ ] Health checks configured
- [ ] Environment variables set

### Functionality
- [ ] `docker-compose up` starts all services
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend accessible at http://localhost:8000
- [ ] PostgreSQL accessible on port 5432
- [ ] Frontend can call backend API
- [ ] Backend can connect to database
- [ ] Data persists across restarts

---

## Helm Charts

### Frontend Chart
- [ ] `helm/frontend/Chart.yaml` exists
- [ ] `helm/frontend/values.yaml` exists
- [ ] `helm/frontend/templates/deployment.yaml` exists
- [ ] `helm/frontend/templates/service.yaml` exists
- [ ] `helm/frontend/templates/ingress.yaml` exists
- [ ] `helm/frontend/templates/configmap.yaml` exists
- [ ] `helm/frontend/templates/hpa.yaml` exists
- [ ] `helm/frontend/templates/_helpers.tpl` exists
- [ ] `helm/frontend/templates/NOTES.txt` exists

### Backend Chart
- [ ] `helm/backend/Chart.yaml` exists
- [ ] `helm/backend/values.yaml` exists
- [ ] `helm/backend/templates/deployment.yaml` exists
- [ ] `helm/backend/templates/service.yaml` exists
- [ ] `helm/backend/templates/ingress.yaml` exists
- [ ] `helm/backend/templates/secrets.yaml` exists
- [ ] `helm/backend/templates/configmap.yaml` exists
- [ ] `helm/backend/templates/hpa.yaml` exists
- [ ] `helm/backend/templates/_helpers.tpl` exists
- [ ] `helm/backend/templates/NOTES.txt` exists

### Chart Validation
- [ ] Frontend chart lints: `helm lint helm/frontend`
- [ ] Backend chart lints: `helm lint helm/backend`
- [ ] Frontend templates render: `helm template helm/frontend`
- [ ] Backend templates render: `helm template helm/backend`
- [ ] Frontend dry-run works: `helm install --dry-run frontend helm/frontend`
- [ ] Backend dry-run works: `helm install --dry-run backend helm/backend`

---

## Minikube Deployment

### Cluster Setup
- [ ] Minikube installed
- [ ] Minikube starts: `minikube start --cpus=4 --memory=8192`
- [ ] Ingress enabled: `minikube addons enable ingress`
- [ ] `kubectl cluster-info` works
- [ ] `kubectl get nodes` shows Ready

### Image Loading
- [ ] Frontend image built
- [ ] Backend image built
- [ ] Frontend loaded: `minikube image load todo-frontend`
- [ ] Backend loaded: `minikube image load todo-backend`
- [ ] Images visible: `minikube image ls | grep todo`

### Helm Installation
- [ ] Backend installed: `helm install backend helm/backend`
- [ ] Frontend installed: `helm install frontend helm/frontend`
- [ ] `helm list` shows both releases
- [ ] `kubectl get pods` shows 2/2 for each

### Pod Health
- [ ] Backend pods Running
- [ ] Frontend pods Running
- [ ] All pods ready (2/2)
- [ ] No pods in CrashLoopBackOff
- [ ] No pods in ImagePullBackOff

### Service Access
- [ ] Backend service exists: `kubectl get svc backend`
- [ ] Frontend service exists: `kubectl get svc frontend`
- [ ] Minikube service works: `minikube service backend --url`
- [ ] Minikube tunnel works: `minikube tunnel`
- [ ] Frontend accessible via NodePort
- [ ] Backend API accessible via NodePort

### Functionality Tests
- [ ] Frontend loads without errors
- [ ] Can navigate to /dashboard
- [ ] Can create task via UI
- [ ] Task persists to database
- [ ] Can list tasks
- [ ] Can complete task
- [ ] Can delete task

---

## Documentation

### Deployment Guides
- [ ] `docs/MINIKUBE_DEPLOYMENT_GUIDE.md` exists
- [ ] `docs/KUBERNETES_QUICK_REFERENCE.md` exists

### Spec Files
- [ ] `specs/004-kubernetes/spec.md` complete
- [ ] `specs/004-kubernetes/plan.md` complete
- [ ] `specs/004-kubernetes/quickstart.md` complete
- [ ] `specs/004-kubernetes/tasks.md` complete
- [ ] `specs/004-kubernetes/data-model.md` complete

---

## Security

### Container Security
- [ ] Frontend runs as non-root user (nextjs:1001)
- [ ] Backend runs as non-root user (appuser:1001)
- [ ] No privileged containers
- [ ] Read-only root filesystem (where applicable)

### Kubernetes Security
- [ ] Secrets used for sensitive data
- [ ] No secrets in ConfigMaps
- [ ] RBAC configured (if applicable)
- [ ] Network policies (optional)

---

## Performance

### Resource Limits
- [ ] Frontend has resource requests
- [ ] Frontend has resource limits
- [ ] Backend has resource requests
- [ ] Backend has resource limits
- [ ] PostgreSQL has resource limits

### Health Checks
- [ ] Frontend has liveness probe
- [ ] Frontend has readiness probe
- [ ] Backend has liveness probe
- [ ] Backend has readiness probe
- [ ] Probes configured correctly

---

## Rollback Testing

### Helm Rollback
- [ ] Can rollback frontend: `helm rollback frontend`
- [ ] Can rollback backend: `helm rollback backend`
- [ ] Rollback restores previous version
- [ ] Application works after rollback

### Clean Up
- [ ] Can uninstall frontend: `helm uninstall frontend`
- [ ] Can uninstall backend: `helm uninstall backend`
- [ ] Can stop Minikube: `minikube stop`
- [ ] Can delete Minikube: `minikube delete`

---

## Success Criteria

Phase IV is complete when:
- [ ] All Docker images build and run
- [ ] Docker Compose works locally
- [ ] All Helm charts pass linting
- [ ] Application deploys to Minikube
- [ ] All services accessible and functional
- [ ] All documentation complete
- [ ] Security requirements met
- [ ] Performance requirements met

---

## Sign-off

**Developer**: _________________ **Date**: _______

**Reviewer**: _________________ **Date**: _______
