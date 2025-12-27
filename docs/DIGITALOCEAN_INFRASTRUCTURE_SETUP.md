# DigitalOcean Infrastructure Setup Guide

**Phase**: V - Cloud Deployment with Event-Driven Architecture
**Option**: 1 - Start with Infrastructure
**Last Updated**: 2025-12-25
**Estimated Time**: 2-3 hours
**Estimated Cost**: ~$143/month

---

## Overview

This guide will walk you through setting up the complete DigitalOcean infrastructure for the Todo application with event-driven architecture using Dapr, Redpanda, and microservices.

### Architecture

```
DigitalOcean Kubernetes (DOKS)
├── 3 Nodes (s-4vcpu-8gb)
├── Services:
│   ├── Frontend (Next.js) + Dapr Sidecar
│   ├── Backend (FastAPI) + Dapr Sidecar
│   └── Notification Service + Dapr Sidecar
├── Load Balancers: 3x DO LB
├── Storage:
│   ├── Redpanda Cluster (3 replicas, 50GB each)
│   ├── DO Managed Redis (1GB)
│   └── PostgreSQL (Neon external)
└── Registry: DO Container Registry
```

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Credit card for DigitalOcean account
- [ ] Computer with admin privileges
- [ ] Git installed
- [ ] Docker installed and running
- [ ] kubectl installed
- [ ] Helm 3.x installed
- [ ] Python 3.11+ installed
- [ ] ~$200 credit on DigitalOcean (new accounts get $200/60 days)

---

## Phase 1: DigitalOcean Account Setup

### Step 1.1: Create DigitalOcean Account

1. Go to https://www.digitalocean.com/
2. Click "Sign Up"
3. Choose one of:
   - **Sign up with Email** (recommended)
   - **Sign up with Google**
   - **Sign up with GitHub**
4. Enter email, password, and account details
5. **Add billing information** (required for free tier)
   - Credit/Debit card or PayPal
   - You will NOT be charged immediately
   - New accounts get $200 free credit for 60 days
6. Verify email address
7. Complete phone verification (if prompted)

### Step 1.2: Generate API Token

You'll need an API token for CLI access:

1. Log in to DigitalOcean Control Panel
2. Click **API** in left sidebar (or go to https://cloud.digitalocean.com/settings/api/tokens)
3. Click **Generate New Token**
4. Enter token details:
   - **Token Name**: `todo-app-cli` (or descriptive name)
   - **Expiration**: No Expiration (for development) or set a date
5. Click **Generate Token**
6. **COPY THE TOKEN IMMEDIATELY** - it won't be shown again!
7. Save it securely (password manager or environment variable)

```bash
# Export as environment variable
export DIGITALOCEAN_ACCESS_TOKEN=your_token_here
```

---

## Phase 2: Install and Configure CLI Tools

### Step 2.1: Install doctl (DigitalOcean CLI)

**Windows (using PowerShell):**

```powershell
# Download latest doctl
Invoke-WebRequest -Uri "https://github.com/digitalocean/doctl/releases/download/v1.115.0/doctl-1.115.0-windows-amd64.zip" -OutFile "doctl.zip"

# Extract
Expand-Archive -Path doctl.zip -DestinationPath .

# Move to PATH (requires admin)
Move-Item doctl.exe "C:\Windows\System32\"

# Verify installation
doctl version
```

**Or use Chocolatey:**
```powershell
choco install doctl
```

**Linux/macOS:**
```bash
# Using curl
curl -sL https://github.com/digitalocean/doctl/releases/download/v1.115.0/doctl-1.115.0-linux-amd64.tar.gz | tar xz
sudo mv doctl /usr/local/bin/

# Using Homebrew (macOS/Linux)
brew install doctl

# Verify
doctl version
```

### Step 2.2: Authenticate doctl

```bash
# Authenticate with your API token
doctl auth init

# Paste your token when prompted

# Verify authentication
doctl account get

# You should see your account details
```

### Step 2.3: Install kubectl (if not already installed)

**Windows:**
```powershell
# Using Chocolatey
choco install kubernetes-cli

# Or download manually
# https://kubernetes.io/docs/tasks/tools/
```

**Linux:**
```bash
# Download latest kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify
kubectl version --client
```

**macOS:**
```bash
brew install kubectl
```

### Step 2.4: Install Helm 3 (if not already installed)

**Windows:**
```powershell
choco install kubernetes-helm
```

**Linux:**
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**macOS:**
```bash
brew install helm
```

**Verify Helm:**
```bash
helm version
```

---

## Phase 3: Create DigitalOcean Kubernetes Cluster (DOKS)

### Step 3.1: Choose Your Region

Available regions (choose closest to your users):
- `nyc1` - New York 1 (recommended for US East)
- `nyc3` - New York 3
- `sfo2` - San Francisco 2 (recommended for US West)
- `ams3` - Amsterdam 3 (recommended for Europe)
- `fra1` - Frankfurt 1
- `lon1` - London 1
- `sgp1` - Singapore 1
- `blr1` - Bangalore 1

### Step 3.2: Create DOKS Cluster

Using doctl CLI:

```bash
# Create cluster with 3 nodes
# Region: NYC1 (change if needed)
# Node size: s-4vcpu-8gb (4 CPUs, 8GB RAM)
# Auto-scaling: 2-5 nodes
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --version 1.29.2-do.0 \
  --node-pool "name=pool-1;size=s-4vcpu-8gb;count=3;auto-scale=true;min-nodes=2;max-nodes=5" \
  --maintenance-window "any=00:00-04:00" \
  --tag-name todo-app
```

**Expected Output:**
```
Notice: Cluster is being created, this can take a while ...
ID                                      12345678-1234-1234-1234-123456789012
Name                                    todo-cluster
Region                                  nyc1
Version                                 1.29.2-do.0
Status                                  provisioning
...
```

**Or Create via Web UI:**
1. Go to https://cloud.digitalocean.com/kubernetes
2. Click "Create Cluster"
3. Configure:
   - **Kubernetes Version**: Latest (1.29+)
   - **Region**: Choose nearest
   - **Node Plan**: Basic (General Purpose)
   - **Node Size**: $60/month (4GB RAM, 2 vCPUs) or $120/month (8GB RAM, 4 vCPUs)
   - **Number of Nodes**: 3
   - **Cluster Name**: todo-cluster
   - **Project**: (select or create new)
4. Click "Create Cluster"
5. Wait ~10-15 minutes for cluster to be ready

### Step 3.3: Get Cluster Kubeconfig

```bash
# Save kubeconfig to your machine
doctl kubernetes cluster kubeconfig save todo-cluster

# Verify you can connect to cluster
kubectl get nodes

# You should see 3 nodes with Ready status
# NAME                                STATUS   ROLES    AGE   VERSION
# pool-1-abc12-def34-5678-ghij        Ready    <none>   5m    v1.29.2
# pool-1-klm90-nop78-qrst-uvwx        Ready    <none>   5m    v1.29.2
# pool-1-yz12-ab34-cd56-ef78          Ready    <none>   5m    v1.29.2
```

### Step 3.4: Verify Cluster Health

```bash
# Check cluster info
kubectl cluster-info

# Check all system pods are running
kubectl get pods -n kube-system

# Check nodes
kubectl get nodes -o wide

# Check cluster capacity
kubectl top nodes
```

---

## Phase 4: Install Dapr Runtime

### Step 4.1: Install Dapr CLI

**Windows:**
```powershell
# Download Dapr CLI
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1" -OutFile "install.ps1"
./install.ps1

# Verify
dapr --version
```

**Linux/macOS:**
```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Verify
dapr --version
```

### Step 4.2: Initialize Dapr on Kubernetes

```bash
# Initialize Dapr in Kubernetes mode
dapr init --kubernetes

# Expected output:
# Deployment is already completed!
# Making the jump to hyperspace...
# Downloading binaries and setting up components...
# Success! Dapr is up and running.

# Verify Dapr pods are running
kubectl get pods -n dapr-system

# You should see:
# NAME                                     READY   STATUS    RESTARTS   AGE
# dapr-dashboard-7b6f7f8f9-x9k2l           1/1     Running   0          2m
# dapr-operator-7f9f8f7f8-abc12            1/1     Running   0          2m
# dapr-placement-7f9f8f7f8-xyz34           1/1     Running   0          2m
# dapr-sentry-7f9f8f7f8-def56              1/1     Running   0          2m
# dapr-sidecar-injector-7f9f8f7f8-ghi78   1/1     Running   0          2m
```

### Step 4.3: Install Dapr Dashboard (Optional but Recommended)

```bash
# The dashboard should already be installed from dapr init
# Access it via port-forward
kubectl port-forward -n dapr-system svc/dapr-dashboard 8080:8080

# Open browser to: http://localhost:8080
```

---

## Phase 5: Deploy Redpanda Cluster

### Step 5.1: Add Redpanda Helm Repository

```bash
# Add Redpanda Helm repo
helm repo add redpanda https://charts.redpanda.com
helm repo update

# Verify
helm search repo redpanda
```

### Step 5.2: Create Storage Class for Redpanda

Redpanda needs fast storage with direct I/O:

```bash
# Create a custom values file for Redpanda
cat > redpanda-values.yaml << 'EOF'
# Redpanda configuration for DOKS
replicas: 3

# Storage configuration
persistence:
  # Use DigitalOcean Block Storage
  storageClass: do-block-storage
  size: 50Gi
  # Number of partitions per disk
  partitions: 1

# Resource allocation
resources:
  requests:
    cpu: 2
    memory: 4Gi
  limits:
    cpu: 4
    memory: 8Gi

# Redpanda configuration
config:
  cluster:
    # Enable developer mode for smaller clusters
    developer_mode: true

# External access (optional, for external tools)
external:
  enabled: true

# Tolerations for running on control plane nodes (if needed)
tolerations: []
EOF
```

### Step 5.3: Install Redpanda

```bash
# Create namespace for Redpanda
kubectl create namespace redpanda-system

# Install Redpanda with custom values
helm install redpanda redpanda/redpanda \
  --namespace redpanda-system \
  --values redpanda-values.yaml \
  --timeout 15m

# Wait for Redpanda to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda -n redpanda-system --timeout=600s

# Check Redpanda pods
kubectl get pods -n redpanda-system

# You should see 3 Redpanda pods:
# NAME                        READY   STATUS    RESTARTS   AGE
# redpanda-0                  1/1     Running   0          3m
# redpanda-1                  1/1     Running   0          3m
# redpanda-2                  1/1     Running   0          3m
```

### Step 5.4: Create Kafka Topics

```bash
# Port-forward to Redpanda admin API
kubectl port-forward -n redpanda-system svc/redpanda 9644:9644

# In another terminal, create topics
# Or use rpk (Redpanda CLI) from within the pod

# Create topics using kubectl exec
kubectl exec -n redpanda-system redpanda-0 -- rpk topic create task-created --replicas 3
kubectl exec -n redpanda-system redpanda-0 -- rpk topic create task-updated --replicas 3
kubectl exec -n redpanda-system redpanda-0 -- rpk topic create task-completed --replicas 3
kubectl exec -n redpanda-system redpanda-0 -- rpk topic create task-deleted --replicas 3
kubectl exec -n redpanda-system redpanda-0 -- rpk topic create task-due-soon --replicas 3
kubectl exec -n redpanda-system redpanda-0 -- rpk topic create recurring-task-due --replicas 3

# List topics to verify
kubectl exec -n redpanda-system redpanda-0 -- rpk topic list

# Expected output:
# task-created
# task-updated
# task-completed
# task-deleted
# task-due-soon
# recurring-task-due
```

### Step 5.5: Get Redpanda Connection Details

```bash
# Get Redpanda service
kubectl get svc -n redpanda-system

# The internal Kafka broker URL will be:
# redpanda.redpanda-system.svc.cluster.local:9092

# Save this for Dapr configuration
echo "Redpanda Kafka Broker: redpanda.redpanda-system.svc.cluster.local:9092"
```

---

## Phase 6: Create DigitalOcean Managed Redis

### Step 6.1: Create Redis Database

```bash
# Create DO Managed Redis (Valkey)
doctl databases create todo-redis \
  --engine redis \
  --region nyc1 \
  --size 1gb \
  --num-nodes 1

# Note the output - it contains important connection info
# ID            12345678-1234-1234-1234-123456789012
# Name          todo-redis
# Engine        redis
# Version       7.2
# Connection    [details]
```

### Step 6.2: Get Redis Connection Details

```bash
# Get connection details as JSON
doctl databases connection todo-redis --format json > redis-connection.json

# Parse and export connection details
export REDIS_HOST=$(cat redis-connection.json | grep -o '"host":"[^"]*' | cut -d'"' -f4)
export REDIS_PORT=$(cat redis-connection.json | grep -o '"port":[0-9]*' | cut -d':' -f2)
export REDIS_PASSWORD=$(cat redis-connection.json | grep -o '"password":"[^"]*' | cut -d'"' -f4)
export REDIS_URI=$(cat redis-connection.json | grep -o '"uri":"[^"]*' | cut -d'"' -f4)

# Display connection info
echo "Redis Host: $REDIS_HOST"
echo "Redis Port: $REDIS_PORT"
echo "Redis URI: $REDIS_URI"

# Save for later use
cat > redis-env.txt << EOF
REDIS_HOST=$REDIS_HOST
REDIS_PORT=$REDIS_PORT
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_URI=$REDIS_URI
EOF
```

### Step 6.3: Test Redis Connection (Optional)

```bash
# Connect to Redis using redis-cli (if installed)
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD PING

# Should return: PONG
```

---

## Phase 7: Create DigitalOcean Container Registry

### Step 7.1: Create Container Registry

```bash
# Create container registry
doctl registry create

# Or create with specific name and region
doctl registry create --region nyc3

# Expected output:
# Name              registry.digitalocean.com
# Region            nyc3
# Created          2025-12-25 12:00:00 +0000 UTC
# Subscription Tier: Basic
```

### Step 7.2: Configure Docker Authentication

```bash
# Login to Docker registry
doctl registry login

# This configures Docker to authenticate with DO registry
# You can now push/pull images

# Verify login
docker pull registry.digitalocean.com
```

### Step 7.3: Create Registry Repository (Optional)

```bash
# Repositories are auto-created on first push
# But you can create manually
doctl registry repository create todo-app

# List repositories
doctl registry repository list
```

---

## Phase 8: Configure Kubernetes Secrets

### Step 8.1: Create Namespace for Application

```bash
# Create production namespace
kubectl create namespace production

# Or create development namespace
kubectl create namespace development
```

### Step 8.2: Create Database Secret

```bash
# For Neon PostgreSQL (external)
# Get your connection string from Neon console
export DATABASE_URL="postgresql://user:password@ep-cool-neon.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Create secret
kubectl create secret generic backend-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --namespace=production

# For DO Managed PostgreSQL (if using DO instead of Neon)
# kubectl create secret generic backend-secrets \
#   --from-literal=database-url="$DO_POSTGRES_URL" \
#   --namespace=production
```

### Step 8.3: Create Redis Secret

```bash
# Create Redis connection secret
kubectl create secret generic redis-secrets \
  --from-literal=redis-host="$REDIS_HOST" \
  --from-literal=redis-port="$REDIS_PORT" \
  --from-literal=redis-password="$REDIS_PASSWORD" \
  --namespace=production
```

### Step 8.4: Create Application Secrets

```bash
# Create JWT secret (generate a secure random string)
export JWT_SECRET=$(openssl rand -base64 32)

# Create other secrets
kubectl create secret generic app-secrets \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=groq-api-key="$GROQ_API_KEY" \
  --namespace=production

# Verify secrets
kubectl get secrets -n production
kubectl describe secret backend-secrets -n production
```

---

## Phase 9: Create Dapr Components

### Step 9.1: Create Pub/Sub Component (Redpanda)

Create file `k8s/dapr-components/pubsub-redpanda.yaml`:

```yaml
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
    - name: consumerGroup
      value: "todo-app"
    - name: authRequired
      value: "false"
    - name: maxMessageBytes
      value: "1024"
```

Apply the component:

```bash
# Create directory if needed
mkdir -p k8s/dapr-components

# Apply the component
kubectl apply -f k8s/dapr-components/pubsub-redpanda.yaml

# Verify component
kubectl get components -n production
```

### Step 9.2: Create State Store Component (Redis)

Create file `k8s/dapr-components/statestore-redis.yaml`:

```yaml
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
    - name: keyPrefix
      value: "todo"
```

Apply the component:

```bash
kubectl apply -f k8s/dapr-components/statestore-redis.yaml

# Verify
kubectl get components -n production
kubectl describe component todo-statestore -n production
```

---

## Phase 10: Configure Cloud Firewall

### Step 10.1: Create Cloud Firewall

```bash
# Create firewall for cluster
doctl compute firewall create todo-cluster-fw \
  --inbound-rules="protocol:tcp,ports:443,address:0.0.0.0/0,protocol:tcp,ports:80,address:0.0.0.0/0" \
  --outbound-rules="protocol:tcp,ports:all,address:0.0.0.0/0,protocol:udp,ports:53,address:0.0.0.0/0" \
  --tag-names=k8s,todo-cluster

# Note: Update tag-names based on your actual cluster tags
```

### Step 10.2: Apply Firewall to Cluster

```bash
# Get cluster ID
export CLUSTER_ID=$(doctl kubernetes cluster list | grep todo-cluster | awk '{print $1}')

# Apply firewall
doctl kubernetes cluster update $CLUSTER_ID --firewall todo-cluster-fw
```

---

## Verification Checklist

After completing all phases, verify your infrastructure:

### Cluster Status
```bash
# Check all nodes are ready
kubectl get nodes

# Expected: 3 nodes with Ready status
```

### Dapr Status
```bash
# Check Dapr pods
kubectl get pods -n dapr-system

# Expected: 5 Dapr pods running
```

### Redpanda Status
```bash
# Check Redpanda pods
kubectl get pods -n redpanda-system

# Expected: 3 Redpanda pods running
```

### Components Status
```bash
# Check Dapr components
kubectl get components -n production

# Expected: 2 components (pubsub, statestore)
```

### Secrets Status
```bash
# Check secrets
kubectl get secrets -n production

# Expected: backend-secrets, redis-secrets, app-secrets
```

### Redis Status
```bash
# Check Redis database
doctl databases get todo-redis

# Expected: Status: online
```

---

## Cost Breakdown

| Resource | Quantity | Unit Cost | Monthly Cost |
|----------|----------|-----------|--------------|
| DOKS Nodes (s-4vcpu-8gb) | 3 | $40 | $120 |
| Load Balancers | 3 | $12 | $36 |
| Managed Redis (1GB) | 1 | $15 | $15 |
| Block Storage (50GB × 3) | 150GB | $0.10/GB | $15 |
| Container Registry | 5GB | $0.02/GB | ~$1 |
| Bandwidth | Included | - | $0 |
| **Total** | | | **~$187/month** |

**Note**: With $200 new account credit, you have ~1 month free.
You can reduce costs by:
- Using 2GB RAM nodes instead of 8GB (~$60/month savings)
- Running 2 nodes instead of 3 (~$40/month savings)
- Minimized during development

---

## Next Steps

Once infrastructure is ready:

1. **Build Docker images** for frontend, backend, and notification service
2. **Push images** to DO Container Registry
3. **Update Helm values** with DO-specific configuration
4. **Deploy applications** to production namespace
5. **Configure Load Balancers** for external access
6. **Test end-to-end** connectivity
7. **Set up CI/CD** pipeline

Proceed to [application deployment guide](./APPLICATION_DEPLOYMENT.md) for next steps.

---

## Troubleshooting

### Cluster Won't Create
- Check account has sufficient credits
- Try different region
- Verify node size is available

### Redpanda Pods CrashLoopBackOff
- Check storage class exists: `kubectl get storageclass`
- Verify block storage quota
- Check logs: `kubectl logs -n redpanda-system redpanda-0`

### Dapr Sidecar Not Injecting
- Verify Dapr installed: `kubectl get pods -n dapr-system`
- Check namespace label: `kubectl describe namespace production`
- Manually add label: `kubectl label namespace production dapr.io/enabled=true`

### Redis Connection Failed
- Verify secret exists: `kubectl get secret redis-secrets -n production`
- Check firewall allows Redis port
- Test connection: `redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD PING`

### Can't Access Load Balancer
- Wait 5-10 minutes for DO LB to provision
- Check service type is LoadBalancer
- Verify via doctl: `doctl compute load-balancer list`

---

## Clean Up (if needed)

To delete all infrastructure and stop billing:

```bash
# Delete all deployments
kubectl delete namespace production

# Delete Dapr (optional)
dapr uninstall --kubernetes

# Delete Redpanda
helm uninstall redpanda --namespace redpanda-system
kubectl delete namespace redpanda-system

# Delete cluster
doctl kubernetes cluster delete todo-cluster

# Delete Redis
doctl databases delete todo-redis

# Delete registry
doctl registry delete

# Delete firewall
doctl compute firewall delete todo-cluster-fw
```

**WARNING**: This will delete ALL resources and you will lose all data!

---

## Support and Documentation

- [DigitalOcean Documentation](https://docs.digitalocean.com/)
- [Dapr Documentation](https://dapr.io/docs/)
- [Redpanda Documentation](https://docs.redpanda.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)

---

**Last Updated**: 2025-12-25
**Version**: 1.0
