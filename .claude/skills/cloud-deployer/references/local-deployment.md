# Local Deployment Reference

## Docker Compose

### Overview
Docker Compose is the recommended approach for local development. It provides:
- Isolated development environment
- Easy service orchestration
- Volume mounting for live reload
- Reproducible setup across team members

### docker-compose.yml Structure

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/db
    depends_on:
      - postgres

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Common Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# Run command in container
docker-compose exec backend pytest
docker-compose exec backend alembic upgrade head
```

### Environment Variables

Create `.env` file in project root:

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=tododb

# Backend
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/tododb
JWT_SECRET_KEY=your-secret-key-min-32-chars
GROQ_API_KEY=your-groq-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Minikube / Local Kubernetes

### Overview
Minikube provides a local Kubernetes cluster for testing K8s deployments before production.

### Installation

```bash
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Windows
choco install minikube
```

### Starting Minikube

```bash
# Start with Docker driver (recommended)
minikube start --driver=docker --cpus=4 --memory=8192

# Enable ingress
minikube addons enable ingress

# Enable registry (optional)
minikube addons enable registry
```

### Deploying to Minikube

```bash
# Set Docker environment to use Minikube's daemon
eval $(minikube docker-env)

# Build images within Minikube
docker build -t todo-backend:latest -f backend/Dockerfile backend/
docker build -t todo-frontend:latest -f frontend/Dockerfile frontend/

# Apply Kubernetes manifests
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/

# Access services
minikube service todo-backend
minikube service todo-frontend
```

### Common Minikube Commands

```bash
# Check status
minikube status

# Open dashboard
minikube dashboard

# Get service URL
minikube service <service-name> --url

# SSH into node
minikube ssh

# Delete cluster
minikube delete
```

### Tunnel for LoadBalancer Services

```bash
# Run in separate terminal for LoadBalancer access
minikube tunnel
```

## k3s Alternative

k3s is a lightweight Kubernetes distribution:

```bash
# Install k3s
curl -sfL https://get.k3s.io | sh -

# Access cluster
sudo k3s kubectl get nodes

# Use with kubectl
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
kubectl get nodes
```

## Troubleshooting

### Docker Compose Issues

**Port conflicts**
```bash
# Check what's using ports
netstat -tulpn | grep :3000
# Change ports in docker-compose.yml
```

**Volume permission errors**
```bash
# Fix volume permissions
docker-compose down
docker volume prune
docker-compose up -d
```

### Minikube Issues

**Minikube won't start**
```bash
# Delete and restart
minikube delete
minikube start --driver=docker --force
```

**Images not found**
```bash
# Ensure you're using Minikube's Docker daemon
eval $(minikube docker-env)
docker images
```

**DNS resolution issues**
```bash
# Check CoreDNS
kubectl get pods -n kube-system
kubectl logs -n kube-system -l k8s-app=kube-dns
```

### Performance Tips

1. **Allocate enough resources**: Minikube needs at least 4 CPUs and 8GB RAM
2. **Use Docker driver**: Faster than VirtualBox
3. **Enable container runtime acceleration**: On macOS with HyperKit
4. **Limit resource usage**: Set resource limits in deployment specs
