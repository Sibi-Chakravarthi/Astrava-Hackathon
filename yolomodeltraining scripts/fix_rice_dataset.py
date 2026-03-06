import os
import shutil
import random
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────────────
DATASET_ROOT = r"C:\Users\Aditya Vineeth\Desktop\astrava\DATASET\Rice Disease.v8i.yolov11 (1)"
SPLIT_RATIO  = 0.8   # 80% train, 20% val
SEED         = 42

# ── OLD → NEW CLASS MAPPING ──────────────────────────────────────────────────
# Original indices:
#   0: grain discoloration
#   1: leaf blight
#   2: leaf_blight        ← duplicate of 1, merge into 1
#   3: pesticide residue
#   4: rice blast
#
# New indices after merge:
#   0: rice_grain_discoloration
#   1: rice_leaf_blight
#   2: rice_pesticide_residue
#   3: rice_blast

OLD_TO_NEW = {
    0: 0,   # grain discoloration   → rice_grain_discoloration
    1: 1,   # leaf blight           → rice_leaf_blight
    2: 1,   # leaf_blight (dup)     → rice_leaf_blight  (merged)
    3: 2,   # pesticide residue     → rice_pesticide_residue
    4: 3,   # rice blast            → rice_blast
}

NEW_NAMES = [
    "rice_grain_discoloration",
    "rice_leaf_blight",
    "rice_pesticide_residue",
    "rice_blast",
]

# ── PATHS ────────────────────────────────────────────────────────────────────
root        = Path(DATASET_ROOT)
train_imgs  = root / "train" / "images"
train_lbls  = root / "train" / "labels"
val_imgs    = root / "valid" / "images"
val_lbls    = root / "valid" / "labels"

# ── STEP 1: Collect all training images ─────────────────────────────────────
all_images = sorted(list(train_imgs.glob("*.jpg")) +
                    list(train_imgs.glob("*.jpeg")) +
                    list(train_imgs.glob("*.png")))

print(f"Total images found in train: {len(all_images)}")

random.seed(SEED)
random.shuffle(all_images)

split_idx   = int(len(all_images) * SPLIT_RATIO)
train_set   = all_images[:split_idx]
val_set     = all_images[split_idx:]

print(f"Train split : {len(train_set)} images")
print(f"Val split   : {len(val_set)} images")

# ── STEP 2: Create val directories ──────────────────────────────────────────
val_imgs.mkdir(parents=True, exist_ok=True)
val_lbls.mkdir(parents=True, exist_ok=True)

# ── STEP 3: Move val images + labels to valid/ ───────────────────────────────
moved = 0
for img_path in val_set:
    # move image
    shutil.move(str(img_path), str(val_imgs / img_path.name))

    # move corresponding label
    lbl_path = train_lbls / (img_path.stem + ".txt")
    if lbl_path.exists():
        shutil.move(str(lbl_path), str(val_lbls / lbl_path.name))
    moved += 1

print(f"Moved {moved} images (+labels) to valid/")

# ── STEP 4: Remap class indices in ALL label files (train + val) ─────────────
def remap_labels(label_dir: Path):
    files = list(label_dir.glob("*.txt"))
    for lbl_file in files:
        lines = lbl_file.read_text().strip().splitlines()
        new_lines = []
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            old_cls = int(parts[0])
            new_cls = OLD_TO_NEW.get(old_cls)
            if new_cls is None:
                print(f"  WARNING: unknown class {old_cls} in {lbl_file.name}, skipping line")
                continue
            new_lines.append(f"{new_cls} " + " ".join(parts[1:]))
        lbl_file.write_text("\n".join(new_lines))
    print(f"Remapped {len(files)} label files in {label_dir}")

remap_labels(train_lbls)
remap_labels(val_lbls)

# ── STEP 5: Write new data.yaml ───────────────────────────────────────────────
yaml_content = f"""train: ../train/images
val: ../valid/images

nc: {len(NEW_NAMES)}
names: {NEW_NAMES}

# Remapped from original 5-class dataset
# leaf blight + leaf_blight merged into rice_leaf_blight
# Source: https://universe.roboflow.com/deep-learning-q7eui/rice-disease-eq1pq/dataset/8
"""

yaml_path = root / "data.yaml"
yaml_path.write_text(yaml_content)
print(f"\nWrote updated data.yaml to {yaml_path}")

# ── DONE ─────────────────────────────────────────────────────────────────────
print("\n✓ Done. Summary:")
print(f"  Train images : {len(list(train_imgs.glob('*.*')))}")
print(f"  Val images   : {len(list(val_imgs.glob('*.*')))}")
print(f"  Classes      : {NEW_NAMES}")
