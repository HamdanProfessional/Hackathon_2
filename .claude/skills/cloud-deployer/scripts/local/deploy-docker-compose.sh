#!/bin/bash
# Local deployment using Docker Compose
# Usage: ./scripts/local/deploy-docker-compose.sh [up|down|restart]

set -e

ACTION=${1:-up}
PROJECT_NAME=${PROJECT_NAME:-todo-app}

case "$ACTION" in
  up)
    echo "Starting local development environment..."
    docker-compose up -d
    echo "Services starting..."
    echo "- Frontend: http://localhost:3000"
    echo "- Backend: http://localhost:8000"
    echo "- API Docs: http://localhost:8000/docs"
    ;;
  down)
    echo "Stopping local development environment..."
    docker-compose down
    ;;
  restart)
    echo "Restarting services..."
    docker-compose restart
    ;;
  logs)
    docker-compose logs -f
    ;;
  build)
    echo "Building images..."
    docker-compose build
    ;;
  *)
    echo "Usage: $0 [up|down|restart|logs|build]"
    exit 1
    ;;
esac
