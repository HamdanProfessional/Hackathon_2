# Dapr Event-Driven Architecture Resources

## Official Documentation
- [Dapr Pub/Sub](https://docs.dapr.io/developing-applications/building-blocks/pubsub/)
- [Dapr State Management](https://docs.dapr.io/developing-applications/building-blocks/state-management/)
- [Dapr Python SDK](https://github.com/dapr/python-sdk)

## Message Brokers

### Redis Pub/Sub
Simplest option for development. Use `pubsub.redis` component type.

### Kafka
Production-ready. Use `pubsub.kafka` component type with Kafka broker addresses.

### AWS SNS/SQS
Use `pubsub.snssqs` for AWS cloud-native deployments.

### Azure Service Bus
Use `pubsub.azure.servicebus` for Azure deployments.

## Best Practices

### 1. Idempotent Consumers
```python
import hashlib

def generate_event_id(event: dict) -> str:
    """Generate unique event ID for idempotency."""
    content = f"{event['type']}:{event['data']['id']}:{event['timestamp']}"
    return hashlib.sha256(content.encode()).hexdigest()

# Check if event already processed
if await was_event_processed(event_id):
    return {"status": "already_processed"}
```

### 2. Error Handling
```python
@dapr_app.subscribe(pubsub="todo-pubsub", topic="task-created")
async def handle_task_created(event_data: dict):
    try:
        await process_event(event_data)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Event processing failed: {e}")
        # Dead letter queue logic here
        return {"status": "failed", "error": str(e)}
```

### 3. Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def publish_with_retry(topic: str, data: dict):
    await dapr.publish_event("todo-pubsub", topic, data)
```

## Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-app
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-app"
        dapr.io/app-port: "8000"
    spec:
      containers:
      - name: todo-app
        image: todo-app:latest
```
