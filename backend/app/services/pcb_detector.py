# ---------------------------------------------------------
# PCB Defect Detection Service
# OpenCV + YOLOv8
# ---------------------------------------------------------

from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
from ultralytics import YOLO


# ---------------------------------------------------------
# Project root directory
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------
# YOLO model path
# ---------------------------------------------------------

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "universal_pcb_yolov8s"
    / "best.pt"
)


# ---------------------------------------------------------
# Prediction directory
# ---------------------------------------------------------

PREDICTION_DIR = (
    PROJECT_ROOT
    / "backend"
    / "predictions"
)

PREDICTION_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Load trained YOLO model
# ---------------------------------------------------------

print(f"Loading YOLO model from: {MODEL_PATH}")

model = YOLO(str(MODEL_PATH))

print("YOLO model loaded successfully.")


# ---------------------------------------------------------
# PCB prediction function
# ---------------------------------------------------------

def predict_pcb(
    image_path: str,
    confidence: float = 0.25
):

    # -----------------------------------------------------
    # Convert path
    # -----------------------------------------------------

    image_path = Path(image_path)


    # -----------------------------------------------------
    # Check image file
    # -----------------------------------------------------

    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )


    # -----------------------------------------------------
    # Read image using OpenCV
    # -----------------------------------------------------

    image = cv2.imread(
        str(image_path)
    )


    # -----------------------------------------------------
    # Validate OpenCV image
    # -----------------------------------------------------

    if image is None:

        raise ValueError(
            "OpenCV could not read the image."
        )


    # -----------------------------------------------------
    # Get image dimensions
    # -----------------------------------------------------

    height, width = image.shape[:2]

    print(
        f"OpenCV image size: {width}x{height}"
    )


    # -----------------------------------------------------
    # Create unique prediction folder
    # -----------------------------------------------------

    run_id = (
        f"{image_path.stem}_{uuid4().hex[:8]}"
    )

    output_dir = (
        PREDICTION_DIR / run_id
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    # -----------------------------------------------------
    # Run YOLO prediction
    # -----------------------------------------------------

    results = model.predict(

        source=str(image_path),

        conf=confidence,

        save=True,

        project=str(PREDICTION_DIR),

        name=run_id,

        exist_ok=True,

        verbose=False
    )


    # -----------------------------------------------------
    # Get first result
    # -----------------------------------------------------

    result = results[0]


    # -----------------------------------------------------
    # Extract detections
    # -----------------------------------------------------

    detections = []


    if result.boxes is not None:

        for box in result.boxes:

            class_id = int(
                box.cls[0]
            )

            confidence_score = float(
                box.conf[0]
            )

            x1, y1, x2, y2 = (
                box.xyxy[0].tolist()
            )

            class_name = (
                model.names[class_id]
            )


            detections.append({

                "class_id": class_id,

                "class_name": class_name,

                "confidence": round(
                    confidence_score,
                    4
                ),

                "bbox": {

                    "x1": round(x1, 2),

                    "y1": round(y1, 2),

                    "x2": round(x2, 2),

                    "y2": round(y2, 2)
                }
            })


    # -----------------------------------------------------
    # Determine inspection status
    # -----------------------------------------------------

    if detections:

        status = "defective"

    else:

        status = "normal"


    # -----------------------------------------------------
    # Prediction image path
    # -----------------------------------------------------

    prediction_image = (
        output_dir / image_path.name
    )


    # -----------------------------------------------------
    # Return result
    # -----------------------------------------------------

    return {

        "status": status,

        "total_defects": len(
            detections
        ),

        "defects": detections,

        "original_image": str(
            image_path
        ),

        "prediction_image": str(
            prediction_image
        )
    }


# ---------------------------------------------------------
# Image Hashing for Duplicate Detection
# ---------------------------------------------------------

def compute_phash(image_path: str) -> str:
    """
    Computes a perceptual hash (pHash) for the given image using OpenCV.
    This hash can be used to compare visual similarity between images.
    """
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        return ""
    
    # Resize to 32x32
    resized = cv2.resize(image, (32, 32))
    
    # Compute Discrete Cosine Transform (DCT)
    dct = cv2.dct(np.float32(resized))
    
    # Take the top-left 8x8 (low frequencies)
    dct_lowfreq = dct[:8, :8]
    
    # Compute median (excluding the first DC term)
    med = np.median(dct_lowfreq[1:])
    
    # Create binary hash
    diff = dct_lowfreq > med
    
    # Convert to 64-bit hex string
    return hex(int("".join(["1" if b else "0" for b in diff.flatten()]), 2))[2:].zfill(16)

def hamming_distance(hash1: str, hash2: str) -> int:
    """Calculates the Hamming distance between two hex string hashes."""
    if not hash1 or not hash2:
        return 999
    return bin(int(hash1, 16) ^ int(hash2, 16)).count('1')