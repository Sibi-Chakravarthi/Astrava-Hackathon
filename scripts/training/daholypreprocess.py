"""
Unified dataset pipeline for:
 - augmentation (albumentations)
 - splitting images by class (one image may go to multiple class folders)
 - train/val/test split (ensures augmented images never go to test)

Configuration: change the booleans and path variables below.
"""

import os
import random
import shutil
import cv2
import numpy as np
import albumentations as albu

# ---------------------------
# USER CONFIG (change these)
# ---------------------------
DO_AUGMENT = True                # Run augmentation step
DO_SPLIT_BY_CLASS = True         # Run split-by-class step
DO_TRAIN_VAL_TEST_SPLIT = True   # Run train/val/test split

# Paths - update to your project root
PROJECT_ROOT = r"E:\eocprojectsibi"    # <-- change if needed
IMAGES_DIR = os.path.join(PROJECT_ROOT, "images")       # original images
LABELS_DIR = os.path.join(PROJECT_ROOT, "labels")       # original labels

# Output folders
AUG_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "augmented_by_class")  # per-class augmented outputs
SPLIT_BY_CLASS_DIR = os.path.join(PROJECT_ROOT, "split_by_class")  # images organized per class (original only)
FINAL_SPLIT_DIR = os.path.join(PROJECT_ROOT, "final_dataset")      # train/val/test/class_name

# Augmentation settings
AUG_TARGET_PER_CLASS = None  # integer or None -> if None, script will ask per run or default to existing count
AUG_TRANSFORM = albu.Compose([
    albu.HorizontalFlip(p=0.5),
    albu.VerticalFlip(p=0.2),
    albu.RandomBrightnessContrast(p=0.3),
    albu.GaussianBlur(p=0.1),
    albu.Rotate(limit=15, p=0.3),
    albu.Resize(512, 640)
], bbox_params=albu.BboxParams(format='yolo', label_fields=['class_labels']))

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Train/val/test ratios (must sum to 1.0)
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# ---------------------------
# Helpers
# ---------------------------
def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def list_images(folder):
    return [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

def read_yolo_labels(lbl_path):
    """
    Returns list of (class_id:int, x_center, y_center, w, h) as floats/ints
    """
    boxes = []
    if not os.path.exists(lbl_path):
        return boxes
    with open(lbl_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                cls = int(parts[0])
                x, y, w, h = map(float, parts[1:5])
                boxes.append((cls, x, y, w, h))
    return boxes

def write_yolo_labels(lbl_path, boxes):
    ensure_dir(os.path.dirname(lbl_path))
    with open(lbl_path, 'w') as f:
        for cls, x, y, w, h in boxes:
            f.write(f"{cls} {x} {y} {w} {h}\n")

def clip_bbox_yolo(bbox):
    # bbox is [x_center, y_center, w, h] normalized
    return [
        float(np.clip(bbox[0], 0.0, 1.0)),
        float(np.clip(bbox[1], 0.0, 1.0)),
        float(np.clip(bbox[2], 0.0, 1.0)),
        float(np.clip(bbox[3], 0.0, 1.0))
    ]

# ---------------------------
# STEP A: AUGMENT (per-class)
# ---------------------------
def augment_per_class(classified_folder, output_folder, target_per_class=None, transform=None):
    """
    Input structure (classified_folder):
      <class_folder>/
        images/
          ...jpg
        labels/
          ...txt

    Output: output_folder/<class_name>/images and /labels
    """
    if transform is None:
        raise ValueError("transform must be provided")

    ensure_dir(output_folder)

    # For each class folder
    for class_name in sorted(os.listdir(classified_folder)):
        class_path = os.path.join(classified_folder, class_name)
        if not os.path.isdir(class_path):
            continue

        img_folder = os.path.join(class_path, "images")
        lbl_folder = os.path.join(class_path, "labels")

        existing_images = []
        if os.path.exists(img_folder):
            existing_images = list_images(img_folder)
        num_existing = len(existing_images)

        out_class = os.path.join(output_folder, class_name)
        out_img = os.path.join(out_class, "images")
        out_lbl = os.path.join(out_class, "labels")
        ensure_dir(out_img); ensure_dir(out_lbl)

        if target_per_class is None:
            t = num_existing
        else:
            t = target_per_class

        print(f"[AUG] Class: {class_name} existing={num_existing} target={t}")

        # if there are more existing images than target -> randomly copy target images (no aug)
        if num_existing > t:
            selected = random.sample(existing_images, t)
            for img_name in selected:
                base = os.path.splitext(img_name)[0]
                shutil.copy2(os.path.join(img_folder, img_name), os.path.join(out_img, img_name))
                lbl_src = os.path.join(lbl_folder, base + ".txt")
                if os.path.exists(lbl_src):
                    shutil.copy2(lbl_src, os.path.join(out_lbl, base + ".txt"))

        elif num_existing == t:
            # copy all without augmentation
            for img_name in existing_images:
                base = os.path.splitext(img_name)[0]
                shutil.copy2(os.path.join(img_folder, img_name), os.path.join(out_img, img_name))
                lbl_src = os.path.join(lbl_folder, base + ".txt")
                if os.path.exists(lbl_src):
                    shutil.copy2(lbl_src, os.path.join(out_lbl, base + ".txt"))

        else:
            # copy all originals first
            for img_name in existing_images:
                base = os.path.splitext(img_name)[0]
                shutil.copy2(os.path.join(img_folder, img_name), os.path.join(out_img, img_name))
                lbl_src = os.path.join(lbl_folder, base + ".txt")
                if os.path.exists(lbl_src):
                    shutil.copy2(lbl_src, os.path.join(out_lbl, base + ".txt"))

            # generate needed augmented images
            needed = t - num_existing
            if num_existing == 0:
                print(f"[AUG] WARNING: no source images found for class {class_name}, skipping augmentation.")
                continue

            for i in range(needed):
                img_name = random.choice(existing_images)
                base = os.path.splitext(img_name)[0]
                img_path = os.path.join(img_folder, img_name)
                lbl_path = os.path.join(lbl_folder, base + ".txt")

                image = cv2.imread(img_path)
                if image is None:
                    print(f"[AUG] failed to read {img_path}, skipping")
                    continue

                boxes = read_yolo_labels(lbl_path)
                if not boxes:
                    print(f"[AUG] no boxes found for {img_name}, skipping augmentation for this image")
                    continue

                bboxes = [ [x,y,w,h] for (_, x,y,w,h) in boxes ]
                class_labels = [ int(c) for (c,_,_,_,_) in boxes ]

                try:
                    augmented = transform(image=image, bboxes=bboxes, class_labels=class_labels)
                except Exception as e:
                    print(f"[AUG] albumentations failed for {img_name}: {e}")
                    continue

                aug_img = augmented['image']
                aug_bboxes = augmented['bboxes']  # list of [x,y,w,h]
                aug_bboxes = [clip_bbox_yolo(bb) for bb in aug_bboxes]

                new_name = f"{base}_aug_{i}.jpg"
                new_lbl = f"{base}_aug_{i}.txt"

                cv2.imwrite(os.path.join(out_img, new_name), aug_img)
                # zipped class_labels and aug_bboxes
                with open(os.path.join(out_lbl, new_lbl), 'w') as f:
                    for cls, bb in zip(class_labels, aug_bboxes):
                        f.write(f"{cls} {bb[0]} {bb[1]} {bb[2]} {bb[3]}\n")

            print(f"[AUG] Generated {needed} augmented images for class {class_name}")

    print("[AUG] Completed augmentation step.")

# ---------------------------
# STEP B: SPLIT BY CLASS
# ---------------------------
def split_images_by_class(images_dir, labels_dir, output_dir):
    """
    Splits dataset by class:
    Each class gets:
      output_dir/class_X/images/
      output_dir/class_X/labels/
    """

    ensure_dir(output_dir)

    label_files = [f for f in os.listdir(labels_dir) if f.endswith(".txt")]
    print(f"[SPLIT_BY_CLASS] Found {len(label_files)} label files")

    for label_file in label_files:
        label_path = os.path.join(labels_dir, label_file)
        base = os.path.splitext(label_file)[0]

        # load classes in that label
        class_ids = []
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 1:
                    class_ids.append(parts[0])

        if len(class_ids) == 0:
            print(f"[SPLIT_BY_CLASS] WARNING: no classes in {label_file}, skipping")
            continue

        # find the matching image
        image_path = None
        for ext in [".jpg", ".jpeg", ".png"]:
            candidate = os.path.join(images_dir, base + ext)
            if os.path.exists(candidate):
                image_path = candidate
                break

        if image_path is None:
            print(f"[SPLIT_BY_CLASS] WARNING: missing image for {label_file}, skipping")
            continue

        # copy image + label into each class folder
        for cid in class_ids:
            class_folder = os.path.join(output_dir, f"class_{cid}")
            img_out = os.path.join(class_folder, "images")
            lbl_out = os.path.join(class_folder, "labels")

            ensure_dir(img_out)
            ensure_dir(lbl_out)

            # copy the image
            shutil.copy2(image_path, os.path.join(img_out, os.path.basename(image_path)))

            # copy the label
            shutil.copy2(label_path, os.path.join(lbl_out, label_file))

        print(f"[SPLIT_BY_CLASS] {label_file} → classes {class_ids}")

    print("[SPLIT_BY_CLASS] Done.")



# ---------------------------
# STEP C: TRAIN/VAL/TEST SPLIT
# ---------------------------
def split_dataset_train_val_test(source_dir, output_dir, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
        raise ValueError("Ratios must sum to 1.0")

    ensure_dir(output_dir)
    for s in ["train", "val", "test"]:
        ensure_dir(os.path.join(output_dir, s))

    for class_name in sorted(os.listdir(source_dir)):
        class_path = os.path.join(source_dir, class_name)
        if not os.path.isdir(class_path):
            continue

        img_folder = os.path.join(class_path, "images")
        lbl_folder = os.path.join(class_path, "labels")
        if not os.path.exists(img_folder):
            print(f"[SPLIT] no image folder for {class_name}, skipping")
            continue
        images = list_images(img_folder)
        if not images:
            print(f"[SPLIT] no images in {img_folder}, skipping")
            continue

        # separate augmented filenames from originals
        aug_images = [im for im in images if "_aug_" in im]
        orig_images = [im for im in images if "_aug_" not in im]

        # Shuffle independently
        random.shuffle(aug_images)
        random.shuffle(orig_images)

        # We enforce: test set should NOT contain augmented images.
        # We'll split original images across train/val/test, and then distribute aug_images only to train/val.
        total_orig = len(orig_images)
        train_end = int(total_orig * train_ratio)
        val_end = train_end + int(total_orig * val_ratio)

        train_orig = orig_images[:train_end]
        val_orig = orig_images[train_end:val_end]
        test_orig = orig_images[val_end:]

        # Now assign augmented images: proportionally to train/val only (no test)
        total_aug = len(aug_images)
        # If no originals exist, we still need to put aug images somewhere: put into train/val only.
        aug_train_count = int(total_aug * (train_ratio / (train_ratio + val_ratio))) if (train_ratio + val_ratio) > 0 else total_aug
        aug_train = aug_images[:aug_train_count]
        aug_val = aug_images[aug_train_count:]

        # final lists
        train_imgs = train_orig + aug_train
        val_imgs = val_orig + aug_val
        test_imgs = test_orig  # guaranteed no aug images

        # create class folders inside final output WITH images/ and labels/
        for split in ["train", "val", "test"]:
            ensure_dir(os.path.join(output_dir, split, class_name, "images"))
            ensure_dir(os.path.join(output_dir, split, class_name, "labels"))

        def copy_list(lst, split_name):
            for img_name in lst:
                src_img = os.path.join(img_folder, img_name)
                src_lbl = os.path.join(lbl_folder, os.path.splitext(img_name)[0] + ".txt")
                dst_img = os.path.join(output_dir, split_name, class_name, "images", img_name)
                dst_lbl = os.path.join(output_dir, split_name, class_name, "labels", os.path.splitext(img_name)[0] + ".txt")
                shutil.copy2(src_img, dst_img)
                if os.path.exists(src_lbl):
                    shutil.copy2(src_lbl, dst_lbl)

        copy_list(train_imgs, "train")
        copy_list(val_imgs, "val")
        copy_list(test_imgs, "test")

        print(f"[SPLIT] {class_name} → {len(train_imgs)} train, {len(val_imgs)} val, {len(test_imgs)} test (aug in train/val: {len(aug_train)+len(aug_val)})")

    print("[SPLIT] Train/Val/Test split complete.")

# =============================
#          MAIN LOOP
# =============================
if __name__ == "__main__":
    print("===== PIPELINE CONFIG =====")
    print(" DO_SPLIT_BY_CLASS =", DO_SPLIT_BY_CLASS)
    print(" DO_AUGMENT =", DO_AUGMENT)
    print(" DO_TRAIN_VAL_TEST_SPLIT =", DO_TRAIN_VAL_TEST_SPLIT)
    print(" PROJECT_ROOT =", PROJECT_ROOT)
    print(" IMAGES_DIR =", IMAGES_DIR)
    print(" LABELS_DIR =", LABELS_DIR)
    print(" SPLIT_BY_CLASS_DIR =", SPLIT_BY_CLASS_DIR)
    print(" AUG_OUTPUT_DIR =", AUG_OUTPUT_DIR)
    print(" FINAL_SPLIT_DIR =", FINAL_SPLIT_DIR)
    print("===========================\n")

    # ----------------------------------------------------
    # 1) SPLIT-BY-CLASS  (ALWAYS RUNS BEFORE AUGMENT)
    # ----------------------------------------------------
    if DO_SPLIT_BY_CLASS:
        print("[MAIN] Running split_by_class...")
        ensure_dir(SPLIT_BY_CLASS_DIR)
        split_images_by_class(IMAGES_DIR, LABELS_DIR, SPLIT_BY_CLASS_DIR)
        print("[MAIN] split_by_class completed.\n")
    else:
        # If not asked but needed for augmentation, create anyway
        if DO_AUGMENT and not os.path.isdir(SPLIT_BY_CLASS_DIR):
            print("[AUTO] split_by_class folder missing, creating it automatically...")
            ensure_dir(SPLIT_BY_CLASS_DIR)
            split_images_by_class(IMAGES_DIR, LABELS_DIR, SPLIT_BY_CLASS_DIR)
            print("[AUTO] split_by_class created.\n")

    # ----------------------------------------------------
    # 2) AUGMENTATION (NOW SAFE — FOLDER ALWAYS EXISTS)
    # ----------------------------------------------------
    if DO_AUGMENT:
        ensure_dir(AUG_OUTPUT_DIR)

        # Determine target count
        target = AUG_TARGET_PER_CLASS

        # If None → ASK the user
        if target is None:
            try:
                user_in = input("Enter how many images you want per class (target_per_class): ")
                target = int(user_in)
            except:
                print("[WARN] Invalid input. Falling back to auto mode.")
                counts = []
                for c in os.listdir(SPLIT_BY_CLASS_DIR):
                    img_dir = os.path.join(SPLIT_BY_CLASS_DIR, c, "images")
                    if os.path.isdir(img_dir):
                        counts.append(len(list_images(img_dir)))
                target = max(counts) if counts else 0

        print(f"[MAIN] Using target_per_class = {target}")

        print("[MAIN] Running augmentation...")
        augment_per_class(
            SPLIT_BY_CLASS_DIR,
            AUG_OUTPUT_DIR,
            target_per_class=target,
            transform=AUG_TRANSFORM
        )
        print("[MAIN] Augmentation completed.\n")

    # ----------------------------------------------------
    # 3) FINAL TRAIN/VAL/TEST SPLIT
    # ----------------------------------------------------
    if DO_TRAIN_VAL_TEST_SPLIT:
        # Choose source directory:
        source_for_final = (
            AUG_OUTPUT_DIR if (DO_AUGMENT and os.path.isdir(AUG_OUTPUT_DIR))
            else SPLIT_BY_CLASS_DIR
        )

        print(f"[MAIN] Final split using: {source_for_final}")
        ensure_dir(FINAL_SPLIT_DIR)

        split_dataset_train_val_test(
            source_for_final,
            FINAL_SPLIT_DIR,
            TRAIN_RATIO,
            VAL_RATIO,
            TEST_RATIO
        )

        print("[MAIN] Final train/val/test split completed.\n")

    print("===== PIPELINE FINISHED SUCCESSFULLY =====")
