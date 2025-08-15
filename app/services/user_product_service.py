from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user_product import UserProduct
from app.models.user_model import User
from app.models.product_model import Product
from app.models.nutrition_model import Nutrition

from app.utils.product_utils import check_user_product_exists
from datetime import datetime
from app.services.notification_service import (
    send_notification_to_user,
    add_notification_to_db,
)
from app.services.product_service import add_product_to_inventory


async def create_user_product(
    user_id: str,
    product_name: str,
    quantity: int,
    expiry_date: str,
    notes: str,
    is_scanned_product: bool,
    db: Session,
):
    exists_user = db.query(User).filter_by(id=user_id).first()

    if not exists_user:
        raise HTTPException(
            status_code=404, detail="User with the provided userId does not exist."
        )

    # if not product_name or not expiry_date:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="All fields are required: name, quantity, and expiryDate.",
    #     )

    product_exists = db.query(Product).filter(Product.name == product_name).first()

    if not product_exists:

        # If product does not exist, create it
        await add_product_to_inventory(
            user_id, {"productName": product_name, "category": "Uncategorized"}, db
        )
        # Query again to get the newly created product
        product_exists = db.query(Product).filter(Product.name == product_name).first()

    if product_exists:
        # Refresh to retrieve the newly created product data (id, nutrients)
        db.refresh(product_exists)

    product_id = product_exists.id if product_exists else None

    new_product = {
        "userId": user_id,
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

    if is_scanned_product:
        product_nutrition = (
            db.query(Nutrition)
            .filter(Nutrition.id == product_exists.nutritionId)
            .first()
        )
        await add_notification_to_db(
            user_id=user_id,
            message="Product Scanned successfully",
            productName=product_name,
            type="info",
            db=db,
        )
        await send_notification_to_user(
            user_id,
            {
                "type": "Product_Scanned",
                "message": "Product Scanned successfully",
                "data": {
                    "name": product_name,  # Access the "name" key
                    # "confidence": detection[
                    #     "confidence"
                    # ],  # Access the "confidence" key
                    "confidence": 0.9,  # Placeholder confidence value
                    "quantity": quantity,
                    "notes": "Detected by YOLO with 90% confidence",
                    "expiryDate": expiry_date,
                    "nutrition": {
                        "energy_kcal": product_nutrition.energy_kcal,
                        "carbohydrate": product_nutrition.carbohydrate,
                        "total_sugars": product_nutrition.total_sugars,
                        "fiber": product_nutrition.fiber,
                        "protein": product_nutrition.protein,
                        "saturated_fat": product_nutrition.saturated_fat,
                        "vitamin_a": product_nutrition.vitamin_a,
                        "vitamin_c": product_nutrition.vitamin_c,
                        "potassium": product_nutrition.potassium,
                        "iron": product_nutrition.iron,
                        "calcium": product_nutrition.calcium,
                        "sodium": product_nutrition.sodium,
                        "cholesterol": product_nutrition.cholesterol,
                    },
                },
            },
        )

    return {
        "message": "New Product added to user inventory successfully",
        "productId": new_user_product.productId,
        "name": product_name,
        "quantity": quantity,
        "expiryDate": expiry_date,
    }


async def get_user_product_list(user_id: str, db: Session):
    user_products = (
        db.query(UserProduct)
        .filter(UserProduct.userId == user_id)
        .order_by(UserProduct.addedAt.desc())
        .all()
    )

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
                    "energy_kcal": nutrition_data.energy_kcal,
                    "carbohydrate": nutrition_data.carbohydrate,
                    "total_sugars": nutrition_data.total_sugars,
                    "fiber": nutrition_data.fiber,
                    "protein": nutrition_data.protein,
                    "saturated_fat": nutrition_data.saturated_fat,
                    "vitamin_a": nutrition_data.vitamin_a,
                    "vitamin_c": nutrition_data.vitamin_c,
                    "potassium": nutrition_data.potassium,
                    "iron": nutrition_data.iron,
                    "calcium": nutrition_data.calcium,
                    "sodium": nutrition_data.sodium,
                    "cholesterol": nutrition_data.cholesterol,
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
    return user_product_data


async def update_user_product_data(
    user_id: str, product_id: str, product: dict, db: Session
):

    existing_user_product = check_user_product_exists(user_id, product_id, db)

    if not existing_user_product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} does not exist in user inventory.",
        )

    if product.get("quantity") is None or product.get("expiryDate") is None:
        raise HTTPException(
            status_code=400,
            detail="Both quantity and expiryDate are required for update.",
        )

    # Check if the new values are the same as existing ones
    if existing_user_product.quantity == product.get(
        "quantity"
    ) and existing_user_product.expiryDate == product.get("expiryDate"):
        raise HTTPException(
            status_code=400,
            detail="No changes detected. Please provide new values for quantity or expiryDate.",
        )

    existing_user_product.quantity = (
        product.get("quantity")
        if product.get("quantity")
        else existing_user_product.quantity
    )
    existing_user_product.expiryDate = (
        product.get("expiryDate")
        if product.get("expiryDate")
        else existing_user_product.expiryDate
    )
    existing_user_product.notes = (
        product.get("notes") if product.get("notes") else existing_user_product.notes
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


async def delete_user_product_data(user_id: str, product_id: str, db: Session):
    existing_user_product = check_user_product_exists(user_id, product_id, db)

    if not existing_user_product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} does not exist in user inventory.",
        )

    db.delete(existing_user_product)
    db.commit()

    return {"message": "Product removed from user inventory successfully."}


async def add_mass_user_products(
    user_id: str,
    products: list,
    db: Session,
):
    """
    Adds multiple products to a user's inventory.
    Each product should be a dict with: productName, quantity, expiryDate, notes, is_scanned_product.
    Returns a summary of successes and failures.
    """
    results = {"success": [], "failed": []}

    exists_user = db.query(User).filter_by(id=user_id).first()
    if not exists_user:
        return {"success": [], "failed": [{"reason": "User does not exist"}]}

    for product in products:
        try:
            # If using Pydantic models, use attribute access; if dicts, use .get()
            product_name = getattr(product, "productName", None) or product.get(
                "productName"
            )
            quantity = getattr(product, "quantity", None) or product.get("quantity")
            expiry_date = getattr(product, "expiryDate", None) or product.get(
                "expiryDate"
            )
            notes = getattr(product, "notes", None) or product.get("notes", "")
            is_scanned_product = getattr(
                product, "is_scanned_product", None
            ) or product.get("is_scanned_product", False)

            if not product_name or not quantity or not expiry_date:
                results["failed"].append(
                    {
                        "product": {
                            "productName": product_name,
                            "quantity": quantity,
                            "expiryDate": expiry_date,
                        },
                        "reason": "Missing required fields",
                    }
                )
                continue

            res = await create_user_product(
                user_id=user_id,
                product_name=product_name,
                quantity=quantity,
                expiry_date=expiry_date,
                notes=notes,
                is_scanned_product=is_scanned_product,
                db=db,
            )
            results["success"].append(res)
        except Exception as e:
            results["failed"].append(
                {
                    "product": {
                        "productName": product_name,
                        "quantity": quantity,
                        "expiryDate": expiry_date,
                    },
                    "reason": str(e),
                }
            )

    return results
