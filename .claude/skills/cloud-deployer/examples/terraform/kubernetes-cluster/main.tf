# DigitalOcean Kubernetes Cluster (DOKS) Example
#
# This example creates a complete Kubernetes cluster with:
# - Multiple node pools for different workloads
# - Load balancer for external access
# - Managed PostgreSQL database
# - Spaces integration for object storage
# - Application deployment with ingress controller
# - Auto-scaling and health checks
#
# Usage:
#   terraform init
#   terraform apply
#   terraform destroy

terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }

  required_version = ">= 1.0"
}

provider "digitalocean" {
  token = var.do_token
}

# =============================================================================
# Kubernetes Cluster with Multiple Node Pools
# =============================================================================

resource "digitalocean_kubernetes_cluster" "main" {
  name    = "${var.project_name}-cluster"
  region  = var.region
  version = var.kubernetes_version

  # Auto-upgrade cluster to latest stable version
  auto_upgrade = true

  # HA control plane (recommended for production)
  ha = var.ha_enabled

  # Maintenance window (UTC)
  maintenance_policy {
    start_time = "0:00"
    day        = "sunday"
  }

  # Default node pool for general workloads
  default_node_pool {
    name       = "general-pool"
    size       = var.default_node_size
    node_count = var.default_node_count

    # Auto-scale nodes
    auto_scale = true
    min_nodes  = var.min_nodes
    max_nodes  = var.max_nodes

    # Labels for node selection
    labels = {
      workload = "general"
      tier     = "standard"
    }

    # Taints for dedicated workloads
    taint = [
      {
        key    = "workload"
        value  = "general"
        effect = "NoSchedule"
      }
    ]
  }

  # Tags for cost tracking and organization
  tags = var.cluster_tags
}

# High-memory node pool for database workloads
resource "digitalocean_kubernetes_node_pool" "database" {
  cluster_id = digitalocean_kubernetes_cluster.main.id

  name       = "database-pool"
  size       = var.database_node_size
  node_count = var.database_node_count

  auto_scale = true
  min_nodes  = 1
  max_nodes  = 3

  labels = {
    workload = "database"
    tier     = "memory-optimized"
  }

  taint = [
    {
      key    = "workload"
      value  = "database"
      effect = "NoSchedule"
    }
  ]
}

# GPU node pool for ML/AI workloads (optional)
resource "digitalocean_kubernetes_node_pool" "gpu" {
  cluster_id = digitalocean_kubernetes_cluster.main.id

  name       = "gpu-pool"
  size       = "gpu-2x-4x"  # GPU optimized droplet
  node_count = 0  # Start with 0, scale as needed

  auto_scale = true
  min_nodes  = 0
  max_nodes  = 2

  labels = {
    workload = "gpu"
    tier     = "accelerated"
  }

  taint = [
    {
      key    = "nvidia.com/gpu"
      value  = "true"
      effect = "NoSchedule"
    }
  ]

  # Only create if GPU is enabled
  count = var.enable_gpu_nodes ? 1 : 0
}

# =============================================================================
# Load Balancer for External Access
# =============================================================================

resource "digitalocean_load_balancer" "main" {
  name   = "${var.project_name}-lb"
  region = var.region

  # Forward traffic to Kubernetes nodes
  forwarding_rule {
    entry_port     = 80
    entry_protocol = "http"

    target_port     = 30080  # NodePort for ingress
    target_protocol = "http"
  }

  forwarding_rule {
    entry_port     = 443
    entry_protocol = "https"

    target_port     = 30443  # NodePort for ingress TLS
    target_protocol = "https"
  }

  # Health check
  health_check {
    protocol               = "http"
    port                   = 30080
    path                   = "/healthz"
    check_interval_seconds = 10
    response_timeout_seconds = 5
    healthy_threshold   = 5
    unhealthy_threshold = 3
  }

  # Sticky sessions (if needed)
  sticky_sessions {
    type             = "cookies"
    cookie_name      = "DO_LB"
    cookie_ttl_seconds = 3600
  }

  # SSL termination (optional)
  redirect_http_to_https = var.redirect_http_to_https

  # Enable PROXY protocol
  enable_proxy_protocol = true

  # Attach to nodes via tag
  droplet_tag = "${var.project_name}-k8s-worker"

  # Tags
  tags = var.cluster_tags
}

# =============================================================================
# Managed PostgreSQL Database
# =============================================================================

resource "digitalocean_database_cluster" "postgres" {
  name       = "${var.project_name}-db"
  engine     = "pg"
  version    = var.postgres_version
  size       = var.db_size
  region     = var.region
  node_count = var.db_node_count

  # Highly available setup
  ha = var.db_ha_enabled

  # Maintenance window
  maintenance_window {
    day  = "sunday"
    hour = "0"
  }

  # Backup policy
  backup_retention_period = var.db_backup_retention_days

  # Private network connection to Kubernetes
  private_network_uuid = digitalocean_vpc.main.id

  tags = var.cluster_tags
}

# Create database and user
resource "digitalocean_database_db" "app_db" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = var.db_name
}

resource "digitalocean_database_user" "app_user" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = var.db_user
}

# Create firewall for database
resource "digitalocean_database_firewall" "postgres_fw" {
  cluster_id = digitalocean_database_cluster.postgres.id

  # Allow from Kubernetes cluster
  rule {
    type  = "k8s"
    value = digitalocean_kubernetes_cluster.main.id
  }

  # Allow from specific IPs (if needed)
  dynamic "rule" {
    for_each = var.db_allowed_ips
    content {
      type  = "ip_addr"
      value = rule.value
    }
  }
}

# =============================================================================
# Spaces for Object Storage
# =============================================================================

resource "digitalocean_spaces_bucket" "assets" {
  name   = "${var.project_name}-assets"
  region = var.spaces_region

  # Enable CDN
  cdn_enabled = var.spaces_cdn_enabled

  # Lifecycle rules
  lifecycle_rule {
    enabled = true

    # Transition old files to Glacier
    noncurrent_version_transition {
      days          = 30
      storage_class = "GLACIER"
    }

    # Expire old versions
    noncurrent_version_expiration {
      days = 90
    }
  }

  # CORS configuration
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = var.spaces_cors_origins
    max_age_seconds = 3600
  }
}

# =============================================================================
# VPC for Private Networking
# =============================================================================

resource "digitalocean_vpc" "main" {
  name   = "${var.project_name}-vpc"
  region = var.region

  # IP range for VPC
  ip_range = var.vpc_ip_range
}

# =============================================================================
# Kubernetes Configuration
# =============================================================================

# Retrieve cluster credentials
data "digitalocean_kubernetes_cluster" "credentials" {
  name = digitalocean_kubernetes_cluster.main.id
}

# Save kubeconfig file
resource "local_file" "kubeconfig" {
  content  = data.digitalocean_kubernetes_cluster.credentials.kube_config[0].raw_config
  filename = "${path.module}/kubeconfig_${var.project_name}"

  # Set file permissions for security
  file_permission = "0600"
}

# =============================================================================
# Project for Organization
# =============================================================================

resource "digitalocean_project" "main" {
  name        = "${var.project_name}-k8s"
  description = "${var.project_name} application - Kubernetes cluster with managed services"
  purpose     = "Kubernetes Application"
  environment = var.environment

  # Assign resources to project
  resources = [
    digitalocean_kubernetes_cluster.main.urn,
    digitalocean_load_balancer.main.urn,
    digitalocean_database_cluster.postgres.urn,
    digitalocean_spaces_bucket.assets.urn,
    digitalocean_vpc.main.urn,
  ]
}

# =============================================================================
# Kubernetes Provider (for deploying resources)
# =============================================================================

provider "kubernetes" {
  host  = data.digitalocean_kubernetes_cluster.credentials.endpoint
  token = data.digitalocean_kubernetes_cluster.credentials.kube_config[0].token
  cluster_ca_certificate = base64decode(
    data.digitalocean_kubernetes_cluster.credentials.kube_config[0].cluster_ca_certificate
  )
}

provider "helm" {
  kubernetes {
    host  = data.digitalocean_kubernetes_cluster.credentials.endpoint
    token = data.digitalocean_kubernetes_cluster.credentials.kube_config[0].token
    cluster_ca_certificate = base64decode(
      data.digitalocean_kubernetes_cluster.credentials.kube_config[0].cluster_ca_certificate
    )
  }
}

# Deploy Nginx Ingress Controller via Helm
resource "helm_release" "nginx_ingress" {
  name       = "nginx-ingress"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  namespace  = "ingress-nginx"

  create_namespace = true

  set {
    name  = "controller.service.type"
    value = "NodePort"
  }

  set {
    name  = "controller.service.nodePorts.http"
    value = "30080"
  }

  set {
    name  = "controller.service.nodePorts.https"
    value = "30443"
  }

  set {
    name  = "controller.publishService.enabled"
    value = "true"
  }
}

# Deploy Cert-Manager for TLS certificates
resource "helm_release" "cert_manager" {
  name       = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  namespace  = "cert-manager"

  create_namespace = true

  set {
    name  = "installCRDs"
    value = "true"
  }

  depends_on = [
    helm_release.nginx_ingress
  ]
}
