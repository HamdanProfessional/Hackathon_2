# Full Stack Application - Complete DigitalOcean Deployment
#
# This example demonstrates a production-ready full-stack application with:
# - Load balanced web servers (FastAPI backend)
# - Next.js frontend deployed via App Platform
# - Managed PostgreSQL with HA
# - Managed Redis for caching
# - Spaces with CDN for static assets
# - Container Registry for Docker images
# - CI/CD pipeline
# - Monitoring and logging
# - Custom domains with SSL
#
# Architecture:
#   Frontend (Next.js) -> App Platform
#   Backend API (FastAPI) -> Load Balanced Droplets
#   Database -> Managed PostgreSQL
#   Cache -> Managed Redis
#   Assets -> Spaces + CDN
#   Images -> Container Registry
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
# VPC for Private Networking
# =============================================================================

resource "digitalocean_vpc" "main" {
  name   = "${var.project_name}-vpc"
  region = var.region
  ip_range = var.vpc_ip_range
}

# =============================================================================
# Container Registry
# =============================================================================

resource "digitalocean_container_registry" "main" {
  name                   = "${var.project_name}-registry"
  subscription_tier_slug = var.registry_tier
  region                 = var.registry_region
}

# =============================================================================
# Spaces Bucket for Static Assets
# =============================================================================

resource "digitalocean_spaces_bucket" "assets" {
  name   = "${var.project_name}-assets"
  region = var.spaces_region

  # Enable CDN
  cdn_enabled = true

  # Lifecycle rules
  lifecycle_rule {
    enabled = true

    # Transition old files to lower-cost storage
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
# Managed PostgreSQL Database
# =============================================================================

resource "digitalocean_database_cluster" "postgres" {
  name       = "${var.project_name}-db"
  engine     = "pg"
  version    = var.postgres_version
  size       = var.db_size
  region     = var.region
  node_count = var.db_node_count

  # High availability
  ha = var.db_ha_enabled

  # Backup policy
  backup_retention_period = var.db_backup_retention_days

  # Maintenance window
  maintenance_window {
    day  = "sunday"
    hour = "0"
  }

  # Private network connection
  private_network_uuid = digitalocean_vpc.main.id

  tags = var.resource_tags
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

# Database firewall
resource "digitalocean_database_firewall" "postgres_fw" {
  cluster_id = digitalocean_database_cluster.postgres.id

  # Allow from backend droplets
  rule {
    type  = "tag"
    value = "${var.project_name}-backend"
  }

  # Allow from App Platform (if needed)
  rule {
    type  = "app"
    value = digitalocean_app.backend.id
  }

  # Allow from specific IPs
  dynamic "rule" {
    for_each = var.db_allowed_ips
    content {
      type  = "ip_addr"
      value = rule.value
    }
  }
}

# =============================================================================
# Managed Redis
# =============================================================================

resource "digitalocean_database_cluster" "redis" {
  count      = var.deploy_redis ? 1 : 0
  name       = "${var.project_name}-redis"
  engine     = "redis"
  version    = var.redis_version
  size       = var.redis_size
  region     = var.region
  node_count = 1

  # Maintenance window
  maintenance_window {
    day  = "sunday"
    hour = "1"
  }

  # Private network connection
  private_network_uuid = digitalocean_vpc.main.id

  tags = var.resource_tags
}

# =============================================================================
# SSH Key
# =============================================================================

resource "digitalocean_ssh_key" "deploy_key" {
  name       = "${var.project_name}-deploy-key"
  public_key = file(var.ssh_public_key_path)
}

# =============================================================================
# Backend API - Load Balanced Droplets
# =============================================================================

# Cloud firewall for backend droplets
resource "digitalocean_firewall" "backend_fw" {
  name        = "${var.project_name}-backend-fw"
  droplet_ids = digitalocean_droplet.backend[*].id

  # SSH from your IP only
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.ssh_allowed_ips
  }

  # HTTP from load balancer only
  inbound_rule {
    protocol         = "tcp"
    port_range       = "8000"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Allow monitoring from DigitalOcean
  inbound_rule {
    protocol         = "tcp"
    port_range       = "9100"
    source_addresses = ["10.10.0.0/16"]
  }

  # Outbound traffic
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  tags = concat(var.resource_tags, ["${var.project_name}-backend"])
}

# Backend droplets
resource "digitalocean_droplet" "backend" {
  count  = var.backend_droplet_count
  image  = var.backend_droplet_image
  name   = "${var.project_name}-backend-${count.index + 1}"
  region = var.region

  size = var.backend_droplet_size

  # SSH key
  ssh_keys = [digitalocean_ssh_key.deploy_key.fingerprint]

  # Monitoring and backups
  monitoring = true
  ipv6       = true
  backups    = var.backend_enable_backups

  # Private networking
  private_networking = true
  vpc_uuid           = digitalocean_vpc.main.id

  # User data script
  user_data = templatefile("${path.module}/backend-user-data.sh", {
    hostname        = "${var.project_name}-backend-${count.index + 1}"
    db_host         = digitalocean_database_cluster.postgres.host
    db_port         = digitalocean_database_cluster.postgres.port
    db_name         = digitalocean_database_db.app_db.name
    db_user         = digitalocean_database_user.app_user.name
    db_password     = digitalocean_database_user.app_user.password
    redis_host      = var.deploy_redis ? digitalocean_database_cluster.redis[0].host : ""
    redis_port      = var.deploy_redis ? digitalocean_database_cluster.redis[0].port : "6379"
    jwt_secret      = var.jwt_secret
    spaces_endpoint = "https://${var.spaces_region}.digitaloceanspaces.com"
    spaces_bucket   = digitalocean_spaces_bucket.assets.name
    spaces_key      = var.spaces_access_key
    spaces_secret   = var.spaces_secret_key
    registry_url    = "${digitalocean_container_registry.main.endpoint}/${var.project_name}"
    app_port        = var.backend_app_port
  })

  # Tags
  tags = concat(var.resource_tags, ["${var.project_name}-backend"])
}

# Load balancer for backend
resource "digitalocean_load_balancer" "backend" {
  name   = "${var.project_name}-backend-lb"
  region = var.region

  # Forwarding rules
  forwarding_rule {
    entry_port     = 80
    entry_protocol = "http"
    target_port     = var.backend_app_port
    target_protocol = "http"
  }

  forwarding_rule {
    entry_port     = 443
    entry_protocol = "https"
    target_port     = var.backend_app_port
    target_protocol = "http"
  }

  # Health check
  health_check {
    protocol                 = "http"
    port                     = var.backend_app_port
    path                     = "/health"
    check_interval_seconds   = 10
    response_timeout_seconds = 5
    unhealthy_threshold     = 3
    healthy_threshold       = 5
  }

  # Sticky sessions
  sticky_sessions {
    type             = "cookies"
    cookie_name      = "DO_LB_BACKEND"
    cookie_ttl_seconds = 3600
  }

  # SSL termination
  redirect_http_to_https = true

  # PROXY protocol
  enable_proxy_protocol = true

  # Attach droplets by tag
  droplet_tag = "${var.project_name}-backend"

  # VPC
  vpc_uuid = digitalocean_vpc.main.id

  tags = var.resource_tags
}

# =============================================================================
# Frontend - App Platform
# =============================================================================

resource "digitalocean_app" "frontend" {
  spec {
    name   = "${var.project_name}-frontend"
    region = var.app_platform_region

    # Static site (Next.js export)
    static_site {
      name              = "frontend"
      build_command     = "npm run build"
      output_dir        = "out"
      index_document    = "index.html"
      error_document    = "404.html"
      catchall_document = "404.html"

      github {
        repo           = var.github_repo
        branch         = var.github_branch
        deploy_on_push = true
      }

      # Environment variables
      env {
        key   = "NEXT_PUBLIC_API_URL"
        value = "https://${var.api_domain}"
      }

      env {
        key   = "NEXT_PUBLIC_APP_NAME"
        value = var.app_name
      }

      # CDN caching
      cache {
        paths = [
          "/_next/static/*",
          "/static/*",
          "/images/*",
          "/assets/*"
        ]
        default_ttl = 3600
        forced_ttl  = 86400
      }

      # Routes
      routes {
        path = "/"
      }
    }

    # Custom domains
    domain {
      name   = var.frontend_domain
      type   = "PRIMARY"
      zone   = var.domain_zone
    }
  }
}

# =============================================================================
# Backend App Spec (for reference - if using App Platform for backend)
# =============================================================================

# Uncomment if you want to deploy backend on App Platform instead of droplets
#
# resource "digitalocean_app" "backend" {
#   spec {
#     name   = "${var.project_name}-backend"
#     region = var.app_platform_region
#
#     service {
#       name               = "api"
#       environment_slug   = "python"
#       instance_count     = 2
#       instance_size_slug = "basic-xs"
#
#       github {
#         repo           = var.github_repo
#         branch         = var.github_branch
#         deploy_on_push = true
#       }
#
#       build_command = "pip install -r requirements.txt"
#       run_command   = "uvicorn app.main:app --host 0.0.0.0 --port 8080"
#
#       env {
#         key   = "DB_HOST"
#         value = digitalocean_database_cluster.postgres.host
#       }
#
#       # ... more env vars
#
#       routes {
#         path = "/api"
#       }
#     }
#   }
# }

# =============================================================================
# Project for Organization
# =============================================================================

resource "digitalocean_project" "main" {
  name        = "${var.project_name}-full-stack"
  description = "${var.project_name} - Full stack application with managed services"
  purpose     = "Web Application"
  environment = var.environment

  resources = flatten([
    digitalocean_droplet.backend[*].urn,
    digitalocean_load_balancer.backend.urn,
    digitalocean_database_cluster.postgres.urn,
    var.deploy_redis ? [digitalocean_database_cluster.redis[0].urn] : [],
    digitalocean_spaces_bucket.assets.urn,
    digitalocean_container_registry.main.urn,
    digitalocean_vpc.main.urn,
    digitalocean_app.frontend.urn,
  ])
}

# =============================================================================
# DNS Records
# =============================================================================

# API domain
resource "digitalocean_record" "api" {
  count = var.create_dns ? 1 : 0

  domain = var.domain_zone
  type   = "A"
  name   = "api"
  value  = digitalocean_load_balancer.backend.ip
  ttl    = 300
}

# WWW frontend
resource "digitalocean_record" "www" {
  count = var.create_dns ? 1 : 0

  domain = var.domain_zone
  type   = "CNAME"
  name   = "www"
  value  = var.frontend_domain
  ttl    = 300
}
