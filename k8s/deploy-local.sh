#!/bin/bash
# Local/Minikube Deployment Script
# This script deploys the Todo application to a local Minikube cluster
# without affecting production deployments on Digital Ocean.

set -e

echo "========================================="
echo "Deploying Todo App to Local Minikube"
echo "========================================="
echo ""

# Check if minikube is running
echo "Checking Minikube status..."
if ! minikube status &> /dev/null; then
    echo "Error: Minikube is not running. Start it with: minikube start"
    exit 1
fi
echo "Minikube is running"
echo ""

# Set namespace to default (NOT production)
NAMESPACE="default"

# Function to deploy a component
deploy_component() {
    local name=$1
    local path=$2
    echo "Deploying $name..."
    kubectl apply -f "$path" -n "$NAMESPACE"
}

# Deploy backend
echo ""
echo "========================================="
echo "1. Backend Deployment"
echo "========================================="
deploy_component "Backend ConfigMap" "k8s/backend/configmap.yaml"
deploy_component "Backend Secrets" "k8s/backend/secrets.yaml"
deploy_component "Backend Deployment" "k8s/backend/deployment.yaml"
deploy_component "Backend Service" "k8s/backend/service.yaml"
deploy_component "Backend Ingress" "k8s/backend/ingress.yaml"

# Deploy frontend
echo ""
echo "========================================="
echo "2. Frontend Deployment"
echo "========================================="
deploy_component "Frontend Deployment" "k8s/frontend/deployment.yaml"
deploy_component "Frontend Service" "k8s/frontend/service.yaml"
deploy_component "Frontend Ingress" "k8s/frontend/ingress.yaml"

# Wait for deployments to be ready
echo ""
echo "========================================="
echo "3. Waiting for deployments to be ready..."
echo "========================================="
kubectl wait --for=condition=available deployment/todo-backend -n "$NAMESPACE" --timeout=300s || true
kubectl wait --for=condition=available deployment/todo-frontend -n "$NAMESPACE" --timeout=300s || true

# Show status
echo ""
echo "========================================="
echo "4. Deployment Status"
echo "========================================="
kubectl get pods -n "$NAMESPACE"
kubectl get svc -n "$NAMESPACE"
kubectl get ingress -n "$NAMESPACE"

echo ""
echo "========================================="
echo "Local deployment complete!"
echo "========================================="
echo ""
echo "Access URLs:"
echo "  Backend NodePort: $(minikube service todo-backend --url -n "$NAMESPACE")"
echo "  Frontend NodePort: $(minikube service todo-frontend --url -n "$NAMESPACE")"
echo ""
echo "For ingress access, add to /etc/hosts:"
echo "  $(minikube ip) todo-backend.local"
echo "  $(minikube ip) todo.local"
echo ""
echo "Then access:"
echo "  Backend: http://todo-backend.local"
echo "  Frontend: http://todo.local"
echo ""
