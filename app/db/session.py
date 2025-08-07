from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.base import Base
from dotenv import load_dotenv

import os
import urllib.parse

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# DATABASE_URL = (
#     f"mssql+pyodbc://{DB_USER}:{urllib.parse.quote_plus(DB_PASSWORD)}"
#     f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
# )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Ensures the connection is alive before using it
    pool_recycle=3600,  # Recycle connections every hour
    pool_size=5,
    max_overflow=2,
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
