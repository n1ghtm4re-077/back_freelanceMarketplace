from fastapi import FastAPI

import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return "Hello world"
