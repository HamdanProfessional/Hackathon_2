#!/bin/bash
# ==============================================================================
# DigitalOcean Kubernetes (DOKS) Deployment Script
# ==============================================================================
# This script deploys applications to DigitalOcean Kubernetes clusters
#
# Usage:
#   ./deploy-doks.sh                    # Interactive mode
#   ./deploy-doks.sh --cluster my-k8s  # Specify cluster
#   ./deploy-doks.sh --skip-build      # Skip Docker build
# ==============================================================================

set -e  # Exit on error
set -o pipefail  # Catch errors in pipes

# ==============================================================================
# CONFIGURATION
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"

# Default values
CLUSTER_NAME="${CLUSTER_NAME:-}"
REGION="${REGION:-nyc1}"
NAMESPACE="${NAMESPACE:-todo-app}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-registry.digitalocean.com}"
DOCKER_IMAGE="${DOCKER_IMAGE:-todo-backend}"
DOCKER_TAG="${DOCKER_TAG:-latest}"
SKIP_BUILD="${SKIP_BUILD:-false}"
SKIP_PUSH="${SKIP_PUSH:-false}"
DRY_RUN="${DRY_RUN:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==============================================================================
# FUNCTIONS
# ==============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

check_dependencies() {
    log_info "Checking dependencies..."

    local missing_deps=()

    command -v doctl >/dev/null 2>&1 || missing_deps+=("doctl")
    command -v kubectl >/dev/null 2>&1 || missing_deps+=("kubectl")
    command -v docker >/dev/null 2>&1 || missing_deps+=("docker")

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        echo ""
        echo "Install missing tools:"
        for dep in "${missing_deps[@]}"; do
            case $dep in
                doctl)
                    echo "  doctl:  curl -sSL https://digitalocean.com/doctl/install.sh | bash"
                    ;;
                kubectl)
                    echo "  kubectl: curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                    ;;
                docker)
                    echo "  docker:  https://docs.docker.com/get-docker/"
                    ;;
            esac
        done
        exit 1
    fi

    log_success "All dependencies found"
}

install_doctl() {
    if ! command -v doctl >/dev/null 2>&1; then
        log_info "Installing doctl..."
        curl -sSL https://digitalocean.com/doctl/install.sh | bash
        log_success "doctl installed"
    fi
}

authenticate_doctl() {
    log_info "Authenticating with DigitalOcean..."

    if ! doctl account get >/dev/null 2>&1; then
        log_warning "Not authenticated with DigitalOcean"
        echo "Please authenticate:"
        doctl auth init
    fi

    local account=$(doctl account get --format Email --no-header 2>/dev/null)
    log_success "Authenticated as: $account"
}

select_cluster() {
    log_info "Available Kubernetes clusters:"

    local clusters=($(doctl kubernetes cluster list --format Name --no-header 2>/dev/null))

    if [ ${#clusters[@]} -eq 0 ]; then
        log_error "No Kubernetes clusters found"
        echo ""
        echo "Create a cluster with:"
        echo "  doctl kubernetes cluster create --region nyc1 --size s-2vcpu-4gb --count 3 my-cluster"
        exit 1
    fi

    echo ""
    local i=1
    for cluster in "${clusters[@]}"; do
        echo "  [$i] $cluster"
        ((i++))
    done

    if [ -z "$CLUSTER_NAME" ]; then
        echo ""
        read -p "Select cluster [1-${#clusters[@]}]: " selection

        if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "${#clusters[@]}" ]; then
            CLUSTER_NAME="${clusters[$((selection-1))]}"
        else
            log_error "Invalid selection"
            exit 1
        fi
    fi

    log_success "Selected cluster: $CLUSTER_NAME"
}

configure_kubectl() {
    log_info "Configuring kubectl for cluster: $CLUSTER_NAME"

    local cluster_id=$(doctl kubernetes cluster get "$CLUSTER_NAME" --format ID --no-header)

    if [ -z "$cluster_id" ]; then
        log_error "Cluster not found: $CLUSTER_NAME"
        exit 1
    fi

    doctl kubernetes cluster kubeconfig save "$CLUSTER_NAME" >/dev/null 2>&1

    # Verify connection
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "Cannot connect to cluster"
        exit 1
    fi

    log_success "kubectl configured for cluster: $CLUSTER_NAME"
}

create_namespace() {
    log_info "Ensuring namespace exists: $NAMESPACE"

    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY RUN] Would create namespace: $NAMESPACE"
        return
    fi

    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    log_success "Namespace ready: $NAMESPACE"
}

build_docker_image() {
    if [ "$SKIP_BUILD" = "true" ]; then
        log_info "Skipping Docker build"
        return
    fi

    print_header "Building Docker Image"

    cd "$PROJECT_ROOT"

    local dockerfile="${DOCKERFILE:-backend/Dockerfile}"
    local context="${DOCKER_CONTEXT:-backend}"

    if [ ! -f "$dockerfile" ]; then
        log_error "Dockerfile not found: $dockerfile"
        exit 1
    fi

    log_info "Building image: ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}"

    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY RUN] Would build: ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}"
        return
    fi

    docker build -f "$dockerfile" -t "${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}" "$context"

    log_success "Docker image built"
}

push_docker_image() {
    if [ "$SKIP_PUSH" = "true" ]; then
        log_info "Skipping Docker push"
        return
    fi

    log_info "Pushing image to registry..."

    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY RUN] Would push: ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}"
        return
    fi

    docker push "${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}"

    log_success "Image pushed to registry"
}

deploy_to_kubernetes() {
    print_header "Deploying to Kubernetes"

    cd "$PROJECT_ROOT"

    local manifests="${MANIFESTS:-k8s}"

    if [ ! -d "$manifests" ]; then
        log_error "Kubernetes manifests not found: $manifests"
        exit 1
    fi

    # Apply manifests in order
    local order=("secrets" "configmap" "deployment" "service" "ingress")

    for resource in "${order[@]}"; do
        local files=($(find "$manifests" -name "${resource}.yaml" -o -name "${resource}.yml" 2>/dev/null))

        if [ ${#files[@]} -gt 0 ]; then
            log_info "Applying $resource manifests..."

            for file in "${files[@]}"; do
                echo "  - $file"

                if [ "$DRY_RUN" = "true" ]; then
                    echo "[DRY RUN] Would apply: $file"
                else
                    kubectl apply -n "$NAMESPACE" -f "$file"
                fi
            done
        fi
    done

    log_success "Kubernetes manifests applied"
}

wait_for_deployment() {
    log_info "Waiting for deployment to be ready..."

    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY RUN] Would wait for deployment"
        return
    fi

    kubectl wait --for=condition=available deployment -l app=backend -n "$NAMESPACE" --timeout=5m

    log_success "Deployment is ready"
}

get_deployment_status() {
    print_header "Deployment Status"

    echo "Pods:"
    kubectl get pods -n "$NAMESPACE" -l app=backend

    echo ""
    echo "Services:"
    kubectl get svc -n "$NAMESPACE"

    echo ""
    echo "Ingress:"
    kubectl get ingress -n "$NAMESPACE" 2>/dev/null || echo "No ingress found"
}

get_service_url() {
    local ingress_url=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' 2>/dev/null)

    if [ -n "$ingress_url" ]; then
        echo ""
        log_success "Application URL: http://$ingress_url"
    fi
}

print_logs() {
    echo ""
    read -p "View logs? (y/N): " view_logs

    if [[ "$view_logs" =~ ^[Yy]$ ]]; then
        kubectl logs -n "$NAMESPACE" -l app=backend --tail=100 -f
    fi
}

cleanup() {
    log_info "Cleaning up old resources..."

    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY RUN] Would cleanup old resources"
        return
    fi

    # Remove old Docker images
    local image_count=$(docker images "${DOCKER_REGISTRY}/${DOCKER_IMAGE}" --format "{{.Tag}}" | wc -l)

    if [ "$image_count" -gt 5 ]; then
        docker images "${DOCKER_REGISTRY}/${DOCKER_IMAGE}" --format "{{.Tag}}" | tail -n +6 | while read -r tag; do
            docker rmi "${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${tag}" 2>/dev/null || true
        done
        log_success "Cleaned up old Docker images"
    fi
}

show_help() {
    cat << EOF
DigitalOcean Kubernetes Deployment Script

Usage: $0 [OPTIONS]

Options:
  -c, --cluster NAME      Cluster name (default: interactive selection)
  -n, --namespace NAME    Kubernetes namespace (default: todo-app)
  -r, --region REGION     DigitalOcean region (default: nyc1)
  -i, --image NAME        Docker image name (default: todo-backend)
  -t, --tag TAG          Docker image tag (default: latest)
      --skip-build        Skip Docker build
      --skip-push         Skip Docker push
      --dry-run           Show what would be done without executing
  -h, --help             Show this help message

Examples:
  $0                                    # Interactive mode
  $0 --cluster my-k8s                  # Use specific cluster
  $0 --skip-build --tag v1.0.0         # Use existing image
  $0 --namespace production --dry-run  # Preview production deployment

Environment Variables:
  CLUSTER_NAME              Kubernetes cluster name
  NAMESPACE                 Kubernetes namespace
  REGION                    DigitalOcean region
  DOCKER_REGISTRY          Docker registry
  DOCKER_IMAGE             Docker image name
  DOCKER_TAG               Docker image tag
  SKIP_BUILD               Skip Docker build
  SKIP_PUSH                Skip Docker push
  DRY_RUN                  Dry run mode
EOF
}

# ==============================================================================
# MAIN
# ==============================================================================

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--cluster)
                CLUSTER_NAME="$2"
                shift 2
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -i|--image)
                DOCKER_IMAGE="$2"
                shift 2
                ;;
            -t|--tag)
                DOCKER_TAG="$2"
                shift 2
                ;;
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --skip-push)
                SKIP_PUSH=true
                shift
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
}

main() {
    parse_args "$@"

    print_header "DigitalOcean Kubernetes Deployment"

    # Setup
    check_dependencies
    install_doctl
    authenticate_doctl
    select_cluster
    configure_kubectl

    # Prepare
    create_namespace
    build_docker_image
    push_docker_image

    # Deploy
    deploy_to_kubernetes
    wait_for_deployment

    # Status
    get_deployment_status
    get_service_url

    # Optional
    cleanup
    print_logs

    log_success "Deployment complete!"
}

main "$@"
