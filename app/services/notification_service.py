from fastapi import WebSocket, Query, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from fastapi.websockets import WebSocketDisconnect

from app.utils.jwt import decode_access_token

from app.utils.jwt import decode_access_token
from datetime import datetime

from app.models.notification_model import Notification
import json

notification_connections = {}


async def send_notification_to_user(user_id: str, message: dict):
    print(f"Attempting to send notification to user: {user_id}")
    print(f"Active connections: {list(notification_connections.keys())}")

    if user_id in notification_connections:
        try:
            print("Sending notification")
            await notification_connections[user_id].send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending notification to user {user_id}: {e}")
            # Remove disconnected connection
            del notification_connections[user_id]


async def notification_websocket(websocket: WebSocket, access_token: str = Query(None)):
    if not access_token:
        await websocket.close(code=1008, reason="Access token required")

    await websocket.accept()

    payload = decode_access_token(access_token)
    user_id = payload.get("userId")

    notification_connections[user_id] = websocket
    db = next(get_db())
    # pending_notifications = (
    #     db.query(Notification)
    #     .filter(
    #         Notification.userId == user_id,
    #         Notification.read == False,  # If you have a 'read' column
    #     )
    #     .all()
    # )
    # notification_types = {"info": "Product_Scanned", "warning": "product_expiration"}
    # for notification in pending_notifications:
    #     notif_type = (
    #         notification.type.value
    #         if hasattr(notification.type, "value")
    #         else str(notification.type)
    #     )
    #     try:
    #         await websocket.send_text(
    #             json.dumps(
    #                 {
    #                     "id": notification.id,
    #                     "message": notification.message,
    #                     "type": notification_types.get(notif_type, notif_type),
    #                     "productName": notification.productName,
    #                     "expiryDate": notification.created_at,
    #                 }
    #             )
    #         )
    #         notification = (
    #             db.query(Notification)
    #             .filter(Notification.id == notification.id)
    #             .first()
    #         )
    #         if notification:
    #             notification.read = True
    #             db.commit()
    #             db.refresh(notification)
    #             print(f"Notification {notification_id} marked as read")
    #     except Exception as e:
    #         print(f"Error sending notification to user {user_id}: {e}")
    #         continue

    await websocket.send_text(
        json.dumps(
            {
                "type": "CONNECTION_ESTABLISHED",
                "message": "Notification WebSocket connected",
                "userId": user_id,
            }
        )
    )
    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)

            if data_json.get("action") == "mark_read" and data_json.get("id"):
                print("Marking notification as read")
                notification_id = data_json["id"]
                notification = (
                    db.query(Notification)
                    .filter(Notification.id == notification_id)
                    .first()
                )
                if notification:
                    notification.read = True
                    db.commit()

            if data == "PING":
                await websocket.send_text(json.dumps({"type": "pong"}))
            else:
                await websocket.send_text(
                    json.dumps({"message": f"Notification received: {data}"})
                )
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user {user_id}")
        db.close()
        if user_id in notification_connections:
            del notification_connections[user_id]


async def add_notification_to_db(
    user_id: str,
    productName: str,
    message: str,
    type: str,
    db: Session,
):

    new_notification = Notification(
        userId=user_id,
        message=message,
        type=type,
        productName=productName,
        read=False,
        created_at=datetime.utcnow().isoformat(),
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    print("Notification added to DB:", new_notification)
    return new_notification
