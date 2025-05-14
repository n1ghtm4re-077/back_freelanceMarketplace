from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database
import uvicorn

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

@app.get("/")
def root():
    return "Hello world"

if __name__ == "__main__":
    uvicorn.run("main:app", reload = True)
