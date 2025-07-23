import uuid

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default= lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    dob = Column(String(255), nullable=True)
    created_at = Column(String(255), nullable=False)