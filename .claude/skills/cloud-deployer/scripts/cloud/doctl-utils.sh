#!/bin/bash
# ==============================================================================
# DigitalOcean doctl Utilities Script
# ==============================================================================
# Common utilities for DigitalOcean management
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

# ==============================================================================
# KUBERNETES CLUSTER MANAGEMENT
# ==============================================================================

list_clusters() {
    log_info "Listing Kubernetes clusters..."
    doctl kubernetes cluster list
}

create_cluster() {
    local name="$1"
    local region="${2:-nyc1}"
    local size="${3:-s-2vcpu-4gb}"
    local count="${4:-3}"
    local version="${5:-latest}"

    log_info "Creating Kubernetes cluster: $name"

    doctl kubernetes cluster create \
        "$name" \
        --region "$region" \
        --size "$size" \
        --count "$count" \
        --version "$version" \
        --auto-upgrade \
        --maintenance-window "sun=02:00"

    log_success "Cluster creation initiated"
}

delete_cluster() {
    local name="$1"

    log_warning "Deleting cluster: $name"
    read -p "Are you sure? (yes/no): " confirm

    if [ "$confirm" = "yes" ]; then
        doctl kubernetes cluster delete "$name" --dangerous
        log_success "Cluster deleted"
    fi
}

get_cluster_kubeconfig() {
    local name="$1"

    log_info "Getting kubeconfig for: $name"
    doctl kubernetes cluster kubeconfig save "$name"
    log_success "Kubeconfig saved to ~/.kube/config"
}

# ==============================================================================
# DROPLET MANAGEMENT
# ==============================================================================

list_droplets() {
    log_info "Listing droplets..."
    doctl compute droplet list
}

create_droplet() {
    local name="$1"
    local region="${2:-nyc1}"
    local size="${3:-s-1vcpu-1gb}"
    local image="${4:-ubuntu-22-04-x64}"

    log_info "Creating droplet: $name"

    doctl compute droplet create \
        "$name" \
        --region "$region" \
        --size "$size" \
        --image "$image" \
        --enable-ipv6 \
        --enable-monitoring

    log_success "Droplet created"
}

delete_droplet() {
    local id="$1"

    log_warning "Deleting droplet: $id"
    read -p "Are you sure? (yes/no): " confirm

    if [ "$confirm" = "yes" ]; then
        doctl compute droplet delete "$id" --dangerous
        log_success "Droplet deleted"
    fi
}

# ==============================================================================
# LOAD BALANCER MANAGEMENT
# ==============================================================================

list_load_balancers() {
    log_info "Listing load balancers..."
    doctl compute load-balancer list
}

create_load_balancer() {
    local name="$1"
    local region="${2:-nyc1}"
    local algorithm="${3:-round_robin}"
    local redirect_http_to_https="${4:-true}"

    log_info "Creating load balancer: $name"

    doctl compute load-balancer create \
        "$name" \
        --region "$region" \
        --algorithm "$algorithm" \
        --redirect-http-to-https \
        --health-check /

    log_success "Load balancer created"
}

add_droplets_to_lb() {
    local lb_id="$1"
    shift
    local droplet_ids=("$@")

    log_info "Adding droplets to load balancer: $lb_id"
    doctl compute load-balancer add-droplets "$lb_id" "${droplet_ids[@]}"
    log_success "Droplets added"
}

# ==============================================================================
# SPACES MANAGEMENT
# ==============================================================================

list_spaces() {
    log_info "Listing Spaces..."
    doctl spaces list
}

create_spaces() {
    local name="$1"
    local region="${2:-nyc3}"

    log_info "Creating Spaces: $name"

    doctl spaces create "$name" --region "$region"

    log_success "Spaces created"
}

list_spaces_buckets() {
    local name="$1"

    log_info "Listing buckets in Spaces: $name"
    doctl spaces list-buckets "$name"
}

enable_spaces_cdn() {
    local name="$1"
    local ttl="${2:-3600}"

    log_info "Enabling CDN for Spaces: $name"
    doctl spaces cdn create "$name" --ttl "$ttl"
    log_success "CDN enabled"
}

# ==============================================================================
# DATABASE MANAGEMENT
# ==============================================================================

list_databases() {
    log_info "Listing databases..."
    doctl databases list
}

create_database() {
    local name="$1"
    local engine="${2:-pg}"
    local version="${3:-15}"
    local size="${4:-db-s-1vcpu-1gb}"
    local region="${5:-nyc1}"
    local nodes="${6:-1}"

    log_info "Creating database: $name"

    doctl databases create \
        "$name" \
        --engine "$engine" \
        --version "$version" \
        --size "$size" \
        --region "$region" \
        --num-nodes "$nodes"

    log_success "Database creation initiated"
}

get_database_connection_info() {
    local id="$1"

    log_info "Getting connection info for database: $id"
    doctl databases connection "$id"
}

# ==============================================================================
# FIREWALL MANAGEMENT
# ==============================================================================

list_firewalls() {
    log_info "Listing firewalls..."
    doctl compute firewall list
}

create_firewall() {
    local name="$1"
    local inbound_rules="${2:-22,80,443,8000}"
    local outbound_rules="all"

    log_info "Creating firewall: $name"

    # Parse inbound rules
    IFS=',' read -ra ports <<< "$inbound_rules"

    local rules_cmd=""
    for port in "${ports[@]}"; do
        rules_cmd="$rules_cmd --inbound-rules=protocol:tcp,ports:$port,sources:0.0.0.0/0"
    done

    doctl compute firewall create "$name" $rules_cmd

    log_success "Firewall created"
}

add_droplets_to_firewall() {
    local firewall_id="$1"
    shift
    local droplet_ids=("$@")

    log_info "Adding droplets to firewall: $firewall_id"
    doctl compute firewall add-droplets "$firewall_id" "${droplet_ids[@]}"
    log_success "Droplets added to firewall"
}

# ==============================================================================
# PROJECT MANAGEMENT
# ==============================================================================

list_projects() {
    log_info "Listing projects..."
    doctl projects list
}

create_project() {
    local name="$1"
    local description="${2:-}"
    local purpose="${3:-}"
    local environment="${4:-production}"

    log_info "Creating project: $name"

    doctl projects create \
        --name "$name" \
        --description "$description" \
        --purpose "$purpose" \
        --environment "$environment"

    log_success "Project created"
}

assign_resource_to_project() {
    local project_id="$1"
    local resource_urn="$2"

    log_info "Assigning resource to project: $resource_urn"
    doctl projects resources assign "$project_id" --resource="$resource_urn"
    log_success "Resource assigned"
}

# ==============================================================================
# VOLUME MANAGEMENT
# ==============================================================================

list_volumes() {
    log_info "Listing volumes..."
    doctl compute volume list
}

create_volume() {
    local name="$1"
    local size="${2:-10G}"
    local region="${3:-nyc1}"
    local filesystem_type="${4:-ext4}"

    log_info "Creating volume: $name ($size)"

    doctl compute volume create \
        "$name" \
        --size "$size" \
        --region "$region" \
        --fs-type "$filesystem_type"

    log_success "Volume created"
}

attach_volume() {
    local volume_id="$1"
    local droplet_id="$2"

    log_info "Attaching volume $volume_id to droplet $droplet_id"
    doctl compute volume attach "$volume_id" "$droplet_id"
    log_success "Volume attached"
}

# ==============================================================================
# SNAPSHOT MANAGEMENT
# ==============================================================================

list_snapshots() {
    log_info "Listing snapshots..."
    doctl compute snapshot list
}

create_snapshot_from_droplet() {
    local droplet_id="$1"
    local snapshot_name="${2:-snapshot-$(date +%Y%m%d-%H%M%S)}"

    log_info "Creating snapshot from droplet: $droplet_id"
    doctl compute droplet snapshots "$droplet_id" --snapshot-name "$snapshot_name"
    log_success "Snapshot created: $snapshot_name"
}

create_snapshot_from_volume() {
    local volume_id="$1"
    local snapshot_name="${2:-snapshot-$(date +%Y%m%d-%H%M%S)}"

    log_info "Creating snapshot from volume: $volume_id"
    doctl compute volume snapshots "$volume_id" --snapshot-name "$snapshot_name"
    log_success "Snapshot created: $snapshot_name"
}

restore_droplet_from_snapshot() {
    local snapshot_id="$1"
    local droplet_name="${2:-restored-droplet}"
    local region="${3:-nyc1}"
    local size="${4:-s-1vcpu-1gb}"

    log_info "Restoring droplet from snapshot: $snapshot_id"
    doctl compute droplet create-from-snapshot "$snapshot_id" \
        --droplet-name "$droplet_name" \
        --region "$region" \
        --size "$size"
    log_success "Droplet restored"
}

# ==============================================================================
# CERTIFICATE MANAGEMENT
# ==============================================================================

list_certificates() {
    log_info "Listing certificates..."
    doctl compute certificate list
}

create_letsencrypt_certificate() {
    local name="$1"
    local dns_names="$2"

    log_info "Creating Let's Encrypt certificate: $name"
    doctl compute certificate create "$name" \
        --type lets_encrypt \
        --dns-names "$dns_names" \
        --leaf-certificate-space
    log_success "Certificate creation initiated"
}

# ==============================================================================
# MONITORING
# ==============================================================================

get_droplet_metrics() {
    local droplet_id="$1"

    log_info "Getting metrics for droplet: $droplet_id"
    doctl monitoring droplet-metrics "$droplet_id" --no-header
}

get_load_balancer_metrics() {
    local lb_id="$1"

    log_info "Getting metrics for load balancer: $lb_id"
    doctl monitoring load-balancer-metrics "$lb_id" --no-header
}

# ==============================================================================
# TAGS
# ==============================================================================

list_tags() {
    log_info "Listing tags..."
    doctl compute tag list
}

create_tag() {
    local name="$1"

    log_info "Creating tag: $name"
    doctl compute tag create "$name"
    log_success "Tag created"
}

tag_resource() {
    local tag_name="$1"
    local resource_id="$2"
    local resource_type="${3:-droplet}"

    log_info "Tagging resource $resource_id with: $tag_name"
    doctl compute tag assign "$tag_name" --resource "$resource_id:$resource_type"
    log_success "Resource tagged"
}

# ==============================================================================
# HELP
# ==============================================================================

show_help() {
    cat << EOF
DigitalOcean doctl Utilities

Usage: $0 <command> [args]

Cluster Commands:
  list-clusters              List Kubernetes clusters
  create-cluster NAME        Create Kubernetes cluster
  delete-cluster NAME        Delete cluster
  get-kubeconfig NAME        Get kubeconfig for cluster

Droplet Commands:
  list-droplets              List droplets
  create-droplet NAME        Create droplet
  delete-droplet ID          Delete droplet

Load Balancer Commands:
  list-lbs                   List load balancers
  create-lb NAME             Create load balancer
  add-droplets-to-lb ID...   Add droplets to LB

Spaces Commands:
  list-spaces                List Spaces
  create-spaces NAME         Create Spaces
  list-buckets NAME          List buckets in Spaces
  enable-cdn NAME            Enable CDN for Spaces

Database Commands:
  list-dbs                   List databases
  create-db NAME             Create database
  get-db-conn ID             Get connection info

Firewall Commands:
  list-firewalls             List firewalls
  create-firewall NAME       Create firewall
  add-to-firewall ID...      Add droplets to firewall

Volume Commands:
  list-volumes               List volumes
  create-volume NAME         Create volume
  attach-volume ID DROPLET   Attach volume

Snapshot Commands:
  list-snapshots             List snapshots
  snapshot-droplet ID        Snapshot droplet
  snapshot-volume ID         Snapshot volume
  restore-droplet SNAP       Restore from snapshot

Certificate Commands:
  list-certs                 List certificates
  create-letsencrypt-cert    Create Let's Encrypt cert

Monitoring Commands:
  droplet-metrics ID         Get droplet metrics
  lb-metrics ID              Get load balancer metrics

Tag Commands:
  list-tags                  List tags
  create-tag NAME            Create tag
  tag-resource TAG ID        Tag resource

Examples:
  $0 list-clusters
  $0 create-cluster my-k8s nyc1 s-2vcpu-4gb 3
  $0 get-kubeconfig my-k8s
  $0 list-droplets
  $0 create-droplet my-droplet nyc1 s-1vcpu-1gb
  $0 create-spaces my-assets nyc3
  $0 enable-cdn my-assets
EOF
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    local command="$1"
    shift

    case "$command" in
        # Cluster commands
        list-clusters) list_clusters ;;
        create-cluster) create_cluster "$@" ;;
        delete-cluster) delete_cluster "$@" ;;
        get-kubeconfig) get_cluster_kubeconfig "$@" ;;

        # Droplet commands
        list-droplets) list_droplets ;;
        create-droplet) create_droplet "$@" ;;
        delete-droplet) delete_droplet "$@" ;;

        # Load balancer commands
        list-lbs) list_load_balancers ;;
        create-lb) create_load_balancer "$@" ;;
        add-droplets-to-lb) add_droplets_to_lb "$@" ;;

        # Spaces commands
        list-spaces) list_spaces ;;
        create-spaces) create_spaces "$@" ;;
        list-buckets) list_spaces_buckets "$@" ;;
        enable-cdn) enable_spaces_cdn "$@" ;;

        # Database commands
        list-dbs) list_databases ;;
        create-db) create_database "$@" ;;
        get-db-conn) get_database_connection_info "$@" ;;

        # Firewall commands
        list-firewalls) list_firewalls ;;
        create-firewall) create_firewall "$@" ;;
        add-to-firewall) add_droplets_to_firewall "$@" ;;

        # Volume commands
        list-volumes) list_volumes ;;
        create-volume) create_volume "$@" ;;
        attach-volume) attach_volume "$@" ;;

        # Snapshot commands
        list-snapshots) list_snapshots ;;
        snapshot-droplet) create_snapshot_from_droplet "$@" ;;
        snapshot-volume) create_snapshot_from_volume "$@" ;;
        restore-droplet) restore_droplet_from_snapshot "$@" ;;

        # Certificate commands
        list-certs) list_certificates ;;
        create-letsencrypt-cert) create_letsencrypt_certificate "$@" ;;

        # Monitoring commands
        droplet-metrics) get_droplet_metrics "$@" ;;
        lb-metrics) get_load_balancer_metrics "$@" ;;

        # Tag commands
        list-tags) list_tags ;;
        create-tag) create_tag "$@" ;;
        tag-resource) tag_resource "$@" ;;

        # Help
        -h|--help|help) show_help ;;

        *)
        log_error "Unknown command: $command"
        show_help
        exit 1
        ;;
    esac
}

main "$@"
