# DigitalOcean Load Balancer with Multiple Droplets

This example demonstrates a high-availability web application setup with multiple droplets behind a DigitalOcean Load Balancer.

## Architecture

```
                            ┌─────────────────────────┐
                            │  DigitalOcean Load     │
                            │  Balancer              │
                            │  - SSL Termination     │
                            │  - Health Checks       │
                            │  - Sticky Sessions     │
                            └───────────┬─────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
            ┌───────▼────────┐  ┌──────▼────────┐  ┌──────▼────────┐
            │  Web Server 1  │  │  Web Server 2 │  │  Web Server 3 │
            │  (Ubuntu)      │  │  (Ubuntu)     │  │  (Ubuntu)     │
            │  - FastAPI     │  │  - FastAPI    │  │  - FastAPI    │
            │  - Nginx       │  │  - Nginx      │  │  - Nginx      │
            └───────┬────────┘  └──────┬────────┘  └──────┬────────┘
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
            ┌───────▼────────┐                  ┌───────────▼────────┐
            │  PostgreSQL    │                  │  Redis (Optional)  │
            │  (Managed)     │                  │  (Managed)         │
            │  - HA Enabled  │                  │                    │
            └────────────────┘                  └────────────────────┘
```

## Features

- **High Availability**: Multiple droplets with automatic failover
- **Load Balancing**: Distribution of traffic across all droplets
- **Health Checks**: Automatic detection and removal of unhealthy instances
- **SSL Termination**: HTTPS handled at the load balancer level
- **Managed Database**: PostgreSQL with high availability
- **Optional Redis**: Managed Redis for caching and sessions
- **Cloud Firewall**: Security rules to restrict access
- **Sticky Sessions**: Session affinity for stateful applications
- **Private Networking**: VPC for secure internal communication

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

   # Verify installation
   doctl version
   ```

3. **Terraform**
   ```bash
   # macOS
   brew install terraform

   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/

   # Verify installation
   terraform version
   ```

4. **SSH Key Pair**
   ```bash
   # Generate if you don't have one
   ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

   # Copy public key path for terraform.tfvars
   cat ~/.ssh/id_rsa.pub
   ```

## Quick Start

### 1. Configure

```bash
# Navigate to the example directory
cd .claude/skills/cloud-deployer/examples/terraform/load-balancer

# Copy the example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars
# Required: do_token
# Optional: Customize other variables
nano terraform.tfvars
```

### 2. Deploy

```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

Type `yes` when prompted to confirm.

### 3. Test

After deployment completes, test the application:

```bash
# Get the load balancer IP
terraform output load_balancer_ip

# Test health endpoint
curl http://$(terraform output -raw load_balancer_ip)/health

# Test root endpoint
curl http://$(terraform output -raw load_balancer_ip)

# Test multiple requests (you'll see different servers responding)
for i in {1..10}; do
  curl http://$(terraform output -raw load_balancer_ip)/
  echo ""
done
```

### 4. Access Droplets

```bash
# SSH to a specific droplet
ssh root@$(terraform output -raw droplet_ips | grep -o '[0-9.]*' | head -1)

# Or use the provided SSH commands
terraform output ssh_commands
```

## Configuration Options

### Main Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `do_token` | DigitalOcean API token | *Required* |
| `project_name` | Project name for resources | `todo-app` |
| `droplet_count` | Number of web server droplets | `2` |
| `droplet_size` | Droplet size slug | `s-2vcpu-4gb` |
| `region` | DigitalOcean region | `nyc1` |

### Database Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `postgres_version` | PostgreSQL version | `16` |
| `db_size` | Database size | `db-s-2vcpu-4gb` |
| `db_node_count` | Number of DB nodes (1-3) | `2` |
| `db_ha_enabled` | Enable HA for database | `true` |

### Load Balancer Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `redirect_http_to_https` | Redirect HTTP to HTTPS | `true` |

## How It Works

### Health Checks

The load balancer performs health checks on all droplets:

```yaml
health_check:
  protocol: http
  port: 80
  path: /health
  check_interval: 10 seconds
  unhealthy_threshold: 3 failures
  healthy_threshold: 5 successes
```

If a droplet fails 3 consecutive health checks, it's removed from the rotation. Once it passes 5 consecutive checks, it's added back.

### Sticky Sessions

Session affinity is enabled using cookies:

```yaml
sticky_sessions:
  type: cookies
  cookie_name: DO_LB_STICKY
  cookie_ttl_seconds: 3600
```

This ensures that a client's requests are always sent to the same droplet during the session.

### SSL/TLS Termination

The load balancer handles SSL/TLS termination:

1. Client → LB: HTTPS connection
2. LB → Droplet: HTTP connection (or you can enable end-to-end HTTPS)

```yaml
forwarding_rule:
  entry_port: 443
  entry_protocol: https
  target_port: 80
  target_protocol: http
```

### Cloud Firewall

Security rules restrict access:

```yaml
inbound_rules:
  - port: 22
    source: Your IP only
  - port: 80
    source: Anywhere
  - port: 443
    source: Anywhere
```

## Testing

### Test Load Distribution

```bash
# Make 100 requests and count which servers responded
for i in {1..100}; do
  curl -s http://$(terraform output -raw load_balancer_ip)/info | grep -o '"server": "[^"]*"'
done | sort | uniq -c
```

Expected output (with 2 droplets):
```
50 "server": "todo-app-web-1"
50 "server": "todo-app-web-2"
```

### Test Health Checks

```bash
# Kill the application on one droplet
doctl compute droplet ssh <droplet-id> --command "systemctl stop app"

# Wait 30 seconds for health checks to fail

# Verify load balancer redirects to remaining droplets
curl http://$(terraform output -raw load_balancer_ip)/health

# Start the application again
doctl compute droplet ssh <droplet-id> --command "systemctl start app"

# Wait for health checks to pass and droplet to return to rotation
```

### Test Failover

```bash
# Destroy one droplet
terraform destroy -target=digitalocean_droplet.web[0]

# Verify application still responds
curl http://$(terraform output -raw load_balancer_ip)/health

# Recreate the droplet
terraform apply
```

## Monitoring

### View Load Balancer Stats

```bash
# Get load balancer details
doctl compute load-balancer get $(terraform output -raw load_balancer_id)

# List all load balancers
doctl compute load-balancer list
```

### View Droplet Status

```bash
# List droplets
doctl compute droplet list

# Get droplet details
doctl compute droplet get <droplet-id>

# View droplet metrics
doctl monitors droplet-bandwidth --help
```

### View Application Logs

```bash
# SSH to a droplet
ssh root@<droplet-ip>

# View application logs
sudo journalctl -u app -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Scaling

### Scale Up (Add Droplets)

```bash
# Update terraform.tfvars
droplet_count = 4

# Apply changes
terraform apply
```

The load balancer automatically detects and includes new droplets.

### Scale Down (Remove Droplets)

```bash
# Update terraform.tfvars
droplet_count = 2

# Apply changes
terraform apply
```

The load balancer automatically removes droplets from rotation.

### Resize Droplets

```bash
# Update droplet_size in terraform.tfvars
droplet_size = "s-4vcpu-8gb"

# Apply changes (requires recreation)
terraform apply -replace=digitalocean_droplet.web[0]
```

## Troubleshooting

### Load Balancer Not Responding

```bash
# Check load balancer status
doctl compute load-balancer get <lb-id>

# Check droplet health
curl http://<droplet-ip>/health

# Verify firewall rules
doctl compute firewall list
```

### Droplets Not in Rotation

```bash
# Check droplet status
doctl compute droplet list

# Check firewall allows LB traffic
doctl compute firewall get <fw-id>

# Verify droplet tag matches LB configuration
doctl compute droplet tags list <droplet-id>
```

### Database Connection Issues

```bash
# Test database connection from droplet
doctl compute droplet ssh <droplet-id> --command "psql -h <db-host> -U <db-user> -d <db-name>"

# Check database firewall rules
doctl databases firewalls list <db-id>

# Verify VPC configuration
doctl vpcs list
```

### 502 Bad Gateway

```bash
# Check application is running on droplets
doctl compute droplet ssh <droplet-id> --command "systemctl status app"

# Check Nginx configuration
doctl compute droplet ssh <droplet-id> --command "nginx -t"

# View application logs
doctl compute droplet ssh <droplet-id> --command "journalctl -u app -n 50"
```

## Cleanup

### Remove Application

```bash
# Destroy all resources
terraform destroy
```

This will remove:
- Load balancer
- All droplets
- Database cluster
- Redis cluster (if deployed)
- Firewall
- VPC
- Project
- DNS records (if created)
- Floating IP (if created)

## Cost Estimation

Based on default configuration in `nyc1` region:

| Resource | Quantity | Price/hr | Price/month |
|----------|----------|----------|-------------|
| Droplets (s-2vcpu-4gb) | 2 | $0.060 | ~$90 |
| Load Balancer | 1 | $0.020 | ~$15 |
| PostgreSQL (db-s-2vcpu-4gb) | 2 nodes | $0.140 | ~$210 |
| Redis (db-s-1vcpu-1gb) | 1 | $0.040 | ~$30 |
| Backups | 2 droplets | $0.007 | ~$10 |
| **Total** | | | **~$355/month** |

**Cost savings tips**:
- Reduce droplet count for non-critical workloads
- Use smaller droplet sizes in development
- Disable backups for non-production
- Use 1-node database (no HA) for development

## Production Checklist

Before going to production:

- [ ] Set strong passwords and secrets
- [ ] Restrict SSH access to specific IPs
- [ ] Enable database backups
- [ ] Configure custom domain with SSL
- [ ] Set up monitoring and alerts
- [ ] Configure log aggregation
- [ ] Implement disaster recovery plan
- [ ] Test failover procedures
- [ ] Document runbooks
- [ ] Set up CI/CD pipeline
- [ ] Configure cost monitoring
- [ ] Review and optimize costs
- [ ] Enable audit logging
- [ ] Set up automated backups
- [ ] Test backup restoration

## Advanced Topics

### Custom Domain with SSL

```bash
# Add custom domain to load balancer
doctl compute load-balancer add-forwarding-rules <lb-id> \
  --entry-port 443 \
  --entry-protocol https \
  --target-port 80 \
  --target-protocol http \
  --certificate-id <cert-id>

# Create DNS record
doctl compute domain records create example.com \
  --record-type A \
  --record-name app \
  --record-data <lb-ip>
```

### Connection Draining

When removing droplets, gracefully close connections:

```bash
# Gracefully stop application
doctl compute droplet ssh <droplet-id> --command "systemctl stop app"

# Wait for connections to drain
sleep 30

# Now destroy the droplet
terraform destroy -target=digitalocean_droplet.web[0]
```

### Session Affinity Testing

```bash
# Test sticky sessions
curl -c cookies.txt http://<lb-ip>/info
curl -b cookies.txt http://<lb-ip>/info

# You should see the same server responding
```

## Further Reading

- [DigitalOcean Load Balancers](https://docs.digitalocean.com/products/load-balancers/)
- [Load Balancer Pricing](https://www.digitalocean.com/pricing/load-balancers)
- [Terraform DigitalOcean Provider](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs/resources/load_balancer)
- [Droplet Documentation](https://docs.digitalocean.com/products/droplets/)
- [Managed Databases](https://docs.digitalocean.com/products/databases/)
