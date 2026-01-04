#!/bin/bash
# ==============================================================================
# DigitalOcean Spaces CDN Deployment Script
# ==============================================================================
# This script deploys static assets to DigitalOcean Spaces with CDN
#
# Usage:
#   ./deploy-spaces-cdn.sh                       # Interactive mode
#   ./deploy-spaces-cdn.sh --spaces my-assets   # Specify Spaces name
#   ./deploy-spaces-cdn.sh --skip-build         # Skip build step
# ==============================================================================

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"

# Configuration
SPACES_NAME="${SPACES_NAME:-}"
REGION="${REGION:-nyc3}"
DOMAIN="${DOMAIN:-}"
SPACES_ENDPOINT="https://${REGION}.digitaloceanspaces.com"
SKIP_BUILD="${SKIP_BUILD:-false}"
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

    local missing_deps=()

    command -v aws >/dev/null 2>&1 || missing_deps+=("aws-cli")
    command -v doctl >/dev/null 2>&1 || missing_deps+=("doctl")

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        echo ""
        echo "Install AWS CLI for Spaces:"
        echo "  curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'"
        echo "  unzip -q awscliv2.zip"
        echo "  sudo ./aws/install"
        exit 1
    fi

    log_success "Dependencies ready"
}

authenticate_doctl() {
    log_info "Authenticating with DigitalOcean..."

    if ! doctl account get >/dev/null 2>&1; then
        doctl auth init
    fi

    log_success "Authenticated"
}

select_or_create_spaces() {
    print_header "Select or Create Spaces"

    log_info "Existing Spaces:"
    local spaces=($(doctl spaces list --format Name --no-header 2>/dev/null))

    echo ""
    if [ ${#spaces[@]} -eq 0 ]; then
        log_info "No Spaces found. Creating new one..."
    else
        local i=1
        for space in "${spaces[@]}"; do
            echo "  [$i] $space"
            ((i++))
        done

        echo "  [n] Create new Spaces"
        echo ""

        if [ -z "$SPACES_NAME" ]; then
            read -p "Select Spaces [1-${#spaces[@]} or n]: " selection

            if [[ "$selection" =~ ^[Nn]$ ]]; then
                # Create new
                :
            elif [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "${#spaces[@]}" ]; then
                SPACES_NAME="${spaces[$((selection-1))]}"
                log_success "Selected Spaces: $SPACES_NAME"
                return
            else
                log_error "Invalid selection"
                exit 1
            fi
        fi
    fi

    # Create new Spaces
    if [ -z "$SPACES_NAME" ]; then
        read -p "Enter Spaces name: " SPACES_NAME
        read -p "Enter region [nyc3]: " region_input
        REGION="${region_input:-nyc3}"

        log_info "Creating Spaces: $SPACES_NAME"

        if [ "$DRY_RUN" = "true" ]; then
            echo "[DRY RUN] Would create Spaces: $SPACES_NAME"
        else
            doctl spaces create "$SPACES_NAME" --region "$REGION"
        fi

        log_success "Spaces created: $SPACES_NAME"
    fi
}

build_frontend() {
    if [ "$SKIP_BUILD" = "true" ]; then
        log_info "Skipping build step"
        return
    fi

    print_header "Building Frontend"

    cd "$PROJECT_ROOT"

    if [ -d "frontend" ]; then
        cd frontend
    elif [ -f "package.json" ]; then
        : # Already in frontend directory
    else
        log_warning "No frontend directory found"
        return
    fi

    # Detect build tool
    if [ -f "package.json" ]; then
        if grep -q '"build"' package.json; then
            log_info "Running npm run build..."

            if [ "$DRY_RUN" = "true" ]; then
                echo "[DRY RUN] Would run: npm run build"
            else
                npm run build
            fi

            log_success "Frontend built"
        else
            log_warning "No build script found in package.json"
        fi
    fi

    cd "$PROJECT_ROOT"
}

configure_spaces_cdn() {
    print_header "Configuring Spaces CDN"

    local spaces_info=$(doctl spaces get "$SPACES_NAME" --format Name,CDN_Endpoint --no-header 2>/dev/null)

    if echo "$spaces_info" | grep -q "True"; then
        log_success "CDN already enabled"
        return
    fi

    log_info "Enabling CDN for Spaces..."

    if [ -z "$DOMAIN" ]; then
        read -p "Enter custom domain (optional, press Enter to skip): " DOMAIN
    fi

    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY RUN] Would enable CDN for Spaces: $SPACES_NAME"
        return
    fi

    # Enable CDN
    doctl spaces cdn create "$SPACES_NAME" --ttl 3600

    if [ -n "$DOMAIN" ]; then
        log_info "Setting custom domain: $DOMAIN"
        doctl spaces cdn set-custom-domain "$SPACES_NAME" --cdn-endpoint "$SPACES_NAME.$REGION.cdn.digitaloceanspaces.com" --custom-domain "$DOMAIN"
    fi

    log_success "CDN enabled"
}

sync_assets() {
    print_header "Syncing Assets to Spaces"

    local build_dir="frontend/out"
    if [ ! -d "$build_dir" ]; then
        build_dir="frontend/build"
    fi

    if [ ! -d "$build_dir" ]; then
        build_dir="frontend/dist"
    fi

    if [ ! -d "$build_dir" ]; then
        log_error "Build output directory not found"
        log_info "Looked for: frontend/out, frontend/build, frontend/dist"
        exit 1
    fi

    log_info "Build directory: $build_dir"

    # Configure AWS CLI for Spaces
    export AWS_ACCESS_KEY_ID="${SPACES_ACCESS_KEY:-}"
    export AWS_SECRET_ACCESS_KEY="${SPACES_SECRET_KEY:-}"

    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        log_warning "Spaces credentials not set"
        echo ""
        echo "Generate Spaces credentials at:"
        echo "  https://cloud.digitalocean.com/spaces/$SPACES_NAME/keys"
        echo ""
        read -p "Press Enter after setting credentials..."
    fi

    # Sync static assets (long cache)
    log_info "Syncing static assets (images, JS, CSS)..."

    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY RUN] Would sync assets from $build_dir to s3://$SPACES_NAME"
        return
    fi

    aws s3 sync "$build_dir" \
        "s3://$SPACES_NAME" \
        --endpoint="$SPACES_ENDPOINT" \
        --acl public-read \
        --cache-control "public, max-age=31536000, immutable" \
        --exclude "*.html" \
        --include "*.js" \
        --include "*.css" \
        --include "*.png" \
        --include "*.jpg" \
        --include "*.jpeg" \
        --include "*.gif" \
        --include "*.svg" \
        --include "*.ico" \
        --include "*.woff" \
        --include "*.woff2" \
        --include "*.ttf" \
        --include "*.eot"

    # Sync HTML files (short cache)
    log_info "Syncing HTML files..."

    aws s3 sync "$build_dir" \
        "s3://$SPACES_NAME" \
        --endpoint="$SPACES_ENDPOINT" \
        --acl public-read \
        --cache-control "public, max-age=0, must-revalidate" \
        --exclude "*" \
        --include "*.html"

    log_success "Assets synced to Spaces"
}

invalidate_cdn() {
    log_info "Invalidating CDN cache..."

    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY RUN] Would invalidate CDN cache"
        return
    fi

    # Note: CDN invalidation is done automatically on new uploads
    log_success "CDN will be updated automatically"
}

get_deployment_info() {
    print_header "Deployment Information"

    local spaces_info=$(doctl spaces get "$SPACES_NAME" --format Name,Region,CDN_Endpoint,CreationDate --no-header 2>/dev/null)

    if [ -n "$spaces_info" ]; then
        echo "$spaces_info" | awk '{
            print "Spaces Name:    " $1
            print "Region:         " $2
            print "CDN Endpoint:   " $3
            print "Created:        " $4
        }'
    fi

    # Get CDN details
    local cdn_info=$(doctl spaces cdn get "$SPACES_NAME" --format ID,TTL,Endpoint,CustomDomain --no-header 2>/dev/null)

    if [ -n "$cdn_info" ]; then
        echo ""
        echo "CDN Details:"
        echo "$cdn_info" | awk '{
            print "  ID:           " $1
            print "  TTL:          " $2
            print "  Endpoint:     " $3
            if ($4 != "<none>") print "  Custom Domain: " $4
        }'
    fi

    echo ""
    echo "Access URLs:"
    local base_url="https://$SPACES_NAME.$REGION.cdn.digitaloceanspaces.com"
    echo "  Spaces:  https://$SPACES_NAME.$REGION.digitaloceanspaces.com"
    echo "  CDN:     $base_url"

    if [ -n "$DOMAIN" ]; then
        echo "  Custom:  https://$DOMAIN"
    fi
}

show_help() {
    cat << EOF
DigitalOcean Spaces CDN Deployment Script

Usage: $0 [OPTIONS]

Options:
  -s, --spaces NAME      Spaces name
  -r, --region REGION    DigitalOcean region (nyc3, sfo2, ams3, fra1, sgp1)
  -d, --domain DOMAIN    Custom domain for CDN
      --skip-build        Skip frontend build
      --dry-run           Show what would be done
  -h, --help              Show this help

Examples:
  $0                                    # Interactive mode
  $0 --spaces my-assets --region nyc3  # Use specific Spaces
  $0 --skip-build                      # Deploy pre-built assets

Environment Variables:
  SPACES_NAME              Spaces name
  REGION                   DigitalOcean region
  DOMAIN                   Custom domain
  SPACES_ACCESS_KEY        Spaces access key
  SPACES_SECRET_KEY        Spaces secret key
  SKIP_BUILD               Skip build step
  DRY_RUN                  Dry run mode

Spaces Setup:
  1. Create Spaces: doctl spaces create my-assets --region nyc3
  2. Enable CDN:    doctl spaces cdn create my-assets --ttl 3600
  3. Generate keys: https://cloud.digitalocean.com/spaces/my-assets/keys
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--spaces)
                SPACES_NAME="$2"
                shift 2
                ;;
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            --skip-build)
                SKIP_BUILD=true
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

    print_header "DigitalOcean Spaces CDN Deployment"

    check_dependencies
    authenticate_doctl
    select_or_create_spaces
    build_frontend
    configure_spaces_cdn
    sync_assets
    invalidate_cdn
    get_deployment_info

    log_success "Spaces CDN deployment complete!"
}

main "$@"
