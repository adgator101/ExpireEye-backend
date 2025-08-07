# from sqlalchemy.orm import Session
from app.models.user_product import UserProduct
from app.models.product_model import Product
from app.services.notification_service import (
    send_notification_to_user,
    add_notification_to_db,
)

from datetime import datetime

from app.db.session import get_db


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
        notification_message = {
            "type": "product_expiration",
            "message": f"Product {product_details.name} has expired",
            "productName": product_details.name,
            "expiryDate": product.expiryDate,
            "timestamp": current_time,
        }
        print("Attempting to send notification to user", {product.userId})

        await send_notification_to_user(str(product.userId), notification_message)
        await add_notification_to_db(
            user_id=str(product.userId),
            message=f"Product {product_details.name} has expired",
            type="warning",
            db=db,
        )
        db.commit()
    db.close()
