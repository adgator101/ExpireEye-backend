from pydantic import BaseModel, EmailStr
from typing import Optional


class AddProductRequest(BaseModel):
    productName: str
    category: str
    barcode: Optional[str] = None

class AddUserProductRequest(BaseModel):
    name: str
    quantity: int
    expiryDate: str
