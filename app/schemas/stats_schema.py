from pydantic import BaseModel
from typing import List, Dict

class ExpiryTrendItem(BaseModel):
    date: str
    expiring: int
    consumed: int
    wasted_cost: float

class WastageCategoryItem(BaseModel):
    category: str
    percentage: float

class WastedVsEatenItem(BaseModel):
    status: str
    count: int


class ExpiredProductItem(BaseModel):
    date: str
    expired_count: int

class NutrientsDetailData(BaseModel):
    energy_kcal: float
    carbohydrate: float
    protein: float
    fiber: float
    total_sugars: float
    saturated_fat: float
    vitamin_a: float
    vitamin_c: float
    potassium: float
    iron: float
    calcium: float
    sodium: float
    cholesterol: float

class NutrientsResponse(BaseModel):
    item: str
    nutrients: NutrientsDetailData
