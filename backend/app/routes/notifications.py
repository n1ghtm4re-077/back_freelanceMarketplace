from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models import Notification
from backend.app.schemas import NotificationResponse
from backend.app.auth import get_current_user
from backend.app.database import get_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def create_notification(db: Session, notification_data: dict):
    """
    Вспомогательная функция для создания уведомления
    """
    new_notification = Notification(**notification_data)
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification


@router.get("/me", response_model=list[NotificationResponse])
def read_notifications(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Получить все уведомления текущего пользователя
    """
    notifications = db.query(Notification).filter(Notification.user_id == current_user.user_id).all()
    return notifications


@router.put("/{notification_id}/read")
def mark_as_read(notification_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Отметить уведомление как прочитанное
    """
    notification = db.query(Notification).filter(
        Notification.notification_id == notification_id,
        Notification.user_id == current_user.user_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()
    db.refresh(notification)

    return {"status": "marked as read"}