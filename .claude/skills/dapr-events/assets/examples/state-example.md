# Dapr State Management Example

```python
from dapr.ext.fastapi import DaprClient
from fastapi import FastAPI, HTTPException

app = FastAPI()
dapr = DaprClient(app)

@app.post("/cache/{key}")
async def save_to_cache(key: str, value: dict):
    """Save data to Dapr state store."""
    try:
        await dapr.save_state(
            store_name="statestore",
            key=key,
            value=value
        )
        return {"status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache/{key}")
async def get_from_cache(key: str):
    """Get data from Dapr state store."""
    state = await dapr.get_state(
        store_name="statestore",
        key=key
    )

    if not state:
        raise HTTPException(status_code=404, detail="Key not found")

    return state.data

@app.delete("/cache/{key}")
async def delete_from_cache(key: str):
    """Delete data from Dapr state store."""
    await dapr.delete_state(
        store_name="statestore",
        key=key
    )
    return {"status": "deleted"}
```

## State Store Component

```yaml
# statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "localhost:6379"
    - name: redisPassword
      value: ""
    - name: keyPrefix
      value: "none"
```
