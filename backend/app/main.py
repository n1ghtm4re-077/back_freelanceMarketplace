from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database
from backend.app.routes.auth import router as auth_router
from backend.app.auth import get_current_user
from backend.app.models import User
import uvicorn

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()


if __name__ == "__main__":
    uvicorn.run("main:app", reload = True)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])

@app.get("/profile/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "user_id": current_user.user_id
    }
