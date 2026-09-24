# ============================================================
# balance_missing_hole.py
#
# Purpose:
# Only balance the "missing_hole" class in the TRAIN dataset.
#
# Current:
# missing_hole = 486 instances
#
# Target:
# approximately 2,000 missing_hole instances
#
# IMPORTANT:
# - Original images are NOT deleted
# - valid/ is NOT changed
# - test/ is NOT changed
# - data.yaml is NOT changed
# - Other classes are NOT intentionally oversampled
# ============================================================


from pathlib import Path
import cv2
import numpy as np
import random


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_DIR = BASE_DIR / "Universal_PCB_Dataset"

TRAIN_IMAGES = DATASET_DIR / "train" / "images"
TRAIN_LABELS = DATASET_DIR / "train" / "labels"


# ============================================================
# 2. SETTINGS
# ============================================================

# missing_hole class ID
MISSING_HOLE_CLASS_ID = 6

# Current missing_hole instances
CURRENT_TARGET_COUNT = 486

# Desired number of missing_hole instances
TARGET_MISSING_HOLE_COUNT = 2000

# Maximum number of augmentation images to create
# Safety limit so accidental huge generation doesn't happen.
MAX_NEW_IMAGES = 3000

# Random seed
random.seed(42)
np.random.seed(42)


# ============================================================
# 3. AUGMENTATION FUNCTIONS
# ============================================================

def horizontal_flip(image, labels):
    """
    Flip image horizontally and update YOLO bounding boxes.
    """

    image = cv2.flip(image, 1)

    new_labels = []

    for cls, x, y, w, h in labels:

        x = 1.0 - x

        new_labels.append([cls, x, y, w, h])

    return image, new_labels


def vertical_flip(image, labels):
    """
    Flip image vertically and update YOLO bounding boxes.
    """

    image = cv2.flip(image, 0)

    new_labels = []

    for cls, x, y, w, h in labels:

        y = 1.0 - y

        new_labels.append([cls, x, y, w, h])

    return image, new_labels


def rotate_90(image, labels):
    """
    Rotate image 90 degrees clockwise
    and update YOLO bounding boxes.
    """

    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    new_labels = []

    for cls, x, y, w, h in labels:

        new_x = 1.0 - y
        new_y = x

        new_w = h
        new_h = w

        new_labels.append(
            [cls, new_x, new_y, new_w, new_h]
        )

    return image, new_labels


def brightness_change(image, labels):
    """
    Random brightness modification.
    Bounding boxes do not change.
    """

    factor = random.uniform(0.75, 1.25)

    image = image.astype(np.float32) * factor

    image = np.clip(image, 0, 255).astype(np.uint8)

    return image, labels


def contrast_change(image, labels):
    """
    Random contrast modification.
    """

    factor = random.uniform(0.75, 1.25)

    mean = np.mean(image)

    image = (image - mean) * factor + mean

    image = np.clip(image, 0, 255).astype(np.uint8)

    return image, labels


# ============================================================
# 4. RANDOM AUGMENTATION
# ============================================================

def augment_image(image, labels):

    operation = random.choice([
        "horizontal",
        "vertical",
        "rotate",
        "brightness",
        "contrast"
    ])

    if operation == "horizontal":

        return horizontal_flip(image, labels)

    elif operation == "vertical":

        return vertical_flip(image, labels)

    elif operation == "rotate":

        return rotate_90(image, labels)

    elif operation == "brightness":

        return brightness_change(image, labels)

    elif operation == "contrast":

        return contrast_change(image, labels)


# ============================================================
# 5. READ YOLO LABEL FILE
# ============================================================

def read_labels(label_path):

    labels = []

    if not label_path.exists():
        return labels

    with open(label_path, "r") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) != 5:
                continue

            cls = int(parts[0])

            x = float(parts[1])
            y = float(parts[2])
            w = float(parts[3])
            h = float(parts[4])

            labels.append(
                [cls, x, y, w, h]
            )

    return labels


# ============================================================
# 6. WRITE YOLO LABEL FILE
# ============================================================

def write_labels(label_path, labels):

    with open(label_path, "w") as f:

        for cls, x, y, w, h in labels:

            f.write(
                f"{int(cls)} "
                f"{x:.6f} "
                f"{y:.6f} "
                f"{w:.6f} "
                f"{h:.6f}\n"
            )


# ============================================================
# 7. COUNT MISSING_HOLE INSTANCES
# ============================================================

def count_missing_hole():

    total = 0

    for label_file in TRAIN_LABELS.glob("*.txt"):

        labels = read_labels(label_file)

        for label in labels:

            cls = label[0]

            if cls == MISSING_HOLE_CLASS_ID:

                total += 1

    return total


# ============================================================
# 8. FIND IMAGES CONTAINING MISSING_HOLE
# ============================================================

def find_missing_hole_images():

    samples = []

    for label_file in TRAIN_LABELS.glob("*.txt"):

        labels = read_labels(label_file)

        missing_count = sum(
            1
            for label in labels
            if label[0] == MISSING_HOLE_CLASS_ID
        )

        if missing_count > 0:

            image_name = label_file.stem

            image_path = None

            for extension in [
                ".jpg",
                ".jpeg",
                ".png",
                ".JPG",
                ".JPEG",
                ".PNG"
            ]:

                possible = TRAIN_IMAGES / (image_name + extension)

                if possible.exists():

                    image_path = possible
                    break

            if image_path:

                samples.append(
                    (
                        image_path,
                        label_file,
                        missing_count
                    )
                )

    return samples


# ============================================================
# 9. CREATE AUGMENTED IMAGE
# ============================================================

def create_augmented_sample(
    image_path,
    label_path,
    index
):

    image = cv2.imread(str(image_path))

    if image is None:

        print(
            f"[WARNING] Could not read: {image_path}"
        )

        return 0

    labels = read_labels(label_path)

    if not labels:

        return 0

    # Apply augmentation
    augmented_image, augmented_labels = augment_image(
        image.copy(),
        labels.copy()
    )

    # New filename
    new_name = (
        f"{image_path.stem}"
        f"_missing_aug_{index:05d}"
    )

    new_image_path = (
        TRAIN_IMAGES /
        f"{new_name}{image_path.suffix}"
    )

    new_label_path = (
        TRAIN_LABELS /
        f"{new_name}.txt"
    )

    # Save image
    success = cv2.imwrite(
        str(new_image_path),
        augmented_image
    )

    if not success:

        print(
            f"[WARNING] Could not save: "
            f"{new_image_path}"
        )

        return 0

    # Save labels
    write_labels(
        new_label_path,
        augmented_labels
    )

    return sum(
        1
        for label in augmented_labels
        if label[0] == MISSING_HOLE_CLASS_ID
    )


# ============================================================
# 10. MAIN BALANCING PROCESS
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("MISSING_HOLE DATA BALANCING")
    print("=" * 60)

    print("\nDataset:")
    print(DATASET_DIR)

    print("\nTrain images:")
    print(TRAIN_IMAGES)

    print("\nTrain labels:")
    print(TRAIN_LABELS)


    # --------------------------------------------------------
    # Check paths
    # --------------------------------------------------------

    if not TRAIN_IMAGES.exists():

        print("\nERROR: Train images folder not found.")

        return

    if not TRAIN_LABELS.exists():

        print("\nERROR: Train labels folder not found.")

        return


    # --------------------------------------------------------
    # Count current missing_hole
    # --------------------------------------------------------

    current_count = count_missing_hole()

    print("\nCurrent missing_hole instances:")
    print(current_count)

    print("\nTarget missing_hole instances:")
    print(TARGET_MISSING_HOLE_COUNT)


    # --------------------------------------------------------
    # Check whether balancing is already complete
    # --------------------------------------------------------

    if current_count >= TARGET_MISSING_HOLE_COUNT:

        print("\nmissing_hole is already balanced.")

        return


    required_instances = (
        TARGET_MISSING_HOLE_COUNT
        - current_count
    )

    print("\nAdditional instances required:")
    print(required_instances)


    # --------------------------------------------------------
    # Find source images
    # --------------------------------------------------------

    samples = find_missing_hole_images()

    print("\nImages containing missing_hole:")
    print(len(samples))


    if len(samples) == 0:

        print(
            "\nERROR: No missing_hole images found."
        )

        return


    # --------------------------------------------------------
    # Start augmentation
    # --------------------------------------------------------

    print("\nStarting augmentation...")
    print("-" * 60)


    created_images = 0
    created_instances = 0

    sample_index = 0


    while (
        created_instances < required_instances
        and created_images < MAX_NEW_IMAGES
    ):

        # Random source image
        (
            image_path,
            label_path,
            missing_count
        ) = random.choice(samples)


        # Create augmented image
        added = create_augmented_sample(
            image_path,
            label_path,
            sample_index
        )


        if added > 0:

            created_images += 1

            created_instances += added

            sample_index += 1


            if created_images % 50 == 0:

                print(
                    f"Created images: "
                    f"{created_images} | "
                    f"Added missing_hole: "
                    f"{created_instances}"
                )


    # --------------------------------------------------------
    # Final count
    # --------------------------------------------------------

    final_count = count_missing_hole()


    print("\n")
    print("=" * 60)
    print("BALANCING COMPLETE")
    print("=" * 60)

    print(
        f"\nOriginal missing_hole : {current_count}"
    )

    print(
        f"New augmented images  : {created_images}"
    )

    print(
        f"Added instances       : {created_instances}"
    )

    print(
        f"Final missing_hole    : {final_count}"
    )

    print(
        f"Target                : "
        f"{TARGET_MISSING_HOLE_COUNT}"
    )

    print("\nValid dataset:")
    print("NOT CHANGED")

    print("\nTest dataset:")
    print("NOT CHANGED")

    print("\ndata.yaml:")
    print("NOT CHANGED")

    print("\nOriginal images:")
    print("NOT DELETED")

    print("\nDone.")


# ============================================================
# 11. RUN
# ============================================================

if __name__ == "__main__":

    main()
