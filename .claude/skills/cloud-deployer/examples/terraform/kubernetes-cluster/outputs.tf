# =============================================================================
# Kubernetes Cluster Outputs
# =============================================================================

output "cluster_id" {
  description = "ID of the Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.main.id
}

output "cluster_name" {
  description = "Name of the Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.main.name
}

output "cluster_endpoint" {
  description = "Kubernetes API server endpoint"
  value       = digitalocean_kubernetes_cluster.main.endpoint
}

output "cluster_version" {
  description = "Kubernetes version"
  value       = digitalocean_kubernetes_cluster.main.version
}

output "cluster_status" {
  description = "Cluster status"
  value       = digitalocean_kubernetes_cluster.main.status
}

output "kubeconfig_file" {
  description = "Path to kubeconfig file"
  value       = local_file.kubeconfig.filename
}

output "kubeconfig_raw" {
  description = "Raw kubeconfig content"
  value       = nonsensitive(data.digitalocean_kubernetes_cluster.credentials.kube_config[0].raw_config)
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "Base64 encoded cluster CA certificate"
  value       = data.digitalocean_kubernetes_cluster.credentials.kube_config[0].cluster_ca_certificate
  sensitive   = true
}

output "cluster_token" {
  description = "Kubernetes authentication token"
  value       = data.digitalocean_kubernetes_cluster.credentials.kube_config[0].token
  sensitive   = true
}

# =============================================================================
# Node Pool Outputs
# =============================================================================

output "default_node_pool" {
  description = "Default node pool details"
  value = {
    id        = digitalocean_kubernetes_cluster.main.default_node_pool[0].id
    name      = digitalocean_kubernetes_cluster.main.default_node_pool[0].name
    size      = digitalocean_kubernetes_cluster.main.default_node_pool[0].size
    node_count = digitalocean_kubernetes_cluster.main.default_node_pool[0].node_count
    min_nodes = digitalocean_kubernetes_cluster.main.default_node_pool[0].min_nodes
    max_nodes = digitalocean_kubernetes_cluster.main.default_node_pool[0].max_nodes
  }
}

output "database_node_pool" {
  description = "Database node pool details"
  value = {
    id        = digitalocean_kubernetes_node_pool.database[0].id
    name      = digitalocean_kubernetes_node_pool.database[0].name
    size      = digitalocean_kubernetes_node_pool.database[0].size
    node_count = digitalocean_kubernetes_node_pool.database[0].node_count
    min_nodes = digitalocean_kubernetes_node_pool.database[0].min_nodes
    max_nodes = digitalocean_kubernetes_node_pool.database[0].max_nodes
  }
}

output "gpu_node_pool" {
  description = "GPU node pool details (if enabled)"
  value = var.enable_gpu_nodes ? {
    id        = digitalocean_kubernetes_node_pool.gpu[0].id
    name      = digitalocean_kubernetes_node_pool.gpu[0].name
    size      = digitalocean_kubernetes_node_pool.gpu[0].size
    node_count = digitalocean_kubernetes_node_pool.gpu[0].node_count
  } : null
}

output "total_nodes" {
  description = "Total number of nodes across all node pools"
  value = sum([
    digitalocean_kubernetes_cluster.main.default_node_pool[0].node_count,
    digitalocean_kubernetes_node_pool.database[0].node_count,
    var.enable_gpu_nodes ? digitalocean_kubernetes_node_pool.gpu[0].node_count : 0,
  ])
}

# =============================================================================
# Load Balancer Outputs
# =============================================================================

output "load_balancer_id" {
  description = "ID of the load balancer"
  value       = digitalocean_load_balancer.main.id
}

output "load_balancer_ip" {
  description = "Public IP of the load balancer"
  value       = digitalocean_load_balancer.main.ip
}

output "load_balancer_name" {
  description = "Name of the load balancer"
  value       = digitalocean_load_balancer.main.name
}

output "load_balancer_status" {
  description = "Load balancer status"
  value       = digitalocean_load_balancer.main.status
}

output "load_balancer_url" {
  description = "URL to access the application via load balancer"
  value       = var.redirect_http_to_https ? "https://${digitalocean_load_balancer.main.ip}" : "http://${digitalocean_load_balancer.main.ip}"
}

# =============================================================================
# Database Outputs
# =============================================================================

output "database_id" {
  description = "ID of the database cluster"
  value       = digitalocean_database_cluster.postgres.id
}

output "database_name" {
  description = "Name of the database cluster"
  value       = digitalocean_database_cluster.postgres.name
}

output "database_host" {
  description = "Database host (private connection)"
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

output "database_private_host" {
  description = "Database private host"
  value       = digitalocean_database_cluster.postgres.private_host
  sensitive   = true
}

output "database_private_uri" {
  description = "Database private connection URI"
  value       = "postgresql://${digitalocean_database_user.app_user.name}:${digitalocean_database_user.app_user.password}@${digitalocean_database_cluster.postgres.private_host}:${digitalocean_database_cluster.postgres.port}/${digitalocean_database_db.app_db.name}?sslmode=require"
  sensitive   = true
}

# =============================================================================
# Spaces Outputs
# =============================================================================

output "spaces_bucket_name" {
  description = "Name of the Spaces bucket"
  value       = digitalocean_spaces_bucket.assets.name
}

output "spaces_bucket_domain" {
  description = "Bucket domain name"
  value       = digitalocean_spaces_bucket.assets.bucket_domain_name
}

output "spaces_cdn_endpoint" {
  description = "CDN endpoint for Spaces bucket"
  value       = digitalocean_spaces_bucket.assets.cdn_endpoint
}

output "spaces_url" {
  description = "URL to access Spaces (via CDN if enabled, otherwise direct)"
  value       = var.spaces_cdn_enabled ? digitalocean_spaces_bucket.assets.cdn_endpoint : digitalocean_spaces_bucket.assets.bucket_domain_name
}

output "spaces_region" {
  description = "Spaces region"
  value       = digitalocean_spaces_bucket.assets.region
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

output "project_owner_id" {
  description = "Owner ID of the project"
  value       = digitalocean_project.main.owner_id
}

output "project_created_at" {
  description = "Project creation timestamp"
  value       = digitalocean_project.main.created_at
}

# =============================================================================
# Helm Releases Outputs
# =============================================================================

output "nginx_ingress_namespace" {
  description = "Nginx Ingress namespace"
  value       = helm_release.nginx_ingress.namespace
}

output "nginx_ingress_status" {
  description = "Nginx Ingress deployment status"
  value       = helm_release.nginx_ingress.status
}

output "cert_manager_namespace" {
  description = "Cert Manager namespace"
  value       = helm_release.cert_manager.namespace
}

output "cert_manager_status" {
  description = "Cert Manager deployment status"
  value       = helm_release.cert_manager.status
}

# =============================================================================
# Useful Commands Outputs
# =============================================================================

output "kubectl_config_command" {
  description = "Command to configure kubectl"
  value       = "export KUBECONFIG=${abspath(local_file.kubeconfig.filename)}"
}

output "kubectl_get_nodes" {
  description = "Command to get cluster nodes"
  value       = "kubectl get nodes -o wide"
}

output "kubectl_get_pods" {
  description = "Command to get all pods"
  value       = "kubectl get pods --all-namespaces"
}

output "doctl_kubeconfig_save" {
  description = "Command to save kubeconfig using doctl"
  value       = "doctl kubernetes cluster kubeconfig save ${digitalocean_kubernetes_cluster.main.id}"
}

# =============================================================================
# Connection Information
# =============================================================================

output "access_information" {
  description = "Application access information"
  value = {
    application_url  = var.redirect_http_to_https ? "https://${digitalocean_load_balancer.main.ip}" : "http://${digitalocean_load_balancer.main.ip}"
    api_endpoint     = digitalocean_kubernetes_cluster.main.endpoint
    database_host    = digitalocean_database_cluster.postgres.private_host
    storage_url      = var.spaces_cdn_enabled ? digitalocean_spaces_bucket.assets.cdn_endpoint : digitalocean_spaces_bucket.assets.bucket_domain_name
    load_balancer_ip = digitalocean_load_balancer.main.ip
  }
}

output "quick_start_commands" {
  description = "Quick start commands to get started"
  value = <<-EOT
    # Configure kubectl
    export KUBECONFIG=${abspath(local_file.kubeconfig.filename)}

    # Or use doctl
    doctl kubernetes cluster kubeconfig save ${digitalocean_kubernetes_cluster.main.id}

    # Verify cluster connection
    kubectl cluster-info
    kubectl get nodes

    # Check ingress controller
    kubectl get pods -n ingress-nginx

    # Check cert-manager
    kubectl get pods -n cert-manager

    # Access application
    curl http://${digitalocean_load_balancer.main.ip}
  EOT
}
