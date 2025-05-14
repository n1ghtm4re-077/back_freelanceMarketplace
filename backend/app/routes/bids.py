from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models import Bid, Task, User
from backend.app.schemas import BidCreate, BidResponse
from backend.app.auth import get_current_user
from backend.app.database import get_db

router = APIRouter(prefix="/bids", tags=["Bids"])

@router.post("/", response_model=BidResponse)
def create_bid(
    bid: BidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создание нового отклика на задачу
    """
    # Проверяем, что пользователь — фрилансер
    if current_user.user_type != "freelancer":
        raise HTTPException(status_code=403, detail="Only freelancers can send bids")

    # Проверяем, существует ли задача
    task = db.query(Task).filter(Task.task_id == bid.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Проверяем, не отправлен ли уже отклик этим фрилансером
    existing_bid = db.query(Bid).filter(
        Bid.task_id == bid.task_id,
        Bid.freelancer_id == current_user.user_id
    ).first()
    if existing_bid:
        raise HTTPException(status_code=400, detail="You have already sent a bid for this task")

    # Создаем новый отклик
    new_bid = Bid(
        **bid.dict(),
        freelancer_id=current_user.user_id
    )
    db.add(new_bid)
    db.commit()
    db.refresh(new_bid)

    return new_bid


@router.get("/{task_id}/bids", response_model=list[BidResponse])
def get_bids(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    Получение списка откликов по задаче
    """
    # Проверяем, существует ли задача
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Получаем все отклики на эту задачу
    bids = db.query(Bid).filter(Bid.task_id == task_id).all()

    return bids


@router.put("/{bid_id}", response_model=BidResponse)
def update_bid_status(
    bid_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Изменение статуса отклика
    """
    # Проверяем, существует ли отклик
    bid = db.query(Bid).filter(Bid.bid_id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    # Проверяем, что пользователь — заказчик
    if current_user.user_type != "employer":
        raise HTTPException(status_code=403, detail="Only employers can change bid status")

    # Проверяем, что заказчик является владельцем задачи
    if bid.task.owner_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not the owner of this task")

    # Разрешённые статусы
    allowed_statuses = ["pending", "accepted", "rejected"]
    if status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed statuses: {allowed_statuses}")

    # Обновляем статус отклика
    bid.status = status
    db.commit()
    db.refresh(bid)

    return bid


@router.delete("/{bid_id}")
def delete_bid(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление отклика
    """
    # Проверяем, существует ли отклик
    bid = db.query(Bid).filter(Bid.bid_id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    # Проверяем, что пользователь — фрилансер или заказчик
    if current_user.user_type == "freelancer" and bid.freelancer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not the freelancer who sent this bid")
    elif current_user.user_type == "employer" and bid.task.owner_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not the owner of this task")

    # Удаляем отклик
    db.delete(bid)
    db.commit()

    return {"message": "Bid deleted"}