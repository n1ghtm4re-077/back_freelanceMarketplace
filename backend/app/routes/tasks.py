from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models import Task, User
from backend.app.schemas import TaskCreate, TaskResponse
from backend.app.auth import get_current_user
from backend.app.database import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.user_type != "employer":
        raise HTTPException(status_code=403, detail="Only employers can create tasks")

    new_task = Task(**task.dict(), owner_id=current_user.user_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/", response_model=list[TaskResponse])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks
