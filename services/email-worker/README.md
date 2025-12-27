# Email Worker

Email notification microservice for Todo App - handles email notifications via Dapr pub/sub events.

## Features

- **Gmail SMTP Integration**: Sends emails using Gmail SMTP server
- **Dapr Event Subscriptions**: Subscribes to `task-due-soon` and `recurring-task-due` events
- **HTML Email Templates**: Beautiful, responsive email templates
- **Health Checks**: Kubernetes-ready liveness and readiness probes
- **Auto-scaling**: Horizontal Pod Autoscaler support (1-3 replicas)

## Architecture

```
┌─────────────────┐     ┌──────────┐     ┌──────────────────┐
│   Backend API   │────▶│  Dapr    │────▶│  Email Worker    │
│                 │ Pub │  Pub/Sub │ Sub │                  │
│ Event Publisher │     │ (Redpanda)│     │ Gmail SMTP       │
└─────────────────┘     └──────────┘     └──────────────────┘
                                                      │
                                                      ▼
                                              ┌───────────────┐
                                              │ User's Email  │
                                              └───────────────┘
```

## Event Subscriptions

### task-due-soon
Triggered when a task due date is approaching.

**Event Data:**
```json
{
  "task_id": "uuid",
  "user_id": "uuid",
  "title": "Task title",
  "due_date": "2025-12-27T10:00:00Z",
  "priority": "high",
  "description": "Task description",
  "category": "work"
}
```

### recurring-task-due
Triggered when a recurring task instance is due.

**Event Data:**
```json
{
  "recurring_task_id": "uuid",
  "user_id": "uuid",
  "title": "Task title",
  "recurrence_type": "daily",
  "next_due_at": "2025-12-27T10:00:00Z",
  "end_date": "2025-12-31T23:59:59Z",
  "description": "Task description"
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `MAIL_SERVER` | SMTP server hostname | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USERNAME` | Gmail username | Required |
| `MAIL_PASSWORD` | Gmail app password | Required |
| `MAIL_FROM` | From email address | `noreply@hackathon2.testservers.online` |
| `MAIL_FROM_NAME` | From display name | `Todo App` |
| `DEBUG` | Enable debug mode | `false` |

## Development

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
```

### Run Locally

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --port 8003

# Or with Dapr sidecar (for event subscription testing)
dapr run --app-id email-worker --app-protocol http --dapr-http-port 3500 -- uvicorn app.main:app --port 8003
```

### Test Email Sending

```python
from app.email_service import email_service

# Send test email
await email_service.send_email(
    subject="Test Email",
    email=["recipient@example.com"],
    body="This is a test email from Email Worker."
)
```

## Deployment

### Build Docker Image

```bash
docker build -t email-worker:latest .
```

### Deploy with Helm

```bash
# Install Helm chart
helm install email-worker ./helm/email-worker \
  --namespace todo-app \
  --create-namespace \
  --set email.mailPassword="your-app-password"

# Upgrade existing deployment
helm upgrade email-worker ./helm/email-worker \
  --namespace todo-app
```

### Deploy to Kubernetes

```bash
# Apply namespace
kubectl create namespace todo-app

# Create secrets
kubectl create secret generic todo-secrets \
  --from-literal=database-url="postgresql+asyncpg://user:pass@host:5432/db" \
  --namespace todo-app

# Deploy with Helm
helm install email-worker ./helm/email-worker --namespace todo-app

# Check deployment
kubectl get pods -n todo-app -l app.kubernetes.io/name=email-worker

# View logs
kubectl logs -n todo-app -l app.kubernetes.io/name=email-worker -f
```

## Email Templates

Templates are stored in `app/templates/`:

- `task-due.html` - Due date notification email
- `recurring-task-due.html` - Recurring task alert email
- `welcome.html` - Welcome email for new users

### Template Context

Templates receive a context dictionary with:

```python
{
    "title": "Task title",
    "due_date": "December 27, 2025 at 10:00 AM",
    "priority": "High",
    "description": "Task description",
    "category": "Work",
    "app_url": "https://hackathon2.testservers.online"
}
```

## Gmail App Password

To use Gmail SMTP, you need to create an app-specific password:

1. Go to Google Account settings
2. Enable 2-Step Verification (if not enabled)
3. Go to Security → App Passwords
4. Generate a new app password for "Mail"
5. Use the 16-character password in `MAIL_PASSWORD`

**Note:** Gmail has daily sending limits (500 emails/day for free accounts).

## Monitoring

### Health Endpoints

- `GET /health` - General health check
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe

### Dapr Endpoints

- `GET /dapr/subscribe` - Dapr subscription discovery

## Troubleshooting

### Emails Not Sending

1. Check Gmail app password is correct
2. Verify SMTP settings in `helm/email-worker/values.yaml`
3. Check Dapr sidecar is running: `kubectl get pods -n todo-app -l app=dapr`
4. View logs: `kubectl logs -n todo-app -l app.kubernetes.io/name=email-worker`

### Dapr Subscription Not Working

1. Verify Dapr sidecar is injected
2. Check pub/sub component exists: `kubectl get pubsub -n todo-app`
3. Verify topic names match: `task-due-soon`, `recurring-task-due`
4. Check Dapr logs: `kubectl logs -n todo-app <pod-name> -c daprd`

### Database Connection Issues

1. Verify database URL in secret
2. Check network policies allow email-worker to access database
3. Ensure database is accessible from Kubernetes cluster

## License

MIT
