from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, case
from app.db.session import get_db
from app.models.user_product import UserProduct, UserProductStatus
from app.models.nutrition_model import Nutrition
from app.models.product_model import Product
from app.schemas.stats_schema import (
    ExpiryTrendItem,
    WastageCategoryItem,
    WastedVsEatenItem,
    NutrientsResponse,
    ExpiredProductItem,
)
from typing import List
import random

router = APIRouter()

@router.get("/expired-products", response_model=List[ExpiredProductItem])
def get_expired_trend(db: Session = Depends(get_db)):
    result = (
        db.query(
            cast(UserProduct.expiryDate, Date).label("date"),
            func.count(UserProduct.id).label("expired_count")
        )
        .filter(UserProduct.status == UserProductStatus.expired.value)
        .group_by(cast(UserProduct.expiryDate, Date))
        .order_by("date")
        .all()
    )

    return [
        {"date": str(row.date), "expired_count": row.expired_count}
        for row in result
    ]

@router.get("/expiry-trends", response_model=List[ExpiryTrendItem])
def get_expiry_trends(db: Session = Depends(get_db)):
    """
    Bars = expiring items
    Line = simulated consumed before expiry (dummy: 60% of active)
    Area = estimated cost of wasted items (mock cost = 50 per item)
    """
    results = (
        db.query(
            func.date(UserProduct.expiryDate).label("date"),
            func.count(UserProduct.id).label("expiring"),
            func.sum(case((UserProduct.status == "expired", 1), else_=0)).label("expired")
        )
        .group_by(func.date(UserProduct.expiryDate))
        .order_by(func.date(UserProduct.expiryDate))
        .all()
    )

    data = []
    for date, expiring, expired in results:
        active = expiring - expired
        consumed = int(active * random.uniform(0.4, 0.8))
        wasted_cost = expired * 50  
        data.append({
            "date": str(date),
            "expiring": expiring,
            "consumed": consumed,
            "wasted_cost": wasted_cost
        })

    return data

@router.get("/wastage-category", response_model=List[WastageCategoryItem])
def get_wastage_by_category(db: Session = Depends(get_db)):
    """
    Percentage of wasted items by category
    """
    total_expired = db.query(func.count(UserProduct.id)).filter(UserProduct.status == "expired").scalar()
    if total_expired == 0:
        return []

    results = (
        db.query(Product.category, func.count(UserProduct.id))
        .join(Product, Product.id == UserProduct.productId)
        .filter(UserProduct.status == "expired")
        .group_by(Product.category)
        .all()
    )

    return [
        {"category": category, "percentage": round((count / total_expired) * 100, 2)}
        for category, count in results
    ]

@router.get("/wasted-vs-eaten", response_model=List[WastedVsEatenItem])
def get_wasted_vs_eaten(db: Session = Depends(get_db)):
    expired_count = db.query(func.count(UserProduct.id)).filter(UserProduct.status == "expired").scalar()
    active_count = db.query(func.count(UserProduct.id)).filter(UserProduct.status == "active").scalar()

    return [
        {"status": "wasted", "count": expired_count},
        {"status": "active", "count": active_count}
    ]

@router.get("/nutrients/{product_id}", response_model=NutrientsResponse)
def get_nutrients(product_id: str, db: Session = Depends(get_db)):
    """
    Show all key nutrients for Radar Chart (exclude non-nutrient fields and N/A values)
    """
    result = (
        db.query(Product.name, Nutrition)
        .join(Nutrition, Nutrition.id == Product.nutritionId)
        .filter(Product.id == product_id)
        .first()
    )

    if not result:
        return {"item": "Product not found or no nutrition data", "nutrients": {}}

    product_name, nutrition_obj = result

    # Convert Nutrition SQLAlchemy object to dictionary
    nutrition_dict = {col.name: getattr(nutrition_obj, col.name) for col in nutrition_obj.__table__.columns}

    # Remove unwanted keys
    remove_keys = ["id", "addedAt"]
    for key in remove_keys:
        nutrition_dict.pop(key, None)

    # Filter out None or "N/A" values
    filtered_nutrients = {k: float(v) for k, v in nutrition_dict.items() if v not in (None, "N/A")}

    return {
        "item": product_name,
        "nutrients": filtered_nutrients
    }
