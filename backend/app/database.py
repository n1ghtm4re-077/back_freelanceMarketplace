from sqlalchemy import create_engine
from sqlalchemy import sessionmaker
from dotenv import load_dotenv
import os

from sqlalchemy.orm import declarative_base

load_dotenv()

# Подключение к PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/freelance_hub"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()