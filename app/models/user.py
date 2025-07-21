from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    dob = Column(String(255), nullable=True)
    created_at = Column(String(255), nullable=False)


