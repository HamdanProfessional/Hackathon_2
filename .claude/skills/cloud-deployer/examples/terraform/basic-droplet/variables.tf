variable "do_token" {
  type        = string
  description = "DigitalOcean API token"
  sensitive   = true
}

variable "project_name" {
  type        = string
  description = "Project name"
  default     = "todo-app"
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

variable "droplet_size" {
  type        = string
  description = "Droplet size slug"
  default     = "s-1vcpu-1gb"

  validation {
    condition     = can(regex("^s-[0-9]+vcpu-[0-9]+gb$", var.droplet_size))
    error_message = "Droplet size must be a valid size slug (e.g., s-1vcpu-1gb)."
  }
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
  description = "Tags to apply to the droplet"
  default     = ["web", "production", "ubuntu"]
}
