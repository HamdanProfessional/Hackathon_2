---
name: cloud-deployer
description: Cloud deployment automation skills for CI/CD pipelines, container registry management, and production deployments. Use when setting up GitHub Actions workflows, automating deployments to cloud platforms (DOKS/GKE/AKS), configuring build pipelines, or implementing continuous delivery. Essential for Phase V automated deployment.
---

# Cloud Deployment Automation

This skill provides guidance for automating deployments to cloud platforms using CI/CD pipelines.

## When to Use This Skill

Use this skill when:
- Creating GitHub Actions workflows
- Setting up CI/CD pipelines
- Automating deployments to Kubernetes
- Configuring container registries
- Implementing continuous delivery
- Managing production deployments

## Quick Reference

### GitHub Actions Workflow

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Build images
      run: |
        docker build -t image:tag ./path

    - name: Login to registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Push images
      run: docker push image:tag

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

    - name: Deploy
      run: |
        helm upgrade --install release-name chart-name \
          --set image.tag=${{ github.sha }}
```

### Container Registry Commands

```bash
# GitHub Container Registry
docker tag image:tag ghcr.io/owner/image:tag
docker push ghcr.io/owner/image:tag

# Docker Hub
docker tag image:tag username/image:tag
docker push username/image:tag

# Google Container Registry
docker tag image:tag gcr.io/project/image:tag
docker push gcr.io/project/image:tag

# Azure Container Registry
docker tag image:tag registry.azurecr.io/image:tag
docker push registry.azurecr.io/image:tag
```

### Kubernetes Deployment Commands

```bash
# Set context
kubectl config use-context context-name

# Get contexts
kubectl config get-contexts

# Verify cluster
kubectl cluster-info
kubectl get nodes

# Deploy with Helm
helm upgrade --install release chart -f values.yaml

# Verify deployment
kubectl rollout status deployment/deployment-name

# Get pods
kubectl get pods -l app=app-name
```

## GitHub Actions Patterns

### Multi-Stage Pipeline

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: my-app

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run tests
      run: |
        pip install pytest
        pytest tests/

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
    - uses: actions/checkout@v4
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    - name: Login to registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: ./app
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest,${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBECONFIG_STAGING }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
    - name: Deploy to staging
      run: |
        helm upgrade --install myapp ./helm/myapp \
          --set image.tag=${{ github.sha }} \
          --namespace staging \
          --create-namespace

  deploy-production:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBECONFIG_PROD }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
    - name: Deploy to production
      run: |
        helm upgrade --install myapp ./helm/myapp \
          --set image.tag=${{ github.sha }} \
          --namespace production \
          --create-namespace
    - name: Health check
      run: |
        kubectl wait --for=condition=ready pod -l app=myapp -n production --timeout=300s
        curl -f https://api.example.com/health
```

## DigitalOcean Deployment

### Create Cluster via CLI

```bash
# Install doctl
brew install doctl

# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --version 1.29.0 \
  --node-pool "name=pool-1;size=s-4vcpu-8gb;count=3"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-cluster

# Verify
kubectl get nodes
```

### DOKS CI/CD

```yaml
- name: Deploy to DigitalOcean
  run: |
    # Get cluster credentials
    doctl kubernetes cluster kubeconfig save todo-cluster

    # Deploy with Helm
    helm upgrade --install todo-app ./helm/todo-app \
      --set image.tag=${{ github.sha }} \
      --set image.registry=registry.digitalocean.com/todo-app \
      --namespace production
```

## Google Cloud Deployment

### Create Cluster via CLI

```bash
# Set project
gcloud config set project project-id

# Create cluster
gcloud container clusters create todo-cluster \
  --region=us-central1 \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=5

# Get credentials
gcloud container clusters get-credentials todo-cluster \
  --region=us-central1
```

### GCR Push

```bash
# Tag for GCR
docker tag image:tag gcr.io/project-id/image:tag

# Push to GCR
docker push gcr.io/project-id/image:tag
```

### GKE CI/CD

```yaml
- name: Authenticate to GCR
  uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCR_JSON_KEY }}

- name: Configure gcloud
  uses: google-github-actions/setup-gcloud@v2

- name: Deploy to GKE
  run: |
    gcloud container clusters get-credentials todo-cluster \
      --region=us-central1

    helm upgrade --install todo-app ./helm/todo-app \
      --set image.tag=${{ github.sha }} \
      --set image.registry=gcr.io/project-id
```

## Azure Deployment

### Create Cluster via CLI

```bash
# Create resource group
az group create --name todo-rg --location eastus

# Create cluster
az aks create \
  --resource-group todo-rg \
  --name todo-cluster \
  --node-count 3 \
  --node-vm-size Standard_B4ms \
  --enable-managed-identity \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 5

# Get credentials
az aks get-credentials \
  --resource-group todo-rg \
  --name todo-cluster
```

### ACR Push

```bash
# Login to ACR
az acr login --name registry

# Tag for ACR
docker tag image:tag registry.azurecr.io/image:tag

# Push to ACR
docker push registry.azurecr.io/image:tag
```

### AKS CI/CD

```yaml
- name: Login to Azure
  uses: azure/login@v2
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}

- name: Deploy to AKS
  run: |
    az aks get-credentials \
      --resource-group todo-rg \
      --name todo-cluster

    helm upgrade --install todo-app ./helm/todo-app \
      --set image.tag=${{ github.sha }} \
      --set image.registry=registry.azurecr.io
```

## Secrets Management

### GitHub Secrets Required

```
# Container Registry
- GITHUB_TOKEN (automatic)
- REGISTRY_PASSWORD (if using private registry)

# Kubernetes
- KUBECONFIG (base64 encoded kubeconfig file)
- KUBECONFIG_STAGING (staging cluster)
- KUBECONFIG_PROD (production cluster)

# Cloud Providers
- GCR_JSON_KEY (Google Cloud)
- AZURE_CREDENTIALS (Azure)
- DIGITALOCEAN_TOKEN (DigitalOcean)

# Application Secrets
- DATABASE_URL
- JWT_SECRET_KEY
- GROQ_API_KEY
- GEMINI_API_KEY
```

### Create KUBECONFIG Secret

```bash
# Get kubeconfig
kubectl config view --minify --flatten > kubeconfig

# Base64 encode
cat kubeconfig | base64 -w 0

# Add to GitHub Secrets
# Repository > Settings > Secrets > New secret
# Name: KUBECONFIG
# Value: <base64-output>
```

## Health Checks

### Kubernetes Readiness Probe

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### CI/CD Health Check

```yaml
- name: Health check
  run: |
    # Wait for rollout
    kubectl rollout status deployment/backend -n production --timeout=300s

    # Check pod readiness
    kubectl wait --for=condition=ready pod -l app=backend -n production --timeout=300s

    # Test endpoint
    kubectl run -it --rm health-check --image=curlimages/curl --restart=Never \
      -- curl -f http://backend-service:8000/health
```

## Rollback Strategies

### Automatic Rollback on Failure

```yaml
- name: Deploy with rollback
  run: |
    # Deploy
    helm upgrade --install todo-app ./helm/todo-app \
      --set image.tag=${{ github.sha }} \
      --namespace production || \
    (helm rollback todo-app --namespace production && exit 1)
```

### Manual Rollback

```bash
# List revisions
helm history todo-app --namespace production

# Rollback to previous
helm rollback todo-app --namespace production

# Rollback to specific revision
helm rollback todo-app 2 --namespace production
```

## Monitoring Deployments

### Deployment Status

```bash
# Check rollout status
kubectl rollout status deployment/backend

# Check rollout history
kubectl rollout history deployment/backend

# Get recent pods
kubectl get pods -l app=backend --sort-by=.metadata.creationTimestamp
```

### Deployment Metrics

```bash
# Pod resource usage
kubectl top pods -l app=backend

# Node resource usage
kubectl top nodes

# Events
kubectl get events --sort-by=.metadata.creationTimestamp
```

## Best Practices

### Branch Strategy

- `main` - Production deployments
- `develop` - Staging deployments
- `feature/*` - PR testing only

### Tagging Strategy

```bash
# Use git SHA for immutable tags
IMAGE_TAG=${{ github.sha }}

# Use semantic versioning for releases
IMAGE_TAG=${{ github.ref_name }} # v1.0.0
```

### Blue-Green Deployment

```yaml
- name: Blue-Green Deploy
  run: |
    # Deploy to green
    helm upgrade --install todo-app-green ./helm/todo-app \
      --set image.tag=${{ github.sha }}

    # Wait for green ready
    kubectl wait --for=condition=ready pod -l app=todo-app-green

    # Switch service to green
    kubectl patch service todo-app \
      -p '{"spec":{"selector":{"app":"todo-app-green"}}}'

    # Clean up blue
    helm uninstall todo-app-blue
```

## Troubleshooting

### Pipeline Failures

```bash
# Check workflow logs in GitHub Actions
# Repository > Actions > Workflow Run > Job > Step

# Test locally
act -j test-job  # using act CLI

# Debug deployment
helm template --debug chart-name
helm install --dry-run --debug chart-name
```

### Registry Issues

```bash
# Test registry access
docker pull registry/image:tag

# Verify authentication
docker login registry

# Check image exists
helm repo update
helm search repo chart-name
```

## For More Information

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Kubernetes Deployment Strategies](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
