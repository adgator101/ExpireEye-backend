from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    userId = Column(Integer, ForeignKey("user.id"), nullable=False)
    expiryDate = Column(String(255), nullable=False)
    nutritionId = Column(Integer, ForeignKey("nutrition.id"), nullable=True)
