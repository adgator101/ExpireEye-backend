import os

from dotenv import load_dotenv
from fastapi import APIRouter, Request, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.product_model import Product
from app.models.nutrition_model import Nutrition
from app.models.user_product import UserProduct
from app.models.user_model import User
from datetime import datetime

from app.utils.nutrition_utils import check_nutrition_exists, fetch_nutrition
from app.utils.product_utils import generate_product_barcode, check_existing_product

from app.schemas.product_schema import (
    AddProductRequest,
    ProductListResponse,
    UpdateProductRequest,
)

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

    product_barcode = generate_product_barcode(product_name)

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
        "addedAt": datetime.utcnow().isoformat(),
    }

    new_nutrition = Nutrition(**nutrition_data)
    db.add(new_nutrition)
    db.commit()
    db.refresh(new_nutrition)

    product_data = {
        "name": product_name,
        "category": category,
        "barcode": product_barcode if product_barcode else "N/A",
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


@router.get("/inventory/list", response_model=ProductListResponse)
def get_products(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Query(None, description="Filter products by name"),
):
    access_token = request.state.user

    print(f"Access Token: {access_token}")
    if name:
        products = db.query(Product).filter(Product.name.ilike(f"%{name}%")).all()
    else:
        products = db.query(Product).all()

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
                "barcode": product.barcode,
                "nutrition": nutrition,
            }
        )

    return {"products": result}


@router.put("/inventory/update/{product_id}")
def update_product(
    product_id: str,
    product: UpdateProductRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    access_token = request.state.user
    user_id = access_token.get("userId")

    existing_product = check_existing_product(product_id, db)

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} does not exist.",
        )

    if existing_product.id != product_id:
        raise HTTPException(
            status_code=400,
            detail=f"Product ID mismatch. Expected {existing_product.id}.",
        )

    if (
        existing_product.name.lower() == product.name.lower()
        or existing_product.category == product.category
    ):
        raise HTTPException(
            status_code=400,
            detail="No changes detected. Please provide new values for name or category.",
        )

    existing_product.name = (
        product.name.title() if product.name else existing_product.name
    )
    existing_product.category = (
        product.category if product.category else existing_product.category
    )
    existing_product.barcode = (
        product.barcode if product.barcode else existing_product.barcode
    )
    existing_product.updatedAt = datetime.utcnow().isoformat()

    db.commit()
    db.refresh(existing_product)

    return {
        "message": "Product updated successfully",
        "productId": existing_product.id,
        "name": existing_product.name.title(),
    }


@router.delete("/inventory/delete/{product_id}")
def delete_product(product_id: str, request: Request, db: Session = Depends(get_db)):
    access_token = request.state.user
    user_id = access_token.get("userId")

    existing_product = check_existing_product(product_id, db)

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} does not exist.",
        )

    # Check if the product is associated with any user products
    # Delete if it exists to avoid foreign key constraint issues
    db.query(UserProduct).filter(UserProduct.productId == product_id).delete()
    db.commit()

    db.delete(existing_product)
    db.commit()

    return {"message": "Product deleted successfully"}
