# Kubernetes & Docker Deployment - Evolution of TODO

This example shows the actual deployment patterns used in the Evolution of TODO project.

## Dockerfile (Backend)

```dockerfile
# backend/Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Dockerfile (Frontend)

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy built files
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./

# Install production dependencies only
RUN npm ci --production

# Expose port
EXPOSE 3000

# Run with Next.js
CMD ["npm", "start"]
```

## Docker Compose (Local Development)

```yaml
# docker-compose.yml
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
    networks:
      - todo-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/todo
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - CORS_ORIGINS=http://localhost:3000
    depends_on:
      - postgres
    networks:
      - todo-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=todo
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - todo-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:

networks:
  todo-network:
    driver: bridge
```

## Kubernetes Deployment (Backend)

```yaml
# k8s/backend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  namespace: default
  labels:
    app.kubernetes.io/name: backend
    app.kubernetes.io/component: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: backend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: backend
    spec:
      imagePullSecrets:
      - name: registry-pull-secret
      containers:
      - name: backend
        image: registry.digitalocean.com/todo-chatbot-reg/todo-backend:latest
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-backend-secrets
              key: database-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: todo-backend-secrets
              key: jwt-secret
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: todo-backend-secrets
              key: groq-api-key
          optional: true
        - name: CORS_ORIGINS
          valueFrom:
            configMapKeyRef:
              name: todo-backend-config
              key: cors-origins
        - name: APP_NAME
          valueFrom:
            configMapKeyRef:
              name: todo-backend-config
              key: app-name
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 15
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        securityContext:
          runAsNonRoot: true
          runAsUser: 1001
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
```

## Kubernetes Service (Backend)

```yaml
# k8s/backend/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
  namespace: default
  labels:
    app.kubernetes.io/name: backend
    app.kubernetes.io/component: backend
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: http
    protocol: TCP
    name: http
  selector:
    app.kubernetes.io/name: backend
```

## Kubernetes ConfigMap

```yaml
# k8s/backend/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-backend-config
  namespace: default
data:
  app-name: "Todo CRUD API"
  cors-origins: "https://hackathon2.testservers.online,https://frontend-l0e30jmlq-hamdanprofessionals-projects.vercel.app"
  debug: "false"
  jwt-algorithm: "HS256"
  jwt-access-token-expire-minutes: "1440"
```

## Kubernetes Secrets

```yaml
# k8s/backend/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-backend-secrets
  namespace: default
type: Opaque
data:
  # Base64 encoded values
  database-url: cG9zdGdyZXNxbCthc3luY3BnOi8v...
  jwt-secret: eW91ci1qc3Qtc2VjcmV0LWtleS1oZXJlLW1pbi0zMi1jaGFycw==
  groq-api-key: Z3NrX3BYOUlwdFpKMTNsanp6RXN...
  gemini-api-key: QUl6YVN5T2R2aGdNZXhRcH...
```

## Kubernetes Deployment (Frontend)

```yaml
# k8s/frontend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  namespace: default
  labels:
    app.kubernetes.io/name: frontend
    app.kubernetes.io/component: frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: frontend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: frontend
    spec:
      containers:
      - name: frontend
        image: registry.digitalocean.com/todo-chatbot-reg/todo-frontend:latest
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          containerPort: 3000
          protocol: TCP
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.testservers.online"
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: todo-frontend-secrets
              key: better-auth-secret
        livenessProbe:
          httpGet:
            path: /
            port: http
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

## Helm Chart Structure

```
helm/
├── todo-app/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── backend/
│       │   ├── deployment.yaml
│       │   ├── service.yaml
│       │   ├── configmap.yaml
│       │   └── secrets.yaml
│       ├── frontend/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       └── ingress.yaml
```

## Helm Values

```yaml
# helm/todo-app/values.yaml
backend:
  replicaCount: 1

  image:
    repository: registry.digitalocean.com/todo-chatbot-reg/todo-backend
    pullPolicy: IfNotPresent
    tag: "latest"

  service:
    type: ClusterIP
    port: 8000

  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"

  env:
    corsOrigins: "https://hackathon2.testservers.online"
    debug: "false"

frontend:
  replicaCount: 1

  image:
    repository: registry.digitalocean.com/todo-chatbot-reg/todo-frontend
    pullPolicy: IfNotPresent
    tag: "latest"

  service:
    type: ClusterIP
    port: 3000

  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "200m"

  env:
    apiUrl: "https://api.testservers.online"

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: hackathon2.testservers.online
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: todo-app-tls
      hosts:
        - hackathon2.testservers.online
```

## Deployment Commands

### Docker
```bash
# Build images
docker build -t todo-backend ./backend
docker build -t todo-frontend ./frontend

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### Kubernetes (kubectl)
```bash
# Apply all manifests
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/ingress.yaml

# Check pod status
kubectl get pods

# View logs
kubectl logs -f deployment/todo-backend
kubectl logs -f deployment/todo-frontend

# Port forward to local
kubectl port-forward deployment/todo-backend 8000:8000
kubectl port-forward deployment/todo-frontend 3000:3000
```

### Helm
```bash
# Install chart
helm install todo-app ./helm/todo-app

# Upgrade chart
helm upgrade todo-app ./helm/todo-app

# Uninstall chart
helm uninstall todo-app

# List releases
helm list
```

## Production URLs

| Service | URL |
|---------|-----|
| Frontend | https://hackathon2.testservers.online |
| Backend | https://api.testservers.online |
| API Docs | https://api.testservers.online/docs |

## Key Patterns

### 1. Multi-stage Docker Build
- Separate build and runtime stages
- Minimize image size
- Use alpine images when possible

### 2. Health Checks
- Liveness probe (restart if unhealthy)
- Readiness probe (don't send traffic if not ready)
- Proper initial delays and periods

### 3. Resource Management
- Set requests (guaranteed resources)
- Set limits (max resources)
- Prevent resource starvation

### 4. Security
- Run as non-root user
- Drop all capabilities
- Use secrets for sensitive data

### 5. Configuration
- Separate config from code
- Use ConfigMaps for non-sensitive config
- Use Secrets for sensitive data

### 6. Rolling Updates
- Set replicas > 1 for high availability
- Use readiness probes during rollout
- Zero-downtime deployments
