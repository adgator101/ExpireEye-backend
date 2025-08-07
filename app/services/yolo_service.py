from ultralytics import YOLO
import cv2
import numpy as np
import os
from cloudinary.uploader import upload
import cloudinary
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

model = YOLO("best.pt")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_average_color(image):
    if image.size == 0:
        return None
    return np.mean(image, axis=(0, 1))


def detect_objects(file_path: str):
    img = cv2.imread(file_path)
    if img is None:
        raise ValueError(f"Could not load image at {file_path}")
    results = model.predict(source=img, conf=0.25)

    detections = []
    for result in results:
        boxes = result.boxes
        names = model.names

        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cropped = img[y1:y2, x1:x2]
                avg_color = get_average_color(cropped)
                if avg_color is not None:
                    avg_color_rgb = [int(c) for c in avg_color[::-1]]  # BGR → RGB
                else:
                    avg_color_rgb = None

                detections.append(
                    {
                        "name": names[cls_id],
                        "confidence": conf,
                        "bbox": [x1, y1, x2, y2],
                        "avg_color_rgb": avg_color_rgb,
                    }
                )

                # Draw bounding box and label
                label = f"{names[cls_id]} {conf:.2f}"
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    img,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (0, 255, 0),
                    8,
                )

    # If no detections found, you can handle it
    if not detections:
        return {
            "detections": [],
            "message": "No objects detected",
            "annotated_image_url": None,
        }

    # Get the highest confidence detection
    highest_confidence_detection = max(detections, key=lambda d: d["confidence"])

    # Save the annotated image to a temporary file
    annotated_image_path = os.path.join(UPLOAD_FOLDER, "annotated_image.jpg")
    cv2.imwrite(annotated_image_path, img)

    # Upload the annotated image to Cloudinary
    upload_result = upload(annotated_image_path)
    annotated_image_url = upload_result.get("secure_url")

    return {
        "detection": highest_confidence_detection,
        "annotated_image_url": annotated_image_url,
    }
