# Dapr Pub/Sub Examples

## Publishing Events

```python
import dapr.ext.fastapi
from fastapi import FastAPI

app = FastAPI()
dapr = dapr.ext.fastapi.DaprClient(app)

@app.post("/tasks")
async def create_task(task: Task):
    # Save to database
    db_task = await create_task_in_db(task)

    # Publish event
    await dapr.publish_event(
        pubsub_name="todo-pubsub",
        topic_name="task-created",
        data={
            "task_id": db_task.id,
            "user_id": db_task.user_id,
            "title": db_task.title,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    return db_task
```

## Subscribing to Events

```python
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="todo-pubsub", topic="task-created")
async def handle_task_created_event(event_data: dict):
    """Handle task created event."""
    task_id = event_data.get("task_id")
    user_id = event_data.get("user_id")
    title = event_data.get("title")

    # Send email notification
    await send_email(user_id, f"Task Created: {title}")

    return {"status": "processed"}
```

## Dapr Configuration

```yaml
# dapr.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: app-config
spec:
  features:
    - name: PubSub
      enabled: true
```

## Pub/Sub Component

```yaml
# pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.redis
  version: v1
  metadata:
    - name: redisHost
      value: "localhost:6379"
    - name: redisPassword
      value: ""
```
