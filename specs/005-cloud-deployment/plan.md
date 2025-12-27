# Implementation Plan: Cloud Deployment with Event-Driven Architecture

**Feature**: 005-cloud-deployment
**Created**: 2025-12-23
**Completed**: 2025-12-27
**Estimated Duration**: 10 days
**Status**: ✅ **COMPLETE**

---

## 🎉 Production Deployment

| Service | URL |
|---------|-----|
| **Frontend** | https://hackathon2.testservers.online |
| **Backend API** | https://api.testservers.online |
| **API Docs** | https://api.testservers.online/docs |

---

## Overview

This plan breaks down Phase V implementation into 10 days of work, covering database changes, API development, Dapr integration, notification service, cloud deployment, and CI/CD automation.

---

## Day 1: Database Schema and Migrations

### Tasks

1. **Create RecurringTask Model**
   - File: `backend/app/models/recurring_task.py`
   - Fields: id, user_id, title, description, priority, recurrence_type, recurrence_interval, start_date, end_date, next_due_at, is_active

2. **Update Task Model**
   - Add `due_date` field
   - Add `notified` field
   - Add `recurring_task_id` foreign key

3. **Create TaskEventLog Model**
   - File: `backend/app/models/task_event_log.py`
   - Fields: id, task_id, event_type, event_data, created_at

4. **Generate Migration**
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add recurring tasks and due dates"
   alembic upgrade head
   ```

**Validation**:
- [ ] Migration applies successfully
- [ ] New tables exist
- [ ] Foreign keys correct

---

## Day 2: Recurring Tasks CRUD API

### Tasks

1. **Create CRUD Operations**
   - File: `backend/app/crud/recurring_task.py`
   - Functions: create, get, list, update, delete

2. **Create Schemas**
   - File: `backend/app/schemas/recurring_task.py`
   - Schemas: RecurringTaskCreate, RecurringTaskUpdate, RecurringTaskResponse

3. **Create API Endpoints**
   - File: `backend/app/api/recurring_tasks.py`
   - Routes: POST, GET, PUT, DELETE

4. **Update Task API**
   - Modify: `backend/app/api/tasks.py`
   - Add support for `due_date` field

**Validation**:
- [ ] Can create recurring task
- [ ] Can list recurring tasks
- [ ] Can update recurring task
- [ ] Can delete recurring task
- [ ] Due date works on tasks

---

## Day 3: Dapr Integration and Event Publishing

### Tasks

1. **Install Dapr Python SDK**
   ```bash
   pip install dapr
   ```

2. **Create Event Publisher Service**
   - File: `backend/app/services/event_publisher.py`
   - Functions: publish_task_created, publish_task_updated, publish_task_completed

3. **Integrate Event Publishing**
   - Modify: `backend/app/api/tasks.py`
   - Publish events on CRUD operations

4. **Create Dapr Component Manifests**
   - File: `k8s/dapr-components/pubsub-redpanda.yaml`
   - File: `k8s/dapr-components/secrets.yaml`

**Validation**:
- [ ] Dapr SDK installed
- [ ] Events publish without errors
- [ ] Event payload correct
- [ ] Dapr components configured

---

## Day 4: Notification Service Development

### Tasks

1. **Create Notification Service Application**
   - Directory: `services/notifications/`
   - File: `services/notifications/app/main.py`
   - File: `services/notifications/requirements.txt`

2. **Create Due Date Checker**
   - File: `services/notifications/app/workers/due_date_checker.py`
   - Check for tasks due within 24 hours
   - Send notifications

3. **Create Recurring Task Processor**
   - File: `services/notifications/app/workers/recurring_processor.py`
   - Create next occurrence when due
   - Update next_due_at

4. **Create Dockerfile**
   - File: `services/notifications/Dockerfile`

**Validation**:
- [ ] Notification service runs locally
- [ ] Due date checker works
- [ ] Recurring processor creates tasks
- [ ] Docker image builds

---

## Day 5: Notification Service Deployment

### Tasks

1. **Create Helm Chart**
   - Directory: `helm/notifications/`
   - Chart.yaml, values.yaml, templates/

2. **Configure Dapr Sidecar**
   - Add Dapr annotations to deployment
   - Configure app-id and app-port

3. **Create Event Subscriptions**
   - Subscribe to: task-created, task-updated, task-due-soon
   - File: `services/notifications/app/subscriptions.py`

4. **Test Event Flow**
   - Deploy to Minikube
   - Verify subscription works
   - Verify events processed

**Validation**:
- [ ] Notification service deploys
- [ ] Dapr sidecar injected
- [ ] Subscribes to topics
- [ ] Receives and processes events

---

## Day 6: DigitalOcean Cluster Setup

### Tasks

1. **Install and Configure doctl**
   ```bash
   # Install doctl
   brew install doctl  # macOS
   # Or download from https://github.com/digitalocean/doctl/releases

   # Authenticate
   doctl auth init

   # Verify authentication
   doctl account get
   ```

2. **Create DOKS Cluster**
   ```bash
   # Create cluster with 3 nodes
   doctl kubernetes cluster create todo-cluster \
     --region nyc1 \
     --version 1.29.0 \
     --node-pool "name=pool-1;size=s-4vcpu-8gb;count=3;auto-scale=true;min-nodes=2;max-nodes=5"

   # Get kubeconfig
   doctl kubernetes cluster kubeconfig save todo-cluster

   # Verify cluster
   kubectl get nodes
   kubectl cluster-info
   ```

3. **Create DO Managed Redis**
   ```bash
   # Create Redis database
   doctl databases create todo-redis \
     --engine redis \
     --region nyc1 \
     --size 1gb \
     --num-nodes 1

   # Get connection details
   doctl databases connection todo-redis --format json > redis-connection.json
   REDIS_HOST=$(cat redis-connection.json | jq -r '.host')
   REDIS_PORT=$(cat redis-connection.json | jq -r '.port')
   REDIS_PASSWORD=$(cat redis-connection.json | jq -r '.password')
   ```

4. **Create DO Container Registry**
   ```bash
   # Create registry
   doctl registry create

   # Login to registry
   doctl registry login

   # Create repository (optional - auto-created on push)
   # doctl registry repository create todo-app
   ```

5. **Install Dapr on DOKS**
   ```bash
   dapr init --kubernetes
   kubectl get pods -n dapr-system
   ```

6. **Install Redpanda with Block Storage**
   ```bash
   helm repo add redpanda https://charts.redpanda.com
   helm repo update

   helm install redpanda redpanda/redpanda \
     --set replicas=3 \
     --set persistence.size=50Gi \
     --set resources.requests.cpu=2 \
     --set resources.requests.memory=4Gi
   ```

**Validation**:
- [ ] DOKS cluster has 3 nodes running
- [ ] doctl can manage cluster
- [ ] DO Managed Redis is active
- [ ] Container Registry created and accessible
- [ ] Dapr pods running in dapr-system namespace
- [ ] Redpanda has 3 replicas with persistent storage
- [ ] Redpanda pods are Ready

---

## Day 7: Deploy to DigitalOcean

### Tasks

1. **Build and Push Images to DO Container Registry**
   ```bash
   # Build images
   docker build -t todo-frontend:latest ./frontend
   docker build -t todo-backend:latest ./backend
   docker build -t todo-notifications:latest ./services/notifications

   # Tag for DO registry
   docker tag todo-frontend:latest registry.digitalocean.com/todo-app/todo-frontend:latest
   docker tag todo-backend:latest registry.digitalocean.com/todo-app/todo-backend:latest
   docker tag todo-notifications:latest registry.digitalocean.com/todo-app/todo-notifications:latest

   # Push to DO registry
   docker push registry.digitalocean.com/todo-app/todo-frontend:latest
   docker push registry.digitalocean.com/todo-app/todo-backend:latest
   docker push registry.digitalocean.com/todo-app/todo-notifications:latest
   ```

2. **Create DigitalOcean-Specific Values**
   - File: `helm/*/values-do.yaml`
   - Configure DO LoadBalancer
   - Configure resource limits
   - Configure DO Managed Redis connection

   ```yaml
   # values-do.yaml example
   image:
     repository: registry.digitalocean.com/todo-app/todo-backend
     tag: latest

   service:
     type: LoadBalancer  # Provisions DO Load Balancer

   resources:
     requests:
       memory: "256Mi"
       cpu: "250m"
     limits:
       memory: "512Mi"
       cpu: "500m"

   redis:
     host: "<REDIS_HOST>"
     port: "<REDIS_PORT>"
     password: "<REDIS_PASSWORD>"
   ```

3. **Create Kubernetes Secrets**
   ```bash
   # Create backend secrets
   kubectl create secret generic backend-secrets \
     --from-literal=database-url="$DATABASE_URL" \
     --from-literal=jwt-secret="$JWT_SECRET" \
     --from-literal=groq-api-key="$GROQ_API_KEY"

   # Create Redis connection secret
   kubectl create secret generic redis-secrets \
     --from-literal=redis-host="$REDIS_HOST" \
     --from-literal=redis-port="$REDIS_PORT" \
     --from-literal=redis-password="$REDIS_PASSWORD"

   # Create Dapr Redis component for state store
   kubectl create secret generic dapr-redis-secrets \
     --from-literal=redis-host="$REDIS_HOST" \
     --from-literal=redis-password="$REDIS_PASSWORD"
   ```

4. **Deploy Services with Helm**
   ```bash
   # Deploy frontend
   helm install frontend helm/frontend \
     -f helm/frontend/values-do.yaml \
     --namespace production --create-namespace

   # Deploy backend
   helm install backend helm/backend \
     -f helm/backend/values-do.yaml \
     --namespace production --create-namespace

   # Deploy notification service
   helm install notifications helm/notifications \
     -f helm/notifications/values-do.yaml \
     --namespace production --create-namespace
   ```

5. **Verify DO Load Balancers**
   ```bash
   # Check Load Balancers are provisioned
   kubectl get svc -n production

   # Get Load Balancer IPs
   kubectl get svc frontend -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
   kubectl get svc backend -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

   # Verify via doctl
   doctl compute load-balancer list
   ```

6. **Configure DO Cloud Firewall**
   ```bash
   # Create firewall for cluster
   doctl compute firewall create todo-cluster-fw \
     --inbound-rules="protocol:tcp,ports:443,address:0.0.0.0/0,protocol:tcp,ports:80,address:0.0.0.0/0" \
     --outbound-rules="protocol:tcp,ports:all,address:0.0.0.0/0" \
     --tag-names=k8s:todo-cluster

   # Apply to cluster nodes
   doctl kubernetes cluster update todo-cluster --firewall todo-cluster-fw
   ```

**Validation**:
- [ ] Images pushed to DO Container Registry
- [ ] DO Load Balancers provisioned (3 total)
- [ ] Secrets created correctly
- [ ] All pods running in production namespace
- [ ] Services accessible via DO Load Balancers
- [ ] Cloud Firewall configured
- [ ] End-to-end connectivity works

---

## Day 8: CI/CD Pipeline with DigitalOcean

### Tasks

1. **Create DO Container Registry Access Token**
   ```bash
   # Create access token for CI/CD
   doctl registry token create --read-write --expiry-seconds 0 > do_registry_token.txt

   # Copy token value for GitHub Secrets
   cat do_registry_token.txt
   ```

2. **Add GitHub Secrets**
   - `DO_REGISTRY_TOKEN`: Container registry access token
   - `DO_ACCESS_TOKEN`: DigitalOcean API token for doctl
   - `KUBECONFIG`: Base64-encoded kubeconfig for DOKS cluster
   - `DATABASE_URL`: Production database connection string
   - `JWT_SECRET`: Production JWT secret
   - `GROQ_API_KEY`: Groq API key for AI

   ```bash
   # Encode kubeconfig for GitHub
   cat ~/.kube/config | base64 -w 0

   # Add to GitHub: Settings > Secrets > New secret
   ```

3. **Create GitHub Actions Workflow**
   - File: `.github/workflows/deploy-digitalocean.yml`
   - Stages: Build, Test, Push to DO Registry, Deploy to DOKS, Health Check

   ```yaml
   name: Deploy to DigitalOcean

   on:
     push:
       branches: [main]

   jobs:
     build-and-deploy:
       runs-on: ubuntu-latest

       steps:
       - uses: actions/checkout@v4

       - name: Login to DO Registry
         run: docker login registry.digitalocean.com -u ${{ secrets.DO_REGISTRY_TOKEN }} -p ${{ secrets.DO_REGISTRY_TOKEN }}

       - name: Build images
         run: |
           docker build -t registry.digitalocean.com/todo-app/todo-frontend:${{ github.sha }} ./frontend
           docker build -t registry.digitalocean.com/todo-app/todo-backend:${{ github.sha }} ./backend
           docker build -t registry.digitalocean.com/todo-app/todo-notifications:${{ github.sha }} ./services/notifications

       - name: Push images
         run: |
           docker push registry.digitalocean.com/todo-app/todo-frontend:${{ github.sha }}
           docker push registry.digitalocean.com/todo-app/todo-backend:${{ github.sha }}
           docker push registry.digitalocean.com/todo-app/todo-notifications:${{ github.sha }}

       - name: Install doctl
         uses: digitalocean/action-doctl@v2
         with:
           token: ${{ secrets.DO_ACCESS_TOKEN }}

       - name: Configure kubectl
         run: |
           echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
           export KUBECONFIG=kubeconfig

       - name: Deploy to DOKS
         run: |
           helm upgrade --install frontend helm/frontend \
             --set image.tag=${{ github.sha }} \
             --namespace production
           helm upgrade --install backend helm/backend \
             --set image.tag=${{ github.sha }} \
             --namespace production
           helm upgrade --install notifications helm/notifications \
             --set image.tag=${{ github.sha }} \
             --namespace production

       - name: Health Check
         run: |
           kubectl wait --for=condition=ready pod -l app=frontend -n production --timeout=300s
           kubectl wait --for=condition=ready pod -l app=backend -n production --timeout=300s
   ```

4. **Test Pipeline**
   ```bash
   # Push to main branch
   git push origin main

   # Monitor workflow in GitHub Actions
   # Verify images pushed to DO Container Registry
   doctl registry repository list

   # Verify deployment on DOKS
   kubectl get pods -n production
   kubectl get svc -n production
   ```

**Validation**:
- [ ] DO Registry access token created
- [ ] GitHub secrets configured
- [ ] Workflow runs on push to main
- [ ] Images build and push to DO Container Registry
- [ ] Automatic deployment to DOKS works
- [ ] Health checks pass
- [ ] DO Load Balancers updated

---

## Day 9: kubectl-ai and kagent

### Tasks

1. **Install kubectl-ai**
   ```bash
   kubectl krew install ai
   ```

2. **Install kagent**
   ```bash
   npm install -g @kagent/cli
   kagent init
   ```

3. **Test AI Operations**
   ```bash
   kubectl ai list pods
   kagent "Scale backend to 3 replicas"
   ```

**Validation**:
- [ ] kubectl-ai installed
- [ ] kagent configured
- [ ] Can perform operations with AI
- [ ] Can troubleshoot with AI

---

## Day 10: Monitoring and Documentation

### Tasks

1. **Install Prometheus/Grafana**
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/kube-prometheus-stack
   ```

2. **Create Dashboards**
   - Kubernetes Cluster
   - Dapr Metrics
   - Application Metrics

3. **End-to-End Testing**
   - Create task with due date
   - Create recurring task
   - Verify notifications
   - Check event flow

4. **Documentation**
   - Update README
   - Create runbook
   - Document rollback procedures

**Validation**:
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards visible
- [ ] All E2E tests pass
- [ ] Documentation complete

---

## Rollback Plan

### Helm Rollback
```bash
helm rollback frontend
helm rollback backend
helm rollback notifications
```

### Emergency Disable
```bash
helm uninstall frontend
helm uninstall backend
helm uninstall notifications
```

---

## Success Criteria

Phase V complete when:
- [x] All services deployed to cloud
- [x] Dapr sidecars running
- [x] Redpanda cluster healthy
- [x] Events publishing/consuming
- [x] Recurring tasks working
- [x] Due date notifications working
- [x] CI/CD automated
- [x] Monitoring active
- [x] AI tools functional
- [x] E2E tests passing
- [x] Documentation complete

---

## Estimated Timeline

| Phase | Days | Status |
|-------|------|--------|
| Database Changes | 1 | ✅ Complete |
| Recurring Tasks API | 1 | ✅ Complete |
| Dapr Integration | 1 | ✅ Complete |
| Notification Service | 2 | ✅ Complete |
| Cloud Cluster Setup | 1 | ✅ Complete |
| Cloud Deployment | 1 | ✅ Complete |
| CI/CD Pipeline | 1 | ✅ Complete |
| AI Tools Setup | 1 | ✅ Complete |
| Monitoring & Docs | 1 | ✅ Complete |

**Total**: 10 days | **Actual**: Completed 2025-12-27
