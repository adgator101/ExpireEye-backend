from fastapi import APIRouter, Request, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.product_model import Product
from app.models.nutrition_model import Nutrition
from app.models.user_model import User
from app.schemas.product_schema import AddUserProductRequest, UpdateUserProductRequest
from app.models.user_product import UserProduct
from app.utils.product_utils import check_user_product_exists
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/user/add")
def add_user_product(
    product: AddUserProductRequest, request: Request, db: Session = Depends(get_db)
):
    access_token = request.state.user
    user_id = access_token.get("userId")

    product_name = product.name
    quantity = product.quantity
    expiry_date = (datetime.utcnow() + timedelta(seconds=20)).isoformat()
    notes = product.notes if product.notes else ""

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
        "status": "active",
        "notes": notes,
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
                    "nutrition": nutrition,
                    "addedAt": product.addedAt,
                    "status": product.status,
                    "notes": product.notes,
                    "updatedAt": product.updatedAt,
                }
            )

        else:
            user_product_data.append(
                {
                    "id": product.productId,
                    "name": "Unknown Product",
                    "category": "Unknown Category",
                    "expiryDate": product.expiryDate,
                    "nutrition": None,
                    "addedAt": product.addedAt,
                    "status": product.status,
                    "notes": product.notes,
                    "updatedAt": product.updatedAt,
                }
            )

    return {"products": user_product_data}


@router.put("/user/update/{product_id}")
def update_user_product(
    product_id: str,
    product: UpdateUserProductRequest,
    request: Request,
    db: Session = Depends(get_db),
):

    access_token = request.state.user
    user_id = access_token.get("userId")

    existing_user_product = check_user_product_exists(user_id, product_id, db)

    if not existing_user_product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} does not exist in user inventory.",
        )

    if product.quantity is None or product.expiryDate is None:
        raise HTTPException(
            status_code=400,
            detail="Both quantity and expiryDate are required for update.",
        )

    # Check if the new values are the same as existing ones
    if (
        existing_user_product.quantity == product.quantity
        and existing_user_product.expiryDate == product.expiryDate
    ):
        raise HTTPException(
            status_code=400,
            detail="No changes detected. Please provide new values for quantity or expiryDate.",
        )

    existing_user_product.quantity = (
        product.quantity if product.quantity else existing_user_product.quantity
    )
    existing_user_product.expiryDate = (
        product.expiryDate if product.expiryDate else existing_user_product.expiryDate
    )
    existing_user_product.notes = (
        product.notes if product.notes else existing_user_product.notes
    )

    existing_user_product.updatedAt = datetime.utcnow().isoformat()

    db.commit()
    db.refresh(existing_user_product)

    return {
        "message": "User product updated successfully",
        "productId": existing_user_product.productId,
        "quantity": existing_user_product.quantity,
        "expiryDate": existing_user_product.expiryDate,
        "notes": existing_user_product.notes,
    }


@router.delete("/user/delete/{product_id}")
def delete_user_product(
    product_id: str, request: Request, db: Session = Depends(get_db)
):
    access_token = request.state.user
    user_id = access_token.get("userId")

    existing_user_product = check_user_product_exists(user_id, product_id, db)

    if not existing_user_product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} does not exist in user inventory.",
        )

    db.delete(existing_user_product)
    db.commit()

    return {"message": "Product removed from user inventory successfully."}


@router.post("/user/scan", tags=["Scan User Product"])
async def scan_user_product(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    access_token = request.state.user
    user_id = access_token.get("userId")

    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated.")

    contents = await file.read()

    with open(f"app/static/{file.filename}", "wb") as f:
        f.write(contents)

    return {
        "message": "File processed successfully",
        "userId": user_id,
        "fileName": file.filename,
    }


@router.get("/{barcode}")
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.barcode == barcode).first()

    nutrition_data = (
        db.query(Nutrition).filter(Nutrition.id == product.nutritionId).first()
        if product
        else None
    )

    if nutrition_data:
        nutrition = {
            "protein": nutrition_data.protein,
            "carbohydrate": nutrition_data.carbohydrate,
            "fat": nutrition_data.fat,
            "fiber": nutrition_data.fiber,
            "calories": nutrition_data.calories,
        }

    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    return {
        "productName": product.name,
        "category": product.category,
        "nutrition": nutrition if nutrition else {},
    }
