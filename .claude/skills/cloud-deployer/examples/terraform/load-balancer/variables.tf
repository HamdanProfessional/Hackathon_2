variable "do_token" {
  type        = string
  description = "DigitalOcean API token"
  sensitive   = true
}

variable "project_name" {
  type        = string
  description = "Project name for resources"
  default     = "todo-app"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must be lowercase alphanumeric with hyphens only."
  }
}

variable "environment" {
  type        = string
  description = "Environment (production, staging, development)"
  default     = "production"

  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be production, staging, or development."
  }
}

variable "region" {
  type        = string
  description = "DigitalOcean region"
  default     = "nyc1"

  validation {
    condition     = contains(["nyc1", "nyc2", "nyc3", "ams3", "sfo2", "sfo3", "fra1", "sgp1"], var.region)
    error_message = "Region must be a valid DigitalOcean region."
  }
}

# =============================================================================
# Droplet Configuration
# =============================================================================

variable "droplet_count" {
  type        = number
  description = "Number of web server droplets"
  default     = 2

  validation {
    condition     = var.droplet_count >= 1 && var.droplet_count <= 10
    error_message = "Droplet count must be between 1 and 10."
  }
}

variable "droplet_size" {
  type        = string
  description = "Droplet size slug"
  default     = "s-2vcpu-4gb"

  validation {
    condition     = can(regex("^[sg]-[0-9]+vcpu-[0-9]+gb$", var.droplet_size))
    error_message = "Droplet size must be a valid size slug."
  }
}

variable "droplet_image" {
  type        = string
  description = "Droplet image slug"
  default     = "ubuntu-22-04-x64"
}

variable "ssh_public_key_path" {
  type        = string
  description = "Path to SSH public key"
  default     = "~/.ssh/id_rsa.pub"
}

variable "ssh_allowed_ips" {
  type        = list(string)
  description = "IP addresses allowed to SSH (use 0.0.0.0/0 for all)"
  default     = ["0.0.0.0/0"]
}

variable "droplet_tags" {
  type        = list(string)
  description = "Tags to apply to droplets"
  default     = ["web", "production", "ubuntu"]
}

variable "enable_backups" {
  type        = bool
  description = "Enable automatic backups for droplets"
  default     = true
}

# =============================================================================
# Application Configuration
# =============================================================================

variable "app_port" {
  type        = number
  description = "Port the application listens on"
  default     = 80
}

variable "jwt_secret" {
  type        = string
  description = "JWT secret key"
  sensitive   = true
}

# =============================================================================
# Database Configuration
# =============================================================================

variable "postgres_version" {
  type        = string
  description = "PostgreSQL version"
  default     = "16"
}

variable "db_size" {
  type        = string
  description = "Database droplet size"
  default     = "db-s-2vcpu-4gb"
}

variable "db_node_count" {
  type        = number
  description = "Number of database nodes"
  default     = 2
}

variable "db_ha_enabled" {
  type        = bool
  description = "Enable high availability for database"
  default     = true
}

variable "db_name" {
  type        = string
  description = "Database name"
  default     = "appdb"
}

variable "db_user" {
  type        = string
  description = "Database user"
  default     = "appuser"
}

variable "db_backup_retention_days" {
  type        = number
  description = "Database backup retention in days"
  default     = 7
}

variable "db_allowed_ips" {
  type        = list(string)
  description = "IP addresses allowed to connect to database"
  default     = []
}

# =============================================================================
# Redis Configuration
# =============================================================================

variable "deploy_redis" {
  type        = bool
  description = "Deploy managed Redis"
  default     = true
}

variable "redis_version" {
  type        = string
  description = "Redis version"
  default     = "7"
}

variable "redis_size" {
  type        = string
  description = "Redis droplet size"
  default     = "db-s-1vcpu-1gb"
}

variable "redis_host" {
  type        = string
  description = "Redis host (if deploying externally)"
  default     = ""
}

variable "redis_port" {
  type        = number
  description = "Redis port"
  default     = 6379
}

# =============================================================================
# Load Balancer Configuration
# =============================================================================

variable "redirect_http_to_https" {
  type        = bool
  description = "Redirect HTTP traffic to HTTPS"
  default     = true
}

# =============================================================================
# VPC Configuration
# =============================================================================

variable "vpc_ip_range" {
  type        = string
  description = "VPC IP range"
  default     = "10.20.0.0/16"
}

# =============================================================================
# Optional Features
# =============================================================================

variable "create_floating_ip" {
  type        = bool
  description = "Create a floating IP for the first droplet"
  default     = false
}

variable "create_dns_records" {
  type        = bool
  description = "Create DNS records (requires domain managed by DO)"
  default     = false
}

variable "domain_name" {
  type        = string
  description = "Domain name (must be managed by DigitalOcean DNS)"
  default     = "example.com"
}

variable "subdomain" {
  type        = string
  description = "Subdomain for the application"
  default     = "app"
}
