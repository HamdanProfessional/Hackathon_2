# Data Model: Kubernetes Deployment

**Feature**: 004-kubernetes
**Note**: This is a deployment phase - no new database schema changes.

---

## Database Schema

### No Changes

Phase IV (Kubernetes Deployment) does not introduce any new database tables or schema changes.

Existing tables from Phases I-III remain unchanged:
- `users` - User accounts (Phase II)
- `tasks` - Task items (Phase I)
- `conversations` - AI chat conversations (Phase III)
- `messages` - Chat messages (Phase III)

---

## Kubernetes Resources

This section defines the Kubernetes resource model for deployment.

### Frontend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  labels:
    app: todo-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
    spec:
      containers:
      - name: frontend
        image: todo-frontend:latest
        ports:
        - containerPort: 3000
```

### Backend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  labels:
    app: todo-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
```

---

## Configuration Model

### Environment Variables

#### Frontend ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
data:
  NEXT_PUBLIC_API_URL: "http://backend-service:8000"
```

#### Backend ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  CORS_ORIGINS: "http://localhost:3000,https://yourdomain.com"
  APP_NAME: "Todo CRUD API"
  DEBUG: "false"
```

### Secrets Model

#### Backend Secrets
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
type: Opaque
stringData:
  database-url: "postgresql+asyncpg://user:pass@host/db"
  jwt-secret: "your-production-jwt-secret"
  groq-api-key: "gsk_xxx..."
  gemini-api-key: "AIzaSyxxx..."
```

---

## Service Model

### Frontend Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort
  selector:
    app: todo-frontend
  ports:
  - port: 3000
    targetPort: 3000
    nodePort: 30001
```

### Backend Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: NodePort
  selector:
    app: todo-backend
  ports:
  - port: 8000
    targetPort: 8000
    nodePort: 30002
```

---

## Storage Model

### No Volumes Required

The application is stateless and uses:
- **External Database**: Neon PostgreSQL (cloud-hosted)
- **No Local Storage**: No PVCs required

---

## Resource Model

### Frontend Resources
```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Backend Resources
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

---

## Health Check Model

### Frontend Health
```yaml
livenessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Backend Health
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```
