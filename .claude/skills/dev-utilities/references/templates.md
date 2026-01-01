# Dev-Utilities - Reusable Templates

## Git Commit Template

```bash
<type>(<scope>): <description>

[optional body]

[optional footer]
```

## CORS Configuration Template

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",") or [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,  # JWT in header
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Type Conversion Template

| Python | TypeScript |
|--------|------------|
| `int` | `number` |
| `str` | `string` |
| `bool` | `boolean` |
| `datetime` | `string` |
| `UUID` | `string` |
| `Optional[T]` | `T \| null` |
| `List[T]` | `T[]` |
| `Dict[K,V]` | `Record<K,V>` |
