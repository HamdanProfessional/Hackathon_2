# Email Notification Configuration Guide

## Environment Variables

### Email Worker Configuration

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `EMAIL_KEY` | API key for email service | `emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d` | Yes |
| `EMAIL_API_URL` | Email API endpoint | `https://email.testservers.online/api/send` | Yes |
| `MAIL_FROM` | From email address | `noreply@hackathon2.testservers.online` | Yes |
| `MAIL_FROM_NAME` | From display name | `Todo App` | No |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` | Yes |
| `DAPR_HTTP_HOST` | Dapr sidecar host | `localhost` | No |
| `DAPR_HTTP_PORT` | Dapr sidecar port | `3500` | No |
| `DAPR_PUBSUB_NAME` | Dapr pub/sub component name | `todo-pubsub` | No |

## Kubernetes Secrets

### Create Secret

```bash
kubectl create secret generic email-worker-secrets \
  --from-literal=email-key='emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d' \
  --namespace=hackathon2
```

### Verify Secret

```bash
kubectl get secret email-worker-secrets -n hackathon2
kubectl describe secret email-worker-secrets -n hackathon2
```

### Update Secret

```bash
kubectl patch secret email-worker-secrets \
  --from-literal=email-key='new-key-here' \
  --namespace=hackathon2
```

## Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: email-worker
  namespace: hackathon2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: email-worker
  template:
    metadata:
      labels:
        app: email-worker
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "email-worker"
        dapr.io/app-port: "8003"
    spec:
      containers:
      - name: email-worker
        image: registry.digitalocean.com/hackathon2/email-worker:v3
        ports:
        - containerPort: 8003
        env:
        - name: EMAIL_KEY
          valueFrom:
            secretKeyRef:
              name: email-worker-secrets
              key: email-key
        - name: EMAIL_API_URL
          value: "https://email.testservers.online/api/send"
        - name: MAIL_FROM
          value: "noreply@hackathon2.testservers.online"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secrets
              key: database-url
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8003
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8003
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service YAML

```yaml
apiVersion: v1
kind: Service
metadata:
  name: email-worker
  namespace: hackathon2
spec:
  selector:
    app: email-worker
  ports:
  - port: 8003
    targetPort: 8003
    name: http
```

## Dapr Configuration

### Pub/Sub Component

**File**: `k8s/dapr/components/pubsub.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
  namespace: hackathon2
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis:6379
  - name: redisPassword
    secretKeyRef:
      name: redis-secrets
      key: password
```

### Subscription Configuration

Email worker auto-registers subscriptions via `/dapr/subscribe` endpoint:

```json
{
  "subscriptions": [
    {"pubsubname": "todo-pubsub", "topic": "task-created", "route": "/task-created"},
    {"pubsubname": "todo-pubsub", "topic": "task-updated", "route": "/task-updated"},
    {"pubsubname": "todo-pubsub", "topic": "task-completed", "route": "/task-completed"},
    {"pubsubname": "todo-pubsub", "topic": "task-deleted", "route": "/task-deleted"},
    {"pubsubname": "todo-pubsub", "topic": "task-due-soon", "route": "/task-due-soon"},
    {"pubsubname": "todo-pubsub", "topic": "recurring-task-due", "route": "/recurring-task-due"}
  ]
}
```

## Local Development

### Docker Compose

**File**: `docker-compose.yml`

```yaml
services:
  email-worker:
    build: ./services/email-worker
    ports:
      - "8003:8003"
    environment:
      EMAIL_KEY: emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d
      EMAIL_API_URL: https://email.testservers.online/api/send
      MAIL_FROM: noreply@hackathon2.testservers.online
      DATABASE_URL: postgresql+asyncpg://postgres:password@db:5432/todo
      DAPR_HTTP_HOST: localhost
      DAPR_HTTP_PORT: 3500
      DAPR_PUBSUB_NAME: todo-pubsub
      DEBUG: "true"
    depends_on:
      - db
      - redis
      - dapr-sidecar
```

### Environment File

**File**: `services/email-worker/.env`

```bash
EMAIL_KEY=emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d
EMAIL_API_URL=https://email.testservers.online/api/send
MAIL_FROM=noreply@hackathon2.testservers.online
MAIL_FROM_NAME=Todo App
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/todo
DAPR_HTTP_HOST=localhost
DAPR_HTTP_PORT=3500
DAPR_PUBSUB_NAME=todo-pubsub
DEBUG=true
```

## Email API Configuration

### IP Whitelisting

1. Get your cluster's public IP:
```bash
kubectl get nodes -o wide
```

2. Whitelist the IP in email service control panel at `email.testservers.online`

3. Verify whitelist:
```bash
curl -I https://email.testservers.online
```

### Test API Connection

```bash
curl -X POST https://email.testservers.online/api/send \
  -H "Authorization: Bearer emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "test@example.com",
    "subject": "Test Email",
    "body": "This is a test email from the Todo App."
  }'
```

Expected response:
```json
{"status": "success", "message": "Email sent successfully"}
```

## Troubleshooting

### Common Configuration Issues

#### 1. Email Key Not Found
**Error**: `KeyError: 'EMAIL_KEY'`

**Solution**:
```bash
# Verify secret exists
kubectl get secret email-worker-secrets -n hackathon2

# Check deployment references secret correctly
kubectl describe deployment email-worker -n hackathon2
```

#### 2. Database Connection Failed
**Error**: `sqlalchemy.exc.OperationalError: could not connect`

**Solution**:
```bash
# Verify database URL secret
kubectl get secret database-secrets -n hackathon2

# Check database connectivity
kubectl exec -it email-worker-xxx -n hackathon2 -- ping db.hackathon2.svc.cluster.local
```

#### 3. Dapr Sidecar Not Ready
**Error**: `fail to subscribe error="rpc error: code = Unavailable"`

**Solution**:
```bash
# Check Dapr sidecar is injected
kubectl describe pod email-worker-xxx -n hackathon2

# Restart pod
kubectl delete pod email-worker-xxx -n hackathon2
```

#### 4. IP Not Whitelisted
**Error**: `{"error":"Access denied","message":"IP X.X.X.X is not whitelisted"}`

**Solution**:
1. Get current IP: `curl ifconfig.me`
2. Whitelist IP in email service control panel
3. Wait for whitelist to propagate (up to 5 minutes)

### Debug Mode

Enable debug logging:

```yaml
env:
- name: DEBUG
  value: "true"
```

Or locally:
```bash
DEBUG=true uvicorn app.main:app --reload
```

### Log Viewing

```bash
# View email worker logs
kubectl logs -f deployment/email-worker -n hackathon2

# View Dapr sidecar logs
kubectl logs -f deployment/email-worker -c daprd -n hackathon2

# View logs for specific event
kubectl logs deployment/email-worker -n hackathon2 | grep "task-created"
```

## Verification Checklist

After configuration, verify:

- [ ] Secret `email-worker-secrets` created
- [ ] Deployment `email-worker` running
- [ ] Pod health checks passing
- [ ] Dapr sidecar injected
- [ ] `/dapr/subscribe` returns 6 subscriptions
- [ ] Test email endpoint works
- [ ] Email received in inbox
- [ ] Task CRUD events trigger emails
