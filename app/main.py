from fastapi import FastAPI, Depends
from . import models, database
from app.routes.auth import router as auth_router
from app.routes.reviews import router as reviews_router
from app.auth import get_current_user
from app.models import User
from app.routes import auth, tasks, bids, chats, notifications, users

import uvicorn

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="FreelanceHub API",
    description="API для платформы фрилансеров и работодателей",
    version="1.0.0",
    openapi_tags=[...]
)

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
        "user_id": current_user.user_id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "user_type": current_user.user_type,
        "created_at": current_user.created_at
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)