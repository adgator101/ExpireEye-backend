from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base
import enum


class NotificationType(enum.Enum):
    info = "info"
    warning = "warning"
    error = "error"


class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey("user.id"), nullable=False)
    productId = Column(Integer, ForeignKey("product.id"), nullable=False)
    message = Column(String(255), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    created_at = Column(String(255), nullable=False)
