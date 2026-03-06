import os
from pathlib import Path

# ── CONFIG ───────────────────────────────────────────────────────────────────
DATASET_ROOT = r"C:\Users\Aditya Vineeth\Desktop\astrava\DATASET\cotton"

# ── OLD → NEW CLASS MAPPING ──────────────────────────────────────────────────
# 0: blight       → cotton_bacterial_blight
# 1: curl         → cotton_leaf_curl_virus
# 2: grey mildew  → cotton_grey_mildew
# 3: healthy      → cotton_healthy
# 4: leaf spot    → cotton_alternaria_leaf_spot
# 5: wilt         → cotton_wilt (ambiguous between verticillium/fusarium, keeping generic)

OLD_TO_NEW = {
    0: 0,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
}

NEW_NAMES = [
    "cotton_bacterial_blight",
    "cotton_leaf_curl_virus",
    "cotton_grey_mildew",
    "cotton_healthy",
    "cotton_alternaria_leaf_spot",
    "cotton_wilt",
]

# ── PATHS ────────────────────────────────────────────────────────────────────
root       = Path(DATASET_ROOT)
label_dirs = [
    root / "train" / "labels",
    root / "valid" / "labels",
    root / "test"  / "labels",
]

# ── REMAP LABELS ─────────────────────────────────────────────────────────────
def remap_labels(label_dir: Path):
    if not label_dir.exists():
        print(f"  SKIP (not found): {label_dir}")
        return
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

for d in label_dirs:
    remap_labels(d)

# ── WRITE NEW YAML ────────────────────────────────────────────────────────────
yaml_content = f"""train: ../train/images
val: ../valid/images
test: ../test/images

nc: {len(NEW_NAMES)}
names: {NEW_NAMES}

# Remapped from original: blight / curl / grey mildew / healthy / leaf spot / wilt
# Note: grey mildew added to master class list (not in original brief)
# Note: wilt kept generic — dataset does not distinguish verticillium vs fusarium
# Source: https://universe.roboflow.com/disease-detection-wounm/cotton-disease-detection-xevxs/dataset/1
"""

yaml_path = root / "data.yaml"
yaml_path.write_text(yaml_content)
print(f"\nWrote updated data.yaml to {yaml_path}")

print("\n✓ Done. Classes:")
for i, name in enumerate(NEW_NAMES):
    print(f"  {i}: {name}")
