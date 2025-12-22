# API Contract: Kubernetes Resources

**Feature**: 004-kubernetes

This document defines the Kubernetes resource specifications for deployment.

---

## Service Contract

### Frontend Service

**Type**: NodePort (Minikube) / LoadBalancer (Cloud)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  labels:
    app: todo-frontend
spec:
  type: NodePort
  selector:
    app: todo-frontend
  ports:
  - port: 3000
    targetPort: 3000
    protocol: TCP
    name: http
    nodePort: 30001  # Minikube only
  sessionAffinity: None
```

**Endpoints**:
- `:3000` - HTTP (container)
- `:30001` - NodePort (Minikube)
- LoadBalancer IP (cloud)

---

### Backend Service

**Type**: NodePort (Minikube) / LoadBalancer (Cloud)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  labels:
    app: todo-backend
spec:
  type: NodePort
  selector:
    app: todo-backend
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
    nodePort: 30002  # Minikube only
  sessionAffinity: None
```

**Endpoints**:
- `:8000` - HTTP (container)
- `:30002` - NodePort (Minikube)
- LoadBalancer IP (cloud)

---

## Deployment Contract

### Frontend Deployment

**Replicas**: 2

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
      securityContext:
        fsGroup: 1001
        runAsNonRoot: true
      containers:
      - name: frontend
        image: todo-frontend:latest
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          containerPort: 3000
          protocol: TCP
        securityContext:
          runAsUser: 1001
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false
        env:
        - name: NEXT_PUBLIC_API_URL
          valueFrom:
            configMapKeyRef:
              name: frontend-config
              key: NEXT_PUBLIC_API_URL
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: http
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

---

### Backend Deployment

**Replicas**: 2

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
      securityContext:
        fsGroup: 1001
        runAsNonRoot: true
      containers:
      - name: backend
        image: todo-backend:latest
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        securityContext:
          runAsUser: 1001
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: database-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: jwt-secret
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: groq-api-key
              optional: true
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: gemini-api-key
              optional: true
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
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
```

---

## ConfigMap Contract

### Frontend ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
data:
  NEXT_PUBLIC_API_URL: "http://backend-service:8000"
```

### Backend ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  CORS_ORIGINS: "http://localhost:3000,https://yourdomain.com"
  APP_NAME: "Todo CRUD API"
  DEBUG: "false"
  JWT_ALGORITHM: "HS256"
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "1440"
```

---

## Secret Contract

### Backend Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
type: Opaque
stringData:
  # Required
  database-url: "postgresql+asyncpg://user:pass@host:5432/db"
  jwt-secret: "your-production-jwt-secret-min-32-chars"

  # Optional (AI features)
  groq-api-key: "gsk_xxx..."
  gemini-api-key: "AIzaSyxxx..."
  openai-api-key: "sk-xxx..."
```

**Secret Creation**:
```bash
kubectl create secret generic backend-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=groq-api-key="$GROQ_API_KEY" \
  --from-literal=gemini-api-key="$GEMINI_API_KEY"
```

---

## Ingress Contract (Optional)

### Frontend Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  rules:
  - host: app.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 3000
  tls:
  - hosts:
    - app.yourdomain.com
    secretName: frontend-tls
```

### Backend Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backend-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: backend-tls
```

---

## HorizontalPodAutoscaler Contract

### Frontend HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Backend HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Pod Disruption Budget Contract

### Frontend PDB

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: frontend-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: todo-frontend
```

### Backend PDB

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: backend-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: todo-backend
```
