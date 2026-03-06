import os
from pathlib import Path

# ── CONFIG ───────────────────────────────────────────────────────────────────
DATASET_ROOT = r"C:\Users\Aditya Vineeth\Desktop\astrava\DATASET\wheat"

# ── OLD → NEW CLASS MAPPING ──────────────────────────────────────────────────
# 0: Powdery_Mildew  → wheat_powdery_mildew
# 1: Septoria        → wheat_septoria_leaf_blotch
# 2: Stem_Rust       → wheat_stem_rust
# 3: Yellow_Rust     → wheat_yellow_rust

OLD_TO_NEW = {
    0: 0,
    1: 1,
    2: 2,
    3: 3,
}

NEW_NAMES = [
    "wheat_powdery_mildew",
    "wheat_septoria_leaf_blotch",
    "wheat_stem_rust",
    "wheat_yellow_rust",
]

# ── PATHS ────────────────────────────────────────────────────────────────────
root       = Path(DATASET_ROOT)
label_dirs = [
    root / "train" / "labels",
    root / "valid" / "labels",
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

nc: {len(NEW_NAMES)}
names: {NEW_NAMES}

# Remapped from original Powdery_Mildew / Septoria / Stem_Rust / Yellow_Rust
# Source: https://universe.roboflow.com/wheatdisease/wheat-disease-efcmq/dataset/1
"""

yaml_path = root / "data.yaml"
yaml_path.write_text(yaml_content)
print(f"\nWrote updated data.yaml to {yaml_path}")

print("\n✓ Done. Classes:")
for i, name in enumerate(NEW_NAMES):
    print(f"  {i}: {name}")
