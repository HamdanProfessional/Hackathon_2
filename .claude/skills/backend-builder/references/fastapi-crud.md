# FastAPI CRUD Resources

## Official Documentation
- [FastAPI Tutorial - User Guide](https://fastapi.tiangolo.com/tutorial/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Best Practices
1. **Use SQLModel for database models** - Combines Pydantic and SQLAlchemy
2. **Separate schemas** - Create, Update, Read schemas for each model
3. **Repository pattern** - Abstract database operations behind repository classes
4. **Dependency injection** - Use FastAPI's Depends for database sessions
5. **Error handling** - Proper HTTP status codes and error messages

## Common Patterns

### Authentication with CRUD
```python
from fastapi import Depends
from app.auth import get_current_user

@router.post("/", response_model=TaskRead)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    db_task = Task.from_orm(task, user_id=current_user.id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
```

### Pagination
```python
@router.get("/", response_model=List[TaskRead])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    tasks = session.exec(
        select(Task)
        .offset(skip)
        .limit(limit)
    ).all()
    return tasks
```

### Filtering
```python
@router.get("/", response_model=List[TaskRead])
async def list_tasks(
    completed: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    query = select(Task)
    if completed is not None:
        query = query.where(Task.completed == completed)
    tasks = session.exec(query).all()
    return tasks
```
