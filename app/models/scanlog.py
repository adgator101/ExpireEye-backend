from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base
import enum


class ScanStatus(enum.Enum):
    scanned = "scanned"
    expired = "expired"
    not_found = "not_found"


class ScanLog(Base):
    __tablename__ = "scanlog"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey("user.id"), nullable=False)
    barcode = Column(String(255), nullable=False)
    productId = Column(Integer, ForeignKey("product.id"), nullable=False)
    status = Column(Enum(ScanStatus), nullable=False)
    scanned_at = Column(String(255), nullable=False)
