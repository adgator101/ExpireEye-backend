from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base
import enum
import uuid


class NotificationType(enum.Enum):
    info = "info"
    warning = "warning"
    error = "error"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    userId = Column(String(36), ForeignKey("users.id"), nullable=False)
    # userProductId = Column(String(36), ForeignKey("userProducts.id"), nullable=False)
    message = Column(String(255), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    created_at = Column(String(255), nullable=False)
