import os
import shutil
from pathlib import Path

# ── OUTPUT ───────────────────────────────────────────────────────────────────
OUT_ROOT = Path(r"C:\Users\Aditya Vineeth\Desktop\astrava\DATASET\ALLINONE")

# ── MASTER CLASS LIST ────────────────────────────────────────────────────────
MASTER_NAMES = [
    "cotton_bacterial_blight",      # 0
    "cotton_leaf_curl_virus",       # 1
    "cotton_grey_mildew",           # 2
    "cotton_healthy",               # 3
    "cotton_alternaria_leaf_spot",  # 4
    "cotton_wilt",                  # 5
    "rice_grain_discoloration",     # 6
    "rice_leaf_blight",             # 7
    "rice_pesticide_residue",       # 8
    "rice_blast",                   # 9
    "tomato_early_blight",          # 10
    "tomato_septoria_leaf_spot",    # 11
    "tomato_healthy",               # 12
    "tomato_bacterial_spot",        # 13
    "tomato_late_blight",           # 14
    "tomato_mosaic_virus",          # 15
    "tomato_yellow_leaf_curl_virus",# 16
    "tomato_leaf_mold",             # 17
    "tomato_spider_mite",           # 18
    "wheat_powdery_mildew",         # 19
    "wheat_septoria_leaf_blotch",   # 20
    "wheat_stem_rust",              # 21
    "wheat_yellow_rust",            # 22
]

MASTER_INDEX = {name: i for i, name in enumerate(MASTER_NAMES)}

# ── PER-DATASET CONFIG ───────────────────────────────────────────────────────
# Each entry:
#   root       : dataset folder
#   prefix     : filename prefix to avoid collisions
#   splits     : which splits exist
#   local_names: class names in LOCAL index order (index 0,1,2... → master name)

DATASETS = [
    {
        "root": Path(r"C:\Users\Aditya Vineeth\Desktop\astrava\DATASET\cotton"),
        "prefix": "cotton",
        "splits": ["train", "valid", "test"],
        "local_names": [
            "cotton_bacterial_blight",
            "cotton_leaf_curl_virus",
            "cotton_grey_mildew",
            "cotton_healthy",
            "cotton_alternaria_leaf_spot",
            "cotton_wilt",
        ],
    },
    {
        "root": Path(r"C:\Users\Aditya Vineeth\Desktop\astrava\DATASET\rice"),
        "prefix": "rice",
        "splits": ["train", "valid"],
        "local_names": [
            "rice_grain_discoloration",
            "rice_leaf_blight",
            "rice_pesticide_residue",
            "rice_blast",
        ],
    },
    {
        "root": Path(r"C:\Users\Aditya Vineeth\Desktop\astrava\DATASET\tomato"),
        "prefix": "tomato",
        "splits": ["train", "valid", "test"],
        # Tomato still has original names — mapped here to master names
        "local_names": [
            "tomato_early_blight",          # 0: Tomato Early blight leaf
            "tomato_septoria_leaf_spot",    # 1: Tomato Septoria leaf spot
            "tomato_healthy",               # 2: Tomato leaf (healthy)
            "tomato_bacterial_spot",        # 3: Tomato leaf bacterial spot
            "tomato_late_blight",           # 4: Tomato leaf late blight
            "tomato_mosaic_virus",          # 5: Tomato leaf mosaic virus
            "tomato_yellow_leaf_curl_virus",# 6: Tomato leaf yellow virus
            "tomato_leaf_mold",             # 7: Tomato mold leaf
            "tomato_spider_mite",           # 8: Tomato two spotted spider mites leaf
        ],
    },
    {
        "root": Path(r"C:\Users\Aditya Vineeth\Desktop\astrava\DATASET\wheat"),
        "prefix": "wheat",
        "splits": ["train", "valid"],
        "local_names": [
            "wheat_powdery_mildew",
            "wheat_septoria_leaf_blotch",
            "wheat_stem_rust",
            "wheat_yellow_rust",
        ],
    },
]

# ── CREATE OUTPUT DIRS ────────────────────────────────────────────────────────
for split in ["train", "valid", "test"]:
    (OUT_ROOT / split / "images").mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / split / "labels").mkdir(parents=True, exist_ok=True)

print(f"Created output structure at {OUT_ROOT}\n")

# ── PROCESS EACH DATASET ──────────────────────────────────────────────────────
total_images = 0
total_labels = 0

for ds in DATASETS:
    root        = ds["root"]
    prefix      = ds["prefix"]
    splits      = ds["splits"]
    local_names = ds["local_names"]

    # Build local index → master index map
    local_to_master = {}
    for local_idx, local_name in enumerate(local_names):
        master_idx = MASTER_INDEX.get(local_name)
        if master_idx is None:
            print(f"  WARNING: '{local_name}' not found in master list, will be skipped")
        local_to_master[local_idx] = master_idx

    print(f"Processing: {prefix.upper()}")

    for split in splits:
        img_dir = root / split / "images"
        lbl_dir = root / split / "labels"

        # valid → valid, test → test, train → train
        out_split = split  # keep same split name

        out_img_dir = OUT_ROOT / out_split / "images"
        out_lbl_dir = OUT_ROOT / out_split / "labels"

        if not img_dir.exists():
            print(f"  SKIP {split}: images dir not found")
            continue

        images = sorted(
            list(img_dir.glob("*.jpg")) +
            list(img_dir.glob("*.jpeg")) +
            list(img_dir.glob("*.png"))
        )

        for img_path in images:
            new_name = f"{prefix}_{img_path.name}"

            # Copy image
            shutil.copy2(img_path, out_img_dir / new_name)
            total_images += 1

            # Process label
            lbl_path = lbl_dir / (img_path.stem + ".txt")
            new_lbl_name = f"{prefix}_{img_path.stem}.txt"

            if lbl_path.exists():
                lines = lbl_path.read_text().strip().splitlines()
                new_lines = []
                for line in lines:
                    if not line.strip():
                        continue
                    parts = line.split()
                    local_cls = int(parts[0])
                    master_cls = local_to_master.get(local_cls)
                    if master_cls is None:
                        continue
                    new_lines.append(f"{master_cls} " + " ".join(parts[1:]))
                (out_lbl_dir / new_lbl_name).write_text("\n".join(new_lines))
                total_labels += 1
            else:
                # Write empty label file if no annotation exists
                (out_lbl_dir / new_lbl_name).write_text("")

        print(f"  {split}: {len(images)} images copied")

print(f"\nTotal images copied : {total_images}")
print(f"Total labels written: {total_labels}")

# ── WRITE COMBINED YAML ───────────────────────────────────────────────────────
yaml_content = f"""train: ../train/images
val: ../valid/images
test: ../test/images

nc: {len(MASTER_NAMES)}
names: {MASTER_NAMES}

# ALLINONE — Combined dataset
# Sources:
#   Cotton  : https://universe.roboflow.com/disease-detection-wounm/cotton-disease-detection-xevxs/dataset/1
#   Rice    : https://universe.roboflow.com/deep-learning-q7eui/rice-disease-eq1pq/dataset/8
#   Tomato  : https://universe.roboflow.com/aryan-rajvanshi-xvuyg/crop-disease-axhjj/dataset/1
#   Wheat   : https://universe.roboflow.com/wheatdisease/wheat-disease-efcmq/dataset/1
"""

yaml_path = OUT_ROOT / "data.yaml"
yaml_path.write_text(yaml_content)
print(f"\nWrote combined data.yaml to {yaml_path}")

print("\n✓ Done. Master classes:")
for i, name in enumerate(MASTER_NAMES):
    print(f"  {i:2d}: {name}")
