# app/routers/reviews.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models import Review, Task, User
from backend.app.schemas import ReviewCreate, ReviewResponse, ReviewUpdate
from backend.app.auth import get_current_user
from backend.app.database import get_db

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Оставить отзыв о пользователе после выполнения задачи.
    Только заказчик или фрилансер могут отправлять отзыв.
    """

    # Проверяем, существует ли задача
    task = db.query(Task).filter(Task.task_id == review_data.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Проверяем, является ли пользователь участником задачи (заказчик или фрилансер)
    is_employer = current_user.user_type == "employer" and task.employer_id == current_user.user_id
    is_freelancer = current_user.user_type == "freelancer" and task.freelancer_id == current_user.user_id

    if not is_employer and not is_freelancer:
        raise HTTPException(status_code=403, detail="You are not a participant of this task")

    # Проверяем, не писал ли уже отзыв на этого пользователя по этой задаче
    existing_review = db.query(Review).filter(
        Review.task_id == review_data.task_id,
        Review.reviewer_id == current_user.user_id
    ).first()

    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this task")

    # Создаем новый отзыв
    new_review = Review(**review_data.dict(), reviewer_id=current_user.user_id)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


@router.get("/me", response_model=list[ReviewResponse])
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список отзывов, которые оставили о тебе
    """
    reviews = db.query(Review).filter(Review.reviewed_user_id == current_user.user_id).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found")
    return reviews


@router.get("/{task_id}", response_model=ReviewResponse)
def get_task_review(task_id: int, db: Session = Depends(get_db)):
    """
    Получить отзыв по конкретной задаче
    """
    review = db.query(Review).filter(Review.task_id == task_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.put("/{review_id}")
def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить свой отзыв
    """
    review = db.query(Review).filter(Review.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.reviewer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only edit your own reviews")

    for key, value in review_update.dict(exclude_unset=True).items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)

    return {"message": "Review updated", "review": review}


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить свой отзыв
    """
    review = db.query(Review).filter(Review.review_id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.reviewer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own reviews")

    db.delete(review)
    db.commit()

    return {"message": "Review deleted"}