variable "do_token" {
  type        = string
  description = "DigitalOcean API token"
  sensitive   = true
}

variable "project_name" {
  type        = string
  description = "Project name (used for resource naming)"
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
  description = "DigitalOcean region for cluster"
  default     = "nyc1"

  validation {
    condition     = contains(["nyc1", "nyc2", "nyc3", "ams3", "sfo2", "sfo3", "fra1", "sgp1", "lon1", "tor1", "bangalore"], var.region)
    error_message = "Region must be a valid DigitalOcean region."
  }
}

variable "spaces_region" {
  type        = string
  description = "DigitalOcean region for Spaces (must support Spaces)"
  default     = "nyc3"

  validation {
    condition     = contains(["nyc3", "ams3", "sfo2", "sfo3", "sgp1", "fra1"], var.spaces_region)
    error_message = "Spaces region must support Spaces object storage."
  }
}

variable "kubernetes_version" {
  type        = string
  description = "Kubernetes version (leave empty for latest)"
  default     = "1.28.2-do.0"

  validation {
    condition     = can(regex("^1\\.(2[4-9]|[3-9][0-9])\\.", var.kubernetes_version))
    error_message = "Kubernetes version must be valid format (e.g., 1.28.2-do.0)."
  }
}

# =============================================================================
# Node Pool Configuration
# =============================================================================

variable "default_node_size" {
  type        = string
  description = "Droplet size for default node pool"
  default     = "s-2vcpu-4gb"

  validation {
    condition     = can(regex("^[sg]-[0-9]+vcpu-[0-9]+gb$", var.default_node_size))
    error_message = "Node size must be valid format (e.g., s-2vcpu-4gb)."
  }
}

variable "default_node_count" {
  type        = number
  description = "Initial node count for default pool"
  default     = 2

  validation {
    condition     = var.default_node_count >= 1 && var.default_node_count <= 100
    error_message = "Node count must be between 1 and 100."
  }
}

variable "min_nodes" {
  type        = number
  description = "Minimum nodes for auto-scaling"
  default     = 1

  validation {
    condition     = var.min_nodes >= 1
    error_message = "Minimum nodes must be at least 1."
  }
}

variable "max_nodes" {
  type        = number
  description = "Maximum nodes for auto-scaling"
  default     = 5

  validation {
    condition     = var.max_nodes >= var.min_nodes
    error_message = "Maximum nodes must be greater than or equal to minimum nodes."
  }
}

# =============================================================================
# Database Node Pool
# =============================================================================

variable "database_node_size" {
  type        = string
  description = "Droplet size for database node pool"
  default     = "s-4vcpu-16gb"  # Memory optimized

  validation {
    condition     = can(regex("^[sg]-[0-9]+vcpu-[0-9]+gb$", var.database_node_size))
    error_message = "Database node size must be valid format."
  }
}

variable "database_node_count" {
  type        = number
  description = "Initial node count for database pool"
  default     = 1

  validation {
    condition     = var.database_node_count >= 1
    error_message = "Database node count must be at least 1."
  }
}

# =============================================================================
# GPU Nodes
# =============================================================================

variable "enable_gpu_nodes" {
  type        = bool
  description = "Enable GPU node pool for ML/AI workloads"
  default     = false
}

# =============================================================================
# High Availability
# =============================================================================

variable "ha_enabled" {
  type        = bool
  description = "Enable HA control plane (3 replicas, recommended for production)"
  default     = true
}

# =============================================================================
# Database Configuration
# =============================================================================

variable "postgres_version" {
  type        = string
  description = "PostgreSQL version"
  default     = "16"

  validation {
    condition     = contains(["14", "15", "16"], var.postgres_version)
    error_message = "PostgreSQL version must be 14, 15, or 16."
  }
}

variable "db_size" {
  type        = string
  description = "Database droplet size"
  default     = "db-s-2vcpu-4gb"

  validation {
    condition     = can(regex("^db-[sgs]-[0-9]+vcpu-[0-9]+gb$", var.db_size))
    error_message = "Database size must be valid format (e.g., db-s-2vcpu-4gb)."
  }
}

variable "db_node_count" {
  type        = number
  description = "Number of database nodes (1 for standalone, 2-3 for HA)"
  default     = 2

  validation {
    condition     = var.db_node_count >= 1 && var.db_node_count <= 3
    error_message = "Database node count must be between 1 and 3."
  }
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
  description = "Number of days to retain backups"
  default     = 7

  validation {
    condition     = var.db_backup_retention_days >= 1 && var.db_backup_retention_days <= 28
    error_message = "Backup retention must be between 1 and 28 days."
  }
}

variable "db_allowed_ips" {
  type        = list(string)
  description = "IP addresses allowed to connect to database"
  default     = []
}

# =============================================================================
# Spaces Configuration
# =============================================================================

variable "spaces_cdn_enabled" {
  type        = bool
  description = "Enable CDN for Spaces bucket"
  default     = true
}

variable "spaces_cors_origins" {
  type        = list(string)
  description = "Allowed CORS origins for Spaces"
  default     = ["https://*.example.com", "https://example.com"]
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
  description = "IP range for VPC"
  default     = "10.10.0.0/16"

  validation {
    condition     = can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]+$", var.vpc_ip_range))
    error_message = "VPC IP range must be valid CIDR notation."
  }
}

# =============================================================================
# Tags
# =============================================================================

variable "cluster_tags" {
  type        = list(string)
  description = "Tags to apply to all resources"
  default     = ["kubernetes", "production", "todo-app"]
}
