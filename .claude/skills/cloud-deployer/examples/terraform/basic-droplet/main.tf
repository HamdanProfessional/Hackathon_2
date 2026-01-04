# Basic DigitalOcean Droplet Example
#
# This example creates a simple Ubuntu droplet with:
# - SSH key access
# - Cloud firewall (SSH, HTTP, HTTPS only)
# - Monitoring enabled
# - User data script for initial setup
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
}

provider "digitalocean" {
  token = var.do_token
}

# SSH Key for droplet access
resource "digitalocean_ssh_key" "deploy_key" {
  name       = "deploy-key"
  public_key = file(var.ssh_public_key_path)
}

# Cloud Firewall - only allow SSH, HTTP, HTTPS
resource "digitalocean_firewall" "web_firewall" {
  name        = "web-firewall"
  droplet_ids = [digitalocean_droplet.web.id]

  # SSH from your IP only
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.ssh_allowed_ips
  }

  # HTTP from anywhere
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

  # Outbound traffic
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  tags = ["web", "production"]
}

# Ubuntu Droplet
resource "digitalocean_droplet" "web" {
  image  = "ubuntu-22-04-x64"
  name   = "${var.project_name}-web-${var.environment}"
  region = var.region

  size = var.droplet_size

  # SSH key
  ssh_keys = [digitalocean_ssh_key.deploy_key.fingerprint]

  # Enable monitoring and backups
  monitoring  = true
  ipv6        = true

  # User data script for initial setup
  user_data = file("${path.module}/user-data.sh")

  # Tags for organization
  tags = var.droplet_tags

  # Backup policy
  backups {
    # Keep daily backups for 1 week
  # Keep weekly backups for 1 month
  retention_days = 30
  }
}

# Project for organization
resource "digitalocean_project" "web_project" {
  name        = "${var.project_name}-${var.environment}"
  description = "${var.project_name} web application - ${var.environment} environment"
  purpose     = "Web Application"
  environment = var.environment

  resources = [
    digitalocean_droplet.web.urn
  ]
}
