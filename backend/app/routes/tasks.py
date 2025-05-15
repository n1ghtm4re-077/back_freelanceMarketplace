from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.app.models import Task, User, Category, Bid
from backend.app.schemas import TaskCreate, TaskResponse, TaskUpdate, BidResponse
from backend.app.auth import get_current_user
from backend.app.database import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создание новой задачи (только для заказчиков)
    """
    if current_user.user_type != "employer":
        raise HTTPException(status_code=403, detail="Only employers can create tasks")

    # Проверяем, существует ли категория
    category = db.query(Category).filter(Category.category_id == task_data.category_id).first()
    if not category and task_data.category_id is not None:
        raise HTTPException(status_code=404, detail="Category not found")

    new_task = Task(**task_data.dict(), employer_id=current_user.user_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """
    Получение информации о задаче по ID
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/me", response_model=list[TaskResponse])
def read_my_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Получение задач, созданных пользователем или назначенных ему
    """
    if current_user.user_type == "employer":
        tasks = db.query(Task).filter(Task.employer_id == current_user.user_id).all()
    elif current_user.user_type == "freelancer":
        tasks = db.query(Task).filter(Task.freelancer_id == current_user.user_id).all()
    else:
        raise HTTPException(status_code=403, detail="Unknown user type")

    return tasks


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    category_id: int = None,
    min_budget: float = None,
    max_budget: float = None,
    status: str = None,
    deadline_gte: str = None,   # Дата в формате YYYY-MM-DD
    deadline_lte: str = None,   # Дата в формате YYYY-MM-DD
    db: Session = Depends(get_db)
):
    """
    Получить список задач с фильтрами:
    - category_id
    - min_budget / max_budget
    - status
    - deadline_gte (после этой даты)
    - deadline_lte (до этой даты)
    """

    query = db.query(Task)

    # Фильтрация по категории
    if category_id:
        query = query.filter(Task.category_id == category_id)

    # Фильтрация по бюджету
    if min_budget is not None:
        query = query.filter(Task.budget >= min_budget)
    if max_budget is not None:
        query = query.filter(Task.budget <= max_budget)

    # Фильтрация по статусу
    if status:
        query = query.filter(Task.status == status)

    # Фильтрация по дедлайну
    from datetime import datetime
    if deadline_gte:
        try:
            date = datetime.strptime(deadline_gte, "%Y-%m-%d")
            query = query.filter(Task.deadline >= date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for deadline_gte. Use YYYY-MM-DD")

    if deadline_lte:
        try:
            date = datetime.strptime(deadline_lte, "%Y-%m-%d")
            query = query.filter(Task.deadline <= date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format for deadline_lte. Use YYYY-MM-DD")

    # Применяем пагинацию
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.put("/{task_id}")
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновление задачи (только автором)
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.employer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not the owner of this task")

    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return {"message": "Task updated", "task": task}


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление задачи (только владельцем)
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.employer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not the owner of this task")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted"}


@router.get("/{task_id}/bids", response_model=list[BidResponse])
def get_bids(task_id: int, db: Session = Depends(get_db)):
    """
    Получение всех откликов на задачу
    """
    bids = db.query(Bid).filter(Bid.task_id == task_id).all()
    if not bids:
        raise HTTPException(status_code=404, detail="No bids found for this task")

    return bids