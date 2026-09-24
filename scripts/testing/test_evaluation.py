from ultralytics import YOLO


# ---------------------------------------------------------
# 1. Load the trained Universal PCB YOLO model
# ---------------------------------------------------------
model = YOLO(
    r"D:\PCB_defect_detiction\models\universal_pcb_yolov8s\best.pt"
)


# ---------------------------------------------------------
# 2. Evaluate the model on the separate TEST dataset
# ---------------------------------------------------------
results = model.val(
    data=r"D:\PCB_defect_detiction\datasets\universal\Universal_PCB_Dataset\data.yaml",
    split="test",
    imgsz=512,
    conf=0.25,
    device="cpu",
    plots=True
)


# ---------------------------------------------------------
# 3. Print completion message
# ---------------------------------------------------------
print("\n========================================")
print("TEST EVALUATION COMPLETED")
print("========================================")