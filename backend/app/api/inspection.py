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
    HTTPException
)

from backend.app.services.pcb_detector import (
    predict_pcb
)


# ---------------------------------------------------------
# Create router
# ---------------------------------------------------------

router = APIRouter(

    prefix="/api/inspection",

    tags=["PCB Inspection"]
)


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
    file: UploadFile = File(...)
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
        "/predictions/"
        + prediction_path.parent.name
        + "/"
        + prediction_path.name
    )


    # -----------------------------------------------------
    # Return response
    # -----------------------------------------------------

    return {

        "message":
            "PCB inspection completed successfully",

        "filename":
            file.filename,

        "status":
            prediction["status"],

        "total_defects":
            prediction["total_defects"],

        "defects":
            prediction["defects"],

        "prediction_image":
            prediction_url
    }