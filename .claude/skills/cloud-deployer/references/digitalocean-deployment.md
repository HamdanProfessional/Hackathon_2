# DigitalOcean Deployment References

Official DigitalOcean documentation and resources for cloud deployment.

## Table of Contents
1. [Official Documentation](#official-documentation)
2. [Kubernetes (DOKS)](#kubernetes-doks)
3. [App Platform](#app-platform)
4. [Spaces & CDN](#spaces--cdn)
5. [Functions (Serverless)](#functions-serverless)
6. [Load Balancers](#load-balancers)
7. [Databases](#databases)
8. [Monitoring & Logging](#monitoring--logging)
9. [Security](#security)
10. [API Reference](#api-reference)
11. [Community Resources](#community-resources)

---

## Official Documentation

### Main Documentation
- **DigitalOcean Docs**: https://docs.digitalocean.com/
- **Product Documentation**: https://docs.digitalocean.com/products/
- **Getting Started**: https://docs.digitalocean.com/guides/getting-started-with-digitalocean/

### Developer Tools
- **doctl Documentation**: https://docs.digitalocean.com/reference/doctl/
- **doctl GitHub**: https://github.com/digitalocean/doctl
- **doctl Installation**: https://github.com/digitalocean/doctl#installing-doctl

---

## Kubernetes (DOKS)

### Official Docs
- **DOKS Overview**: https://docs.digitalocean.com/products/kubernetes/
- **Quick Start**: https://docs.digitalocean.com/products/kubernetes/quickstart/
- **Clusters**: https://docs.digitalocean.com/products/kubernetes/clusters/

### Tutorials
- **Kubernetes Basics**: https://docs.digitalocean.com/products/kubernetes/kubernetes-basics/
- **Deploying Nginx**: https://docs.digitalocean.com/products/kubernetes/how-to/deploy-nginx-on-digitalocean-kubernetes/
- **Helm Charts**: https://docs.digitalocean.com/products/kubernetes/how-to/install-helm-on-digitalocean-kubernetes/

### Best Practices
- **Cluster Sizing**: https://docs.digitalocean.com/products/kubernetes/details/#cluster-and-pool-sizing
- **Node Pools**: https://docs.digitalocean.com/products/kubernetes/details/#node-pools
- **Auto-scaling**: https://docs.digitalocean.com/products/kubernetes/details/#cluster-auto-scaling

### Common Tasks
```bash
# List clusters
doctl kubernetes cluster list

# Create cluster
doctl kubernetes cluster create my-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 3

# Get kubeconfig
doctl kubernetes cluster kubeconfig save my-cluster

# Delete cluster
doctl kubernetes cluster delete my-cluster
```

---

## App Platform

### Official Docs
- **App Platform Overview**: https://docs.digitalocean.com/products/app-platform/
- **Quick Start**: https://docs.digitalocean.com/products/app-platform/quickstart/
- **Deploying from Git**: https://docs.digitalocean.com/products/app-platform/deploying-from-git/

### App Specification
- **App Spec Reference**: https://docs.digitalocean.com/products/app-platform/reference/app-spec/
- **Components**: https://docs.digitalocean.com/products/app-platform/components/
- **Environment Variables**: https://docs.digitalocean.com/products/app-platform/how-to/use-environment-variables/

### Features
- **Auto-scaling**: https://docs.digitalocean.com/products/app-platform/how-to/use-autoscaling/
- **Health Checks**: https://docs.digitalocean.com/products/app-platform/how-to/configure-health-checks/
- **Deployments**: https://docs.digitalocean.com/products/app-platform/deployments/
- **Pre-deploy Jobs**: https://docs.digitalocean.com/products/app-platform/how-to/run-pre-deploy-jobs/

### Example App Spec
```yaml
name: example-app
region: nyc3
services:
- name: web
  github:
    repo: username/repo
    branch: main
  dockerfile_path: Dockerfile
  http_port: 8080
  instance_count: 2
  instance_size_slug: basic-xxs
```

---

## Spaces & CDN

### Official Docs
- **Spaces Overview**: https://docs.digitalocean.com/products/spaces/
- **CDN Overview**: https://docs.digitalocean.com/products/spaces/cdn/
- **Quick Start**: https://docs.digitalocean.com/products/spaces/quickstart/

### Tools
- **Spaces with AWS CLI**: https://docs.digitalocean.com/products/spaces/how-to/use-spaces-with-the-aws-cli/
- **s3cmd**: https://docs.digitalocean.com/products/spaces/how-to/use-s3cmd/
- **Terraform Provider**: https://docs.digitalocean.com/products/spaces/how-to/use-terraform-with-spaces/

### CDN Configuration
- **Enable CDN**: https://docs.digitalocean.com/products/spaces/how-to/enable-cdn/
- **Custom Domains**: https://docs.digitalocean.com/products/spaces/how-to/set-up-a-custom-domain-with-spaces-cdn/
- **CDN Endpoints**: https://docs.digitalocean.com/products/spaces/details/#cdn-endpoints

### Common Tasks
```bash
# Create Spaces
doctl spaces create my-spaces --region nyc3

# List Spaces
doctl spaces list

# Enable CDN
doctl spaces cdn create my-spaces --ttl 3600

# Sync with AWS CLI
aws s3 sync ./local-dir s3://my-spaces \
  --endpoint=https://nyc3.digitaloceanspaces.com
```

---

## Functions (Serverless)

### Official Docs
- **Functions Overview**: https://docs.digitalocean.com/products/functions/
- **Quick Start**: https://docs.digitalocean.com/products/functions/quickstart/
- **Deploying Functions**: https://docs.digitalocean.com/products/functions/deploying-functions/

### doctl Serverless Plugin
- **Installation**: https://docs.digitalocean.com/products/functions/how-to/install-the-doctl-serverless-plugin/
- **Commands**: https://docs.digitalocean.com/products/functions/reference/doctl-serverless-commands/

### Function Examples
- **JavaScript Functions**: https://docs.digitalocean.com/products/functions/examples/javascript-functions/
- **Go Functions**: https://docs.digitalocean.com/products/functions/examples/go-functions/
- **Python Functions**: https://docs.digitalocean.com/products/functions/examples/python-functions/

### Triggers & Packages
- **Triggers**: https://docs.digitalocean.com/products/functions/triggers/
- **Packages**: https://docs.digitalocean.com/products/functions/packages/
- **Invoking Functions**: https://docs.digitalocean.com/products/functions/invoking-functions/

---

## Load Balancers

### Official Docs
- **Load Balancers Overview**: https://docs.digitalocean.com/products/load-balancers/
- **Features**: https://docs.digitalocean.com/products/load-balancers/features/
- **Pricing**: https://docs.digitalocean.com/products/load-balancers/pricing/

### Configuration
- **Create LB**: https://docs.digitalocean.com/products/load-balancers/how-to/create-load-balancers/
- **Forwarding Rules**: https://docs.digitalocean.com/products/load-balancers/how-to/configure-forwarding-rules/
- **Health Checks**: https://docs.digitalocean.com/products/load-balancers/how-to/configure-health-checks/
- **Sticky Sessions**: https://docs.digitalocean.com/products/load-balancers/how-to/use-sticky-sessions/

### SSL/TLS
- **SSL Termination**: https://docs.digitalocean.com/products/load-balancers/how-to/use-termination-with-load-balancers/
- **Certificate Upload**: https://docs.digitalocean.com/products/load-balancers/how-to/enable-ssl-termination/
- **Let's Encrypt**: https://docs.digitalocean.com/products/load-balancers/how-to/enable-lets-encrypt-certificates/

---

## Databases

### Official Docs
- **Managed Databases**: https://docs.digitalocean.com/products/databases/
- **Supported Engines**: https://docs.digitalocean.com/products/databases/supported-engines/
- **High Availability**: https://docs.digitalocean.com/products/databases/details/#high-availability-clustering

### PostgreSQL
- **PostgreSQL Overview**: https://docs.digitalocean.com/products/databases/postgresql/
- **Connection Pooling**: https://docs.digitalocean.com/products/databases/postgresql/details/#connection-pooling
- **Features**: https://docs.digitalocean.com/products/databases/postgresql/features/

### MySQL
- **MySQL Overview**: https://docs.digitalocean.com/products/databases/mysql/
- **Replication**: https://docs.digitalocean.com/products/databases/mysql/details/#replication-and-clustering/

### Redis
- **Redis Overview**: https://docs.digitalocean.com/products/databases/redis/
- **Clustering**: https://docs.digitalocean.com/products/databases/redis/details/#clustering-and-high-availability/

### Common Tasks
```bash
# Create database
doctl databases create my-db \
  --engine pg \
  --version 15 \
  --size db-s-1vcpu-1gb \
  --region nyc1 \
  --num-nodes 1

# Get connection info
doctl databases connection my-db

# List databases
doctl databases list
```

---

## Monitoring & Logging

### Official Docs
- **Monitoring Overview**: https://docs.digitalocean.com/products/monitoring/
- **Metrics**: https://docs.digitalocean.com/products/monitoring/details/

### Cloud Monitoring
- **Droplet Metrics**: https://docs.digitalocean.com/products/monitoring/how-to/use-cloud-monitoring/
- **Metrics API**: https://docs.digitalocean.com/products/monitoring/how-to/retrieve-metrics-with-the-api/

### Alerting
- **Alert Policies**: https://docs.digitalocean.com/products/monitoring/how-to/create-alert-policies/
- **Email Notifications**: https://docs.digitalocean.com/products/monitoring/how-to/configure-email-notifications/

### Logs
- **App Logs**: https://docs.digitalocean.com/products/app-platform/logs/
- **Kubernetes Logs**: https://docs.digitalocean.com/products/kubernetes/how-to/troubleshoot-kubernetes-with-logs/

---

## Security

### Official Docs
- **Cloud Firewalls**: https://docs.digitalocean.com/products/firewalls/
- **SSH Keys**: https://docs.digitalocean.com/products/droplets/how-to/add-ssh-keys-to-droplets/
- **Certificates**: https://docs.digitalocean.com/products/certificates/

### Cloud Firewalls
- **Creating Firewalls**: https://docs.digitalocean.com/products/firewalls/how-to/configure-firewalls/
- **Inbound Rules**: https://docs.digitalocean.com/products/firewalls/how-to/configure-inbound-rules/
- **Outbound Rules**: https://docs.digitalocean.com/products/firewalls/how-to/configure-outbound-rules/

### SSL/TLS Certificates
- **Let's Encrypt**: https://docs.digitalocean.com/products/networking/how-to/create-lets-encrypt-certificates/
- **Custom Certificates**: https://docs.digitalocean.com/products/networking/how-to/upload-custom-ssl-certificates/

### Secrets Management
- **Kubernetes Secrets**: https://docs.digitalocean.com/products/kubernetes/how-to/create-kubernetes-secrets/
- **App Platform Secrets**: https://docs.digitalocean.com/products/app-platform/how-to/use-environment-variables/

---

## API Reference

### Official API Docs
- **API v2**: https://docs.digitalocean.com/reference/api/api-v2
- **OpenAPI Spec**: https://developers.digitalocean.com/documentation/v2/

### Common Endpoints
- **Droplets**: https://docs.digitalocean.com/reference/api/api-v2/#droplets
- **Kubernetes**: https://docs.digitalocean.com/reference/api/api-v2/#kubernetes
- **Load Balancers**: https://docs.digitalocean.com/reference/api/api-v2/#load-balancers
- **Spaces**: https://docs.digitalocean.com/reference/api/api-v2/#spaces

### Authentication
- **Personal Access Tokens**: https://docs.digitalocean.com/reference/api/api-v2/#authentication
- **OAuth**: https://docs.digitalocean.com/reference/api/api-v2/#oauth

### SDKs
- **doctl**: https://github.com/digitalocean/doctl
- **Terraform Provider**: https://github.com/digitalocean/terraform-provider-digitalocean
- **Python**: https://github.com/digitalocean/python-digitalocean
- **Go**: https://github.com/digitalocean/godo
- **Ruby**: https://github.com/digitalocean/droplet_kit

---

## Community Resources

### Community Tools
- **Terraform Provider**: https://github.com/digitalocean/terraform-provider-digitalocean
- **Kubernetes Provider**: https://github.com/digitalocean/digitalocean-cloud-controller-manager
- **CSI Driver**: https://github.com/digitalocean/csi-digitalocean

### Tutorials
- **Community Tutorials**: https://docs.digitalocean.com/tutorials/
- **Product Tutorials**: https://docs.digitalocean.com/products/

### Writing Guides
- **Getting Started**: https://www.digitalocean.com/community/tutorials?q=getting+started
- **Kubernetes**: https://www.digitalocean.com/community/tutorials?categories=kubernetes
- **Docker**: https://www.digitalocean.com/community/tutorials?categories=docker

### Marketplace
- **Marketplace**: https://marketplace.digitalocean.com/
- **One-Click Apps**: https://marketplace.digitalocean.com/apps
- **Kubernetes-based Apps**: https://marketplace.digitalocean.com/kubernetes

---

## Pricing

### Pricing Calculator
- **Pricing**: https://www.digitalocean.com/pricing
- **Calculator**: https://www.digitalocean.com/pricing-calculator

### Product Pricing
- **Droplets**: https://www.digitalocean.com/pricing/droplets
- **Kubernetes**: https://www.digitalocean.com/pricing/kubernetes
- **App Platform**: https://www.digitalocean.com/pricing/app-platform
- **Load Balancers**: https://www.digitalocean.com/pricing/load-balancers
- **Spaces**: https://www.digitalocean.com/pricing/spaces
- **Databases**: https://www.digitalocean.com/pricing/databases

---

## Support

### Support Options
- **Support Portal**: https://cloud.digitalocean.com/support
- **Documentation**: https://docs.digitalocean.com/
- **Status Page**: https://status.digitalocean.com/

### Community
- **Community Forum**: https://www.digitalocean.com/community
- **Stack Overflow**: https://stackoverflow.com/questions/tagged/digitalocean
- **GitHub**: https://github.com/digitalocean

### Contact
- **Twitter**: https://twitter.com/digitalocean
- **Email**: support@digitalocean.com
