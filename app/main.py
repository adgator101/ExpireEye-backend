from fastapi import FastAPI, Request, WebSocket, Query
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from app.utils.jwt import decode_access_token
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import get_db
from app.models.user_product import UserProduct
from app.models.product_model import Product
from datetime import datetime


from app.routers.auth import router as auth_router
from app.routers.warehouse import router as product_router
from app.routers.user_inventory import router as user_inventory_router
from app.routers.user import router as user_router
from app.routers.detection import router as detection_router
from app.routers.stats import router as stats_router

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import json
import asyncio

app = FastAPI(root_path="/api", root_path_in_servers="/api")
scheduler = AsyncIOScheduler()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

notification_connections = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
)


@app.middleware("http")
async def access_token_middleware(request: Request, call_next):

    # Skip access token check for preflight requests
    if request.method == "OPTIONS":
        return await call_next(request)

    public_paths = [
        "/api/auth/login",
        "/api/auth/signup",
        "/api/status",
        "/docs",
        "/redoc",
        "/api/openapi.json",
    ]

    # Skip access token check for public paths
    if request.url.path in public_paths:
        return await call_next(request)

    # access_token = request.cookies.get("access_token")
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(
            status_code=401,
            content={"detail": "Authorization header missing or invalid."},
        )
    access_token = auth_header.split("Bearer ")[-1].strip()

    if not access_token:
        return JSONResponse(
            status_code=401,
            content={"detail": "Access token is missing or invalid."},
        )
    try:
        payload = decode_access_token(access_token)
        request.state.user = payload  # Store user info in request state

    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={"detail": "Access token is invalid."},
        )

    response = await call_next(request)
    return response


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    errors = exc.errors()
    custom_errors = [
        {
            "field": err["loc"][-1],
            "message": (
                "This field is required."
                if err["msg"] == "field required"
                else err["msg"]
            ),
        }
        for err in errors
    ]
    return JSONResponse(status_code=422, content={"errors": custom_errors})


@app.get("/status", tags=["Status"])
def status():
    return {"status": "OK", "message": "Server Is Running"}



app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(product_router, prefix="/product", tags=["Product Inventory"])
app.include_router(user_inventory_router, prefix="/product", tags=["User Inventory"])
app.include_router(user_router, prefix="/user", tags=["User Profile"])
app.include_router(detection_router, prefix="/yolo", tags=["YOLO Detection"])
app.include_router(stats_router, prefix="/stats", tags=["Statistics"])


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
        notification_message = {
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


@app.on_event("startup")
async def startup_event():
    scheduler.add_job(check_product_expiry, CronTrigger(second="*/10"))
    scheduler.start()
    print("Scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


@app.websocket("/ws")
async def handshake(websocket: WebSocket, access_token: str = Query(None)):
    if not access_token:
        await websocket.send_text(json.dumps({"message": "Access token required"}))

    await websocket.accept()
    await websocket.send_text(json.dumps({"message": "Hi bro"}))

    while True:
        data = await websocket.receive_text()
        await websocket.send_text(json.dumps({"message": f"Message text was: {data}"}))


@app.websocket("/ws/notification")
async def send_notification(websocket: WebSocket, access_token: str = Query(None)):
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

    while True:
        data = await websocket.receive_text()
        await websocket.send_text(
            json.dumps({"message": f"Notification received: {data}"})
        )
