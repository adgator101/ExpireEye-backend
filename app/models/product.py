from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base
import uuid


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    barcode = Column(String(255), nullable=False, unique=True)
    nutritionId = Column(String(36), ForeignKey("nutritions.id"), nullable=True)
    addedAt = Column(String(255), nullable=False)
