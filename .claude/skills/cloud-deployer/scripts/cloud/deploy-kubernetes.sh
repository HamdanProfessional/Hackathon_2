#!/bin/bash
# Cloud deployment to Kubernetes (DOKS/GKE/AKS)
# Usage: ./scripts/cloud/deploy-kubernetes.sh [deploy|rollback|status]

set -e

ACTION=${1:-deploy}
CLUSTER=${CLUSTER:-}
NAMESPACE=${NAMESPACE:-default}
REGISTRY=${REGISTRY:-registry.digitalocean.com}
PROJECT=${PROJECT:-todo-app}

# Check cluster context
check_cluster() {
  if [ -z "$CLUSTER" ]; then
    echo "Error: CLUSTER environment variable not set"
    echo "Usage: CLUSTER=do-fra1-mycluster $0 deploy"
    exit 1
  fi
  kubectl config use-context $CLUSTER
}

# Build and push images
build_images() {
  echo "Building and pushing images..."

  BACKEND_TAG=${REGISTRY}/${PROJECT}/backend:$(git rev-parse --short HEAD)
  FRONTEND_TAG=${REGISTRY}/${PROJECT}/frontend:$(git rev-parse --short HEAD)

  # Build backend
  docker build -t $BACKEND_TAG -f backend/Dockerfile backend/
  docker push $BACKEND_TAG

  # Build frontend
  docker build -t $FRONTEND_TAG -f frontend/Dockerfile frontend/
  docker push $FRONTEND_TAG

  # Update deployment images
  kubectl set image deployment/todo-backend backend=$BACKEND_TAG -n $NAMESPACE
  kubectl set image deployment/todo-frontend frontend=$FRONTEND_TAG -n $NAMESPACE
}

case "$ACTION" in
  deploy)
    check_cluster
    echo "Deploying to Kubernetes cluster: $CLUSTER"

    # Apply secrets and configmaps
    kubectl apply -f k8s/backend/secrets.yaml -n $NAMESPACE
    kubectl apply -f k8s/backend/configmap.yaml -n $NAMESPACE

    # Build and push images
    build_images

    # Apply deployments and services
    kubectl apply -f k8s/backend/deployment.yaml -n $NAMESPACE
    kubectl apply -f k8s/backend/service.yaml -n $NAMESPACE
    kubectl apply -f k8s/frontend/deployment.yaml -n $NAMESPACE
    kubectl apply -f k8s/frontend/service.yaml -n $NAMESPACE

    echo "Waiting for rollout..."
    kubectl rollout status deployment/todo-backend -n $NAMESPACE --timeout=5m
    kubectl rollout status deployment/todo-frontend -n $NAMESPACE --timeout=5m

    echo "Deployment complete!"
    kubectl get pods,svc -n $NAMESPACE
    ;;
  rollback)
    check_cluster
    REVISION=${2:-}
    if [ -z "$REVISION" ]; then
      echo "Available revisions:"
      kubectl rollout history deployment/todo-backend -n $NAMESPACE
      echo "Usage: $0 rollback <revision>"
      exit 1
    fi
    kubectl rollout undo deployment/todo-backend --to-revision=$REVISION -n $NAMESPACE
    kubectl rollout undo deployment/todo-frontend --to-revision=$REVISION -n $NAMESPACE
    ;;
  status)
    check_cluster
    echo "Cluster: $CLUSTER"
    echo "Namespace: $NAMESPACE"
    echo ""
    kubectl get all -n $NAMESPACE
    echo ""
    kubectl get ingress -n $NAMESPACE
    ;;
  logs)
    check_cluster
    POD=${2:-}
    if [ -z "$POD" ]; then
      kubectl get pods -n $NAMESPACE
      echo "Usage: $0 logs <pod-name>"
      exit 1
    fi
    kubectl logs -f $POD -n $NAMESPACE
    ;;
  restart)
    check_cluster
    kubectl rollout restart deployment/todo-backend -n $NAMESPACE
    kubectl rollout restart deployment/todo-frontend -n $NAMESPACE
    ;;
  scale)
    check_cluster
    REPLICAS=${2:-2}
    kubectl scale deployment/todo-backend --replicas=$REPLICAS -n $NAMESPACE
    kubectl scale deployment/todo-frontend --replicas=$REPLICAS -n $NAMESPACE
    ;;
  *)
    echo "Usage: $0 [deploy|rollback|status|logs|restart|scale]"
    exit 1
    ;;
esac
