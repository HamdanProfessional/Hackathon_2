# DigitalOcean Load Balancer with Multiple Droplets
#
# This example demonstrates a high-availability web application setup with:
# - Multiple droplets behind a load balancer
# - Automatic health checks
# - SSL termination
# - Sticky sessions
# - Cloud firewalls
# - Managed database
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
# SSH Key for Droplet Access
# =============================================================================

resource "digitalocean_ssh_key" "deploy_key" {
  name       = "lb-deploy-key"
  public_key = file(var.ssh_public_key_path)
}

# =============================================================================
# Cloud Firewall (Security)
# =============================================================================

resource "digitalocean_firewall" "web_fw" {
  name        = "web-firewall"
  droplet_ids = digitalocean_droplet.web[*].id

  # SSH from your IP only
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.ssh_allowed_ips
  }

  # HTTP from anywhere (or limit to load balancer)
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # HTTPS from anywhere
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Allow health checks from DigitalOcean
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["10.10.0.0/16"]  # DO internal network
  }

  # Outbound traffic
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  tags = var.droplet_tags
}

# =============================================================================
# Multiple Web Server Droplets
# =============================================================================

resource "digitalocean_droplet" "web" {
  count  = var.droplet_count
  image  = var.droplet_image
  name   = "${var.project_name}-web-${count.index + 1}"
  region = var.region

  size = var.droplet_size

  # SSH key
  ssh_keys = [digitalocean_ssh_key.deploy_key.fingerprint]

  # Monitoring and backups
  monitoring = true
  ipv6       = true
  backups    = var.enable_backups

  # User data script for initial setup
  user_data = templatefile("${path.module}/user-data.sh", {
    hostname      = "${var.project_name}-web-${count.index + 1}"
    db_host       = digitalocean_database_cluster.postgres.host
    db_port       = digitalocean_database_cluster.postgres.port
    db_name       = digitalocean_database_db.app_db.name
    db_user       = digitalocean_database_user.app_user.name
    db_password   = digitalocean_database_user.app_user.password
    redis_host    = var.redis_host
    redis_port    = var.redis_port
    jwt_secret    = var.jwt_secret
    app_port      = var.app_port
  })

  # Tags for identification
  tags = concat(var.droplet_tags, [var.project_name])
}

# =============================================================================
# Load Balancer
# =============================================================================

resource "digitalocean_load_balancer" "web" {
  name   = "${var.project_name}-lb"
  region = var.region

  # Forwarding rules
  forwarding_rule {
    entry_port     = 80
    entry_protocol = "http"

    target_port     = 80
    target_protocol = "http"
  }

  forwarding_rule {
    entry_port     = 443
    entry_protocol = "https"

    target_port     = 80
    target_protocol = "http"
  }

  # Health check
  health_check {
    protocol                 = "http"
    port                     = 80
    path                     = "/health"
    check_interval_seconds   = 10
    response_timeout_seconds = 5
    unhealthy_threshold     = 3
    healthy_threshold       = 5
  }

  # Sticky sessions (if needed)
  sticky_sessions {
    type             = "cookies"
    cookie_name      = "DO_LB_STICKY"
    cookie_ttl_seconds = 3600
  }

  # SSL termination
  redirect_http_to_https = var.redirect_http_to_https

  # Enable PROXY protocol (sends original client IP)
  enable_proxy_protocol = true

  # Attach droplets by tag
  droplet_tag = var.project_name

  # VPC integration (optional)
  vpc_uuid = digitalocean_vpc.main.id

  tags = var.droplet_tags
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

  tags = var.droplet_tags
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

# Database firewall (only allow from droplets)
resource "digitalocean_database_firewall" "postgres_fw" {
  cluster_id = digitalocean_database_cluster.postgres.id

  rule {
    type  = "k8s"
    value = digitalocean_droplet.web[0].id
  }

  # Allow from specific IPs if needed
  dynamic "rule" {
    for_each = var.db_allowed_ips
    content {
      type  = "ip_addr"
      value = rule.value
    }
  }
}

# =============================================================================
# Managed Redis (Optional)
# =============================================================================

resource "digitalocean_database_cluster" "redis" {
  count      = var.deploy_redis ? 1 : 0
  name       = "${var.project_name}-redis"
  engine     = "redis"
  version    = var.redis_version
  size       = var.redis_size
  region     = var.region
  node_count = 1  # Redis doesn't support HA in DO

  # Maintenance window
  maintenance_window {
    day  = "sunday"
    hour = "1"
  }

  # Private network connection
  private_network_uuid = digitalocean_vpc.main.id

  tags = var.droplet_tags
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
# Project for Organization
# =============================================================================

resource "digitalocean_project" "main" {
  name        = "${var.project_name}-lb"
  description = "${var.project_name} application with load balancer"
  purpose     = "Web Application"
  environment = var.environment

  resources = flatten([
    digitalocean_droplet.web[*].urn,
    digitalocean_load_balancer.web.urn,
    digitalocean_database_cluster.postgres.urn,
    var.deploy_redis ? [digitalocean_database_cluster.redis[0].urn] : [],
    digitalocean_vpc.main.urn,
  ])
}

# =============================================================================
# Floating IP (Optional - for failover)
# =============================================================================

resource "digitalocean_floating_ip" "main" {
  count = var.create_floating_ip ? 1 : 0
  region = var.region
  droplet_id = digitalocean_droplet.web[0].id
}

# =============================================================================
# DNS Records (Optional)
# =============================================================================

# Assuming you have a domain managed by DigitalOcean DNS
resource "digitalocean_record" "app" {
  count = var.create_dns_records ? 1 : 0

  domain = var.domain_name
  type   = "A"
  name   = var.subdomain
  value  = digitalocean_load_balancer.web.ip
  ttl    = 300
}

resource "digitalocean_record" "www" {
  count = var.create_dns_records ? 1 : 0

  domain = var.domain_name
  type   = "CNAME"
  name   = "www"
  value  = "${var.subdomain}.${var.domain_name}"
  ttl    = 300
}
