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
    db.close()
    return {
        "notifications": [
            {
                "id": notification.id,
                "type": notification.type,
                "message": notification.message,
                "createdAt": notification.created_at,
                "isRead": notification.read,
            }
            for notification in notifications
        ]
    }


@router.post("/mark-read/{notification_id}")
def mark_notification_as_read(notification_id: str, db: Session = Depends(get_db)):
    notification = (
        db.query(Notification).filter(Notification.id == notification_id).first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.read = True
    db.commit()
    db.refresh(notification)
    db.close()
    return {"message": "Notification marked as read"}
