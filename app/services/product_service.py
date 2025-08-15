from fastapi import HTTPException

from sqlalchemy.orm import Session
from app.services.notification_service import (
    send_notification_to_user,
    add_notification_to_db,
)

from datetime import datetime
from app.db.session import get_db

from app.utils.nutrition_utils import check_nutrition_exists, fetch_nutrition
from app.utils.product_utils import generate_product_barcode, check_existing_product
from app.models.nutrition_model import Nutrition
from app.models.user_model import User
from app.models.user_product import UserProduct
from app.models.product_model import Product
from app.models.notification_model import Notification


async def check_product_expiry():

    db = next(get_db())  # Get db session through iterator
    current_time = datetime.utcnow().isoformat()

    expired_products = (
        db.query(UserProduct)
        .filter(
            (UserProduct.expiryDate < current_time) & (UserProduct.status == "active")
        )
        .all()
    )
    # # Send test notification to all connected users
    # test_message = {
    #     "type": "test",
    #     "message": "Test notification",
    #     "timestamp": current_time,
    # }
    # for user_id in notification_connections.keys():
    #     await send_notification_to_user(user_id, test_message)

    for product in expired_products:
        product_details = (
            db.query(Product).filter(Product.id == product.productId).first()
        )
        print(f"Found expired product: {product.productId}")
        product.status = "expired"
        product.updatedAt = current_time
        db.add(product)

        # notification = Notification(
        #     userId=product.userId,
        #     productName=product_details.name,
        #     message=f"Product {product_details.name} has expired",
        #     type="warning",
        #     read=False,
        #     created_at=current_time,
        # )
        notification = await add_notification_to_db(
            user_id=str(product.userId),
            productName=product_details.name,
            message=f"Product {product_details.name} has expired",
            type="warning",
            db=db,
        )

        notification_message = {
            "id": notification.id,
            "type": "product_expiration",
            "message": f"Product {product_details.name} has expired",
            "productName": product_details.name,
            "expiryDate": product.expiryDate,
            "timestamp": current_time,
        }
        print("Attempting to send notification to user", {product.userId})
        await send_notification_to_user(str(product.userId), notification_message)
        db.commit()
    db.close()


async def add_product_to_inventory(user_id: str, product: dict, db: Session):

    # product_name = product.productName
    # category = product.category
    product_name = product["productName"]
    category = product["category"]
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

    food_nutrition = fetch_nutrition(product_name)

    nutrition_data = {
        "energy_kcal": check_nutrition_exists("Energy (KCAL)", food_nutrition),
        "carbohydrate": check_nutrition_exists(
            "Carbohydrate, by difference (G)", food_nutrition
        ),
        "total_sugars": check_nutrition_exists("Total Sugars (G)", food_nutrition),
        "fiber": check_nutrition_exists("Fiber, total dietary (G)", food_nutrition),
        "protein": check_nutrition_exists("Protein (G)", food_nutrition),
        "saturated_fat": check_nutrition_exists(
            "Fatty acids, total saturated (G)", food_nutrition
        ),
        "vitamin_a": check_nutrition_exists("Vitamin A, IU (IU)", food_nutrition),
        "vitamin_c": check_nutrition_exists(
            "Vitamin C, total ascorbic acid (MG)", food_nutrition
        ),
        "potassium": check_nutrition_exists("Potassium, K (MG)", food_nutrition),
        "iron": check_nutrition_exists("Iron, Fe (MG)", food_nutrition),
        "calcium": check_nutrition_exists("Calcium, Ca (MG)", food_nutrition),
        "sodium": check_nutrition_exists("Sodium, Na (MG)", food_nutrition),
        "cholesterol": check_nutrition_exists("Cholesterol (MG)", food_nutrition),
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


async def get_inventory_product_list(name: str, db: Session):

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
                "energy_kcal": nutrition.energy_kcal,
                "carbohydrate": nutrition.carbohydrate,
                "protein": nutrition.protein,
                "fiber": nutrition.fiber,
                "total_sugars": nutrition.total_sugars,
                "saturated_fat": nutrition.saturated_fat,
                "vitamin_a": nutrition.vitamin_a,
                "vitamin_c": nutrition.vitamin_c,
                "potassium": nutrition.potassium,
                "iron": nutrition.iron,
                "calcium": nutrition.calcium,
                "sodium": nutrition.sodium,
                "cholesterol": nutrition.cholesterol,
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


async def update_inventory_product_data(product_id: str, product: dict, db: Session):

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
    # print("Existing Product Category:", existing_product.category)
    if existing_product.name == product.get(
        "name", ""
    ) or existing_product.category == product.get("category", ""):
        raise HTTPException(
            status_code=400,
            detail="No changes detected. Please provide new values for name or category.",
        )

    existing_product.name = (
        product.get("name", "").title()
        if product.get("name", "")
        else existing_product.name
    )
    existing_product.category = (
        product.get("category", "")
        if product.get("category", "")
        else existing_product.category
    )
    existing_product.barcode = (
        product.get("barcode", "")
        if product.get("barcode", "")
        else existing_product.barcode
    )
    existing_product.updatedAt = datetime.utcnow().isoformat()

    db.commit()
    db.refresh(existing_product)

    return {product_id: existing_product.id, "name": existing_product.name.title()}


async def delete_inventory_product_data(product_id: str, db: Session):

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


async def add_mass_products_to_inventory(user_id: str, products: list, db: Session):
    """
    Adds multiple products to the inventory for a user.
    Returns a summary of successes and failures.
    """
    results = {"success": [], "failed": []}

    for product in products:
        try:
            # Use attribute access for Pydantic objects
            product_name = product.productName
            category = product.category

            if not product_name or not user_id:
                results["failed"].append({
                    "product": {"productName": product_name, "category": category},
                    "reason": "Missing productName or userId"
                })
                continue

            if len(product_name) < 3:
                results["failed"].append({
                    "product": {"productName": product_name, "category": category},
                    "reason": "Product name must be at least 3 characters long"
                })
                continue

            exists_user = db.query(User).filter_by(id=user_id).first()
            if not exists_user:
                results["failed"].append({
                    "product": {"productName": product_name, "category": category},
                    "reason": "User does not exist"
                })
                continue

            product_barcode = generate_product_barcode(product_name)
            food_nutrition = fetch_nutrition(product_name)
            nutrition_data = {
                "energy_kcal": check_nutrition_exists("Energy (KCAL)", food_nutrition),
                "carbohydrate": check_nutrition_exists("Carbohydrate, by difference (G)", food_nutrition),
                "total_sugars": check_nutrition_exists("Total Sugars (G)", food_nutrition),
                "fiber": check_nutrition_exists("Fiber, total dietary (G)", food_nutrition),
                "protein": check_nutrition_exists("Protein (G)", food_nutrition),
                "saturated_fat": check_nutrition_exists("Fatty acids, total saturated (G)", food_nutrition),
                "vitamin_a": check_nutrition_exists("Vitamin A, IU (IU)", food_nutrition),
                "vitamin_c": check_nutrition_exists("Vitamin C, total ascorbic acid (MG)", food_nutrition),
                "potassium": check_nutrition_exists("Potassium, K (MG)", food_nutrition),
                "iron": check_nutrition_exists("Iron, Fe (MG)", food_nutrition),
                "calcium": check_nutrition_exists("Calcium, Ca (MG)", food_nutrition),
                "sodium": check_nutrition_exists("Sodium, Na (MG)", food_nutrition),
                "cholesterol": check_nutrition_exists("Cholesterol (MG)", food_nutrition),
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

            results["success"].append({
                "productId": new_product.id,
                "name": new_product.name.title()
            })
        except Exception as e:
            db.rollback()
            results["failed"].append({
                "product": {"productName": product_name, "category": category},
                "reason": str(e)
            })

    return results