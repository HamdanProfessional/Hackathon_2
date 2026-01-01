# CORS Fix Examples

Common CORS issues and their solutions.

## Error 1: Credentials Mode Conflict

**Browser Error**:
```
Access to fetch has been blocked by CORS policy: The value of the
'Access-Control-Allow-Origin' header must not be the wildcard '*' when
the request's credentials mode is 'include'.
```

**Solution 1**: Remove credentials mode (RECOMMENDED for JWT)

```typescript
// frontend/lib/api.ts
const response = await fetch(url, {
  // Remove: credentials: "include"
  headers: { Authorization: `Bearer ${token}` }
});
```

**Solution 2**: Specify exact origins

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://frontend.vercel.app"
    ],
    allow_credentials=True,
)
```

## Error 2: Missing Authorization Header

**Browser Error**:
```
Request header field authorization is not allowed by Access-Control-Allow-Headers
```

**Solution**:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],  # Include Authorization
)
```

## Complete CORS Configuration

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Todo App API")

cors_origins_str = os.environ.get("CORS_ORIGINS", "")
CORS_ORIGINS = cors_origins_str.split(",") if cors_origins_str else [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,  # JWT in header, not cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```
