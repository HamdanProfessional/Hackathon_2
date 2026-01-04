---
name: dapr-events
description: Configure Dapr sidecars by adding dapr.io/enabled annotations to Kubernetes deployment.yaml, publish events to Kafka/Redpanda via dapr_client.publish_event(pubsub_name='todo-pubsub', topic_name='task-created'), subscribe with @dapr_app.subscribe(pubsub='todo-pubsub', topic='task-created') decorators, and manage state with dapr_client.save_state(store_name='todo-state', key=f'task:{id}'). Use when implementing event-driven microservices, creating task notification workflows, or building email workers that listen to task-created events.
---

# Dapr Event-Driven Architecture

Configure Dapr pub/sub, state management, and service-to-service communication for event-driven microservices.

## File Structure

```
k8s/dapr/
├── pubsub.yaml           # Kafka/Redpanda pubsub component
├── statestore.yaml       # Redis state store
└── subscriptions.yaml    # Declarative subscriptions

docker-compose.yml         # Local Kafka/Redpanda setup

backend/
├── app/
│   ├── events/           # Event publishers
│   │   ├── publisher.py   # Dapr publish wrapper
│   │   └── subscribers.py # Event handlers
│   └── main.py           # Dapr FastAPI integration
```

## Quick Commands

```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
dapr init

# Start Kafka with Docker Compose
docker-compose up -d kafka redpanda

# Deploy Dapr components
kubectl apply -f k8s/dapr/

# Run service with Dapr sidecar locally
dapr run --app-id backend --app-port 8000 --dapr-http-port 3500 \
  uvicorn app.main:app --host 0.0.0.0 --port 8000

# Publish test event
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-created \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "title": "Test Task"}'
```

## Common Scenarios

### Scenario 1: Setup Dapr Pub/Sub with Kafka
**User Request**: "Setup event streaming with Dapr and Kafka"

**File: `k8s/dapr/pubsub.yaml`**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: kafka:9092
  - name: consumerGroup
    value: task-processing-group
  - name: authRequired
    value: "false"
```

**Apply Commands**:
```bash
kubectl apply -f k8s/dapr/pubsub.yaml

# Add Dapr sidecar annotation to deployment
# In k8s/backend/deployment.yaml:
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend"
  dapr.io/app-port: "8000"
```

### Scenario 2: Publish Events from FastAPI
**User Request**: "Publish events when tasks are created"

**File: `backend/app/events/publisher.py`**
```python
import httpx
import os

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_HOST = os.getenv("DAPR_HOST", "localhost")

async def publish_event(pubsub_name: str, topic_name: str, data: dict):
    """Publish event via Dapr sidecar."""
    url = f"http://{DAPR_HOST}:{DAPR_HTTP_PORT}/v1.0/publish/{pubsub_name}/{topic_name}"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        response.raise_for_status()

# Usage in router
@router.post("/tasks/", status_code=201)
async def create_task(task: TaskCreate, user_id: UUID = Depends(get_current_user)):
    task = Task(user_id=user_id, **task.dict())
    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish event
    await publish_event(
        pubsub_name="kafka-pubsub",
        topic_name="task-created",
        data={"id": task.id, "title": task.title, "user_id": str(user_id)}
    )
    return task
```

### Scenario 3: Subscribe to Events
**File: `backend/app/events/subscribers.py`**
```python
from fastapi import FastAPI
from pydantic import BaseModel

class TaskCreatedEvent(BaseModel):
    id: int
    title: str
    user_id: str

def register_subscriptions(app: FastAPI):
    @app.post("/events/task-created")
    async def handle_task_created(event: TaskCreatedEvent):
        print(f"Received event: task {event.id} created")
        # Process event (send email, update cache)
        return {"status": "processed"}
```

### Scenario 4: Fix Event Not Received
**Troubleshooting Commands**:
```bash
# Check Dapr sidecar
kubectl get pods -l app=backend-dapr

# Check component
kubectl get components
kubectl describe component kafka-pubsub

# View Dapr logs
kubectl logs -l app=backend -c daprd
```

# List Dapr instances
dapr list

# Check Dapr version
dapr --version

# Verify Dapr installation
kubectl get pods -n dapr-system
```

### Dapr Component Management

```bash
# Apply component
kubectl apply -f component.yaml

# List components
dapr components -k

# Check component status
kubectl describe component component-name
```

### Python Dapr SDK

```python
from dapr import DaprClient
import json

# Create Dapr client
dapr = DaprClient()

# Publish event
dapr.publish_event(
    pubsub_name="todo-pubsub",
    topic_name="task-created",
    data=json.dumps(event_data),
    data_content_type="application/json"
)

# Save state
dapr.save_state(
    store_name="todo-state",
    key="task-123",
    value=json.dumps(task_data)
)

# Get state
state = dapr.get_state(store_name="todo-state", key="task-123")
```

## Dapr Component Configuration

### Pub/Sub Component (Redpanda)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
  namespace: default
spec:
  type: pubsub.redpanda
  version: v1
  metadata:
  - name: brokers
    value: "redpanda-0.redpanda.default.svc.cluster.local:9092"
  - name: authRequired
    value: "false"
  - name: allowedTopics
    value: "task-created,task-updated,task-completed,task-due-soon"
  - name: consumerID
    value: "todo-consumer-group"
```

### State Store Component (Redis)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-state
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "redis:6379"
  - name: redisPassword
    secretKeyRef:
      name: redis-secrets
      key: password
```

### Secret Component

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-secret
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
  - name: secrets
    value: "backend-secrets,frontend-secrets"
```

## Dapr Sidecar Configuration

### Deployment Annotations

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "debug"
        dapr.io/sidecar-cpu-limit: "500m"
        dapr.io/sidecar-memory-limit: "512Mi"
```

### Annotation Options

| Annotation | Description | Default |
|------------|-------------|---------|
| dapr.io/enabled | Enable Dapr sidecar | false |
| dapr.io/app-id | Unique application ID | required |
| dapr.io/app-port | Application port | required |
| dapr.io/log-level | Debug, info, warning, error | info |
| dapr.io/config | Dapr configuration | default |
| dapr.io/sidecar-cpu-limit | CPU limit | 500m |
| dapr.io/sidecar-memory-limit | Memory limit | 512Mi |

## Event Publishing

### FastAPI Event Publisher

```python
from dapr.clients import DaprClient
import json

class EventPublisher:
    def __init__(self):
        self.dapr = DaprClient()

    async def publish_task_created(self, task: Task):
        event_data = {
            "event_id": str(uuid.uuid4()),
            "event_type": "task-created",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "task_id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None
            }
        }

        self.dapr.publish_event(
            pubsub_name="todo-pubsub",
            topic_name="task-created",
            data=json.dumps(event_data),
            data_content_type="application/json"
        )
```

### Usage in API Endpoint

```python
@router.post("/api/tasks")
async def create_task(task_data: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = await create_task(db, task_data)

    # Publish event
    await event_publisher.publish_task_created(task)

    return task
```

## Event Subscription

### FastAPI Subscription

```python
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="todo-pubsub", topic="task-created")
async def handle_task_created(event_data: dict):
    task_id = event_data["data"]["task_id"]
    due_date = event_data["data"].get("due_date")

    if due_date:
        await schedule_notification(task_id, due_date)

    # Log event
    await log_task_event(task_id, "task-created", event_data)
```

### Bulk Subscription

```python
# Subscribe to multiple topics
topics = ["task-created", "task-updated", "task-completed"]

for topic in topics:
    @dapr_app.subscribe(pubsub="todo-pubsub", topic=topic)
    async def handle_task_event(event_data: dict):
        event_type = event_data.get("event_type")
        await process_event(event_type, event_data)
```

## Redpanda Configuration

### Install Redpanda via Helm

```bash
# Add Redpanda Helm repo
helm repo add redpanda https://charts.redpanda.com
helm repo update

# Install Redpanda with 3 replicas
helm install redpanda redpanda/redpanda \
  --set replicas=3 \
  --set persistence.size=10Gi
```

### Create Topics

```bash
# Connect to Redpanda pod
kubectl exec -it redpanda-0 -- sh

# Create topic
rpk topic create task-created -p 3 -r 3

# List topics
rpk topic list

# Produce to topic
rpk topic produce task-created < events.json

# Consume from topic
rpk topic consume task-created
```

### Topic Configuration

| Topic | Partitions | Replication | Retention |
|-------|-----------|-------------|-----------|
| task-created | 3 | 3 | 7 days |
| task-updated | 3 | 3 | 7 days |
| task-completed | 3 | 3 | 7 days |
| task-due-soon | 3 | 3 | 1 day |

## Service Invocation

### Invoke Service via Dapr

```python
from dapr.clients import DaprClient

dapr = DaprClient()

# Invoke service
response = dapr.invoke_method(
    app_id="todo-backend",
    method_name="api/tasks",
    data=task_data_json,
    http_verb="POST"
)

# Get response
result = response.json()
```

### Using HTTP

```bash
# Invoke via Dapr HTTP API
curl -X POST http://localhost:3500/v1.0/invoke/todo-backend/method/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task"}'
```

## State Management

### Save State

```python
dapr.save_state(
    store_name="todo-state",
    key=f"task:{task_id}",
    value=json.dumps(task_dict)
)
```

### Get State

```python
state = dapr.get_state(
    store_name="todo-state",
    key=f"task:{task_id}"
)
task_dict = json.loads(state.data)
```

### Delete State

```python
dapr.delete_state(
    store_name="todo-state",
    key=f"task:{task_id}"
)
```

## Troubleshooting

### Dapr Sidecar Not Starting

```bash
# Check pod annotations
kubectl get pod pod-name -o yaml | grep dapr

# Check Dapr logs
kubectl logs pod-name -c daprd

# Verify component installation
dapr components -k
```

### Event Publishing Fails

```bash
# Check Dapr logs
kubectl logs pod-name -c daprd --tail=100

# Verify component exists
kubectl get component todo-pubsub

# Check Redpanda connectivity
kubectl exec pod-name -c daprd -- curl http://dapr-sidecar:3500/v1.0/healthz
```

### Subscription Not Receiving Events

```bash
# Check subscription registration
kubectl logs pod-name -c daprd | grep subscribe

# Verify topic exists
kubectl exec -it redpanda-0 -- rpk topic list

# Check consumer group
kubectl exec -it redpanda-0 -- rpk group list
```

## Best Practices

### Event Schema

```json
{
    "event_id": "uuid",
    "event_type": "event-name",
    "timestamp": "ISO-8601",
    "correlation_id": "uuid",
    "data": {
        "entity_id": "uuid",
        "entity_data": {}
    }
}
```

### Error Handling

```python
try:
    dapr.publish_event(
        pubsub_name="todo-pubsub",
        topic_name="task-created",
        data=json.dumps(event_data)
    )
except Exception as e:
    # Log error
    logger.error(f"Failed to publish event: {e}")

    # Retry with exponential backoff
    await retry_publish_event(event_data, retry_count=3)
```

### Idempotency

```python
# Use event_id for deduplication
async def handle_task_created(event_data: dict):
    event_id = event_data.get("event_id")

    # Check if already processed
    if await is_event_processed(event_id):
        return

    # Process event
    await process_task_event(event_data)

    # Mark as processed
    await mark_event_processed(event_id)
```

## For More Information

- [Dapr Documentation](https://dapr.io/docs/)
- [Redpanda Documentation](https://docs.redpanda.com/)
- [Dapr Python SDK](https://github.com/dapr/python-sdk)
