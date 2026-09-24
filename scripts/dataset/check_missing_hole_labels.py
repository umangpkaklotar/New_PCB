# ============================================================
# check_missing_hole_labels.py
#
# Purpose:
# Visually verify YOLO labels after missing_hole augmentation.
#
# This script:
# 1. Finds training images containing missing_hole
# 2. Selects random samples
# 3. Draws YOLO bounding boxes
# 4. Shows class names
# 5. Saves the checked images
#
# IMPORTANT:
# This script DOES NOT modify original images or labels.
# ============================================================


from pathlib import Path
import cv2
import random


# ============================================================
# 1. DATASET PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_DIR = BASE_DIR / "Universal_PCB_Dataset"

TRAIN_IMAGES = DATASET_DIR / "train" / "images"

TRAIN_LABELS = DATASET_DIR / "train" / "labels"


# ============================================================
# 2. OUTPUT FOLDER
# ============================================================

OUTPUT_DIR = BASE_DIR / "missing_hole_label_check"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 3. CLASS NAMES
# ============================================================

CLASS_NAMES = [
    "copper",
    "mousebite",
    "open",
    "pin-hole",
    "short",
    "spur",
    "missing_hole"
]


# ============================================================
# 4. SETTINGS
# ============================================================

# Number of images to check
NUMBER_OF_IMAGES = 20

# Random seed
random.seed(42)


# ============================================================
# 5. READ YOLO LABELS
# ============================================================

def read_labels(label_path):

    labels = []

    if not label_path.exists():
        return labels

    with open(label_path, "r") as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) != 5:
                continue

            class_id = int(parts[0])

            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])

            labels.append(
                (
                    class_id,
                    x_center,
                    y_center,
                    width,
                    height
                )
            )

    return labels


# ============================================================
# 6. FIND IMAGES WITH MISSING_HOLE
# ============================================================

def find_missing_hole_images():

    image_files = []

    for label_file in TRAIN_LABELS.glob("*.txt"):

        labels = read_labels(label_file)

        has_missing_hole = any(
            label[0] == 6
            for label in labels
        )

        if not has_missing_hole:
            continue

        image_stem = label_file.stem

        possible_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".JPG",
            ".JPEG",
            ".PNG"
        ]

        for extension in possible_extensions:

            image_path = (
                TRAIN_IMAGES /
                f"{image_stem}{extension}"
            )

            if image_path.exists():

                image_files.append(
                    image_path
                )

                break

    return image_files


# ============================================================
# 7. DRAW YOLO BOXES
# ============================================================

def draw_labels(image, labels):

    image_height, image_width = image.shape[:2]

    for label in labels:

        (
            class_id,
            x_center,
            y_center,
            box_width,
            box_height
        ) = label

        # Convert YOLO normalized coordinates
        # to pixel coordinates.

        x_center_pixel = x_center * image_width
        y_center_pixel = y_center * image_height

        box_width_pixel = box_width * image_width
        box_height_pixel = box_height * image_height

        x1 = int(
            x_center_pixel -
            box_width_pixel / 2
        )

        y1 = int(
            y_center_pixel -
            box_height_pixel / 2
        )

        x2 = int(
            x_center_pixel +
            box_width_pixel / 2
        )

        y2 = int(
            y_center_pixel +
            box_height_pixel / 2
        )

        # Keep box inside image
        x1 = max(0, x1)
        y1 = max(0, y1)

        x2 = min(image_width - 1, x2)
        y2 = min(image_height - 1, y2)

        # Class name
        if 0 <= class_id < len(CLASS_NAMES):

            class_name = CLASS_NAMES[class_id]

        else:

            class_name = f"class_{class_id}"

        # Draw bounding box
        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        # Label text
        text = f"{class_id}: {class_name}"

        # Text background
        (text_width, text_height), baseline = (
            cv2.getTextSize(
                text,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                1
            )
        )

        text_y = max(
            y1 - 5,
            text_height + 5
        )

        cv2.rectangle(
            image,
            (
                x1,
                text_y - text_height - baseline
            ),
            (
                x1 + text_width,
                text_y + baseline
            ),
            (0, 255, 0),
            -1
        )

        # Draw text
        cv2.putText(
            image,
            text,
            (x1, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            cv2.LINE_AA
        )

    return image


# ============================================================
# 8. MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("MISSING_HOLE LABEL VISUAL CHECK")
    print("=" * 60)

    print()
    print("Dataset:")
    print(DATASET_DIR)

    print()
    print("Searching for missing_hole images...")

    image_files = find_missing_hole_images()

    print()
    print(
        "Total images containing missing_hole:",
        len(image_files)
    )

    if len(image_files) == 0:

        print()
        print("ERROR: No missing_hole images found.")

        return

    # --------------------------------------------------------
    # Select random images
    # --------------------------------------------------------

    sample_count = min(
        NUMBER_OF_IMAGES,
        len(image_files)
    )

    selected_images = random.sample(
        image_files,
        sample_count
    )

    print()
    print(
        f"Checking {sample_count} random images..."
    )

    print()
    print("-" * 60)


    # --------------------------------------------------------
    # Process images
    # --------------------------------------------------------

    for index, image_path in enumerate(
        selected_images,
        start=1
    ):

        label_path = (
            TRAIN_LABELS /
            f"{image_path.stem}.txt"
        )

        image = cv2.imread(
            str(image_path)
        )

        if image is None:

            print(
                f"[WARNING] Could not read: "
                f"{image_path.name}"
            )

            continue

        labels = read_labels(
            label_path
        )

        # Draw boxes
        result = draw_labels(
            image,
            labels
        )

        # Output filename
        output_path = (
            OUTPUT_DIR /
            f"check_{index:02d}_{image_path.name}"
        )

        cv2.imwrite(
            str(output_path),
            result
        )

        # Count missing holes
        missing_count = sum(
            1
            for label in labels
            if label[0] == 6
        )

        print(
            f"{index:02d}. "
            f"{image_path.name} | "
            f"missing_hole: {missing_count}"
        )


    # --------------------------------------------------------
    # Finish
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("VISUAL CHECK FILES CREATED")
    print("=" * 60)

    print()
    print("Open this folder:")

    print(OUTPUT_DIR)

    print()
    print(
        "Check whether the missing_hole bounding boxes "
        "are actually around the holes."
    )

    print()
    print("Original dataset was NOT modified.")


# ============================================================
# 9. RUN
# ============================================================

if __name__ == "__main__":

    main()