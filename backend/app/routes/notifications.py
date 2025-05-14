from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models import Notification, User
from backend.app.schemas import NotificationResponse
from backend.app.auth import get_current_user
from backend.app.database import get_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/me", response_model=list[NotificationResponse])
def get_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Notification).filter(Notification.user_id == current_user.user_id).all()