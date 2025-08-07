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
            await websocket.send_text(
                json.dumps({"message": f"Notification received: {data}"})
            )
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user {user_id}")
        if user_id in notification_connections:
            del notification_connections[user_id]


async def add_notification_to_db(
    user_id: str,
    message: str,
    type: str,
    db: Session,
):
    print("Hi")

    new_notification = Notification(
        userId=user_id,
        message=message,
        type=type,
        created_at=datetime.utcnow().isoformat(),
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    print("Notification added to DB:", new_notification)
