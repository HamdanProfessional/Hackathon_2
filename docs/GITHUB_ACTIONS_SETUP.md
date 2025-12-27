# GitHub Actions CI/CD Setup Guide

This document describes how to configure GitHub Actions for deploying the Todo application to DigitalOcean Kubernetes (DOKS).

## Overview

The project includes two GitHub Actions workflows:

1. **Backend CI/CD** (`.github/workflows/backend-deploy.yml`) - Deploys the FastAPI backend service
2. **Notifications CI/CD** (`.github/workflows/notifications-deploy.yml`) - Deploys the notification microservice

## Required GitHub Secrets

You need to configure the following secrets in your GitHub repository:

### GitHub Secrets Configuration

Navigate to: **Repository Settings** > **Secrets and variables** > **Actions** > **New repository secret**

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `DIGITALOCEAN_ACCESS_TOKEN` | DigitalOcean API token with Kubernetes read/write access | Create at [DigitalOcean Control Panel](https://cloud.digitalocean.com/settings/api/tokens) |
| `DO_REGISTRY_USERNAME` | DigitalOcean Container Registry username | Your DigitalOcean account email or API token |
| `DO_REGISTRY_ACCESS_TOKEN` | DigitalOcean Container Registry access token | Use the same as `DIGITALOCEAN_ACCESS_TOKEN` or create a registry-specific token |

### Setting Up DigitalOcean Access Token

1. Go to [DigitalOcean API Tokens](https://cloud.digitalocean.com/settings/api/tokens)
2. Click **Generate New Token**
3. Set token name: `GitHub Actions - Todo App`
4. Select scopes:
   - `Read` (for cluster info)
   - `Write` (for deployments)
5. Copy the token immediately (it won't be shown again)
6. Add to GitHub as `DIGITALOCEAN_ACCESS_TOKEN`

### Setting Up Container Registry Access

The same DigitalOcean API token can be used for registry access, or you can create a registry-specific token:

```bash
# Using doctl CLI
doctl registry create todo-chatbot-reg

# Get registry credentials
doctl registry login

# For registry-specific token (optional)
doctl registry token create --expiry-seconds 0 --read-write --registry-name todo-chatbot-reg
```

Add the registry credentials to GitHub:
- `DO_REGISTRY_USERNAME`: Your DigitalOcean account email
- `DO_REGISTRY_ACCESS_TOKEN`: The API token or registry token

## Cluster Configuration

The workflows are configured to use the following DigitalOcean Kubernetes cluster:

```yaml
CLUSTER_NAME: do-fra1-hackathon2h1
CLUSTER_REGION: fra1
NAMESPACE: production
```

If your cluster has a different name, update the workflow files:
- `.github/workflows/backend-deploy.yml`
- `.github/workflows/notifications-deploy.yml`

## Workflow Features

### Backend CI/CD Pipeline

1. **Test Stage**: Runs pytest with coverage
2. **Lint Stage**: Runs ruff, bandit security scan
3. **Build Stage**: Builds and pushes Docker image with SHA tag
4. **Deploy Stage**: Deploys to DOKS using Helm
5. **Health Check**: Post-deployment smoke tests
6. **Rollback**: Automatic rollback on failure

### Notifications CI/CD Pipeline

1. **Test Stage**: Runs pytest for notification service
2. **Lint Stage**: Security scanning and linting
3. **Dapr Validation**: Validates Dapr component manifests
4. **Build Stage**: Builds and pushes image with Trivy vulnerability scan
5. **Deploy Stage**: Deploys with Dapr sidecar injection
6. **Health Check**: Validates Dapr and service health

## Container Registry

Images are pushed to:
```
registry.digitalocean.com/todo-chatbot-reg/todo-backend:<sha>
registry.digitalocean.com/todo-chatbot-reg/notification-service:<sha>
```

### Image Tagging Strategy

- `git commit SHA`: e.g., `abc123def456`
- `latest`: Points to the most recent commit on main branch
- Semantic version tags (if using git tags)

## Helm Deployment

Both workflows use Helm charts located in:
- `helm/backend/` - Backend service chart
- `helm/notifications/` - Notification service chart

### Helm Commands Used

```bash
helm upgrade --install <release-name> <chart-path> \
  --namespace production \
  --set image.repository=<registry>/<image-name> \
  --set image.tag=<git-sha> \
  --set image.pullPolicy=Always \
  --wait \
  --timeout 10m \
  --atomic \
  --cleanup-on-fail
```

## Manual Deployment

You can trigger a workflow manually:

1. Go to **Actions** tab in GitHub
2. Select the workflow (Backend or Notifications)
3. Click **Run workflow**
4. Optionally skip tests by setting `skip_tests` to `true`

## Troubleshooting

### Workflow fails at "Configure kubectl"

Ensure `DIGITALOCEAN_ACCESS_TOKEN` has the correct permissions and the cluster name matches.

### Workflow fails at "Log in to DO Container Registry"

Verify:
1. Registry name is correct: `todo-chatbot-reg`
2. `DO_REGISTRY_USERNAME` and `DO_REGISTRY_ACCESS_TOKEN` are correct
3. Token has registry read/write permissions

### Helm upgrade fails

Check the Helm chart values match your environment:
```bash
# Test locally
helm lint helm/backend/
helm upgrade --install todo-backend helm/backend/ --dry-run --debug
```

### Pods not starting after deployment

```bash
# Check pod status
kubectl get pods -n production

# Check pod logs
kubectl logs -n production <pod-name>

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'
```

### Dapr sidecar not injecting

Ensure:
1. Dapr is installed on the cluster: `kubectl get pods -n dapr-system`
2. The Helm chart has `dapr.enabled: true`
3. Pod annotations include `dapr.io/enabled: "true"`

## Security Best Practices

1. **Rotate secrets regularly**: Update tokens every 90 days
2. **Use least privilege**: Tokens should only have required permissions
3. **Enable branch protection**: Require reviews before merging to main
4. **Monitor workflow runs**: Check for suspicious activity
5. **Keep dependencies updated**: Run `dependabot` to track security updates

## Workflow Status Badges

Add these badges to your README.md:

```markdown
[![Backend CI/CD](https://github.com/your-org/todo-app/actions/workflows/backend-deploy.yml/badge.svg)](https://github.com/your-org/todo-app/actions/workflows/backend-deploy.yml)
[![Notifications CI/CD](https://github.com/your-org/todo-app/actions/workflows/notifications-deploy.yml/badge.svg)](https://github.com/your-org/todo-app/actions/workflows/notifications-deploy.yml)
```

## CI/CD Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub Push to Main                       │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Test & Lint Stage                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Pytest  │  │  Ruff    │  │ Bandit   │  │ Dapr Validation  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Build Stage                               │
│  ┌──────────────────┐  ┌─────────────────┐  ┌────────────────┐   │
│  │ Docker Build     │  │ Push to DO CR   │  │ Trivy Scan     │   │
│  └──────────────────┘  └─────────────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Deploy Stage                              │
│  ┌──────────────────┐  ┌─────────────────┐  ┌────────────────┐   │
│  │ Helm Lint        │  │ Helm Deploy     │  │ Rollback       │   │
│  │                  │  │ (Atomic)         │  │ (on failure)   │   │
│  └──────────────────┘  └─────────────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Health Check                              │
│  ┌──────────────────┐  ┌─────────────────┐  ┌────────────────┐   │
│  │ Pod Readiness    │  │ Health Endpoint │  │ Dapr Health    │   │
│  └──────────────────┘  └─────────────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [DigitalOcean Kubernetes](https://docs.digitalocean.com/products/kubernetes/)
- [Helm Documentation](https://helm.sh/docs/)
- [Dapr Documentation](https://docs.dapr.io/)
