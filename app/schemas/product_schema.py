from pydantic import BaseModel, EmailStr
from typing import Optional, List


class NutritionResponse(BaseModel):
    energy_kcal: str
    carbohydrate: str
    protein: str
    fiber: str
    total_sugars: str
    saturated_fat: str
    vitamin_a: str
    vitamin_c: str
    potassium: str
    iron: str
    calcium: str
    sodium: str
    cholesterol: str


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
    name: Optional[str] = None
    quantity: Optional[int] = 1
    category: Optional[str] = "Uncategorized"
    # barcode: Optional[str] = None
    expiryDate: Optional[str] = None
    notes: Optional[str] = None
    isScannedProduct: Optional[bool] = False


class UpdateUserProductRequest(BaseModel):
    quantity: Optional[int] = None
    expiryDate: Optional[str] = None
    notes: Optional[str] = None


class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    barcode: Optional[str] = None
