import os

import requests
from fastapi import APIRouter, Request
from app.schemas.product import AddProductRequest
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from dotenv import load_dotenv
from app.models.product import Product
from app.models.nutrition import Nutrition
from app.models.user import User
from app.utils.nutrition_utils import check_nutrition_exists, fetch_nutrition

load_dotenv()


router = APIRouter()

API_KEY = os.getenv("API_KEY")


@router.post("/add")
async def add_product(
    product: AddProductRequest, request: Request, db: Session = Depends(get_db)
):
    product_name = product.productName
    expiry_date = product.expiryDate
    access_token = request.state.user
    user_id = access_token.get("userId")

    if not product_name or not user_id or not expiry_date:
        raise HTTPException(
            status_code=400,
            detail="All fields are required: productName, userId, and expiryDate.",
        )

    if len(product_name) < 3:
        raise HTTPException(
            status_code=400, detail="Product name must be at least 3 characters long."
        )

    exists_user = db.query(User).filter_by(id=user_id).first()
    if not exists_user:
        raise HTTPException(
            status_code=404, detail="User with the provided userId does not exist."
        )

    food_nutrition = fetch_nutrition(product_name)[0]

    nutrition_data = {
        "protein": check_nutrition_exists("protein_g", food_nutrition),
        "carbohydrate": check_nutrition_exists("carbohydrates_total_g", food_nutrition),
        "fat": check_nutrition_exists("fat_total_g", food_nutrition),
        "fiber": check_nutrition_exists("fiber_g", food_nutrition),
        "calories": check_nutrition_exists("calories", food_nutrition),
    }

    new_nutrition = Nutrition(**nutrition_data)
    db.add(new_nutrition)
    db.commit()
    db.refresh(new_nutrition)
    product_data = {
        "name": product_name,
        "userId": user_id,
        "expiryDate": expiry_date,
        "category": "Other",
        "nutritionId": new_nutrition.id,
    }
    new_product = Product(**product_data)

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product added successfully",
        "productId": new_product.id,
        "name": new_product.name.title(),
        "expiryDate": new_product.expiryDate,
    }


@router.get("/list")
def get_products(request: Request, db: Session = Depends(get_db)):
    product_name = request.query_params.get("productName")
    access_token = request.state.user
    user_id = access_token.get("userId")

    if not user_id:
        raise HTTPException(
            status_code=401, detail="Access token is missing or invalid."
        )
    existing_user = db.query(User).filter_by(id=user_id).first()

    if not existing_user:
        raise HTTPException(
            status_code=404, detail="User doesn't exist. Please sign up first."
        )

    if not product_name:
        raise HTTPException(
            status_code=400,
            detail="You haven't entered product name in query. Please provide 'productName' as a query parameter.",
        )

    products = (
        db.query(Product)
        .filter(Product.name == product_name, Product.userId == user_id)
        .all()
    )

    nutrition_query = db.query(Nutrition).filter(Nutrition.id == Product.nutritionId)

    result = []

    for product in products:
        nutrition = None
        if product.nutritionId:
            nutrition = nutrition_query.filter(
                Nutrition.id == product.nutritionId
            ).first()
            nutrition = {
                "protein": nutrition.protein,
                "carbohydrate": nutrition.carbohydrate,
                "fat": nutrition.fat,
                "fiber": nutrition.fiber,
                "calories": nutrition.calories,
            }
        result.append(
            {
                "id": product.id,
                "name": product.name,
                "expiryDate": product.expiryDate,
                "category": product.category,
                "nutrition": nutrition,
            }
        )

    return {"products": result}
