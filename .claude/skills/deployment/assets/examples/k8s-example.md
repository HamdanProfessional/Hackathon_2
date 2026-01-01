# Kubernetes Deployment Example

## Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  namespace: production
spec:
  replicas: 3
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
        image: registry.digitalocean.com/todo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 3
```

## Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend-service
  namespace: production
spec:
  selector:
    app: todo-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
  namespace: production
type: Opaque
stringData:
  database-url: "postgresql://user:pass@host:5432/db"
  secret-key: "your-secret-key-here"
```

## Deploy

```bash
# Apply manifests
kubectl apply -f k8s/

# Check rollout status
kubectl rollout status deployment/todo-backend -n production

# View logs
kubectl logs -f deployment/todo-backend -n production
```
