# =============================================================================
# Load Balancer Outputs
# =============================================================================

output "load_balancer_id" {
  description = "ID of the load balancer"
  value       = digitalocean_load_balancer.web.id
}

output "load_balancer_ip" {
  description = "Public IP of the load balancer"
  value       = digitalocean_load_balancer.web.ip
}

output "load_balancer_name" {
  description = "Name of the load balancer"
  value       = digitalocean_load_balancer.web.name
}

output "load_balancer_status" {
  description = "Load balancer status"
  value       = digitalocean_load_balancer.web.status
}

output "load_balancer_url" {
  description = "URL to access the application"
  value       = var.redirect_http_to_https ? "https://${digitalocean_load_balancer.web.ip}" : "http://${digitalocean_load_balancer.web.ip}"
}

# =============================================================================
# Droplet Outputs
# =============================================================================

output "droplet_ids" {
  description = "IDs of all web droplets"
  value       = digitalocean_droplet.web[*].id
}

output "droplet_names" {
  description = "Names of all web droplets"
  value       = digitalocean_droplet.web[*].name
}

output "droplet_ips" {
  description = "Public IPs of all web droplets"
  value       = digitalocean_droplet.web[*].ipv4_address
}

output "droplet_private_ips" {
  description = "Private IPs of all web droplets"
  value       = digitalocean_droplet.web[*].ipv4_address_private
}

output "droplet_count" {
  description = "Number of droplets"
  value       = var.droplet_count
}

output "ssh_commands" {
  description = "SSH commands to connect to each droplet"
  value = [
    for ip in digitalocean_droplet.web[*].ipv4_address :
    "ssh root@${ip}"
  ]
}

# =============================================================================
# Database Outputs
# =============================================================================

output "database_id" {
  description = "ID of the database cluster"
  value       = digitalocean_database_cluster.postgres.id
}

output "database_host" {
  description = "Database host"
  value       = digitalocean_database_cluster.postgres.host
  sensitive   = true
}

output "database_port" {
  description = "Database port"
  value       = digitalocean_database_cluster.postgres.port
}

output "database_uri" {
  description = "Database connection URI"
  value       = "postgresql://${digitalocean_database_user.app_user.name}:${digitalocean_database_user.app_user.password}@${digitalocean_database_cluster.postgres.host}:${digitalocean_database_cluster.postgres.port}/${digitalocean_database_db.app_db.name}?sslmode=require"
  sensitive   = true
}

output "database_user" {
  description = "Database user"
  value       = digitalocean_database_user.app_user.name
}

output "database_password" {
  description = "Database password"
  value       = digitalocean_database_user.app_user.password
  sensitive   = true
}

# =============================================================================
# Redis Outputs
# =============================================================================

output "redis_id" {
  description = "ID of the Redis cluster"
  value       = var.deploy_redis ? digitalocean_database_cluster.redis[0].id : null
}

output "redis_host" {
  description = "Redis host"
  value       = var.deploy_redis ? digitalocean_database_cluster.redis[0].host : var.redis_host
  sensitive   = true
}

output "redis_port" {
  description = "Redis port"
  value       = var.deploy_redis ? digitalocean_database_cluster.redis[0].port : var.redis_port
}

output "redis_uri" {
  description = "Redis connection URI"
  value       = var.deploy_redis ? "redis://${digitalocean_database_cluster.redis[0].host}:${digitalocean_database_cluster.redis[0].port}" : ""
  sensitive   = true
}

# =============================================================================
# Firewall Outputs
# =============================================================================

output "firewall_id" {
  description = "ID of the firewall"
  value       = digitalocean_firewall.web_fw.id
}

output "firewall_name" {
  description = "Name of the firewall"
  value       = digitalocean_firewall.web_fw.name
}

# =============================================================================
# VPC Outputs
# =============================================================================

output "vpc_id" {
  description = "ID of the VPC"
  value       = digitalocean_vpc.main.id
}

output "vpc_name" {
  description = "Name of the VPC"
  value       = digitalocean_vpc.main.name
}

output "vpc_ip_range" {
  description = "VPC IP range"
  value       = digitalocean_vpc.main.ip_range
}

# =============================================================================
# Floating IP Outputs
# =============================================================================

output "floating_ip" {
  description = "Floating IP address (if created)"
  value       = var.create_floating_ip ? digitalocean_floating_ip.main[0].ip_address : null
}

# =============================================================================
# Project Outputs
# =============================================================================

output "project_id" {
  description = "ID of the project"
  value       = digitalocean_project.main.id
}

output "project_name" {
  description = "Name of the project"
  value       = digitalocean_project.main.name
}

# =============================================================================
# Access Information
# =============================================================================

output "access_information" {
  description = "Summary of access information"
  value = {
    application_url    = var.redirect_http_to_https ? "https://${digitalocean_load_balancer.web.ip}" : "http://${digitalocean_load_balancer.web.ip}"
    load_balancer_ip   = digitalocean_load_balancer.web.ip
    droplet_ips        = digitalocean_droplet.web[*].ipv4_address
    droplet_names      = digitalocean_droplet.web[*].name
    database_host      = digitalocean_database_cluster.postgres.host
    redis_host         = var.deploy_redis ? digitalocean_database_cluster.redis[0].host : null
    floating_ip        = var.create_floating_ip ? digitalocean_floating_ip.main[0].ip_address : null
  }
}

# =============================================================================
# Useful Commands
# =============================================================================

output "curl_commands" {
  description = "Commands to test the application"
  value = [
    "curl http://${digitalocean_load_balancer.web.ip}",
    "curl https://${digitalocean_load_balancer.web.ip}",
    "curl http://${digitalocean_load_balancer.web.ip}/health",
  ]
}

output "quick_start_commands" {
  description = "Quick start commands"
  value = <<-EOT
    # Test the application
    curl http://${digitalocean_load_balancer.web.ip}/health

    # SSH to a droplet
    ssh root@${digitalocean_droplet.web[0].ipv4_address}

    # Check droplet status
    doctl compute droplet list

    # Check load balancer status
    doctl compute load-balancer get ${digitalocean_load_balancer.web.id}

    # View application logs
    doctl compute droplet ssh ${digitalocean_droplet.web[0].id} --command "journalctl -u app -f"
  EOT
}
