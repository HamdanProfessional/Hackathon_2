# DigitalOcean Deployment Quick Reference

Quick cheat sheet for common DigitalOcean deployment commands and patterns.

## doctl Commands

### Authentication
```bash
# Authenticate
doctl auth init

# Check current user
doctl account get

# List authentication tokens
doctl auth tokens
```

### Kubernetes (DOKS)
```bash
# List clusters
doctl kubernetes cluster list

# Create cluster
doctl kubernetes cluster create my-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 3 \
  --version latest \
  --auto-upgrade \
  --maintenance-window "sun=02:00"

# Get cluster details
doctl kubernetes cluster get my-cluster

# Get kubeconfig
doctl kubernetes cluster kubeconfig save my-cluster

# Delete cluster
doctl kubernetes cluster delete my-cluster

# Create node pool
doctl kubernetes cluster node-pool create my-cluster \
  --name pool-2 \
  --size s-4vcpu-8gb \
  --count 2 \
  --auto-scale \
  --min-nodes 2 \
  --max-nodes 5

# Update node pool
doctl kubernetes cluster node-pool update my-cluster pool-2 \
  --count 3

# Get cluster upgrade info
doctl kubernetes cluster upgrades get my-cluster

# Trigger cluster upgrade
doctl kubernetes cluster upgrade upgrade my-cluster \
  --version latest
```

### App Platform
```bash
# List apps
doctl apps list

# Create app from spec
doctl apps create --spec app.yaml

# Update app
doctl apps update $APP_ID --spec app.yaml

# Get app details
doctl apps get $APP_ID

# List deployments
doctl apps list-deployments $APP_ID

# Get deployment logs
doctl apps logs $APP_ID --deployment $DEPLOYMENT_ID --type build --follow

# Delete app
doctl apps delete $APP_ID

# Propagate configuration
doctl apps create-spec --spec app.yaml
```

### Spaces
```bash
# List spaces
doctl spaces list

# Create spaces
doctl spaces create my-assets --region nyc3

# List buckets
doctl spaces list-buckets my-assets

# Enable CDN
doctl spaces cdn create my-assets --ttl 3600

# Set custom domain
doctl spaces cdn set-custom-domain my-assets \
  --cdn-endpoint my-assets.nyc3.cdn.digitaloceanspaces.com \
  --custom-domain cdn.example.com

# Delete spaces
doctl spaces delete my-assets
```

### Droplets
```bash
# List droplets
doctl compute droplet list

# Create droplet
doctl compute droplet create my-droplet \
  --region nyc1 \
  --size s-1vcpu-1gb \
  --image ubuntu-22-04-x64 \
  --ssh-keys $SSH_KEY_FINGERPRINT \
  --enable-ipv6 \
  --enable-monitoring

# Get droplet details
doctl compute droplet get $DROPLET_ID

# SSH into droplet
doctl compute droplet ssh $DROPLET_ID

# Take snapshot
doctl compute droplet snapshots $DROPLET_ID \
  --snapshot-name my-snapshot

# Delete droplet
doctl compute droplet delete $DROPLET_ID
```

### Load Balancers
```bash
# List load balancers
doctl compute load-balancer list

# Create load balancer
doctl compute load-balancer create my-lb \
  --region nyc1 \
  --algorithm round_robin \
  --forwarding-rules="entry_protocol:tcp,entry_port:80,target_protocol:tcp,target_port:8080" \
  --health-check="protocol:tcp,port:8080,path:/health" \
  --droplet-ids $DROPLET_ID1,$DROPLET_ID2

# Add droplets to LB
doctl compute load-balancer add-droplets $LB_ID $DROPLET_ID1 $DROPLET_ID2

# Remove droplets from LB
doctl compute load-balancer remove-droplets $LB_ID $DROPLET_ID1

# Delete load balancer
doctl compute load-balancer delete $LB_ID
```

### Databases
```bash
# List databases
doctl databases list

# Create database
doctl databases create my-db \
  --engine pg \
  --version 15 \
  --size db-s-1vcpu-1gb \
  --region nyc1 \
  --num-nodes 1

# Get connection info
doctl databases connection $DATABASE_ID

# List backups
doctl databases backups $DATABASE_ID

# Create read-only replica
doctl databases replica create $DATABASE_ID \
  --region nyc1 \
  --size db-s-1vcpu-1gb

# Delete database
doctl databases delete $DATABASE_ID
```

### Firewalls
```bash
# List firewalls
doctl compute firewall list

# Create firewall
doctl compute firewall create my-firewall \
  --inbound-rules="protocol:tcp,ports:22,sources:0.0.0.0/0" \
  --inbound-rules="protocol:tcp,ports:80,sources:0.0.0.0/0" \
  --inbound-rules="protocol:tcp,ports:443,sources:0.0.0.0/0" \
  --outbound-rules="protocol:tcp,ports:all,destinations:0.0.0.0/0"

# Add droplets to firewall
doctl compute firewall add-droplets $FIREWALL_ID $DROPLET_ID1 $DROPLET_ID2

# Remove droplets from firewall
doctl compute firewall remove-droplets $FIREWALL_ID $DROPLET_ID1

# Delete firewall
doctl compute firewall delete $FIREWALL_ID
```

### Volumes
```bash
# List volumes
doctl compute volume list

# Create volume
doctl compute volume create my-volume \
  --region nyc1 \
  --size 10G \
  --fs-type ext4

# Attach volume
doctl compute volume attach $VOLUME_ID $DROPLET_ID

# Detach volume
doctl compute volume detach $VOLUME_ID

# Take snapshot
doctl compute volume snapshot $VOLUME_ID \
  --snapshot-name my-snapshot

# Delete volume
doctl compute volume delete $VOLUME_ID
```

### Certificates
```bash
# List certificates
doctl compute certificate list

# Create Let's Encrypt certificate
doctl compute certificate create my-cert \
  --type lets_encrypt \
  --dns-names example.com,www.example.com \
  --leaf-certificate-space

# Upload custom certificate
doctl compute certificate create my-cert \
  --type custom \
  --private-key-path /path/to/key.pem \
  --certificate-chain-path /path/to/cert.pem \
  --dns-names example.com

# Delete certificate
doctl compute certificate delete $CERT_ID
```

---

## kubectl Commands (DOKS)

### Basic Operations
```bash
# Get nodes
kubectl get nodes

# Get all resources
kubectl get all

# Get pods
kubectl get pods

# Get services
kubectl get services

# Get deployments
kubectl get deployments

# Describe resource
kubectl describe pod $POD_NAME

# Get logs
kubectl logs $POD_NAME

# Follow logs
kubectl logs -f $POD_NAME

# Execute command in pod
kubectl exec -it $POD_NAME -- /bin/bash

# Port forward
kubectl port-forward $POD_NAME 8080:80
```

### Deployment
```bash
# Apply manifest
kubectl apply -f deployment.yaml

# Update deployment image
kubectl set image deployment/my-app my-app=my-app:v2

# Rollout restart
kubectl rollout restart deployment/my-app

# Rollout status
kubectl rollout status deployment/my-app

# Rollback
kubectl rollout undo deployment/my-app

# Scale deployment
kubectl scale deployment/my-app --replicas=5
```

### Namespace Operations
```bash
# Create namespace
kubectl create namespace my-app

# Set default namespace
kubectl config set-context --current --namespace=my-app

# Get resources in namespace
kubectl get all -n my-app
```

### Secrets
```bash
# Create secret from literals
kubectl create secret generic my-secret \
  --from-literal=password=mypassword \
  --namespace=my-app

# Create secret from file
kubectl create secret generic tls-cert \
  --cert=/path/to/cert.pem \
  --key=/path/to/key.pem

# Get secret
kubectl get secret my-secret -o yaml

# Decode secret
kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 -d
```

---

## Terraform Patterns

### Provider Setup
```hcl
terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}
```

### Resource Naming
```hcl
resource "digitalocean_droplet" "web" {
  name  = "${var.project_name}-web-${var.environment}"
  # ...
}
```

### Output Values
```hcl
output "droplet_ip" {
  value = digitalocean_droplet.web.ipv4_address
}

output "kubeconfig" {
  value     = digitalocean_kubernetes_cluster.my.kube_config[0].raw_config
  sensitive = true
}
```

### Data Sources
```hcl
data "digitalocean_kubernetes_cluster" "existing" {
  name = var.cluster_name
}

data "digitalocean_image" "ubuntu" {
  slug = "ubuntu-22-04-x64"
}
```

---

## Common Workflows

### Deploy to DOKS
```bash
# 1. Get kubeconfig
doctl kubernetes cluster kubeconfig save my-cluster

# 2. Verify connection
kubectl cluster-info

# 3. Deploy manifests
kubectl apply -f k8s/

# 4. Wait for rollout
kubectl rollout status deployment/backend

# 5. Get logs
kubectl logs -l app=backend --tail=100 -f
```

### Deploy to App Platform
```bash
# 1. Create app spec
cat > app.yaml << EOF
name: my-app
region: nyc3
services:
- name: web
  github:
    repo: username/repo
    branch: main
  dockerfile_path: Dockerfile
  instance_count: 2
EOF

# 2. Deploy
doctl apps create --spec app.yaml

# 3. Wait for deployment
doctl apps wait-for-deployment $APP_ID

# 4. Get URL
doctl apps get $APP_ID --format URL --no-header
```

### Deploy to Spaces CDN
```bash
# 1. Configure AWS CLI for Spaces
export AWS_ACCESS_KEY_ID=$SPACES_KEY
export AWS_SECRET_ACCESS_KEY=$SPACES_SECRET

# 2. Sync assets
aws s3 sync ./build s3://my-assets \
  --endpoint=https://nyc3.digitaloceanspaces.com \
  --acl public-read \
  --cache-control "public, max-age=31536000"

# 3. Enable CDN
doctl spaces cdn create my-assets --ttl 3600
```

---

## Environment Variables

### Common Variables
```bash
# DigitalOcean
export DIGITALOCEAN_TOKEN="dop_v1_xxxxx"

# Spaces
export SPACES_ACCESS_KEY="DO00xxxxx"
export SPACES_SECRET_KEY="xxxxx/xxxxx"
export SPACES_ENDPOINT="https://nyc3.digitaloceanspaces.com"

# App Platform
export APP_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Database
export DATABASE_HOST="xxx.db.ondigitalocean.com"
export DATABASE_PORT="25060"
export DATABASE_NAME="defaultdb"
export DATABASE_USER="doadmin"
export DATABASE_PASSWORD="xxxxx"
```

---

## Troubleshooting

### DOKS
```bash
# Check cluster status
doctl kubernetes cluster get my-cluster

# Check node status
kubectl get nodes -o wide

# Check pods not running
kubectl get pods --all-namespaces --field-selector=status.phase!=Running

# Describe pod
kubectl describe pod $POD_NAME

# Get node logs
doctl kubernetes cluster logs my-cluster

# Restart node
doctl kubernetes node delete $NODE_ID --dangerous
```

### App Platform
```bash
# Check app status
doctl apps get $APP_ID

# View logs
doctl apps logs $APP_ID --type build --follow

# Check deployment
doctl apps list-deployments $APP_ID

# Rebuild app
doctl apps update $APP_ID --force-rebuild
```

### Load Balancer
```bash
# Check LB status
doctl compute load-balancer get $LB_ID

# List droplets
doctl compute load-balancer list-droplets $LB_ID

# Check health checks
doctl compute load-balancer get $LB_ID --format HealthCheck --no-header
```

### Database
```bash
# Check cluster status
doctl databases get $DATABASE_ID

# Get connection info
doctl databases connection $DATABASE_ID

# View maintenance window
doctl databases get $DATABASE_ID --format MaintenanceWindow --no-header
```

---

## Pricing References

### Droplet Sizes (Common)
- `s-1vcpu-1gb`: $6/month
- `s-2vcpu-4gb`: $24/month
- `s-4vcpu-8gb`: $48/month
- `c-2-4gb`: $40/month (compute optimized)
- `m-2vcpu-8gb`: $60/month (memory optimized)

### Kubernetes Nodes
- `basic-2xx`: $10/month
- `basic-4xx`: $40/month
- `basic-8xx`: $80/month

### Database Sizes
- `db-s-1vcpu-1gb`: $15/month
- `db-s-2vcpu-4gb`: $60/month
- `db-s-4vcpu-8gb`: $120/month

### Load Balancers
- Starting at $12/month

### Spaces + CDN
- Storage: $0.02/GB/month
- CDN: $0.01/GB (first 10TB free with some plans)
