from fastapi import APIRouter, Request, HTTPException, Depends, File, UploadFile, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.product_model import Product
from app.models.nutrition_model import Nutrition
from app.models.user_model import User
from app.schemas.product_schema import AddUserProductRequest, UpdateUserProductRequest
from app.models.user_product import UserProduct
from app.utils.product_utils import (
    get_product_name_from_barcode,
    get_product_shelf_life,
)
from datetime import datetime, timedelta
from app.models.notification_model import Notification
from app.services.user_product_service import (
    create_user_product,
    get_user_product_list,
    update_user_product_data,
    delete_user_product_data,
    add_mass_user_products,
)

router = APIRouter()


@router.post("/user/add")
async def add_user_product(
    product: AddUserProductRequest,
    request: Request,
    barcode: str = Query(None, description="Barcode of the product"),
    db: Session = Depends(get_db),
):
    if barcode:
        product_name = get_product_name_from_barcode(barcode, db)
        if not product_name:
            raise HTTPException(
                status_code=404,
                detail="Product not found for the provided barcode",
            )
        quantity = 1
        notes = f"Scanned Via Barcode with Code {barcode}"
        is_scanned_product = True
        expiry_date = (datetime.utcnow() + timedelta(seconds=20)).isoformat()
    else:
        product_name = product.name
        quantity = product.quantity
        notes = product.notes if product.notes else ""
        is_scanned_product = product.isScannedProduct
        if is_scanned_product:
            shelf_life = get_product_shelf_life(product_name)
            expiry_date = (datetime.utcnow() + timedelta(days=shelf_life)).isoformat()
        else:
            expiry_date = (datetime.utcnow() + timedelta(seconds=10)).isoformat()
    access_token = request.state.user
    user_id = access_token.get("userId")
    # expiry_date = product.expiryDate
    print("is_scanned_product:", is_scanned_product)

    result = await create_user_product(
        user_id=user_id,
        product_name=product_name,
        quantity=quantity,
        expiry_date=expiry_date,
        notes=notes,
        is_scanned_product=is_scanned_product,
        db=db,
    )
    return result


@router.get("/user/list")
async def get_user_products(request: Request, db: Session = Depends(get_db)):
    access_token = request.state.user
    user_id = access_token.get("userId")

    result = await get_user_product_list(user_id, db)
    return {"products": result}


@router.put("/user/update/{product_id}")
async def update_user_product(
    product_id: str,
    product: UpdateUserProductRequest,
    request: Request,
    db: Session = Depends(get_db),
):

    access_token = request.state.user
    user_id = access_token.get("userId")

    result = await update_user_product_data(
        user_id,
        product_id,
        {
            "quantity": product.quantity,
            "expiryDate": product.expiryDate,
            "notes": product.notes,
        },
        db,
    )

    return result


@router.delete("/user/delete/{product_id}")
async def delete_user_product(
    product_id: str, request: Request, db: Session = Depends(get_db)
):
    access_token = request.state.user
    user_id = access_token.get("userId")

    result = await delete_user_product_data(user_id, product_id, db)

    return result


@router.post("/user/add-mass")
async def add_mass_user_products_endpoint(
    request: Request, body: dict, db: Session = Depends(get_db)
):
    access_token = request.state.user
    user_id = access_token.get("userId")
    products = body.get("products", [])
    result = await add_mass_user_products(user_id=user_id, products=products, db=db)
    return result
