# Terraform DigitalOcean Provider Reference

Complete reference for using Terraform with DigitalOcean infrastructure.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Provider Configuration](#provider-configuration)
3. [Droplets](#droplets)
4. [Kubernetes](#kubernetes)
5. [Load Balancers](#load-balancers)
6. [Spaces](#spaces)
7. [Databases](#databases)
8. [Firewalls](#firewalls)
9. [App Platform](#app-platform)
10. [Examples](#examples)

---

## Getting Started

### Installation
```bash
# Install Terraform
brew install terraform  # macOS
# Or download from: https://www.terraform.io/downloads

# Install DigitalOcean provider
terraform init
```

### Initial Configuration
```hcl
# main.tf
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
```

### Environment Variables
```bash
export DIGITALOCEAN_TOKEN="your-api-token"
terraform plan
```

---

## Provider Configuration

### Provider Block
```hcl
provider "digitalocean" {
  token = var.do_token
  spaces_access_id  = var.spaces_access_id
  spaces_secret_key = var.spaces_secret_key
}
```

### Required Resources
- **API Token**: Generate at https://cloud.digitalocean.com/settings/api/tokens
- **Spaces Keys**: For Spaces resources (optional for compute only)

### Example Variables
```hcl
variable "do_token" {
  type        = string
  sensitive   = true
  description = "DigitalOcean API token"
}

variable "spaces_access_id" {
  type        = string
  sensitive   = true
  description = "Spaces access key"
}

variable "spaces_secret_key" {
  type        = string
  sensitive   = true
  description = "Spaces secret key"
}
```

---

## Droplets

### Basic Droplet
```hcl
resource "digitalocean_droplet" "web" {
  image  = "ubuntu-22-04-x64"
  name   = "web-1"
  region = "nyc1"
  size   = "s-1vcpu-1gb"

  tags   = ["web", "production"]
}
```

### Droplet with SSH Keys
```hcl
resource "digitalocean_ssh_key" "my_key" {
  name       = "my-key"
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "digitalocean_droplet" "web" {
  image  = "ubuntu-22-04-x64"
  name   = "web-1"
  region = "nyc1"
  size   = "s-1vcpu-1gb"

  ssh_keys = [digitalocean_ssh_key.my_key.fingerprint]
}
```

### Droplet with Monitoring
```hcl
resource "digitalocean_droplet" "web" {
  image  = "ubuntu-22-04-x64"
  name   = "web-1"
  region = "nyc1"
  size   = "s-1vcpu-1gb"

  monitoring  = true
  ipv6        = true
}
```

### Multiple Droplets
```hcl
resource "digitalocean_droplet" "web" {
  count  = 3

  image  = "ubuntu-22-04-x64"
  name   = "web-${count.index + 1}"
  region = "nyc1"
  size   = "s-1vcpu-1gb"

  tags   = ["web", "production"]
}
```

---

## Kubernetes

### Basic Cluster
```hcl
resource "digitalocean_kubernetes_cluster" "my_cluster" {
  name    = "my-cluster"
  region  = "nyc1"

  version = "latest"

  node_pool {
    name       = "worker-pool"
    size       = "s-2vcpu-4gb"
    node_count = 3
  }
}
```

### Advanced Cluster
```hcl
resource "digitalocean_kubernetes_cluster" "my_cluster" {
  name    = "my-cluster"
  region  = "nyc1"

  version         = "1.27.1-do.0"
  auto_upgrade    = true
  surge_upgrade    = true
  ha              = true

  maintenance_policy {
    day        = "sunday"
    start_time = "02:00"
  }

  node_pool {
    name       = "worker-pool"
    size       = "s-2vcpu-4gb"
    node_count = 3
    auto_scale = true
    min_nodes  = 3
    max_nodes  = 10

    labels = {
      environment = "production"
      workload     = "general"
    }

    taint {
      key    = "workload"
      value  = "general"
      effect = "NoSchedule"
    }
  }
}
```

### Multiple Node Pools
```hcl
resource "digitalocean_kubernetes_cluster" "my_cluster" {
  name   = "my-cluster"
  region = "nyc1"

  node_pool {
    name       = "general"
    size       = "s-2vcpu-4gb"
    node_count = 2
  }

  node_pool {
    name       = "compute"
    size       = "c-2-4gb"
    node_count = 2
  }
}
```

### Cluster Registry
```hcl
data "digitalocean_kubernetes_cluster" "my_cluster" {
  name = digitalocean_kubernetes_cluster.my_cluster.name
}

provider "kubernetes" {
  host  = data.digitalocean_kubernetes_cluster.my_cluster.endpoint
  token = data.digitalocean_kubernetes_cluster.my_cluster.kube_config[0].token
  cluster_ca_certificate = base64decode(
    data.digitalocean_kubernetes_cluster.my_cluster.kube_config[0].cluster_ca_certificate
  )
}
```

---

## Load Balancers

### Basic Load Balancer
```hcl
resource "digitalocean_loadbalancer" "public" {
  name   = "web-lb"
  region = "nyc1"

  forwarding_rule {
    entry_port     = 80
    entry_protocol = "http"

    target_port     = 80
    target_protocol = "http"
  }

  healthcheck {
    port     = 80
    protocol = "http"
    path     = "/"
  }

  droplet_ids = digitalocean_droplet.web[*].id
}
```

### HTTPS Load Balancer
```hcl
resource "digitalocean_certificate" "cert" {
  name             = "my-cert"
  type             = "lets_encrypt"
  domains          = ["example.com", "www.example.com"]
}

resource "digitalocean_loadbalancer" "public" {
  name   = "web-lb"
  region = "nyc1"

  forwarding_rule {
    entry_port     = 80
    entry_protocol = "http"

    target_port     = 80
    target_protocol = "http"

    certificate_id = digitalocean_certificate.cert.id
  }

  forwarding_rule {
    entry_port     = 443
    entry_protocol = "https"

    target_port     = 80
    target_protocol = "http"

    certificate_id = digitalocean_certificate.cert.id
  }

  redirect_http_to_https = true

  droplet_ids = digitalocean_droplet.web[*].id
}
```

### Sticky Sessions
```hcl
resource "digitalocean_loadbalancer" "public" {
  name   = "web-lb"
  region = "nyc1"

  sticky_sessions {
    type             = "cookies"
    cookie_name      = "lb_sticky"
    cookie_ttl_seconds = 300
  }

  # ... rest of configuration
}
```

---

## Spaces

### Spaces Bucket
```hcl
resource "digitalocean_spaces_bucket" "assets" {
  name   = "my-assets"
  region = "nyc3"

  acl = "public-read"

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    max_age_seconds = 3600
  }

  lifecycle_rule {
    enabled = true

    abort_incomplete_multipart_upload_days = 7

    noncurrent_version_expiration_days = 90
  }

  versioning {
    enabled = true
  }
}
```

### Spaces with CDN
```hcl
resource "digitalocean_spaces_bucket" "assets" {
  name   = "my-assets"
  region = "nyc3"

  cdn {
    enabled           = true
    ttl               = 3600
    certificate_name  = "my-cert"
    custom_domain     = "cdn.example.com"
  }
}
```

### Using AWS S3 Provider
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"

  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    s3 = "https://nyc3.digitaloceanspaces.com"
  }
}

resource "aws_s3_bucket" "assets" {
  bucket = "my-assets"
  acl    = "public-read"
}

resource "aws_s3_object" "files" {
  for_each = fileset("assets/", "*")

  bucket = aws_s3_bucket.assets.id
  key    = each.value
  source = "assets/${each.value}"

  etag = filemd5("assets/${each.value}")
}
```

---

## Databases

### PostgreSQL
```hcl
resource "digitalocean_database_cluster" "postgres" {
  name       = "postgres-cluster"
  engine     = "pg"
  version    = "15"
  size       = "db-s-1vcpu-1gb"
  region     = "nyc1"
  node_count = 1

  maintenance_window {
    day  = "sunday"
  hour = 2
  }
}
```

### MySQL
```hcl
resource "digitalocean_database_cluster" "mysql" {
  name       = "mysql-cluster"
  engine     = "mysql"
  version    = "8"
  size       = "db-s-1vcpu-1gb"
  region     = "nyc1"
  node_count = 1
}
```

### Redis
```hcl
resource "digitalocean_database_cluster" "redis" {
  name       = "redis-cluster"
  engine     = "redis"
  version    = "7"
  size       = "db-s-1vcpu-1gb"
  region     = "nyc1"
  node_count = 1
}
```

### Database Connection Data
```hcl
data "digitalocean_database_connection" "postgres_conn" {
  cluster_id = digitalocean_database_cluster.postgres.id
}

output "database_host" {
  value = data.digitalocean_database_connection.postgres_conn.host
}

output "database_port" {
  value = data.digitalocean_database_connection.postgres_conn.port
}

output "database_uri" {
  value     = data.digitalocean_database_connection.postgres_conn.uri
  sensitive = true
}
```

### Database Firewall
```hcl
resource "digitalocean_database_firewall" "postgres_fw" {
  cluster_id = digitalocean_database_cluster.postgres.id

  rule {
    type  = "k8s"
    value = digitalocean_kubernetes_cluster.my_cluster.id
  }
}
```

---

## Firewalls

### Basic Firewall
```hcl
resource "digitalocean_firewall" "web" {
  name        = "web-firewall"
  droplet_ids = digitalocean_droplet.web[*].id

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["192.0.2.0/24"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0"]
  }
}
```

### Kubernetes Firewall
```hcl
resource "digitalocean_firewall" "k8s" {
  name = "k8s-firewall"

  # Get cluster node IPs dynamically
  inbound_rule {
    protocol                  = "tcp"
    port_range                = "6443"  # Kubernetes API
    source_addresses          = ["0.0.0.0/0"]
  }

  # Apply to cluster nodes
  tags = ["k8s", digitalocean_kubernetes_cluster.my_cluster.id]
}
```

---

## App Platform

### Basic App
```hcl
resource "digitalocean_app" "web" {
  spec {
    name   = "web-app"
    region = "nyc1"

    service {
      name               = "web"
      dockerfile_path     = "Dockerfile"
      github {
        repo           = "username/repo"
        branch         = "main"
      }

      instance_count = 2
      instance_size_slug = "basic-xxs"

      http_port = 8080

      env {
        key   = "PORT"
        value = "8080"
      }
    }
  }
}
```

### App with Database
```hcl
resource "digitalocean_app" "web" {
  spec {
    name   = "web-app"
    region = "nyc1"

    service {
      name = "web"
      # ... service config

      env {
        key   = "DATABASE_URL"
        value = digitalocean_database_cluster.postgres.uri
      }
    }

    database {
      name       = "db"
      engine     = "PG"
      version    = "15"
      size       = "db-s-1vcpu-1gb"
      production = true
    }
  }
}
```

### App with Jobs
```hcl
resource "digitalocean_app" "web" {
  spec {
    name   = "web-app"
    region = "nyc1"

    job {
      name           = "migrate"
      dockerfile_path = "Dockerfile"
      github {
        repo   = "username/repo"
        branch = "main"
      }
      kind           = "PRE_DEPLOY"
      run_command    = "alembic upgrade head"

      env {
        key   = "DATABASE_URL"
        value = digitalocean_database_cluster.postgres.uri
      }
    }
  }
}
```

---

## Examples

### Full Stack Web Application
```hcl
terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

# SSH Key
resource "digitalocean_ssh_key" "deploy" {
  name       = "deploy-key"
  public_key = file("~/.ssh/id_rsa.pub")
}

# Droplets
resource "digitalocean_droplet" "app" {
  count  = 2

  image  = "ubuntu-22-04-x64"
  name   = "app-${count.index + 1}"
  region = "nyc1"
  size   = "s-2vcpu-4gb"

  ssh_keys = [digitalocean_ssh_key.deploy.fingerprint]

  monitoring = true
  ipv6       = true

  tags = ["app", "production"]
}

# Load Balancer
resource "digitalocean_loadbalancer" "public" {
  name   = "app-lb"
  region = "nyc1"

  forwarding_rule {
    entry_port     = 80
    entry_protocol = "http"
    target_port     = 8080
    target_protocol = "http"
  }

  healthcheck {
    port     = 8080
    protocol = "http"
    path     = "/health"
  }

  droplet_ids = digitalocean_droplet.app[*].id

  sticky_sessions {
    type             = "cookies"
    cookie_name      = "app_route"
    cookie_ttl_seconds = 300
  }
}

# Spaces for Assets
resource "digitalocean_spaces_bucket" "assets" {
  name   = "app-assets"
  region = "nyc3"

  acl = "public-read"

  cdn {
    enabled = true
    ttl     = 3600
  }
}

# Database
resource "digitalocean_database_cluster" "db" {
  name       = "app-db"
  engine     = "pg"
  version    = "15"
  size       = "db-s-1vcpu-1gb"
  region     = "nyc1"
  node_count = 1
}

# Firewall
resource "digitalocean_firewall" "app" {
  name        = "app-firewall"
  droplet_ids = digitalocean_droplet.app[*].id

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["10.0.0.0/8"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0"]
  }
}

# Outputs
output "load_balancer_ip" {
  value = digitalocean_loadbalancer.public.ip
}

output "app_droplets" {
  value = digitalocean_droplet.app[*].ipv4_address
}

output "database_uri" {
  value     = digitalocean_database_cluster.db.uri
  sensitive = true
}
```

---

## Common Patterns

### Tags
```hcl
resource "digitalocean_tag" "environment" {
  name = "production"
}

resource "digitalocean_droplet" "web" {
  # ... config
  tags = [digitalocean_tag.environment.id]
}
```

### Projects
```hcl
resource "digitalocean_project" "my_project" {
  name        = "my-project"
  description = "My application"
  purpose     = "Web Application"
  environment = "Production"
}

resource "digitalocean_project_resources" "resources" {
  project = digitalocean_project.my_project.id
  resources = [
    digitalocean_droplet.web.urn,
    digitalocean_load_balancer.public.urn
  ]
}
```

### Volumes
```hcl
resource "digitalocean_volume" "data" {
  name                  = "data-volume"
  region                = "nyc1"
  size                  = 100
  description           = "Application data"
  filesystem_type       = "ext4"
  droplet_id            = digitalocean_droplet.app[0].id
}
```

### Snapshots
```hcl
resource "digitalocean_snapshot" "app" {
  name        = "app-snapshot"
  droplet_id  = digitalocean_droplet.app[0].id
}
```
