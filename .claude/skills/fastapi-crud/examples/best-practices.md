# FastAPI CRUD Best Practices

## Model Design

### Always Include Timestamps

```python
# Good
class Task(SQLModel, table=True):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Bad - No audit trail
class Task(SQLModel, table=True):
    pass
```

### Use Proper Indexes

```python
# Good - Compound indexes for common queries
class Task(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="users.id", index=True)
    status: str = Field(index=True)
    created_at: datetime = Field(index=True)

    __table_args__ = (
        Index("ix_tasks_user_status", "user_id", "status"),
        Index("ix_tasks_user_created", "user_id", "created_at"),
    )
```

### Enforce User Isolation

```python
# Good - Always filter by user_id
@router.get("/tasks")
async def list_tasks(
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

# Bad - No user filtering (security issue!)
@router.get("/tasks")
async def list_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()
```

## Pydantic Schemas

### Separate Create/Update/Response

```python
# Create - No user_id (from JWT)
class TaskCreate(BaseModel):
    title: str
    # user_id omitted - extracted from JWT

# Update - All optional
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None

# Response - All fields
class TaskResponse(BaseModel):
    id: int
    user_id: str  # UUID as string
    title: str
    # ... all fields
```

### Validate Input

```python
from pydantic import validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    priority: str = Field(default="normal")

    @validator("priority")
    def validate_priority(cls, v):
        valid = ["low", "normal", "high"]
        if v not in valid:
            raise ValueError(f"Priority must be one of: {valid}")
        return v
```

## Router Design

### Use Proper HTTP Status Codes

| Operation | Status Code | Description |
|-----------|-------------|-------------|
| Create | 201 | Resource created |
| Read (single) | 200 | Success |
| Read (list) | 200 | Success |
| Update | 200 | Success (return updated resource) |
| Delete | 204 | No content (success) |
| Not Found | 404 | Resource doesn't exist |
| Validation Error | 422 | Invalid input |

### Pagination

```python
@router.get("/tasks")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session)
):
    offset = (page - 1) * page_size

    total = len(session.exec(select(Task)).all())
    items = session.exec(
        select(Task)
        .offset(offset)
        .limit(page_size)
    ).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
```

### Error Handling

```python
@router.post("/tasks")
async def create_task(task_data: TaskCreate):
    try:
        task = create_task(task_data)
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
```

## Testing

### Test User Isolation

```python
def test_user_cannot_access_other_tasks(client, user1, user2):
    # Create task for user1
    response = client.post(
        "/tasks",
        json={"title": "User1 Task"},
        headers=user1_headers
    )
    task_id = response.json()["id"]

    # Try to access with user2 token
    response = client.get(
        f"/tasks/{task_id}",
        headers=user2_headers
    )

    assert response.status_code == 404
```

### Test Pagination

```python
def test_pagination(client, auth_headers):
    # Create 25 tasks
    for i in range(25):
        client.post("/tasks", json={"title": f"Task {i}"}, headers=auth_headers)

    # Get first page
    response = client.get("/tasks?page=1&page_size=10", headers=auth_headers)
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 25
    assert data["page"] == 1
    assert data["total_pages"] == 3
```

## Performance

### Use Eager Loading

```python
# Good - Load related data
from sqlmodel import selectinload

statement = select(Task).options(selectinload(Task.comments))
tasks = session.exec(statement).all()

# Bad - N+1 query problem
tasks = session.exec(select(Task)).all()
for task in tasks:
    print(task.comments)  # Separate query for each task!
```

### Use Database Aggregates

```python
# Good - Single query
total = session.exec(
    select(func.count(Task.id)).where(Task.user_id == user_id)
).one()

# Bad - Load all rows
tasks = session.exec(select(Task)).all()
total = len(tasks)
```

## Security Checklist

- [ ] All endpoints check user_id for authorization
- [ ] User cannot access another user's data
- [ ] Input validation on all parameters
- [ ] SQL queries use parameterized statements
- [ ] Rate limiting on expensive operations
- [ ] Sensitive data filtered from responses
- [ ] Proper error messages (no information leakage)
