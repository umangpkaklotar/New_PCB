from pathlib import Path
from collections import Counter


DATASET = Path(
    r"D:\PCB_defect_detiction\Universal_PCB_Dataset"
)


CLASS_NAMES = [
    "copper",
    "mousebite",
    "open",
    "pin-hole",
    "short",
    "spur",
    "missing_hole",
]


print("=" * 60)
print("UNIVERSAL PCB DATASET CHECK")
print("=" * 60)


total_images = 0
total_labels = 0
total_instances = Counter()


for split in ["train", "valid", "test"]:

    image_dir = DATASET / split / "images"
    label_dir = DATASET / split / "labels"

    image_files = []

    for ext in ["*.jpg", "*.jpeg", "*.png"]:
        image_files.extend(image_dir.glob(ext))

    label_files = list(label_dir.glob("*.txt"))

    class_counter = Counter()

    for label_file in label_files:

        with open(
            label_file,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                parts = line.split()

                if len(parts) != 5:
                    continue

                class_id = int(parts[0])

                class_counter[class_id] += 1
                total_instances[class_id] += 1

    total_images += len(image_files)
    total_labels += len(label_files)

    print("\n" + "-" * 60)
    print(split.upper())
    print("-" * 60)

    print("Images :", len(image_files))
    print("Labels :", len(label_files))

    print("\nDefect instances:")

    for class_id, class_name in enumerate(CLASS_NAMES):

        print(
            f"{class_id} - {class_name}: "
            f"{class_counter[class_id]}"
        )


print("\n" + "=" * 60)
print("TOTAL")
print("=" * 60)

print("Total Images :", total_images)
print("Total Labels :", total_labels)

print("\nAll defect instances:")

for class_id, class_name in enumerate(CLASS_NAMES):

    print(
        f"{class_id} - {class_name}: "
        f"{total_instances[class_id]}"
    )


print("\n" + "=" * 60)
print("DATASET CHECK COMPLETED")
print("=" * 60)