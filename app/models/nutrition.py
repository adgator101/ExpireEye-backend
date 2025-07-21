from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base


class Nutrition(Base):
    __tablename__ = "nutrition"

    id = Column(Integer, primary_key=True, autoincrement=True)
    protein = Column(String(255), nullable=False)
    carbohydrate = Column(String(255), nullable=False)
    fat = Column(String(255), nullable=False)
    fiber = Column(String(255), nullable=False)
    calories = Column(String(255), nullable=False)
