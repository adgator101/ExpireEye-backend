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

class NutrientsResponse(BaseModel):
    item: str
    nutrients: Dict[str, float]  # or str if you keep as strings


class ExpiredProductItem(BaseModel):
    date: str
    expired_count: int

class NutrientsDetailResponse(BaseModel):
    item: str
    nutrients: Dict[str, float]
