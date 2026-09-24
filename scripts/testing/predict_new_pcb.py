from pathlib import Path
from ultralytics import YOLO


# ---------------------------------------------------------
# 1. Find the project root directory
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------
# 2. Set model and input image paths
# ---------------------------------------------------------
MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "universal_pcb_yolov8s"
    / "best.pt"
)

IMAGE_PATH = (
    PROJECT_ROOT
    / "test_images"
    / "new_pcb"
    / "pcb1.jpg"
)


# ---------------------------------------------------------
# 3. Set output directory
# ---------------------------------------------------------
OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "predictions"
)


# ---------------------------------------------------------
# 4. Check whether the image exists
# ---------------------------------------------------------
if not IMAGE_PATH.exists():
    print("ERROR: PCB image not found!")
    print(f"Expected image location:")
    print(IMAGE_PATH)
    exit()


# ---------------------------------------------------------
# 5. Load the trained YOLO model
# ---------------------------------------------------------
print("=" * 60)
print("NEW PCB PREDICTION")
print("=" * 60)

print("\nModel:")
print(MODEL_PATH)

print("\nLoading model...")

model = YOLO(str(MODEL_PATH))

print("Model loaded successfully.")


# ---------------------------------------------------------
# 6. Run prediction on the new PCB image
# ---------------------------------------------------------
print("\nImage:")
print(IMAGE_PATH)

print("\nStarting prediction...")

results = model.predict(
    source=str(IMAGE_PATH),
    imgsz=512,
    conf=0.50,
    save=True,
    project=str(OUTPUT_DIR),
    name="new_pcb",
    exist_ok=True
)


# ---------------------------------------------------------
# 7. Display prediction results
# ---------------------------------------------------------
print("\n" + "-" * 60)

result = results[0]

if len(result.boxes) == 0:

    print("RESULT: NO DEFECT DETECTED")

else:

    print("Detected defects:")

    for box in result.boxes:

        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        class_name = result.names[class_id]

        print(
            f"  {class_name}: "
            f"{confidence:.2f}"
        )


# ---------------------------------------------------------
# 8. Show output location
# ---------------------------------------------------------
print("\n" + "-" * 60)

print("Prediction image saved to:")

print(
    OUTPUT_DIR
    / "new_pcb"
)

print("\n" + "=" * 60)
print("NEW PCB PREDICTION COMPLETED")
print("=" * 60)