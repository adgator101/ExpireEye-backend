from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base
import enum
import uuid


class ScanStatus(enum.Enum):
    scanned = "scanned"
    expired = "expired"
    not_found = "not_found"


class ScanLog(Base):
    __tablename__ = "scanlogs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    userId = Column(String(36), ForeignKey("users.id"), nullable=False)
    barcode = Column(String(255), nullable=False)
    productId = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(Enum(ScanStatus), nullable=False)
    scanned_at = Column(String(255), nullable=False)
