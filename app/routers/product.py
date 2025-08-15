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

from app.utils.product_utils import check_existing_product

from app.schemas.product_schema import (
    AddProductRequest,
    ProductListResponse,
    UpdateProductRequest,
    MassProductRequest
)

from app.services.product_service import (
    add_product_to_inventory,
    get_inventory_product_list,
    update_inventory_product_data,
    delete_inventory_product_data,
    add_mass_products_to_inventory,
)

load_dotenv()


router = APIRouter()

API_KEY = os.getenv("API_KEY")


@router.post("/inventory/add")
async def add_product(
    product: AddProductRequest, request: Request, db: Session = Depends(get_db)
):
    access_token = request.state.user
    user_id = access_token.get("userId")

    add_product_result = await add_product_to_inventory(
        user_id=user_id,
        product={"productName": product.productName, "category": product.category},
        db=db,
    )

    return add_product_result


@router.get("/inventory/list", response_model=ProductListResponse)
async def get_products(
    db: Session = Depends(get_db),
    name: str = Query(None, description="Filter products by name"),
):

    get_products_result = await get_inventory_product_list(name, db)
    return get_products_result


@router.put("/inventory/update/{product_id}")
async def update_product(
    product_id: str,
    product: UpdateProductRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    access_token = request.state.user
    user_id = access_token.get("userId")
    print("Product Category:", product.category)
    update_inventory_product_result = await update_inventory_product_data(
        product_id=product_id,
        product={
            "name": product.name,
            "category": product.category,
            "barcode": product.barcode,
        },
        db=db,
    )

    return {
        "message": "Product updated successfully",
        "productId": update_inventory_product_result.get("productId"),
        "name": update_inventory_product_result.get("name"),
    }


@router.delete("/inventory/delete/{product_id}")
async def delete_product(
    product_id: str, request: Request, db: Session = Depends(get_db)
):
    access_token = request.state.user
    user_id = access_token.get("userId")
    delete_inventory_product_result = await delete_inventory_product_data(
        product_id=product_id, db=db
    )

    return delete_inventory_product_result


@router.get("/barcodes")
def get_products_barcode(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    result = [
        {
            "productName": product.name,
            "barcode": product.barcode,
        }
        for product in products
    ]
    return {"products": result}


@router.post("/inventory/add-mass")
async def add_mass_products(
    request: Request,
    body: MassProductRequest,
    db: Session = Depends(get_db)
):
    access_token = request.state.user
    user_id = access_token.get("userId")
    result = await add_mass_products_to_inventory(
        user_id=user_id, products=body.products, db=db
    )
    return result