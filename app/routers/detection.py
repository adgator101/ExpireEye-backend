from fastapi import APIRouter, UploadFile, File, HTTPException, Request
import shutil
import os
from app.services.yolo_service import detect_objects
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/detect")
async def detect_image(request: Request, file: UploadFile = File(...)):
    access_token = request.state.user
    user_id = access_token.get("userId")

    logger.info("Received detection request from user ID: %s", user_id)
    file_location = os.path.join(UPLOAD_FOLDER, str(file.filename))
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = detect_objects(file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result
