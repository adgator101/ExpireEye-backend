from pydantic import BaseModel, EmailStr
from typing import Optional, List


class NutritionResponse(BaseModel):
    protein: Optional[str] = "0.0"
    carbohydrate: Optional[str] = "0.0"
    fat: Optional[str] = "0.0"
    fiber: Optional[str] = "0.0"
    calories: Optional[str] = "0.0"


class ProductResponse(BaseModel):
    id: str
    name: str
    category: str
    barcode: str
    nutrition: Optional[NutritionResponse]


class ProductListResponse(BaseModel):
    products: List[ProductResponse]


class AddProductRequest(BaseModel):
    productName: str
    category: str
    barcode: Optional[str] = None


class AddUserProductRequest(BaseModel):
    name: str
    quantity: int
    expiryDate: str


class UpdateUserProductRequest(BaseModel):
    quantity: Optional[int] = None
    expiryDate: Optional[str] = None


class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    barcode: Optional[str] = None
    nutritionId: Optional[str] = None
