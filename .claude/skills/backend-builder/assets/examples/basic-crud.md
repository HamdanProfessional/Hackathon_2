# Basic CRUD Example

## User Task Model

```python
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskRead(TaskBase):
    id: int
    created_at: datetime
```

## FastAPI CRUD Router

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.task import Task, TaskCreate, TaskUpdate, TaskRead
from app.database import get_session

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead)
async def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session)
):
    db_task = Task.from_orm(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskRead])
async def list_tasks(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    return tasks

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task: TaskUpdate,
    session: Session = Depends(get_session)
):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = task.dict(exclude_unset=True)
    for key, value in task_data.items():
        setattr(db_task, key, value)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}
```
