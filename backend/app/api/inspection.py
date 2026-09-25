# ---------------------------------------------------------
# PCB Inspection API
# Handles image upload and camera frame inspection
# ---------------------------------------------------------

from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    Form
)
from typing import Optional

from backend.app.db.database import (
    get_or_create_product,
    save_inspection
)

from backend.app.services.pcb_detector import (
    predict_pcb,
    compute_phash
)

import cv2
import numpy as np

import cv2
import numpy as np


# ---------------------------------------------------------
# Create router
# ---------------------------------------------------------

router = APIRouter(
    prefix="/api/inspection",
    tags=["PCB Inspection"]
)

from backend.app.db.database import get_product_by_barcode, inspections_collection, find_matching_pcb_by_hash

@router.get("/barcode/{barcode}")
async def fetch_pcb_by_barcode(barcode: str):
    product, is_new = get_or_create_product(barcode)
    
    if is_new:
        return {
            "message": "New PCB registered",
            "product": product
        }
        
    latest_inspection = inspections_collection.find_one(
        {"product_id": product["product_id"]}, 
        sort=[("created_at", -1)]
    )
    
    response = {
        "message": "Existing PCB details loaded",
        "product": product
    }
    
    if latest_inspection:
        if "_id" in latest_inspection:
            del latest_inspection["_id"]
        response["latest_inspection"] = latest_inspection
        
    return response


# ---------------------------------------------------------
# Project directories
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

UPLOAD_DIR = (
    PROJECT_ROOT
    / "backend"
    / "uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# PCB prediction API
# ---------------------------------------------------------

@router.post("/predict")
async def inspect_pcb(
    file: UploadFile = File(...),
    product_id: Optional[str] = Form(None),
    inspection_request_id: str = Form(...)
):

    # -----------------------------------------------------
    # Allowed image extensions
    # -----------------------------------------------------

    allowed_extensions = {

        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }


    # -----------------------------------------------------
    # Get file extension
    # -----------------------------------------------------

    original_extension = Path(
        file.filename or ""
    ).suffix.lower()


    # -----------------------------------------------------
    # Validate extension
    # -----------------------------------------------------

    if original_extension not in allowed_extensions:

        raise HTTPException(

            status_code=400,

            detail=(
                "Only JPG, JPEG, PNG, BMP "
                "and WEBP images are allowed."
            )
        )


    # -----------------------------------------------------
    # Generate unique filename
    # -----------------------------------------------------

    unique_filename = (
        f"{uuid4().hex}"
        f"{original_extension}"
    )


    image_path = (
        UPLOAD_DIR
        / unique_filename
    )


    # -----------------------------------------------------
    # Read uploaded file
    # -----------------------------------------------------

    file_data = await file.read()

    # -----------------------------------------------------
    # Save image
    # -----------------------------------------------------

    with open(
        image_path,
        "wb"
    ) as image_file:

        image_file.write(
            file_data
        )

    # -----------------------------------------------------
    # Check for duplicate PCB using image hash
    # -----------------------------------------------------
    
    image_hash = compute_phash(str(image_path))
    existing_inspection, existing_product = find_matching_pcb_by_hash(image_hash)
    
    if existing_inspection and existing_product:
        # Match found, delete the newly uploaded image to save space
        if image_path.exists():
            image_path.unlink()
            
        return {
            "message": "Existing PCB detected",
            "filename": file.filename,
            "status": existing_inspection.get("status", "unknown"),
            "total_defects": existing_inspection.get("total_defects", 0),
            "defects": existing_inspection.get("defects", []),
            "prediction_image": existing_inspection.get("prediction_image", ""),
            "product": existing_product,
            "inspection_method": existing_inspection.get("inspection_method", "unknown"),
            "created_at": existing_inspection.get("created_at")
        }

    # -----------------------------------------------------
    # Run YOLO prediction
    # -----------------------------------------------------

    try:

        prediction = predict_pcb(
            str(image_path)
        )

    except Exception as error:

        if image_path.exists():

            image_path.unlink()


        raise HTTPException(

            status_code=500,

            detail=(
                f"PCB prediction failed: {error}"
            )
        )


    # -----------------------------------------------------
    # Convert prediction path to URL
    # -----------------------------------------------------

    prediction_path = Path(
        prediction["prediction_image"]
    )

    prediction_url = (
        f"/predictions/{prediction['status']}/"
        f"{prediction_path.parent.name}/"
        f"{prediction_path.name}"
    )


    # -----------------------------------------------------
    # Save to MongoDB
    # -----------------------------------------------------

    product, is_new = get_or_create_product(product_id)
    
    # Initialize defect counts
    defect_counts = {
        "copper": 0,
        "mousebite": 0,
        "open": 0,
        "pin-hole": 0,
        "short": 0,
        "spur": 0,
        "missing_hole": 0
    }
    
    for defect in prediction["defects"]:
        cls_name = defect["class_name"]
        if cls_name in defect_counts:
            defect_counts[cls_name] += 1
            
    # Check if from camera based on filename
    inspection_method = "camera" if file.filename == "camera_pcb.jpg" else "upload"
    
    inspection_record = {
        "inspection_request_id": inspection_request_id,
        "product_id": product["product_id"],
        "inspection_method": inspection_method,
        "status": prediction["status"],
        "total_defects": prediction["total_defects"],
        "defect_counts": defect_counts,
        "defects": prediction["defects"],
        "original_image": prediction["original_image"],
        "prediction_image": prediction_url,
        "image_hash": image_hash
    }
    
    save_inspection(inspection_record)


    # -----------------------------------------------------
    # Return response
    # -----------------------------------------------------

    return {

        "message":
            "New PCB registered" if is_new else "Existing PCB detected",

        "filename":
            file.filename,

        "status":
            prediction["status"],

        "total_defects":
            prediction["total_defects"],

        "defects":
            prediction["defects"],

        "prediction_image":
            prediction_url,
            
        "product": product,
        
        "inspection_method": inspection_method,
        "created_at": inspection_record.get("created_at")
    }