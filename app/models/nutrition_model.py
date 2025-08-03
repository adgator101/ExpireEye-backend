from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base
import uuid


class Nutrition(Base):
    __tablename__ = "nutritions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    energy_kcal = Column(String(255), nullable=False)
    carbohydrate = Column(String(255), nullable=False)
    total_sugars = Column(String(255), nullable=False)
    fiber = Column(String(255), nullable=False)
    protein = Column(String(255), nullable=False)
    saturated_fat = Column(String(255), nullable=False)
    vitamin_a = Column(String(255), nullable=False)
    vitamin_c = Column(String(255), nullable=False)
    potassium = Column(String(255), nullable=False)
    iron = Column(String(255), nullable=False)
    calcium = Column(String(255), nullable=False)
    sodium = Column(String(255), nullable=False)
    cholesterol = Column(String(255), nullable=False)
    addedAt = Column(String(255), nullable=False)
