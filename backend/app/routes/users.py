from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models import User
from backend.app.schemas import UserResponse
from backend.app.auth import get_current_user
from backend.app.database import get_db

router = APIRouter()

@router.get("/freelancers", response_model=list[UserResponse])
def list_freelancers(db: Session = Depends(get_db)):
    return db.query(User).filter(User.user_type == "freelancer").all()