output "droplet_id" {
  description = "ID of the droplet"
  value       = digitalocean_droplet.web.id
}

output "droplet_name" {
  description = "Name of the droplet"
  value       = digitalocean_droplet.web.name
}

output "droplet_ip" {
  description = "Public IPv4 address of the droplet"
  value       = digitalocean_droplet.web.ipv4_address
}

output "droplet_ip_v6" {
  description = "Public IPv6 address of the droplet"
  value       = digitalocean_droplet.web.ipv6_address
}

output "droplet_urn" {
  description = "URN of the droplet (for project assignment)"
  value       = digitalocean_droplet.web.urn
}

output "ssh_command" {
  description = "SSH command to connect to the droplet"
  value       = "ssh root@${digitalocean_droplet.web.ipv4_address}"
}

output "web_url" {
  description = "URL to access the web application"
  value       = "http://${digitalocean_droplet.web.ipv4_address}"
}

output "firewall_id" {
  description = "ID of the firewall"
  value       = digitalocean_firewall.web_firewall.id
}

output "project_id" {
  description = "ID of the project"
  value       = digitalocean_project.web_project.id
}
