from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base
import uuid
import enum


class UserProductStatus(enum.Enum):
    active = "active"
    expired = "expired"


class UserProduct(Base):
    __tablename__ = "userProducts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    userId = Column(String(36), ForeignKey("users.id"), nullable=False)
    productId = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    expiryDate = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default=UserProductStatus.active)
    notes = Column(String(255), nullable=True)
    addedAt = Column(String(255), nullable=False)
    updatedAt = Column(String(255), nullable=False)
