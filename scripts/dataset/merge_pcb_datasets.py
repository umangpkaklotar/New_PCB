from pathlib import Path
import shutil
import yaml


# ============================================================
# 1. PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# 2. SOURCE DATASETS
# ============================================================
# Color PCB dataset
# IMPORTANT:
# "PCB  Defects" ma 2 spaces che.
# ============================================================

COLOR_DATASET = (
    BASE_DIR / "PCB  Defects DATASET.v2i.yolov8"
)


# Existing B&W / old PCB dataset

OLD_DATASET = (
    BASE_DIR / "PCB_YOLO_Roboflow"
)


# New merged dataset

OUTPUT_DATASET = (
    BASE_DIR / "Universal_PCB_Dataset"
)


# ============================================================
# 3. FINAL COMMON CLASSES
# ============================================================
#
# 0 = copper
# 1 = mousebite
# 2 = open
# 3 = pin-hole
# 4 = short
# 5 = spur
# 6 = missing_hole
#
# ============================================================

FINAL_CLASSES = [
    "copper",
    "mousebite",
    "open",
    "pin-hole",
    "short",
    "spur",
    "missing_hole",
]


# ============================================================
# 4. COLOR DATASET CLASS MAPPING
# ============================================================
#
# Color dataset:
#
# 0 = missing_hole
# 1 = mouse_bite
# 2 = open_circuit
# 3 = short
# 4 = spur
# 5 = spurious_copper
#
# Convert to FINAL_CLASSES:
#
# 0 -> 6
# 1 -> 1
# 2 -> 2
# 3 -> 4
# 4 -> 5
# 5 -> 0
#
# ============================================================

COLOR_CLASS_MAP = {
    0: 6,
    1: 1,
    2: 2,
    3: 4,
    4: 5,
    5: 0,
}


# ============================================================
# 5. OLD DATASET CLASS MAPPING
# ============================================================
#
# Old dataset:
#
# 0 = copper
# 1 = mousebite
# 2 = open
# 3 = pin-hole
# 4 = short
# 5 = spur
#
# IDs already match FINAL_CLASSES.
#
# ============================================================

OLD_CLASS_MAP = {
    0: 0,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
}


# ============================================================
# 6. CHECK SOURCE DATASETS
# ============================================================

def check_dataset(dataset_path, dataset_name):

    print("\nChecking:", dataset_name)
    print("Path:", dataset_path)

    if not dataset_path.exists():

        raise FileNotFoundError(
            f"\n{dataset_name} not found:\n"
            f"{dataset_path}"
        )

    print("FOUND")


# ============================================================
# 7. CREATE OUTPUT FOLDERS
# ============================================================

def create_output_folders():

    for split in [
        "train",
        "valid",
        "test"
    ]:

        image_folder = (
            OUTPUT_DATASET
            / split
            / "images"
        )

        label_folder = (
            OUTPUT_DATASET
            / split
            / "labels"
        )

        image_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        label_folder.mkdir(
            parents=True,
            exist_ok=True
        )


# ============================================================
# 8. FIND ALL IMAGES
# ============================================================

def find_images(folder):

    image_files = []

    extensions = [
        "*.jpg",
        "*.jpeg",
        "*.png",
        "*.JPG",
        "*.JPEG",
        "*.PNG",
    ]

    for extension in extensions:

        image_files.extend(
            folder.glob(extension)
        )

    return image_files


# ============================================================
# 9. CONVERT YOLO LABEL
# ============================================================

def convert_label(
    source_label,
    destination_label,
    class_mapping
):

    # --------------------------------------------------------
    # If label does not exist,
    # create empty label file.
    # This represents a normal/no-defect image.
    # --------------------------------------------------------

    if not source_label.exists():

        destination_label.touch()

        return False


    new_lines = []


    with open(
        source_label,
        "r",
        encoding="utf-8"
    ) as file:

        lines = file.readlines()


    for line_number, line in enumerate(
        lines,
        start=1
    ):

        line = line.strip()


        if not line:

            continue


        parts = line.split()


        # ----------------------------------------------------
        # YOLO format:
        #
        # class x_center y_center width height
        # ----------------------------------------------------

        if len(parts) != 5:

            print(
                f"WARNING: Invalid label format:"
                f"\n{source_label}"
                f"\nLine: {line_number}"
            )

            continue


        try:

            old_class_id = int(parts[0])

        except ValueError:

            print(
                f"WARNING: Invalid class ID:"
                f"\n{source_label}"
                f"\nLine: {line_number}"
            )

            continue


        # ----------------------------------------------------
        # Check class mapping
        # ----------------------------------------------------

        if old_class_id not in class_mapping:

            print(
                f"WARNING: Unknown class ID "
                f"{old_class_id}"
                f"\nFile: {source_label}"
            )

            continue


        new_class_id = (
            class_mapping[old_class_id]
        )


        # ----------------------------------------------------
        # Create converted YOLO line
        # ----------------------------------------------------

        new_line = (
            f"{new_class_id} "
            f"{parts[1]} "
            f"{parts[2]} "
            f"{parts[3]} "
            f"{parts[4]}\n"
        )


        new_lines.append(
            new_line
        )


    # --------------------------------------------------------
    # Save converted label
    # --------------------------------------------------------

    with open(
        destination_label,
        "w",
        encoding="utf-8"
    ) as file:

        file.writelines(
            new_lines
        )


    return True


# ============================================================
# 10. MERGE ONE DATASET
# ============================================================

def merge_dataset(
    dataset_path,
    class_mapping,
    prefix
):

    print("\n")
    print("=" * 70)

    print(
        f"PROCESSING DATASET: {prefix}"
    )

    print(
        f"SOURCE: {dataset_path}"
    )

    print("=" * 70)


    total_images = 0
    total_labels = 0


    for split in [
        "train",
        "valid",
        "test"
    ]:

        source_image_folder = (
            dataset_path
            / split
            / "images"
        )


        source_label_folder = (
            dataset_path
            / split
            / "labels"
        )


        destination_image_folder = (
            OUTPUT_DATASET
            / split
            / "images"
        )


        destination_label_folder = (
            OUTPUT_DATASET
            / split
            / "labels"
        )


        print("\n")
        print(
            f"----- {split.upper()} -----"
        )


        # ----------------------------------------------------
        # Check image folder
        # ----------------------------------------------------

        if not source_image_folder.exists():

            print(
                "WARNING: Image folder not found:"
            )

            print(
                source_image_folder
            )

            continue


        # ----------------------------------------------------
        # Find images
        # ----------------------------------------------------

        image_files = find_images(
            source_image_folder
        )


        print(
            f"Images found: {len(image_files)}"
        )


        # ----------------------------------------------------
        # Process every image
        # ----------------------------------------------------

        for index, image_path in enumerate(
            image_files,
            start=1
        ):


            # ------------------------------------------------
            # Prefix avoids duplicate filenames.
            #
            # Example:
            #
            # COLOR_0001.jpg
            # BW_0001.jpg
            # ------------------------------------------------

            new_image_name = (
                f"{prefix}_{image_path.name}"
            )


            destination_image = (
                destination_image_folder
                / new_image_name
            )


            # ------------------------------------------------
            # Copy image
            # ------------------------------------------------

            shutil.copy2(
                image_path,
                destination_image
            )


            total_images += 1


            # ------------------------------------------------
            # Find source label
            # ------------------------------------------------

            source_label = (
                source_label_folder
                / f"{image_path.stem}.txt"
            )


            destination_label = (
                destination_label_folder
                / f"{Path(new_image_name).stem}.txt"
            )


            # ------------------------------------------------
            # Convert label
            # ------------------------------------------------

            label_exists = convert_label(
                source_label,
                destination_label,
                class_mapping
            )


            if label_exists:

                total_labels += 1


            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            if index % 500 == 0:

                print(
                    f"Processed: {index}"
                )


        print(
            f"Finished {split}: "
            f"{len(image_files)} images"
        )


    print("\n")
    print(
        f"{prefix} total images: "
        f"{total_images}"
    )

    print(
        f"{prefix} total labels: "
        f"{total_labels}"
    )


# ============================================================
# 11. CREATE DATA.YAML
# ============================================================

def create_data_yaml():

    data = {

        "train": "../train/images",

        "val": "../valid/images",

        "test": "../test/images",

        "nc": len(FINAL_CLASSES),

        "names": FINAL_CLASSES,
    }


    yaml_path = (
        OUTPUT_DATASET
        / "data.yaml"
    )


    with open(
        yaml_path,
        "w",
        encoding="utf-8"
    ) as file:

        yaml.dump(
            data,
            file,
            sort_keys=False
        )


    print("\n")
    print(
        "data.yaml created:"
    )

    print(
        yaml_path
    )


# ============================================================
# 12. VERIFY FINAL DATASET
# ============================================================

def verify_dataset():

    print("\n")
    print("=" * 70)
    print("FINAL DATASET VERIFICATION")
    print("=" * 70)


    total_images = 0
    total_labels = 0


    for split in [
        "train",
        "valid",
        "test"
    ]:

        image_folder = (
            OUTPUT_DATASET
            / split
            / "images"
        )


        label_folder = (
            OUTPUT_DATASET
            / split
            / "labels"
        )


        image_files = find_images(
            image_folder
        )


        label_files = list(
            label_folder.glob("*.txt")
        )


        total_images += len(
            image_files
        )


        total_labels += len(
            label_files
        )


        print("\n")
        print(
            split.upper()
        )

        print(
            "Images:",
            len(image_files)
        )

        print(
            "Labels:",
            len(label_files)
        )


        # ----------------------------------------------------
        # Check image/label matching
        # ----------------------------------------------------

        image_stems = {
            image.stem
            for image in image_files
        }


        label_stems = {
            label.stem
            for label in label_files
        }


        missing_labels = (
            image_stems - label_stems
        )


        extra_labels = (
            label_stems - image_stems
        )


        print(
            "Missing labels:",
            len(missing_labels)
        )

        print(
            "Extra labels:",
            len(extra_labels)
        )


    print("\n")
    print(
        "TOTAL IMAGES:",
        total_images
    )

    print(
        "TOTAL LABELS:",
        total_labels
    )


# ============================================================
# 13. MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("UNIVERSAL PCB DATASET MERGER")
    print("=" * 70)


    # --------------------------------------------------------
    # Check exact source folders
    # --------------------------------------------------------

    check_dataset(
        COLOR_DATASET,
        "COLOR PCB DATASET"
    )


    check_dataset(
        OLD_DATASET,
        "OLD B&W DATASET"
    )


    # --------------------------------------------------------
    # If output folder already exists,
    # delete old merged dataset.
    # --------------------------------------------------------

    if OUTPUT_DATASET.exists():

        print("\n")
        print(
            "Old Universal_PCB_Dataset found."
        )

        print(
            "Removing old merged dataset..."
        )


        shutil.rmtree(
            OUTPUT_DATASET
        )


    # --------------------------------------------------------
    # Create fresh output folders
    # --------------------------------------------------------

    create_output_folders()


    # --------------------------------------------------------
    # Merge COLOR dataset
    # --------------------------------------------------------

    merge_dataset(
        COLOR_DATASET,
        COLOR_CLASS_MAP,
        "COLOR"
    )


    # --------------------------------------------------------
    # Merge OLD B&W dataset
    # --------------------------------------------------------

    merge_dataset(
        OLD_DATASET,
        OLD_CLASS_MAP,
        "BW"
    )


    # --------------------------------------------------------
    # Create data.yaml
    # --------------------------------------------------------

    create_data_yaml()


    # --------------------------------------------------------
    # Verify dataset
    # --------------------------------------------------------

    verify_dataset()


    # --------------------------------------------------------
    # Print final classes
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("FINAL CLASSES")
    print("=" * 70)


    for class_id, class_name in enumerate(
        FINAL_CLASSES
    ):

        print(
            f"{class_id}: {class_name}"
        )


    # --------------------------------------------------------
    # Final message
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("MERGE COMPLETED SUCCESSFULLY")
    print("=" * 70)


    print(
        "\nUniversal dataset location:"
    )

    print(
        OUTPUT_DATASET
    )


    print(
        "\nDO NOT TRAIN YET."
    )

    print(
        "First verify the image/label counts."
    )


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    main()