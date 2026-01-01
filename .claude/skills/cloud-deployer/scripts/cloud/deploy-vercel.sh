#!/bin/bash
# Cloud deployment to Vercel
# Usage: ./scripts/cloud/deploy-vercel.sh [frontend|backend|all] [preview|prod]

set -e

SERVICE=${1:-all}
ENV=${2:-prod}

vercel_deploy() {
  local DIR=$1
  local PROJECT_NAME=$2
  local ENV_FLAG=$3

  echo "Deploying $DIR to Vercel ($ENV)..."

  if [ "$ENV" = "prod" ]; then
    ENV_FLAG="--prod"
  fi

  cd $DIR
  npx vercel deploy $ENV_FLAG --yes --token $VERCEL_TOKEN
  cd ..
}

case "$SERVICE" in
  frontend)
    vercel_deploy "frontend" "todo-frontend" $ENV
    ;;
  backend)
    vercel_deploy "backend" "todo-backend" $ENV
    ;;
  all)
    vercel_deploy "backend" "todo-backend" $ENV
    vercel_deploy "frontend" "todo-frontend" $ENV
    ;;
  list)
    echo "Vercel deployments:"
    npx vercel list --token $VERCEL_TOKEN
    ;;
  inspect)
    PROJECT=${2:-}
    if [ -z "$PROJECT" ]; then
      echo "Usage: $0 inspect <project-name>"
      exit 1
    fi
    npx vercel inspect $PROJECT --token $VERCEL_TOKEN
    ;;
  logs)
    PROJECT=${2:-}
    if [ -z "$PROJECT" ]; then
      echo "Usage: $0 logs <project-name>"
      exit 1
    fi
    npx vercel logs $PROJECT --token $VERCEL_TOKEN
    ;;
  *)
    echo "Usage: $0 [frontend|backend|all|list|inspect|logs] [preview|prod]"
    exit 1
    ;;
esac
