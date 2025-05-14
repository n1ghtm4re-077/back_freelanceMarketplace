from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models import User, FreelancerProfile, EmployerProfile
from backend.app.schemas import UserResponse
from backend.app.auth import get_current_user
from backend.app.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def read_users_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Получение данных текущего пользователя
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Получение информации о пользователе по ID
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/me/profile")
def read_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение профиля текущего пользователя (фрилансер или заказчик)
    """
    if current_user.user_type == "freelancer":
        profile = db.query(FreelancerProfile).filter(FreelancerProfile.user_id == current_user.user_id).first()
    elif current_user.user_type == "employer":
        profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == current_user.user_id).first()
    else:
        raise HTTPException(status_code=400, detail="Unknown user type")

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


@router.get("/{user_id}/profile")
def read_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Получение профиля пользователя по ID
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.user_type == "freelancer":
        profile = db.query(FreelancerProfile).filter(FreelancerProfile.user_id == user_id).first()
    elif user.user_type == "employer":
        profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == user_id).first()
    else:
        profile = None

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


@router.get("/freelancers", response_model=list[UserResponse])
def list_freelancers(db: Session = Depends(get_db)):
    """
    Получить список всех фрилансеров
    """
    freelancers = db.query(User).filter(User.user_type == "freelancer").all()
    return freelancers


@router.get("/employers", response_model=list[UserResponse])
def list_employers(db: Session = Depends(get_db)):
    """
    Получить список всех заказчиков
    """
    employers = db.query(User).filter(User.user_type == "employer").all()
    return employers


@router.put("/me/profile")
def update_profile(
    profile_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновление профиля фрилансера или заказчика
    """
    if current_user.user_type == "freelancer":
        profile = db.query(FreelancerProfile).filter(FreelancerProfile.user_id == current_user.user_id).first()
    elif current_user.user_type == "employer":
        profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == current_user.user_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Обновляем поля
    for key, value in profile_data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return {"message": "Profile updated", "profile": profile}