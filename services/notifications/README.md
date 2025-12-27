# Todo Notification Service

Notification microservice for the Todo App - Part of Phase V Event-Driven Architecture.

## Overview

This service handles task notifications and recurring task processing through:
- **Due Date Checker**: Scans for tasks due within 24 hours and sends email notifications
- **Recurring Task Processor**: Creates new task instances from recurring task templates
- **Dapr Event Subscriptions**: Subscribes to Kafka events for task lifecycle tracking

## Features

### Due Date Checker
- Runs every hour (configurable)
- Finds tasks due within 24 hours
- Marks tasks as notified to avoid duplicates
- Sends email notifications to users
- Publishes `task-due-soon` events

### Recurring Task Processor
- Runs every hour (configurable)
- Processes recurring tasks where `next_due_at <= now`
- Creates new task instances from templates
- Updates `next_due_at` for next occurrence
- Sends email notifications for new tasks
- Publishes `recurring-task-due` events

### Dapr Subscriptions
Subscribes to these Kafka topics via Dapr:
- `task-created` → Log to database
- `task-updated` → Log to database
- `task-completed` → Log to database
- `task-deleted` → Log to database
- `task-due-soon` → Send notification
- `recurring-task-due` → Process recurring task

## Project Structure

```
services/notifications/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with lifespan
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── subscriptions.py     # Dapr event handlers
│   ├── models/              # SQLAlchemy models (read-only)
│   │   ├── __init__.py
│   │   ├── task.py
│   │   └── task_event_log.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── notification.py  # Email service
│   └── workers/
│       ├── __init__.py
│       ├── due_checker.py   # Due date checker
│       └── recurring_processor.py  # Recurring task processor
├── tests/
│   └── test_notifications.py
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.13+
- PostgreSQL (Neon for production)
- Dapr sidecar (for event subscriptions)
- Kafka/Redpanda (for event streaming)

### Local Development

1. **Install dependencies**:
```bash
cd services/notifications
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Run the service**:
```bash
uvicorn app.main:app --reload --port 8000
```

### With Dapr (Local)

```bash
# Run Dapr sidecar
dapr run \
  --app-id todo-notifications \
  --app-protocol http \
  --dapr-http-port 3500 \
  --components-path ../../../k8s/dapr-components \
  uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build image
docker build -t todo-notifications:latest .

# Run with Docker
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name todo-notifications \
  todo-notifications:latest
```

### Kubernetes

See `k8s/notifications/` for deployment manifests.

```bash
# Apply namespace
kubectl apply -f k8s/notifications/namespace.yaml

# Apply deployment
kubectl apply -f k8s/notifications/deployment.yaml

# Apply service
kubectl apply -f k8s/notifications/service.yaml
```

## API Endpoints

### Health
- `GET /` - Service information
- `GET /health` - Health check
- `GET /health` - Subscription health check
- `GET /workers/status` - Background workers status

### Dapr Subscriptions
- `POST /subscribe/task-created` - Task created event
- `POST /subscribe/task-updated` - Task updated event
- `POST /subscribe/task-completed` - Task completed event
- `POST /subscribe/task-deleted` - Task deleted event
- `POST /subscribe/task-due-soon` - Task due soon event
- `POST /subscribe/recurring-task-due` - Recurring task due event

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `DAPR_HTTP_HOST` | Dapr sidecar host | `localhost` |
| `DAPR_HTTP_PORT` | Dapr sidecar port | `3500` |
| `DAPR_PUBSUB_NAME` | Dapr pub/sub component name | `todo-pubsub` |
| `DAPR_ENABLED` | Enable Dapr event publishing | `true` |
| `SMTP_HOST` | SMTP server host | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP username | `""` |
| `SMTP_PASSWORD` | SMTP password | `""` |
| `SMTP_FROM` | From email address | `noreply@todoapp.com` |
| `EMAIL_ENABLED` | Enable email notifications | `false` |
| `DUE_CHECK_INTERVAL_SECONDS` | Due checker interval | `3600` |
| `RECURRING_CHECK_INTERVAL_SECONDS` | Recurring processor interval | `3600` |
| `DUE_THRESHOLD_HOURS` | Hours before due to notify | `24` |

## Email Configuration

### Gmail Setup
1. Create an app password: https://myaccount.google.com/apppasswords
2. Set `SMTP_USER` to your Gmail address
3. Set `SMTP_PASSWORD` to the app password (not your account password)
4. Set `EMAIL_ENABLED=true`

### Other Providers
Update `SMTP_HOST`, `SMTP_PORT`, and authentication settings accordingly.

## Database Schema

The notification service reads from the same PostgreSQL database as the main backend:
- `tasks` - User tasks (read-only)
- `recurring_tasks` - Recurring task templates (read/write)
- `task_event_log` - Event audit log (write-only)

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_notifications.py::test_due_checker -v
```

## Monitoring

### Logs
```bash
# Kubernetes logs
kubectl logs -f deployment/todo-notifications -n production
```

### Metrics
- Health check: `GET /health`
- Workers status: `GET /workers/status`

## Troubleshooting

### Emails not sending
- Check `EMAIL_ENABLED=true` in environment
- Verify SMTP credentials are correct
- Check logs for authentication errors

### Workers not running
- Check `/workers/status` endpoint
- Verify `ENVIRONMENT` is not `test`
- Check logs for startup errors

### Dapr subscriptions not working
- Verify Dapr sidecar is running
- Check `k8s/dapr-components/pubsub-redpanda.yaml`
- Verify topic permissions in Kafka

## Development

### Adding New Event Subscriptions

1. Add handler in `app/subscriptions.py`:
```python
@router.post("/subscribe/your-event")
async def handle_your_event(request: Request):
    data = await request.json()
    # Process event
    return {"status": "processed"}
```

2. Update Dapr subscription in `k8s/dapr-components/subscriptions.yaml`

3. Rebuild and redeploy

### Adding New Workers

1. Create worker in `app/workers/your_worker.py`
2. Import and start in `app/main.py` lifespan
3. Add interval to `app/config.py`

## License

MIT
