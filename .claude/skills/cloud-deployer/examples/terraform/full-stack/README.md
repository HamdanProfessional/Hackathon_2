# Full Stack Application - Complete DigitalOcean Deployment

This example demonstrates a **production-ready full-stack application** leveraging all major DigitalOcean services for a scalable, highly available, and secure deployment.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USERS                                      │
└────────────────────────┬────────────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
    ┌───────▼─────────┐       ┌──────▼──────────┐
    │  Frontend       │       │  API Endpoint   │
    │  (App Platform) │       │  (Load Balancer)│
    │  - Next.js      │       │  - SSL Term     │
    │  - Static CDN   │       │  - Health Chk   │
    └───────┬─────────┘       └──────┬──────────┘
            │                         │
            │                         │
            │            ┌────────────┴────────────┐
            │            │                         │
            │      ┌─────▼──────┐          ┌──────▼──────┐
            │      │ Backend-1  │          │ Backend-2   │
            │      │ (Droplet)  │          │ (Droplet)   │
            │      │ - FastAPI  │          │ - FastAPI   │
            │      │ - Docker    │          │ - Docker    │
            │      └─────┬──────┘          └──────┬──────┘
            │            │                        │
            │            └────────────┬────────────┘
            │                         │
            │            ┌────────────▼────────────┐
            │            │                         │
            │      ┌─────▼────────┐      ┌────────▼───────┐
            │      │ PostgreSQL   │      │    Redis       │
            │      │ (Managed)    │      │   (Managed)    │
            │      │ - HA         │      │                │
            │      └──────────────┘      └────────────────┘
            │
      ┌─────▼──────────┐
      │ Spaces + CDN   │
      │ - Static assets│
      │ - Images       │
      └────────────────┘
```

## Components

| Component | Service | Purpose |
|-----------|---------|---------|
| **Frontend** | App Platform | Next.js static site with automatic deployments |
| **Backend API** | Droplets + Load Balancer | FastAPI application with auto-scaling |
| **Database** | Managed PostgreSQL | Persistent data storage with HA |
| **Cache** | Managed Redis | Session storage and caching |
| **Assets** | Spaces + CDN | Static file hosting with global CDN |
| **Registry** | Container Registry | Docker image storage |
| **Networking** | VPC + Firewall | Private networking and security |

## Features

### High Availability
- Multiple backend droplets with automatic failover
- Managed PostgreSQL with 2-node HA configuration
- Load balancer with health checks
- Zero-downtime deployments

### Scalability
- Horizontal scaling for backend (add more droplets)
- App Platform auto-scaling for frontend
- Managed services scale automatically
- CDN for global asset distribution

### Security
- Cloud firewalls restrict access
- Private VPC for service-to-service communication
- SSL/TLS termination at load balancer
- Managed database firewall rules
- Secrets management

### Observability
- Built-in monitoring for all services
- Metrics collection via DigitalOcean monitoring
- Log aggregation via Cloud Logging
- Health checks and alerting

### Developer Experience
- Git-based deployments (App Platform)
- Container registry for Docker images
- CI/CD integration ready
- Environment variable management
- Easy rollback

## Quick Start

### 1. Prerequisites

```bash
# Install required tools
brew install doctl terraform

# Authenticate with DigitalOcean
doctl auth init

# Generate SSH key (if needed)
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

### 2. Configure Variables

```bash
cd .claude/skills/cloud-deployer/examples/terraform/full-stack

cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

**Required variables:**
- `do_token` - DigitalOcean API token
- `github_repo` - Your GitHub repository
- `ssh_public_key_path` - Path to your SSH public key

### 3. Deploy Infrastructure

```bash
terraform init
terraform plan
terraform apply
```

### 4. Access Your Application

After deployment, get the URLs:

```bash
# Frontend URL
terraform output frontend_url

# API URL
terraform output api_url
```

## Cost Estimation

Based on default configuration (monthly):

| Service | Specification | Cost |
|---------|---------------|------|
| **Frontend (App Platform)** | Basic plan | Free |
| **Backend Droplets** | 2x s-2vcpu-4gb + backups | ~$100 |
| **Load Balancer** | 1 unit | ~$15 |
| **PostgreSQL** | 2-node HA, db-s-2vcpu-4gb | ~$210 |
| **Redis** | db-s-1vcpu-1gb | ~$30 |
| **Spaces + CDN** | 100GB storage + 1TB transfer | ~$25 |
| **Container Registry** | Basic tier | ~$5 |
| **VPC + Firewall** | - | Free |
| **Total** | | **~$385/month** |

**Cost optimization tips:**
- Use 1-node database for development (saves ~$105/month)
- Reduce droplet count to 1 for non-critical workloads
- Disable backups for staging/development
- Use smaller droplet sizes (s-1vcpu-2gb)

## Project Structure

Your repository should follow this structure:

```
project/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models/          # Database models
│   │   ├── api/             # API routes
│   │   └── services/        # Business logic
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── pages/               # Next.js pages
│   ├── components/          # React components
│   ├── public/              # Static assets
│   ├── package.json
│   ├── next.config.js
│   └── Dockerfile
├── infrastructure/
│   └── terraform/
│       └── full-stack/      # This example
├── docker-compose.yml       # Local development
└── README.md
```

## Local Development

### Using Docker Compose

```bash
# Start all services locally
docker-compose up -d

# Run backend migrations
docker-compose exec backend alembic upgrade head

# Access services
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment Workflow

### Initial Setup

1. **Push code to GitHub**
2. **Configure Terraform variables**
3. **Run `terraform apply`**
4. **Access application via generated URLs**

### Updates

**Frontend (App Platform):**
```bash
# Push to main branch
git push origin main

# App Platform auto-deploys
# Monitor at: https://cloud.digitalocean.com/apps
```

**Backend (Droplets):**
```bash
# Build and push new Docker image
docker build -t registry.digitalocean.com/your-registry/backend:latest backend/
docker push registry.digitalocean.com/your-registry/backend:latest

# Update droplets via SSH or use CI/CD
doctl compute droplet ssh <droplet-id> --command "docker pull registry.digitalocean.com/your-registry/backend:latest && systemctl restart backend"
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Backend

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          docker build -t registry.digitalocean.com/${{ secrets.REGISTRY_NAME }}/backend:${{ github.sha }} backend/

      - name: Login to DO Registry
        run: |
          echo ${{ secrets.DO_API_TOKEN }} | docker login registry.digitalocean.com -u ${{ secrets.DO_API_TOKEN }} --password-stdin

      - name: Push to Registry
        run: |
          docker push registry.digitalocean.com/${{ secrets.REGISTRY_NAME }}//backend:${{ github.sha }}

      - name: Deploy to Droplets
        run: |
          # Add deployment logic here
```

## Monitoring and Logging

### Application Metrics

```bash
# View droplet metrics
doctl monitors droplet-bandwidth <droplet-id>

# View database metrics
doctl databases metrics <db-id>

# View load balancer stats
doctl compute load-balancer get <lb-id>
```

### Logging

```bash
# View application logs
doctl compute droplet ssh <droplet-id> --command "journalctl -u backend -f"

# View App Platform logs
doctl apps logs <app-id> --follow

# View database logs
doctl databases logs <db-id> --tail 100
```

### Monitoring Dashboard

Access the DigitalOcean dashboard:
- https://cloud.digitalocean.com/apps (App Platform)
- https://cloud.digitalocean.com/databases (Managed databases)
- https://cloud.digitalocean.com/droplets (Droplets)

## Troubleshooting

### Frontend Issues

**Deployment fails:**
```bash
# Check build logs
doctl apps logs <app-id> --type deploy --tail 100

# Common issues:
# - Missing dependencies in package.json
# - Build errors in Next.js
# - Environment variable issues
```

**Site not accessible:**
```bash
# Check app status
doctl apps get <app-id>

# Verify DNS records
doctl compute domain records list <domain>
```

### Backend Issues

**Droplet not responding:**
```bash
# Check droplet status
doctl compute droplet get <droplet-id>

# SSH and check logs
ssh root@<droplet-ip>
sudo journalctl -u backend -f
```

**Load balancer returning 502:**
```bash
# Check health status of droplets
doctl compute load-balancer get <lb-id>

# Verify application is running
curl http://<droplet-ip>:8000/health
```

### Database Issues

**Connection refused:**
```bash
# Check database firewall rules
doctl databases firewalls list <db-id>

# Test connection from droplet
doctl compute droplet ssh <droplet-id> --command "psql -h <db-host> -U <user> -d <db>"
```

### Common Solutions

```bash
# Restart backend service
systemctl restart backend

# Rebuild and redeploy
docker-compose down
docker-compose up -d --build

# Clear application cache
redis-cli FLUSHALL
```

## Scaling

### Horizontal Scaling (Add Droplets)

```bash
# Update terraform.tfvars
backend_droplet_count = 4

# Apply changes
terraform apply
```

### Vertical Scaling (Resize Droplets)

```bash
# Update droplet size in terraform.tfvars
backend_droplet_size = "s-4vcpu-8gb"

# Apply (requires recreation)
terraform apply -replace=digitalocean_droplet.backend[0]
```

### Database Scaling

```bash
# Update database size
db_size = "db-s-4vcpu-16gb"

# Add more nodes for HA
db_node_count = 3
```

## Backup and Disaster Recovery

### Automated Backups

- **Droplets**: Enabled by default (7-day retention)
- **Database**: Automated daily backups (configurable retention)
- **Spaces**: Versioning enabled for recovery

### Manual Backup

```bash
# Snapshot droplets
doctl compute droplet snapshot <droplet-id> --snapshot-name "manual-backup-$(date +%Y%m%d)"

# Backup database
doctl databases backup <db-id> --backup-name "manual-backup-$(date +%Y%m%d)"

# Export Spaces to local
aws s3 sync s3://<bucket-name> ./backup --endpoint=https://<region>.digitaloceanspaces.com
```

### Restore

```bash
# Restore droplet from snapshot
doctl compute snapshot get <snapshot-id>

# Restore database from backup
doctl databases restore <db-id> --backup-id <backup-id> --restore-to-db-name <new-db>
```

## Security Best Practices

1. **Secrets Management**
   - Never commit secrets to git
   - Use environment variables
   - Rotate credentials regularly

2. **Network Security**
   - Use VPC for private communication
   - Restrict firewall rules
   - Enable SSL/TLS everywhere

3. **Access Control**
   - Limit SSH access to specific IPs
   - Use strong passwords
   - Enable 2FA on DigitalOcean account

4. **Application Security**
   - Validate all inputs
   - Use prepared statements
   - Enable CORS properly
   - Implement rate limiting

## Production Checklist

Before deploying to production:

- [ ] Review and optimize costs
- [ ] Set strong passwords and secrets
- [ ] Configure custom domains with SSL
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Implement backup strategy
- [ ] Test disaster recovery
- [ ] Configure CI/CD pipeline
- [ ] Review security settings
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Configure CDN caching
- [ ] Test failover procedures
- [ ] Document runbooks
- [ ] Set up staging environment
- [ ] Configure analytics

## Further Reading

- [DigitalOcean Documentation](https://docs.digitalocean.com/)
- [App Platform Guide](https://docs.digitalocean.com/products/app-platform/)
- [Managed Databases](https://docs.digitalocean.com/products/databases/)
- [Load Balancers](https://docs.digitalocean.com/products/load-balancers/)
- [Container Registry](https://docs.digitalocean.com/products/container-registry/)
- [Terraform Provider](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs)

## Support

- DigitalOcean Community: https://www.digitalocean.com/community
- DO Documentation: https://docs.digitalocean.com/
- Terraform Forums: https://discuss.hashicorp.com/
- GitHub Issues: https://github.com/digitalocean/terraform-provider-digitalocean/issues
