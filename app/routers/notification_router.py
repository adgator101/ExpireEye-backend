from fastapi import FastAPI, Request, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.notification_model import Notification
from app.models.user_product import UserProduct
from app.models.product_model import Product

router = APIRouter()


@router.get("/list")
def list_notifications(request: Request, db: Session = Depends(get_db)):
    access_token = request.state.user
    user_id = access_token.get("userId")

    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    notifications = db.query(Notification).filter(Notification.userId == user_id).all()

    if not notifications:
        return {"message": "No notifications found"}
    return {
        "notifications": [
            {
                "id": notification.id,
                "type": notification.type,
                "message": notification.message,
                "createdAt": notification.created_at,
            }
            for notification in notifications
        ]
    }
