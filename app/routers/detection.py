from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
from app.services.yolo_service import detect_objects

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_FOLDER, str(file.filename))
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = detect_objects(file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result
