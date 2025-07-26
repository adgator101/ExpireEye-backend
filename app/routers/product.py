import os

import requests
from fastapi import APIRouter, Request
from app.schemas.product import AddProductRequest, AddUserProductRequest
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from dotenv import load_dotenv
from app.models.product import Product
from app.models.nutrition import Nutrition
from app.models.user import User
from app.models.user_product import UserProduct

from app.utils.nutrition_utils import check_nutrition_exists, fetch_nutrition
from datetime import datetime

load_dotenv()


router = APIRouter()

API_KEY = os.getenv("API_KEY")


@router.post("/inventory/add")
async def add_product(
    product: AddProductRequest, request: Request, db: Session = Depends(get_db)
):
    product_name = product.productName
    category = product.category

    access_token = request.state.user
    user_id = access_token.get("userId")

    if not product_name or not user_id:
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
        "category": category,
        "barcode": product.barcode if product.barcode else "N/A",
        "nutritionId": new_nutrition.id,
        "addedAt": datetime.utcnow().isoformat(),
    }

    new_product = Product(**product_data)

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product added successfully",
        "productId": new_product.id,
        "name": new_product.name.title(),
    }


@router.get("/inventory/list")
def get_products(request: Request, db: Session = Depends(get_db)):
    product_name = request.query_params.get("productName")
    access_token = request.state.user

    print(f"Access Token: {access_token}")
    if not product_name:
        raise HTTPException(
            status_code=400,
            detail="You haven't entered product name in query. Please provide 'productName' as a query parameter.",
        )

    products = db.query(Product).filter(Product.name == product_name).all()

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
                "category": product.category,
                "nutrition": nutrition,
            }
        )

    return {"products": result}


@router.post("/user/add")
def add_user_product(
    product: AddUserProductRequest, request: Request, db: Session = Depends(get_db)
):
    access_token = request.state.user
    user_id = access_token.get("userId")

    product_name = product.name
    quantity = product.quantity
    expiry_date = product.expiryDate

    exists_user = db.query(User).filter_by(id=user_id).first()

    if not exists_user:
        raise HTTPException(
            status_code=404, detail="User with the provided userId does not exist."
        )

    if not product_name or not expiry_date:
        raise HTTPException(
            status_code=400,
            detail="All fields are required: name, quantity, and expiryDate.",
        )

    check_product = db.query(Product).filter(Product.name == product_name).first()

    if not check_product:
        raise HTTPException(
            status_code=404,
            detail=f"Product '{product_name}' does not exist in warehouse. Please add it first.",
        )
    product_id = check_product.id if check_product else None

    new_product = {
        "userId": access_token.get("userId"),
        "productId": product_id,
        "quantity": quantity,
        "expiryDate": expiry_date,
        "addedAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
    }

    new_user_product = UserProduct(**new_product)
    db.add(new_user_product)
    db.commit()
    db.refresh(new_user_product)

    return {
        "message": "New Product added to user inventory successfully",
        "productId": new_user_product.productId,
        "name": product_name.title(),
        "quantity": quantity,
        "expiryDate": expiry_date,
    }


@router.get("/user/list")
def get_user_products(request: Request, db: Session = Depends(get_db)):
    access_token = request.state.user
    user_id = access_token.get("userId")

    user_products = db.query(UserProduct).filter(UserProduct.userId == user_id).all()

    user_product_data = []
    for product in user_products:
        product_data = db.query(Product).filter(Product.id == product.productId).first()
        if product_data:
            nutrition_data = (
                db.query(Nutrition)
                .filter(Nutrition.id == product_data.nutritionId)
                .first()
            )
            nutrition = (
                {
                    "protein": nutrition_data.protein,
                    "carbohydrate": nutrition_data.carbohydrate,
                    "fat": nutrition_data.fat,
                    "fiber": nutrition_data.fiber,
                    "calories": nutrition_data.calories,
                }
                if nutrition_data
                else None
            )

            user_product_data.append(
                {
                    "id": product_data.id,
                    "name": product_data.name,
                    "category": product_data.category,
                    "quantity": product.quantity,
                    "expiryDate": product.expiryDate,
                    "addedAt": product.addedAt,
                    "nutrition": nutrition,
                }
            )
        
        else:
            user_product_data.append(
                {
                    "id": product.productId,
                    "name": "Unknown Product",
                    "category": "Unknown Category",
                    "expiryDate": product.expiryDate,
                    "addedAt": product.addedAt,
                    "nutrition": None,
                }
            )

    return {"products": user_product_data}
