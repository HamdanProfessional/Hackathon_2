---
name: cloud-devops-lite-core
description: Lite DevOps and cloud preparation for Docker/Kubernetes deployment. Handles containerization, Docker compose setup, Kubernetes manifests preparation for Phase IV, and basic infrastructure automation. Prepares the application for smooth transition from local development to cloud deployment with minimal complexity.
---

# Cloud DevOps Lite Core

## Quick Start

```python
# Initialize DevOps preparation
from cloud_devops_lite_core import CloudDevOpsLite

devops = CloudDevOpsLite(
    project_name="todo-evolution",
    app_name="todo-app"
)

# Prepare for deployment
await devops.prepare_deployment(
    dockerize=True,
    kubernetes=True,
    compose=True
)
```

## Core Capabilities

### 1. Docker Containerization
```python
class Dockerizer:
    """Creates Docker configurations for all phases."""

    def create_dockerfile_phase1(self):
        """Dockerfile for console app."""
        dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install uv
RUN uv sync

# Copy application
COPY . .

# Run application
CMD ["uv", "run", "python", "main.py"]
"""

        self.write_file("apps/console/Dockerfile", dockerfile)

    def create_dockerfile_phase2(self):
        """Dockerfile for web backend."""
        dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install uv
RUN uv sync

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

        self.write_file("apps/backend/Dockerfile", dockerfile)

    def create_dockerfile_phase3(self):
        """Dockerfile for AI chatbot backend."""
        dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install uv
RUN uv sync

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Copy application
COPY . .

# Expose ports
EXPOSE 8000 8001

# Run MCP server and API server
CMD ["sh", "-c", "uv run python mcp_server.py & uv run uvicorn main:app --host 0.0.0.0 --port 8000"]
"""

        self.write_file("apps/chatbot/Dockerfile", dockerfile)

    def optimize_dockerfile(self, dockerfile_path: str):
        """Optimize Dockerfile for production."""
        with open(dockerfile_path, 'r') as f:
            content = f.read()

        # Multi-stage build optimization
        optimized = f"""
# Builder stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY pyproject.toml .
RUN pip install uv
RUN uv sync --dev

# Production stage
FROM python:3.11-slim

# Install only production dependencies
COPY pyproject.toml .
RUN pip install uv
RUN uv sync

WORKDIR /app
COPY --from=builder /app .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

        self.write_file(dockerfile_path, optimized)
```

### 2. Docker Compose Configuration
```python
class DockerComposeManager:
    """Creates Docker Compose configurations."""

    def create_development_compose(self):
        """Development Docker Compose configuration."""
        compose = {
            "version": "3.8",
            "services": {
                "postgres": {
                    "image": "postgres:15-alpine",
                    "container_name": "todo-postgres",
                    "environment": {
                        "POSTGRES_USER": "todo",
                        "POSTGRES_PASSWORD": "password",
                        "POSTGRES_DB": "todo"
                    },
                    "ports": ["5432:5432"],
                    "volumes": [
                        "postgres_data:/var/lib/postgresql/data",
                        "./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql"
                    ]
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "container_name": "todo-redis",
                    "ports": ["6379:6379"],
                    "volumes": ["redis_data:/data"]
                },
                "backend": {
                    "build": "./apps/backend",
                    "container_name": "todo-backend",
                    "ports": ["8000:8000"],
                    "environment": {
                        "DATABASE_URL": "postgresql://todo:password@postgres:5432/todo",
                        "REDIS_URL": "redis://redis:6379/0"
                    },
                    "depends_on": ["postgres", "redis"],
                    "volumes": ["./apps/backend:/app"],
                    "restart": "unless-stopped"
                },
                "frontend": {
                    "build": "./apps/web",
                    "container_name": "todo-frontend",
                    "ports": ["3000:3000"],
                    "environment": {
                        "NEXT_PUBLIC_API_URL": "http://localhost:8000"
                    },
                    "depends_on": ["backend"],
                    "volumes": ["./apps/web:/app"],
                    "restart": "unless-stopped"
                },
                "mcp-server": {
                    "build": "./apps/chatbot",
                    "container_name": "todo-mcp",
                    "ports": ["8001:8001"],
                    "environment": {
                        "DATABASE_URL": "postgresql://todo:password@postgres:5432/todo"
                    },
                    "depends_on": ["postgres"],
                    "volumes": ["./apps/chatbot:/app"],
                    "restart": "unless-stopped"
                }
            },
            "volumes": {
                "postgres_data": None,
                "redis_data": None
            },
            "networks": {
                "todo-network": {
                    "driver": "bridge"
                }
            }
        }

        self.write_yaml("docker-compose.dev.yml", compose)

    def create_production_compose(self):
        """Production Docker Compose configuration."""
        compose = {
            "version": "3.8",
            "services": {
                "backend": {
                    "image": "todo-backend:latest",
                    "container_name": "todo-backend-prod",
                    "ports": ["8000:8000"],
                    "environment": {
                        "DATABASE_URL": "${DATABASE_URL}",
                        "SECRET_KEY": "${SECRET_KEY}"
                    },
                    "restart": "always",
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": "3"
                    }
                },
                "frontend": {
                    "image": "todo-frontend:latest",
                    "container_name": "todo-frontend-prod",
                    "ports": ["3000:3000"],
                    "environment": {
                        "NEXT_PUBLIC_API_URL": "${NEXT_PUBLIC_API_URL}"
                    },
                    "restart": "always"
                }
            }
        }

        self.write_yaml("docker-compose.prod.yml", compose)
```

### 3. Kubernetes Preparation (Phase IV Ready)
```python
class KubernetesPrep:
    """Prepares Kubernetes manifests for deployment."""

    def create_namespace(self):
        """Create Kubernetes namespace."""
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "todo-app",
                "labels": {
                    "app": "todo-evolution",
                    "phase": "web"
                }
            }
        }

        self.write_yaml("k8s/namespace.yaml", namespace)

    def create_backend_deployment(self):
        """Create backend deployment manifest."""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "todo-backend",
                "namespace": "todo-app"
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "todo-backend"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "todo-backend"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "todo-backend",
                            "image": "todo-backend:latest",
                            "ports": [{
                                "containerPort": 8000
                            }],
                            "env": [{
                                "name": "DATABASE_URL",
                                "valueFrom": {
                                    "secretKeyRef": {
                                        "name": "todo-secrets",
                                        "key": "database-url"
                                    }
                                }
                            }],
                            "resources": {
                                "requests": {
                                    "cpu": "100m",
                                    "memory": "128Mi"
                                },
                                "limits": {
                                    "cpu": "500m",
                                    "memory": "512Mi"
                                }
                            }
                        }]
                    }
                }
            }
        }

        self.write_yaml("k8s/backend-deployment.yaml", deployment)

    def create_service_manifests(self):
        """Create service manifests."""
        # Backend service
        backend_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "todo-backend",
                "namespace": "todo-app"
            },
            "spec": {
                "selector": {
                    "app": "todo-backend"
                },
                "ports": [{
                    "port": 80,
                    "targetPort": 8000
                }],
                "type": "ClusterIP"
            }
        }

        self.write_yaml("k8s/backend-service.yaml", backend_service)

        # Ingress for frontend
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": "todo-ingress",
                "namespace": "todo-app"
            },
            "spec": {
                "rules": [{
                    "host": "todo.example.com",
                    "http": {
                        "paths": [{
                            "path": "/api",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": "todo-backend",
                                    "port": {
                                        "number": 80
                                    }
                                }
                            }
                        }]
                    }
                }]
            }
        }

        self.write_yaml("k8s/ingress.yaml", ingress)

    def create_config_maps(self):
        """Create ConfigMap for application configuration."""
        config_map = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "todo-config",
                "namespace": "todo-app"
            },
            "data": {
                "LOG_LEVEL": "INFO",
                "MAX_CONNECTIONS": "100",
                "RATE_LIMIT": "1000"
            }
        }

        self.write_yaml("k8s/configmap.yaml", config_map)

    def create_secrets_template(self):
        """Create secrets template."""
        secrets = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "todo-secrets",
                "namespace": "todo-app"
            },
            "type": "Opaque",
            "data": {
                "database-url": "cG9zdGdyZXNxbC8vdG9kbzpwYXNzd29yZC9kYg==",  # base64 encoded
                "secret-key": "eW91ci1zZWNyZXQta2V5LWhlcmU="  # base64 encoded
            }
        }

        self.write_yaml("k8s/secrets.yaml.template", secrets)
```

### 4. Build and Deployment Scripts
```python
class BuildScripts:
    """Creates build and deployment automation."""

    def create_build_script(self):
        """Create build script."""
        script = """#!/bin/bash
set -e

echo "🏗️  Building Todo Evolution App..."

# Build Docker images
echo "Building backend..."
docker build -t todo-backend:latest ./apps/backend

echo "Building frontend..."
docker build -t todo-frontend:latest ./apps/web

echo "Building MCP server..."
docker build -t todo-mcp:latest ./apps/chatbot

# Tag images
if [ "$1" = "prod" ]; then
    docker tag todo-backend:latest todo-backend:$(git rev-parse --short HEAD)
    docker tag todo-frontend:latest todo-frontend:$(git rev-parse --short HEAD)
    docker tag todo-mcp:latest todo-mcp:$(git rev-parse --short HEAD)
fi

echo "✅ Build complete!"
"""
        self.write_file("scripts/build.sh", script)
        os.chmod("scripts/build.sh", 0o755)

    def create_deploy_script(self):
        """Create deployment script."""
        script = """#!/bin/bash
set -e

ENVIRONMENT=${1:-dev}

echo "🚀 Deploying to $ENVIRONMENT..."

if [ "$ENVIRONMENT" = "dev" ]; then
    # Development deployment with Docker Compose
    docker-compose -f docker-compose.dev.yml up -d

    # Wait for services
    echo "Waiting for services to start..."
    sleep 10

    # Run migrations
    docker-compose exec backend uv run alembic upgrade head

    echo "✅ Development deployment complete!"
    echo "Frontend: http://localhost:3000"
    echo "Backend: http://localhost:8000"
    echo "MCP Server: http://localhost:8001"

elif [ "$ENVIRONMENT" = "prod" ]; then
    # Production deployment to Kubernetes
    kubectl apply -f k8s/

    # Wait for rollout
    kubectl rollout status deployment/todo-backend -n todo-app

    echo "✅ Production deployment complete!"
    echo "Ingress: https://todo.example.com"

else
    echo "Unknown environment: $ENVIRONMENT"
    echo "Usage: $0 [dev|prod]"
    exit 1
fi
"""
        self.write_file("scripts/deploy.sh", script)
        os.chmod("scripts/deploy.sh", 0o755)

    def create_kubernetes_scripts(self):
        """Create Kubernetes management scripts."""
        # Minikube setup
        minikube_setup = """#!/bin/bash
set -e

echo "🎯 Setting up Minikube for Todo App..."

# Start Minikube
minikube start

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Set Docker environment
eval $(minikube docker-env)

# Build and push to Minikube registry
docker build -t todo-backend:latest ./apps/backend
docker build -t todo-frontend:latest ./apps/web

echo "✅ Minikube setup complete!"
"""
        self.write_file("scripts/minikube-setup.sh", minikube_setup)
        os.chmod("scripts/minikube-setup.sh", 0o755)
```

### 5. Basic Infrastructure Automation
```python
class InfrastructureAutomation:
    """Creates basic infrastructure automation."""

    def create_terraform_templates(self):
        """Create Terraform templates for Phase V preparation."""
        # DigitalOcean provider
        provider = """
terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.digitalocean_token
}
"""

        # DOKS cluster
        doks_cluster = """
resource "digitalocean_kubernetes_cluster" "todo-cluster" {
  name   = "todo-cluster"
  region = var.do_region
  version = "1.24.0"

  node_pool {
    name       = "worker-pool"
    size       = "s-2vcpu-4gb"
    node_count = 3
  }
}

resource "digitalocean_kubernetes_cluster" "todo-cluster" {
  name   = "todo-cluster"
  region = var.do_region
  version = "1.24.0"

  node_pool {
    name       = "worker-pool"
    size       = "s-2vcpu-4gb"
    node_count = 3
  }
"""

        self.write_file("terraform/main.tf", provider)
        self.write_file("terraform/cluster.tf", doks_cluster)

    def create_cloudinit_scripts(self):
        """Create cloud-init scripts for VM setup."""
        cloud_init = """#cloud-config
packages:
  - docker
  - docker.io
  - kubectl
  - curl

runcmd:
  - systemctl enable docker
  - systemctl start docker
  - usermod -aG docker ubuntu
  - mkdir -p /opt/todo-app
  - cd /opt/todo-app
  - curl -fsSL https://raw.githubusercontent.com/user/todo-evolution/main/docker-compose.prod.yml -o docker-compose.yml
  - docker-compose up -d
"""
        self.write_file("cloud-init/cloud-init.yaml", cloud_init)

    def create_monitoring_setup(self):
        """Setup basic monitoring configuration."""
        # Prometheus configuration
        prometheus_yml = """
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'todo-backend'
    static_configs:
      - targets: ['todo-backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'todo-mcp'
    static_configs:
      - targets: ['todo-mcp:8001']
    metrics_path: '/metrics'
    scrape_interval: 5s
"""
        self.write_file("monitoring/prometheus.yml", prometheus_yml)

        # Grafana dashboard
        dashboard = {
            "dashboard": {
                "title": "Todo App Dashboard",
                "panels": [
                    {
                        "title": "API Response Time",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
                        }]
                    },
                    {
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
                        }]
                    }
                ]
            }
        }

        self.write_json("monitoring/grafana-dashboard.json", dashboard)
```

## Deployment Preparation for Phase IV

### Container Registry Setup
```python
class ContainerRegistry:
    """Setup container registry configurations."""

    def create_registry_configs(self):
        """Create configurations for container registries."""
        # Docker Hub
        dockerhub_config = """
# Docker Hub configuration
REGISTRY_URL=your-username
IMAGE_PREFIX=your-username/todo-app
"""
        self.write_file(".dockerhub.env", dockerhub_config)

        # GitHub Packages
        github_config = """
# GitHub Packages configuration
GITHUB_TOKEN=your-github-token
REGISTRY=ghcr.io
IMAGE_PREFIX=ghcr.io/your-username/todo-app
"""
        self.write_file(".github.env", github_config)

    def create_multiarch_build(self):
        """Create multi-architecture build configuration."""
        docker_bake = """
# Docker Bake configuration for multi-arch builds
variable "TAG" {
  default = "latest"
}

target "linux_amd64" {
  inherits = ["default"]
  platforms = ["linux/amd64"]
}

target "linux_arm64" {
  inherits = ["default"]
  platforms = ["linux/arm64"]
}

group "default" {
  targets = ["linux_amd64", "linux_arm64"]
}
"""
        self.write_file("docker-bake.hcl", docker_bake)
```

## Documentation and Guides

### Deployment Guide
```markdown
# Deployment Guide

## Phase I: Console App
```bash
# Build and run locally
uv run python main.py

# Docker deployment
docker build -t todo-console .
docker run -it todo-console
```

## Phase II: Web Application
### Development
```bash
# Using Docker Compose
docker-compose -f docker-compose.dev.yml up

# Manual setup
cd apps/backend && uv run uvicorn main:app &
cd apps/web && npm run dev &
```

### Production
```bash
# Build images
./scripts/build.sh prod

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or deploy to Kubernetes
./scripts/deploy.sh prod
```

## Phase III: AI Chatbot
### Development
```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Services will be available:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# MCP Server: http://localhost:8001
```

## Kubernetes Deployment
### Local (Minikube)
```bash
./scripts/minikube-setup.sh
kubectl apply -f k8s/
```

### Cloud (DigitalOcean)
```bash
# Setup infrastructure
terraform init
terraform apply

# Deploy
kubectl apply -f k8s/
```
```

## Integration with Other Agents

### With System-Integrator
- Provides Docker configurations
- Creates deployment manifests
- Manages environment preparation

### With Backend-Engineer
- Containerizes backend applications
- Optimizes images for production
- Configures health checks

### With Frontend-UX-Designer
- Builds frontend containers
- Configures static asset serving
- Sets up build optimization

## Best Practices

### Docker Optimization
1. **Multi-stage builds** - Reduce image size
2. **Non-root users** - Security best practice
3. **Health checks** - Container monitoring
4. **Resource limits** - Resource management
5. .dockerignore - Exclude unnecessary files

### Kubernetes Deployment
1. **Namespace isolation** - Separate environments
2. **Resource requests/limits** - Specify resource needs
3. **Health checks** - Ensure pod health
4. **Secrets management** - Secure credential storage
5. **Rollout strategies** - Zero-downtime deployment

### Deployment Strategy
1. **Blue-green deployment** - Zero downtime
2. **Rolling updates** - Gradual rollout
3. **Canary deployments** - Test with small traffic
4. **Rollback plans** - Quick recovery
5. **Monitoring** - Track deployment health