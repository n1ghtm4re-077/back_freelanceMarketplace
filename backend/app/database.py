from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from sqlalchemy.orm import declarative_base

load_dotenv()

# Подключение к PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()