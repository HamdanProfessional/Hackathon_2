# DigitalOcean Kubernetes Cluster (DOKS) Example

This example demonstrates how to deploy a complete production-ready Kubernetes cluster on DigitalOcean with:

- Multi-node-pool DOKS cluster with auto-scaling
- Managed PostgreSQL database
- DigitalOcean Load Balancer
- Spaces object storage with CDN
- Nginx Ingress Controller with TLS
- Cert-Manager for automatic SSL certificates
- Sample application deployment (backend + frontend)
- Horizontal Pod Autoscaling
- Monitoring with Prometheus and Grafana
- Network policies for security

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DigitalOcean Load Balancer              │
│                      (LB-1vcpu-1)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Kubernetes Cluster (DOKS)                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Ingress Controller (Nginx)                  │    │
│  │         - TLS Termination                          │    │
│  │         - Routing                                   │    │
│  └────────────┬───────────────────────────────────────┘    │
│               │                                             │
│  ┌────────────▼───────────────────────────────────────┐    │
│  │              Application Pods                       │    │
│  │  ┌──────────────────────────────────────────────┐ │    │
│  │  │  Backend (FastAPI) - 2+ pods, HPA enabled    │ │    │
│  │  └──────────────────────────────────────────────┘ │    │
│  │  ┌──────────────────────────────────────────────┐ │    │
│  │  │  Frontend (Next.js) - 2+ pods, HPA enabled  │ │    │
│  │  └──────────────────────────────────────────────┘ │    │
│  │  ┌──────────────────────────────────────────────┐ │    │
│  │  │  Worker - Background jobs                    │ │    │
│  │  └──────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Node Pools                             │  │
│  │  - General Pool: s-2vcpu-4gb (1-5 nodes)           │  │
│  │  - Database Pool: s-4vcpu-16gb (1-3 nodes)         │  │
│  │  - GPU Pool: gpu-2x-4x (0-2 nodes, optional)      │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              DigitalOcean Managed Services                  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  PostgreSQL Database (db-s-2vcpu-4gb)              │  │
│  │  - HA configuration                                │  │
│  │  - Automatic backups                               │  │
│  │  - Private network connection                      │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Spaces Object Storage + CDN                       │  │
│  │  - Static assets                                   │  │
│  │  - Global CDN distribution                         │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **DigitalOcean Account**
   - Sign up at: https://cloud.digitalocean.com
   - Generate API token with Read & Write permissions

2. **doctl CLI**
   ```bash
   # macOS
   brew install doctl

   # Linux
   curl -sL https://github.com/digitalocean/doctl/releases/latest/download/doctl-linux-amd64.tar.gz | tar xz
   sudo mv doctl /usr/local/bin/

   # Windows
   choco install doctl

   # Verify installation
   doctl version
   ```

3. **kubectl CLI**
   ```bash
   # macOS
   brew install kubectl

   # Linux
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

   # Windows
   choco install kubernetes-cli

   # Verify installation
   kubectl version --client
   ```

4. **Terraform**
   ```bash
   # macOS
   brew install terraform

   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/

   # Windows
   choco install terraform

   # Verify installation
   terraform version
   ```

5. **Helm (for Ingress Controller and Cert-Manager)**
   ```bash
   # macOS
   brew install helm

   # Linux
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

   # Windows
   choco install kubernetes-helm

   # Verify installation
   helm version
   ```

## Quick Start

### 1. Clone and Configure

```bash
# Navigate to the example directory
cd .claude/skills/cloud-deployer/examples/terraform/kubernetes-cluster

# Copy the example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars and fill in your values
# Required: do_token
# Optional: Customize other variables as needed
nano terraform.tfvars
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Review the Plan

```bash
terraform plan
```

This will show you what resources will be created. Review carefully before applying.

### 4. Deploy the Infrastructure

```bash
terraform apply
```

Type `yes` when prompted to confirm.

### 5. Configure kubectl

Terraform will create a kubeconfig file. Use one of these methods:

**Option A: Use the generated kubeconfig**
```bash
export KUBECONFIG=$(pwd)/kubeconfig_todo-app
```

**Option B: Use doctl**
```bash
doctl kubernetes cluster kubeconfig save <cluster-id-from-terraform-output>
```

**Option C: Merge with existing kubeconfig**
```bash
export KUBECONFIG=$(pwd)/kubeconfig_todo-app:$HOME/.kube/config
```

### 6. Verify Cluster Connection

```bash
kubectl cluster-info
kubectl get nodes
```

You should see your node pools with the configured number of nodes.

### 7. Deploy the Application

```bash
# Apply all manifests in order
kubectl apply -f manifests/00-namespace.yaml
kubectl apply -f manifests/01-configmap.yaml
kubectl apply -f manifests/02-secrets.yaml

# IMPORTANT: Update secrets with real values from Terraform outputs
terraform output -raw database_private_uri
# Use this value to update the do-db-connection secret

kubectl apply -f manifests/10-deployment.yaml
kubectl apply -f manifests/20-service.yaml
kubectl apply -f manifests/30-ingress.yaml
kubectl apply -f manifests/40-scaling.yaml
kubectl apply -f manifests/50-monitoring.yaml
```

### 8. Update Secrets

After Terraform completes, you need to update the Kubernetes secrets with real values:

```bash
# Get database connection details
DB_HOST=$(terraform output -raw database_private_host)
DB_PORT=$(terraform output -raw database_port)
DB_NAME=$(terraform output -raw database_name)
DB_USER=$(terraform output -raw database_user)
DB_PASSWORD=$(terraform output -raw database_password)

# Create secret with real database credentials
kubectl create secret generic do-db-connection -n todo-app \
  --from-literal=host="$DB_HOST" \
  --from-literal=port="$DB_PORT" \
  --from-literal=database="$DB_NAME" \
  --from-literal=username="$DB_USER" \
  --from-literal=password="$DB_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

# Update application secrets
kubectl create secret generic app-secrets -n todo-app \
  --from-literal=JWT_SECRET="$(openssl rand -base64 32)" \
  --from-literal=DB_PASSWORD="$DB_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 9. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check ingress
kubectl get ingress -n todo-app

# Check HPA status
kubectl get hpa -n todo-app

# Check certificate status
kubectl get certificate -n todo-app
```

### 10. Access Your Application

Get the load balancer IP:

```bash
terraform output load_balancer_ip
```

Or the application URL:

```bash
terraform output load_balancer_url
```

## Configuration Options

### Main Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `do_token` | DigitalOcean API token | *Required* |
| `project_name` | Project name for resources | `todo-app` |
| `environment` | Environment (production/staging/development) | `production` |
| `region` | DOKS region | `nyc1` |
| `kubernetes_version` | Kubernetes version | `1.28.2-do.0` |

### Node Pool Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `default_node_size` | Droplet size for general pool | `s-2vcpu-4gb` |
| `default_node_count` | Initial nodes in general pool | `2` |
| `min_nodes` | Minimum nodes for auto-scaling | `1` |
| `max_nodes` | Maximum nodes for auto-scaling | `5` |
| `database_node_size` | Droplet size for DB pool | `s-4vcpu-16gb` |
| `enable_gpu_nodes` | Enable GPU node pool | `false` |

### Database Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `postgres_version` | PostgreSQL version | `16` |
| `db_size` | Database droplet size | `db-s-2vcpu-4gb` |
| `db_node_count` | Number of DB nodes | `2` |
| `db_ha_enabled` | Enable HA for database | `true` |
| `db_backup_retention_days` | Backup retention period | `7` |

### Spaces Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `spaces_region` | Spaces region | `nyc3` |
| `spaces_cdn_enabled` | Enable CDN for Spaces | `true` |
| `spaces_cors_origins` | Allowed CORS origins | List of domains |

## Monitoring and Observability

### Access Grafana

```bash
# Port forward to access Grafana locally
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Open browser to http://localhost:3000
# Default credentials: admin / admin (change in production!)
```

### Access Prometheus

```bash
# Port forward to access Prometheus locally
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Open browser to http://localhost:9090
```

### View Metrics

```bash
# Get pod metrics
kubectl top pods -n todo-app

# Get node metrics
kubectl top nodes
```

## Scaling

### Horizontal Pod Autoscaling

HPA is configured to automatically scale pods based on CPU and memory usage:

```bash
# View HPA status
kubectl get hpa -n todo-app

# Edit HPA
kubectl edit hpa backend-hpa -n todo-app
```

### Cluster Autoscaling

Node pools are configured with auto-scaling enabled. The cluster will automatically add or remove nodes based on pod resource requests.

```bash
# View node pool status
doctl kubernetes cluster node-pool list <cluster-id>

# Manually resize a node pool
doctl kubernetes cluster node-pool update <cluster-id> <pool-id> --count 3
```

## Troubleshooting

### Common Issues

**1. Pods stuck in Pending state**
```bash
# Describe the pod to see why it's pending
kubectl describe pod <pod-name> -n todo-app

# Check node resources
kubectl top nodes

# Check cluster autoscaler logs
kubectl logs -n kube-system deployment/cluster-autoscaler
```

**2. TLS certificate not issuing**
```bash
# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Check certificate status
kubectl describe certificate app-cert -n todo-app

# Check challenge status
kubectl get challenge -n todo-app
```

**3. Database connection issues**
```bash
# Verify database is accessible
kubectl run -it --rm debug --image=postgres:16 --restart=Never -n todo-app -- \
  psql $DB_URI -c "SELECT 1;"

# Check secrets
kubectl describe secret do-db-connection -n todo-app

# Check network policies
kubectl get networkpolicy -n todo-app
```

**4. High memory/CPU usage**
```bash
# View resource usage
kubectl top pods -n todo-app --containers

# Check resource limits
kubectl describe deployment backend -n todo-app | grep -A 5 Resources

# View HPA metrics
kubectl describe hpa backend-hpa -n todo-app
```

### Useful Commands

```bash
# Get all resources in namespace
kubectl get all -n todo-app

# Watch pod status
kubectl get pods -n todo-app -w

# View pod logs
kubectl logs -f deployment/backend -n todo-app

# Execute command in pod
kubectl exec -it deployment/backend -n todo-app -- /bin/bash

# Port forward to service
kubectl port-forward -n todo-app svc/backend 8000:8000

# Get events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Describe resource
kubectl describe deployment backend -n todo-app
```

## Cleanup

### Remove Application

```bash
# Delete all manifests
kubectl delete -f manifests/50-monitoring.yaml
kubectl delete -f manifests/40-scaling.yaml
kubectl delete -f manifests/30-ingress.yaml
kubectl delete -f manifests/20-service.yaml
kubectl delete -f manifests/10-deployment.yaml
kubectl delete -f manifests/02-secrets.yaml
kubectl delete -f manifests/01-configmap.yaml
kubectl delete -f manifests/00-namespace.yaml
```

### Destroy Infrastructure

```bash
terraform destroy
```

Type `yes` when prompted to confirm. This will remove:
- Kubernetes cluster
- Load balancer
- Database
- Spaces bucket
- VPC
- Project

**Note**: This will delete ALL data in the database and Spaces bucket. Ensure you have backups if needed.

## Cost Estimation

Based on default configuration in `nyc1` region:

| Resource | Quantity | Cost/hr | Cost/month |
|----------|----------|---------|------------|
| Kubernetes control plane | 1 | $0.020 | ~$15 |
| General nodes (s-2vcpu-4gb) | 2 avg | $0.060 | ~$45 |
| Database nodes (s-4vcpu-16gb) | 2 | $0.224 | ~$168 |
| Load Balancer | 1 | $0.020 | ~$15 |
| Spaces (with CDN) | 1 | Varies | ~$5-20 |
| **Total** | | | **~$248-263/month** |

**Cost savings tips**:
- Reduce database node count to 1 for non-critical workloads (saves ~$84/month)
- Use smaller droplet sizes in development
- Delete cluster when not in use
- Use Spot instances when available

## Production Checklist

Before going to production:

- [ ] Set strong passwords and secrets
- [ ] Enable database backups with appropriate retention
- [ ] Configure DNS for custom domains
- [ ] Set up monitoring alerts (Grafana)
- [ ] Configure log aggregation (Loki/ELK)
- [ ] Set up CI/CD pipeline
- [ ] Enable pod disruption budgets
- [ ] Configure resource quotas
- [ ] Set up network policies
- [ ] Enable audit logging
- [ ] Implement disaster recovery plan
- [ ] Document runbooks
- [ ] Configure cost monitoring
- [ ] Set up automated database backups
- [ ] Test failover procedures

## Further Reading

- [DigitalOcean Kubernetes Documentation](https://docs.digitalocean.com/products/kubernetes/)
- [DOKS Scaling Guide](https://docs.digitalocean.com/products/kubernetes/how-to/scale-cluster-nodes/)
- [Terraform DigitalOcean Provider](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Cert-Manager](https://cert-manager.io/)
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)

## Support

For issues or questions:
- DigitalOcean Community: https://www.digitalocean.com/community
- Kubernetes Slack: https://kubernetes.slack.com/
- Terraform Forums: https://discuss.hashicorp.com/
