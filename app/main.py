import os
import shutil
from fastapi import FastAPI, Request, WebSocket, Query, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from app.utils.jwt import decode_access_token
from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime


from app.routers.auth import router as auth_router
from app.routers.product import router as product_router
from app.routers.user_inventory import router as user_inventory_router
from app.routers.user import router as user_router
from app.routers.notification_router import router as notification_router
from app.routers.detection import router as detection_router
from app.routers.stats import router as stats_router

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import json
from app.services.notification_service import notification_websocket
from app.services.product_service import check_product_expiry, add_product_to_inventory

import shutil
import numpy as np
import cv2

app = FastAPI(root_path="/api", root_path_in_servers="/api")
scheduler = AsyncIOScheduler()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://expire-eye.vercel.app",
    "https://476d2d8e876e.ngrok-free.app",
]

notification_connections = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*", "GET", "POST", "PUT", "DELETE", "OPTIONS"],
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


@app.post("/qr", tags=["QR Code"])
async def decode_qr_code(request: Request, file: UploadFile = File(...)):
    access_token = request.state.user
    user_id = access_token.get("userId")

    image_bytes = await file.read()
    np_arr = np.frombuffer(image_bytes, np.uint8)

    print("Numpy array shape:", np_arr.shape)
    # Decode image using OpenCV
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    filename = (
        str(file.filename)
        if file.filename
        else f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    )
    file_path = os.path.join("uploads", filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Initialize QRCode detector
    detector = cv2.QRCodeDetector()

    # Detect and decode
    data, bbox, _ = detector.detectAndDecode(img)

    if bbox is not None and data:
        # await add_product_to_inventory(
        #     user_id=user_id,
        #     product={"productName": data, "category": "Uncategorized"},
        #     db=next(get_db()),
        # )
        return {"message": "QR Scanned successfully", "data": data}
    else:
        return {"error": "No QR code found in the image"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(product_router, prefix="/product", tags=["Product Inventory"])
app.include_router(user_inventory_router, prefix="/product", tags=["User Inventory"])
app.include_router(user_router, prefix="/user", tags=["User Profile"])
app.include_router(notification_router, prefix="/notification", tags=["Notifications"])
app.include_router(detection_router, prefix="/yolo", tags=["YOLO Detection"])
app.include_router(stats_router, prefix="/stats", tags=["Statistics"])


@app.on_event("startup")
async def startup_event():
    scheduler.add_job(check_product_expiry, CronTrigger(second="*/10"))
    scheduler.start()
    print("Scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


# @app.websocket("/ws")
# async def handshake(websocket: WebSocket, access_token: str = Query(None)):
#     if not access_token:
#         await websocket.send_text(json.dumps({"message": "Access token required"}))

#     await websocket.accept()
#     await websocket.send_text(json.dumps({"message": "Hi bro"}))

#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(json.dumps({"message": f"Message text was: {data}"}))


@app.websocket("/ws/notification")
async def websocket_notification_endpoint(
    websocket: WebSocket, access_token: str = Query(None)
):
    await notification_websocket(websocket, access_token)
