from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models import Review, User
from backend.app.schemas import ReviewCreate, ReviewResponse
from backend.app.auth import get_current_user
from backend.app.database import get_db

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=ReviewResponse)
def add_review(review: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_review = Review(**review.dict(), reviewer_id=current_user.user_id)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review