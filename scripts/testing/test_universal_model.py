# ============================================================
# Universal PCB Model - Local Testing
#
# Purpose:
# Test the new Universal YOLOv8s model on PCB images.
#
# Project structure:
# D:\PCB_defect_detiction\
# ├── models\
# ├── test_images\
# ├── outputs\
# └── scripts\testing\
# ============================================================


from pathlib import Path
from ultralytics import YOLO


# ============================================================
# 1. PROJECT ROOT
# ============================================================

# test_universal_model.py is inside:
# scripts/testing/
#
# parents[0] = testing
# parents[1] = scripts
# parents[2] = project root

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# 2. MODEL PATH
# ============================================================

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "universal_pcb_yolov8s"
    / "best.pt"
)


# ============================================================
# 3. TEST IMAGE FOLDERS
# ============================================================

TEST_FOLDERS = [
    PROJECT_ROOT / "test_images" / "normal",
    PROJECT_ROOT / "test_images" / "defective",
    PROJECT_ROOT / "test_images" / "real_color",
]


# ============================================================
# 4. OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "predictions"
)


# ============================================================
# 5. LOAD MODEL
# ============================================================

print()
print("=" * 60)
print("UNIVERSAL PCB MODEL TEST")
print("=" * 60)

print()
print("Project root:")
print(PROJECT_ROOT)

print()
print("Model:")
print(MODEL_PATH)


if not MODEL_PATH.exists():

    print()
    print("ERROR: best.pt not found.")
    print("Expected:")
    print(MODEL_PATH)

    raise SystemExit


print()
print("Loading model...")

model = YOLO(str(MODEL_PATH))

print("Model loaded successfully.")


# ============================================================
# 6. FIND TEST IMAGES
# ============================================================

image_files = []

extensions = [
    "*.jpg",
    "*.jpeg",
    "*.png",
    "*.JPG",
    "*.JPEG",
    "*.PNG",
]


for folder in TEST_FOLDERS:

    if not folder.exists():
        continue

    for extension in extensions:

        image_files.extend(
            folder.glob(extension)
        )


# Remove duplicates
image_files = list(
    dict.fromkeys(image_files)
)


print()
print("Total test images:")
print(len(image_files))


if len(image_files) == 0:

    print()
    print("No test images found.")

    print()
    print("Put images inside:")
    print(PROJECT_ROOT / "test_images" / "normal")
    print(PROJECT_ROOT / "test_images" / "defective")
    print(PROJECT_ROOT / "test_images" / "real_color")

    raise SystemExit


# ============================================================
# 7. RUN PREDICTION
# ============================================================

print()
print("=" * 60)
print("STARTING PREDICTION")
print("=" * 60)


for image_path in image_files:

    print()
    print("-" * 60)

    print("Image:")
    print(image_path.name)

    results = model.predict(
        source=str(image_path),
        imgsz=512,
        conf=0.50,
        save=True,
        project=str(OUTPUT_DIR),
        name="results",
        exist_ok=True,
        verbose=False,
    )


    # --------------------------------------------------------
    # Read detections
    # --------------------------------------------------------

    result = results[0]

    if result.boxes is None or len(result.boxes) == 0:

        print("Result: NO DEFECT DETECTED")

        continue


    print("Detected defects:")


    for box in result.boxes:

        class_id = int(
            box.cls[0]
        )

        confidence = float(
            box.conf[0]
        )

        class_name = model.names[
            class_id
        ]

        print(
            f"  {class_name}: "
            f"{confidence:.2f}"
        )


# ============================================================
# 8. FINISH
# ============================================================

print()
print("=" * 60)
print("TESTING COMPLETE")
print("=" * 60)

print()
print("Prediction output:")
print(OUTPUT_DIR / "results")