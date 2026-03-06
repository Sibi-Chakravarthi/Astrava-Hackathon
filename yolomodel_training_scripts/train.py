import os
import sys


def main():
    from ultralytics import YOLO
    import torch
    import shutil

    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"GPU: {gpu_name} ({vram:.1f} GB VRAM)")
    else:
        print("WARNING: No GPU detected! Training will be very slow.")

    DATA_YAML = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ALLINONE', 'data.yaml')

    if not os.path.exists(DATA_YAML):
        print(f"ERROR: data.yaml not found at: {DATA_YAML}")
        sys.exit(1)

    print(f"Dataset config: {DATA_YAML}")

    model = YOLO('yolo11s.pt')

    # 4. Train
    print("\n" + "=" * 50)
    print("Starting YOLOv11s Object Detection Training")
    print(f"  23 disease classes across 4 crops")
    print(f"  ~7185 train / ~1127 valid / ~521 test images")
    print("=" * 50 + "\n")

    results = model.train(
        data=DATA_YAML,
        epochs=50,
        imgsz=640,
        batch=16,
        device=0,
        plots=True,
        workers=0,      
        patience=10,
        lr0=0.01,
        augment=True,
        project='runs/detect',
        name='agravision',
        exist_ok=True,
        verbose=True,
    )

    best_path = os.path.join('runs', 'detect', 'agravision', 'weights', 'best.pt')
    if os.path.exists(best_path):
        dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'best.pt')
        shutil.copy2(best_path, dest)
        print(f"\nbest.pt copied to: {dest}")
        print("Restart app.py to use the trained model!")
    else:
        print(f"\nWARNING: best.pt not found at {best_path}")
        print("Check the runs/detect/agravision/weights/ directory.")

    print("\nRunning validation on test set...")
    metrics = model.val(data=DATA_YAML, split='test')
    print(f"mAP50: {metrics.box.map50:.3f}")
    print(f"mAP50-95: {metrics.box.map:.3f}")


if __name__ == '__main__':
    main()
