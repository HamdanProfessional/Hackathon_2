# Cloud-Native Deployment Blueprints

This directory contains production-ready cloud-native deployment blueprints for the Todo Application.

## Available Blueprints

### 1. DigitalOcean Kubernetes (DOKS)
- **File**: `digitalocean-kubernetes.md`
- **Platform**: DigitalOcean Kubernetes
- **Services**: Full-stack (Frontend, Backend, Notifications)
- **Features**: Auto-scaling, monitoring, CI/CD

### 2. Google Kubernetes Engine (GKE)
- **File**: `gke-autopilot.md`
- **Platform**: Google Cloud GKE Autopilot
- **Services**: Full-stack with Cloud SQL
- **Features**: Serverless pods, Cloud Armor, Cloud Deploy

### 3. Azure Kubernetes Service (AKS)
- **File**: `aks-standard.md`
- **Platform**: Azure Kubernetes Service
- **Services**: Full-stack with Azure Database
- **Features**: Azure AD integration, Application Gateway

### 4. AWS Elastic Kubernetes Service (EKS)
- **File**: `eks-fargate.md`
- **Platform**: AWS EKS with Fargate
- **Services**: Full-stack with RDS
- **Features**: Serverless compute, AWS WAF, CodePipeline

## Quick Start

```bash
# Choose your cloud provider
cd blueprints/cloud-native

# Example: DigitalOcean
cat digitalocean-kubernetes.md | less

# Apply the blueprint
kubectl apply -f ../../helm/
```

## Blueprint Components

Each blueprint includes:

1. **Infrastructure Setup**
   - Cluster creation commands
   - Network configuration
   - Storage classes

2. **Service Deployment**
   - Helm chart values
   - Environment variables
   - Resource limits

3. **Monitoring & Logging**
   - Prometheus integration
   - Grafana dashboards
   - Log aggregation

4. **CI/CD Pipeline**
   - GitHub Actions workflows
   - Automated deployment
   - Rollback procedures

5. **Security Hardening**
   - Network policies
   - Pod security policies
   - Secrets management

## Prerequisites

- kubectl configured
- Helm 3.x installed
- Cloud provider CLI
- Domain name configured

## Support

For issues or questions, refer to:
- `../../docs/DIGITALOCEAN_QUICK_REFERENCE.md`
- `../../docs/KAFKA_QUICK_REFERENCE.md`
- `../../docs/PHASE5_IMPLEMENTATION_PLAN.md`
