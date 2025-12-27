# DigitalOcean Quick Reference Guide

**Phase V Infrastructure - Quick Commands and References**

---

## One-Liner Setup Commands

### Create DOKS Cluster
```bash
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --version 1.29.2-do.0 \
  --node-pool "name=pool-1;size=s-4vcpu-8gb;count=3;auto-scale=true;min-nodes=2;max-nodes=5" \
  --maintenance-window "any=00:00-04:00"
```

### Get Kubeconfig
```bash
doctl kubernetes cluster kubeconfig save todo-cluster
```

### Install Dapr
```bash
dapr init --kubernetes
```

### Install Redpanda
```bash
helm repo add redpanda https://charts.redpanda.com
helm repo update
helm install redpanda redpanda/redpanda --namespace redpanda-system --create-namespace \
  --set replicas=3 --set persistence.size=50Gi --set persistence.storageClass=do-block-storage
```

### Create Redis
```bash
doctl databases create todo-redis --engine redis --region nyc1 --size 1gb --num-nodes 1
```

### Create Container Registry
```bash
doctl registry create
doctl registry login
```

---

## Environment Variables

```bash
# DigitalOcean
export DIGITALOCEAN_ACCESS_TOKEN=your_token_here

# Database (Neon or DO)
export DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require"

# Redis (from DO)
export REDIS_HOST=$(doctl databases connection todo-redis --format json | jq -r '.host')
export REDIS_PORT=$(doctl databases connection todo-redis --format json | jq -r '.port')
export REDIS_PASSWORD=$(doctl databases connection todo-redis --format json | jq -r '.password')

# Application
export JWT_SECRET=$(openssl rand -base64 32)
export GROQ_API_KEY=your_groq_key_here
```

---

## Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace production

# Backend secrets
kubectl create secret generic backend-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --namespace=production

# Redis secrets
kubectl create secret generic redis-secrets \
  --from-literal=redis-host="$REDIS_HOST" \
  --from-literal=redis-port="$REDIS_PORT" \
  --from-literal=redis-password="$REDIS_PASSWORD" \
  --namespace=production

# App secrets
kubectl create secret generic app-secrets \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=groq-api-key="$GROQ_API_KEY" \
  --namespace=production
```

---

## Dapr Components

### Pub/Sub (Redpanda)
```yaml
# k8s/dapr-components/pubsub-redpanda.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
  namespace: production
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda.redpanda-system.svc.cluster.local:9092"
    - name: allowedTopics
      value: "task-created,task-updated,task-completed,task-deleted,task-due-soon,recurring-task-due"
```

### State Store (Redis)
```yaml
# k8s/dapr-components/statestore-redis.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-statestore
  namespace: production
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      secretKeyRef:
        name: redis-secrets
        key: redis-host
    - name: redisPassword
      secretKeyRef:
        name: redis-secrets
        key: redis-password
    - name: redisPort
      secretKeyRef:
        name: redis-secrets
        key: redis-port
```

---

## Docker Commands

### Build and Push to DO Registry

```bash
# Frontend
docker build -t todo-frontend:latest ./frontend
docker tag todo-frontend:latest registry.digitalocean.com/todo-app/todo-frontend:latest
docker push registry.digitalocean.com/todo-app/todo-frontend:latest

# Backend
docker build -t todo-backend:latest ./backend
docker tag todo-backend:latest registry.digitalocean.com/todo-app/todo-backend:latest
docker push registry.digitalocean.com/todo-app/todo-backend:latest

# Notifications
docker build -t todo-notifications:latest ./services/notifications
docker tag todo-notifications:latest registry.digitalocean.com/todo-app/todo-notifications:latest
docker push registry.digitalocean.com/todo-app/todo-notifications:latest
```

---

## Kafka Topics (Redpanda)

```bash
# Create topics
kubectl exec -n redpanda-system redpanda-0 -- rpk topic create task-created --replicas 3
kubectl exec -n redpanda-system redpanda-0 -- rpk topic create task-updated --replicas 3
kubectl exec -n redpanda-system redpanda-0 -- rpk topic create task-completed --replicas 3
kubectl exec -n redpanda-system redpanda-0 -- rpk topic create task-deleted --replicas 3
kubectl exec -n redpanda-system redpanda-0 -- rpk topic create task-due-soon --replicas 3
kubectl exec -n redpanda-system redpanda-0 -- rpk topic create recurring-task-due --replicas 3

# List topics
kubectl exec -n redpanda-system redpanda-0 -- rpk topic list

# Consume from topic (testing)
kubectl exec -n redpanda-system redpanda-0 -- rpk topic consume task-created
```

---

## Verification Commands

```bash
# Cluster status
kubectl get nodes
kubectl cluster-info

# Dapr status
kubectl get pods -n dapr-system
dapr status -k

# Redpanda status
kubectl get pods -n redpanda-system
kubectl exec -n redpanda-system redpanda-0 -- rpd cluster status

# Components
kubectl get components -n production
kubectl describe component todo-pubsub -n production

# Secrets
kubectl get secrets -n production

# Services
kubectl get svc -n production
kubectl get pods -n production

# Logs
kubectl logs -f deployment/backend -n production
kubectl logs -f deployment/frontend -n production
```

---

## DO CLI Commands

```bash
# List clusters
doctl kubernetes cluster list

# Cluster info
doctl kubernetes cluster get todo-cluster

# Node pools
doctl kubernetes cluster node-pool list todo-cluster

# Databases
doctl databases list
doctl databases get todo-redis
doctl databases connection todo-redis

# Registry
doctl registry repository list
doctl registry garbage-collection start

# Load balancers
doctl compute load-balancer list

# Firewall
doctl compute firewall list
```

---

## Cost Summary

| Item | Cost/Month |
|------|-----------|
| DOKS (3 × s-4vcpu-8gb) | $120 |
| Load Balancers (3 ×) | $36 |
| Redis (1GB) | $15 |
| Block Storage (150GB) | $15 |
| Registry (5GB) | ~$1 |
| **Total** | **~$187** |

**Cost Saving Options:**
- 2GB nodes: Save ~$60/month
- 2 nodes instead of 3: Save ~$40/month
- Development: Run single node when not testing

---

## Port Forwarding

```bash
# Dapr Dashboard
kubectl port-forward -n dapr-system svc/dapr-dashboard 8080:8080
# Open: http://localhost:8080

# Application services
kubectl port-forward -n production svc/frontend 3000:3000
kubectl port-forward -n production svc/backend 8000:8000

# Redpanda admin
kubectl port-forward -n redpanda-system svc/redpanda 9644:9644
```

---

## Troubleshooting

```bash
# Pod issues
kubectl describe pod <pod-name> -n production
kubectl logs <pod-name> -n production --previous

# Node issues
kubectl describe node <node-name>

# Service issues
kubectl describe svc <service-name> -n production

# Events
kubectl get events -n production --sort-by='.lastTimestamp'

# Dapr issues
kubectl logs -l app=dapr-sidecar-injector -n dapr-system
kubectl logs -n dapr-system dapr-sentry-0

# Redpanda issues
kubectl logs -n redpanda-system redpanda-0
kubectl exec -n redpanda-system redpanda-0 -- rpd cluster status
```

---

## Cleanup Commands

```bash
# Delete deployments
kubectl delete namespace production
kubectl delete namespace redpanda-system

# Uninstall Dapr
dapr uninstall --kubernetes

# Delete cluster
doctl kubernetes cluster delete todo-cluster

# Delete Redis
doctl databases delete todo-redis

# Delete registry
doctl registry delete

# Delete firewall
doctl compute firewall delete todo-cluster-fw
```

---

## Important URLs

| Service | URL |
|---------|-----|
| DO Console | https://cloud.digitalocean.com |
| Dapr Docs | https://dapr.io/docs/ |
| Redpanda Docs | https://docs.redpanda.com/ |
| K8s Docs | https://kubernetes.io/docs/ |

---

## Connection Strings

### Redpanda (Kafka)
```
Broker: redpanda.redpanda-system.svc.cluster.local:9092
```

### Redis (from DO)
```
Host: <from doctl databases connection>
Port: 25061 (example)
Password: <from doctl databases connection>
```

### PostgreSQL (Neon)
```
Connection String: <from Neon console>
```

---

**Quick Reference Version**: 1.0
**Last Updated**: 2025-12-25
