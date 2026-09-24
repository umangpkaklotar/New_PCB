# ---------------------------------------------------------
# Test PCB Detector Service
# Tests YOLO model through backend service
# ---------------------------------------------------------

from backend.app.services.pcb_detector import predict_pcb


# ---------------------------------------------------------
# Test image path
# ---------------------------------------------------------

IMAGE_PATH = (
    "test_images/new_pcb/pcb1.jpg"
)


# ---------------------------------------------------------
# Run PCB prediction
# ---------------------------------------------------------

result = predict_pcb(IMAGE_PATH)


# ---------------------------------------------------------
# Print complete result
# ---------------------------------------------------------

print("\n========================================")
print("PCB INSPECTION RESULT")
print("========================================")

print(f"Status: {result['status']}")
print(f"Total Defects: {result['total_defects']}")


# ---------------------------------------------------------
# Print each detected defect
# ---------------------------------------------------------

for index, defect in enumerate(result["defects"], start=1):

    print(f"\nDefect {index}")
    print(f"Class ID: {defect['class_id']}")
    print(f"Class Name: {defect['class_name']}")
    print(f"Confidence: {defect['confidence']}")
    print(f"BBox: {defect['bbox']}")


print("\n========================================")