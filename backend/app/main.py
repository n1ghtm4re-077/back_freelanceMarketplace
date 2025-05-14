from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database
from backend.app.routes.auth import router as auth_router
from backend.app.routes.reviews import router as reviews_router
from backend.app.auth import get_current_user
from backend.app.models import User, Task, Chat, Message, Notification
from backend.app.routes import auth, tasks, bids, chats, notifications, users
from backend.app.database import Base, engine

import uvicorn

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(bids.router)
app.include_router(chats.router)
app.include_router(notifications.router)
app.include_router(users.router)
app.include_router(reviews_router)

@app.get("/profile/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "user_id": current_user.user_id
    }
