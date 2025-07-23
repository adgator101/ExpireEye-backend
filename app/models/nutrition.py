from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base
import uuid

class Nutrition(Base):
    __tablename__ = "nutritions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    protein = Column(String(255), nullable=False)
    carbohydrate = Column(String(255), nullable=False)
    fat = Column(String(255), nullable=False)
    fiber = Column(String(255), nullable=False)
    calories = Column(String(255), nullable=False)
