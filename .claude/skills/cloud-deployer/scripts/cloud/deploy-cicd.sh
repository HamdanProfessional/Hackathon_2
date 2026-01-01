#!/bin/bash
# Setup GitHub Actions CI/CD pipeline
# Usage: ./scripts/cloud/deploy-cicd.sh [setup|validate]

set -e

ACTION=${1:-setup}
WORKFLOW_DIR=.github/workflows

case "$ACTION" in
  setup)
    echo "Setting up GitHub Actions CI/CD..."

    mkdir -p $WORKFLOW_DIR

    # Create CI/CD workflow
    cat > $WORKFLOW_DIR/ci-cd.yml <<'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: registry.digitalocean.com
  IMAGE_NAME_BACKEND: todo-backend
  IMAGE_NAME_FRONTEND: todo-frontend

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run backend tests
        run: |
          cd backend
          pytest

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci

      - name: Run frontend tests
        run: |
          cd frontend
          npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      backend-tag: ${{ steps.meta-backend.outputs.tags }}
      frontend-tag: ${{ steps.meta-frontend.outputs.tags }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to DO Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Extract metadata for backend
        id: meta-backend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME_BACKEND }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=sha,prefix={{branch}}-

      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta-backend.outputs.tags }}
          labels: ${{ steps.meta-backend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Extract metadata for frontend
        id: meta-frontend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME_FRONTEND }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=sha,prefix={{branch}}-

      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ${{ steps.meta-frontend.outputs.tags }}
          labels: ${{ steps.meta-frontend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Save DO kubeconfig
        run: doctl kubernetes cluster kubeconfig save ${{ secrets.KUBERNETES_CLUSTER }}

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/todo-backend \
            backend=${{ needs.build.outputs.backend-tag }} \
            -n ${{ secrets.KUBERNETES_NAMESPACE }}

          kubectl set image deployment/todo-frontend \
            frontend=${{ needs.build.outputs.frontend-tag }} \
            -n ${{ secrets.KUBERNETES_NAMESPACE }}

          kubectl rollout status deployment/todo-backend -n ${{ secrets.KUBERNETES_NAMESPACE }}
          kubectl rollout status deployment/todo-frontend -n ${{ secrets.KUBERNETES_NAMESPACE }}
EOF

    echo "GitHub Actions workflow created at $WORKFLOW_DIR/ci-cd.yml"
    echo ""
    echo "Required secrets to configure in GitHub:"
    echo "  - DIGITALOCEAN_ACCESS_TOKEN"
    echo "  - DOCKER_USERNAME"
    echo "  - DOCKER_PASSWORD"
    echo "  - KUBERNETES_CLUSTER"
    echo "  - KUBERNETES_NAMESPACE"
    echo "  - VERCEL_TOKEN (if using Vercel)"
    ;;
  validate)
    if [ -f "$WORKFLOW_DIR/ci-cd.yml" ]; then
      echo "Workflow file exists"
      echo "Validating syntax..."
      # Check if yamllint is available
      if command -v yamllint &> /dev/null; then
        yamllint $WORKFLOW_DIR/ci-cd.yml
      else
        echo "yamllint not installed, skipping validation"
      fi
    else
      echo "Error: Workflow file not found at $WORKFLOW_DIR/ci-cd.yml"
      exit 1
    fi
    ;;
  *)
    echo "Usage: $0 [setup|validate]"
    exit 1
    ;;
esac
