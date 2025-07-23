from pydantic import BaseModel, EmailStr
from typing import Optional


class AddProductRequest(BaseModel):
    productName: str
    expiryDate: str
