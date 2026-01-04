#!/bin/bash
# ==============================================================================
# DigitalOcean App Platform Deployment Script
# ==============================================================================
# This script deploys applications to DigitalOcean App Platform
#
# Usage:
#   ./deploy-app-platform.sh                    # Interactive mode
#   ./deploy-app-platform.sh --app my-app      # Specify app name
#   ./deploy-app-platform.sh --spec app.yaml   # Use existing spec
# ==============================================================================

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"

# Configuration
APP_NAME="${APP_NAME:-}"
SPEC_FILE="${SPEC_FILE:-.do/app.yaml}"
PROJECT_NAME="${PROJECT_NAME:-todo-project}"
REGION="${REGION:-nyc3}"
ENV="${ENV:-production}"
DRY_RUN="${DRY_RUN:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

check_dependencies() {
    log_info "Checking dependencies..."

    if ! command -v doctl >/dev/null 2>&1; then
        log_warning "doctl not found. Installing..."
        curl -sSL https://digitalocean.com/doctl/install.sh | bash
    fi

    if ! command -v jq >/dev/null 2>&1; then
        log_warning "jq not found. Please install for JSON parsing."
    fi

    log_success "Dependencies ready"
}

authenticate_doctl() {
    log_info "Authenticating with DigitalOcean..."

    if ! doctl account get >/dev/null 2>&1; then
        doctl auth init
    fi

    local account=$(doctl account get --format Email --no-header 2>/dev/null)
    log_success "Authenticated as: $account"
}

create_app_spec() {
    print_header "Creating App Specification"

    local repo_url=$(git config --get remote.origin.url 2>/dev/null || echo "your-org/todo-app")
    local branch=$(git branch --show-current 2>/dev/null || echo "main")

    cat > "$SPEC_FILE" << EOF
name: ${APP_NAME:-todo-backend}
region: ${REGION}
services:
- name: backend
  github:
    repo: ${repo_url}
    branch: ${branch}
  dockerfile_path: backend/Dockerfile
  build_command: pip install -r requirements.txt
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_size_slug: basic-xxs
  instance_count: 2
  http_port: 8080

  envs:
  - key: PORT
    value: "8080"
  - key: APP_ENV
    value: "${ENV}"
  - key: PYTHON_VERSION
    value: "3.11"

  health_check:
    http_path: /health
    initial_delay_seconds: 30
    period_seconds: 10
    timeout_seconds: 5
    success_threshold: 1
    failure_threshold: 3

  autoscaling:
    min_instance_count: 2
    max_instance_count: 10
    cpu_threshold: 70
    memory_threshold: 80

  routes:
  - path: /api
    preserve_path_prefix: false

databases:
- name: todo-db
  engine: PG
  version: "15"
  size: db-s-1vcpu-1gb
  num_nodes: 1
  production: true

jobs:
- name: db-migrate
  kind: PRE_DEPLOY
  github:
    repo: ${repo_url}
    branch: ${branch}
  dockerfile_path: backend/Dockerfile
  run_command: alembic upgrade head
  environment_slug: python
  instance_count: 1

  envs:
  - key: DATABASE_URL
    value: \${db.DATABASE_URL}
EOF

    log_success "App spec created: $SPEC_FILE"
}

deploy_app() {
    print_header "Deploying to App Platform"

    if [ ! -f "$SPEC_FILE" ]; then
        log_error "Spec file not found: $SPEC_FILE"
        create_app_spec
    fi

    log_info "Deploying app from spec: $SPEC_FILE"

    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY RUN] Would deploy app using: $SPEC_FILE"
        cat "$SPEC_FILE"
        return
    fi

    # Create or update app
    local existing_app=$(doctl apps list --format Name --no-header 2>/dev/null | grep "^${APP_NAME}$" || true)

    if [ -n "$existing_app" ]; then
        log_info "Updating existing app: $APP_NAME"
        APP_ID=$(doctl apps list --format ID,Name --no-header | grep "$APP_NAME" | awk '{print $1}')
        doctl apps update "$APP_ID" --spec "$SPEC_FILE"
    else
        log_info "Creating new app: $APP_NAME"
        APP_ID=$(doctl apps create --spec "$SPEC_FILE" --output json | jq -r '.app.id')
    fi

    log_success "App deployment initiated: $APP_ID"
}

wait_for_deployment() {
    log_info "Waiting for deployment to complete..."

    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY RUN] Would wait for deployment"
        return
    fi

    doctl apps wait-for-deployment "$APP_ID"

    log_success "Deployment complete"
}

get_deployment_info() {
    print_header "Deployment Information"

    local app_info=$(doctl apps get "$APP_ID" --format ID,Name,Region,DefaultIngress --no-header 2>/dev/null)

    if [ -n "$app_info" ]; then
        echo "$app_info" | awk '{
            print "ID:        " $1
            print "Name:      " $2
            print "Region:    " $3
            print "URL:       " $4
        }'
    fi

    echo ""
    echo "Active Deployments:"
    doctl apps list-deployments "$APP_ID" --format ID,CreatedAt,Progress,State --no-header 2>/dev/null | head -5
}

print_logs() {
    echo ""
    read -p "View logs? (y/N): " view_logs

    if [[ "$view_logs" =~ ^[Yy]$ ]]; then
        local deployment_id=$(doctl apps list-deployments "$APP_ID" --format ID --no-header 2>/dev/null | head -1)
        doctl apps logs "$APP_ID" --deployment "$deployment_id" --type build --follow 2>/dev/null || \
        doctl apps logs "$APP_ID" --type run --follow 2>/dev/null
    fi
}

show_help() {
    cat << EOF
DigitalOcean App Platform Deployment Script

Usage: $0 [OPTIONS]

Options:
  -a, --app NAME          App name
  -s, --spec FILE         App specification file
  -p, --project NAME      Project name
  -r, --region REGION     DigitalOcean region
  -e, --env ENVIRONMENT   Environment (production/staging/development)
      --dry-run           Show what would be done
  -h, --help              Show this help

Examples:
  $0                                    # Interactive mode
  $0 --app todo-backend                 # Create/update app
  $0 --spec app.yaml --dry-run         # Preview deployment

Environment Variables:
  APP_NAME                 App name
  SPEC_FILE                App spec file
  PROJECT_NAME             Project name
  REGION                   DigitalOcean region
  ENV                      Environment name
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -a|--app)
                APP_NAME="$2"
                shift 2
                ;;
            -s|--spec)
                SPEC_FILE="$2"
                shift 2
                ;;
            -p|--project)
                PROJECT_NAME="$2"
                shift 2
                ;;
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -e|--env)
                ENV="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Set default app name if not provided
    if [ -z "$APP_NAME" ]; then
        APP_NAME="${PROJECT_NAME}-backend"
    fi
}

main() {
    parse_args "$@"

    print_header "DigitalOcean App Platform Deployment"

    check_dependencies
    authenticate_doctl
    create_app_spec
    deploy_app
    wait_for_deployment
    get_deployment_info
    print_logs

    log_success "App Platform deployment complete!"
}

main "$@"
