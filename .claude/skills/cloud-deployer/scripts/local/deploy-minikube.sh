#!/bin/bash
# Local Kubernetes deployment using Minikube
# Usage: ./scripts/local/deploy-minikube.sh [start|stop|deploy|delete]

set -e

ACTION=${1:-deploy}
NAMESPACE=${NAMESPACE:-default}
REGISTRY=${REGISTRY:-localhost:5000}

case "$ACTION" in
  start)
    echo "Starting Minikube..."
    minikube start --driver=docker --cpus=4 --memory=8192
    minikube addons enable ingress
    echo "Enabling local registry..."
    docker run -d -p 5000:5000 --name registry registry:2
    ;;
  stop)
    echo "Stopping Minikube..."
    minikube stop
    ;;
  deploy)
    echo "Deploying to Minikube..."
    eval $(minikube docker-env)

    # Build images for Minikube
    docker build -t ${REGISTRY}/backend:latest -f backend/Dockerfile backend/
    docker build -t ${REGISTRY}/frontend:latest -f frontend/Dockerfile frontend/

    # Apply Kubernetes manifests
    kubectl apply -f k8s/backend/
    kubectl apply -f k8s/frontend/

    echo "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=backend --timeout=120s -n $NAMESPACE
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=frontend --timeout=120s -n $NAMESPACE

    echo "Access application:"
    kubectl get svc -n $NAMESPACE
    ;;
  delete)
    echo "Deleting deployment..."
    kubectl delete -f k8s/frontend/
    kubectl delete -f k8s/backend/
    ;;
  tunnel)
    echo "Starting Minikube tunnel..."
    minikube tunnel
    ;;
  *)
    echo "Usage: $0 [start|stop|deploy|delete|tunnel]"
    exit 1
    ;;
esac
