import cv2
import numpy as np
import os
import pandas as pd
from pathlib import Path

def calculate_severity_from_boxes(img, boxes):
    """
    Calculate disease severity directly from an image array and bounding boxes
    boxes format: [{'class': int, 'bbox': [x1, y1, x2, y2]}]
    """
    if img is None:
        return None
        
    height, width = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Leaf mask
    lower_green = np.array([15, 30, 30])
    upper_green = np.array([90, 255, 255])
    
    leaf_mask = cv2.inRange(hsv, lower_green, upper_green)
    total_leaf_pixels = cv2.countNonZero(leaf_mask)
    
    if total_leaf_pixels == 0:
        return None
        
    if not boxes:
        return None
        
    # Disease detection
    lower_brown = np.array([10, 50, 50]) # Using original values
    upper_brown = np.array([30, 255, 255])
    
    results = []
    for box in boxes:
        x1, y1, x2, y2 = box['bbox']
        
        # Ensure within bounds
        x1, y1 = max(0, int(x1)), max(0, int(y1))
        x2, y2 = min(width, int(x2)), min(height, int(y2))
        
        if x2 <= x1 or y2 <= y1:
            results.append({
                'class': box['class'],
                'severity': 0.0,
                'disease_pixels': 0,
                'total_leaf_pixels': total_leaf_pixels,
            })
            continue
            
        roi = hsv[y1:y2, x1:x2]
        
        disease_mask = cv2.inRange(roi, lower_brown, upper_brown)
        disease_pixels = cv2.countNonZero(disease_mask)
        
        severity = (disease_pixels / total_leaf_pixels) * 100
        
        results.append({
            'class': box['class'],
            'severity': round(severity, 2),
            'disease_pixels': disease_pixels,
            'total_leaf_pixels': total_leaf_pixels,
        })
        
    return results

def calculate_severity(image_path, txt_path):
    """
    Calculate disease severity from image and bounding boxes
    """
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Cannot load {image_path}")
        return None
    
    height, width = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Leaf mask (your working values)
    lower_green = np.array([15, 30, 30])
    upper_green = np.array([90, 255, 255])
    
    leaf_mask = cv2.inRange(hsv, lower_green, upper_green)
    total_leaf_pixels = cv2.countNonZero(leaf_mask)
    
    if total_leaf_pixels == 0:
        print(f"No leaf detected in {image_path}")
        return None
    
    # Read bounding boxes
    boxes = []
    with open(txt_path, 'r') as f:
        for line in f:
            values = line.strip().split()
            if len(values) >= 5:
                class_id = int(float(values[0]))
                x_center = float(values[1]) * width
                y_center = float(values[2]) * height
                w = float(values[3]) * width
                h = float(values[4]) * height
                
                x1 = int(x_center - w/2)
                y1 = int(y_center - h/2)
                x2 = int(x_center + w/2)
                y2 = int(y_center + h/2)
                
                # Ensure within image
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)
                
                if x2 > x1 and y2 > y1:
                    boxes.append({
                        'class': class_id,
                        'bbox': [x1, y1, x2, y2]
                    })
    
    if not boxes:
        print(f"No valid boxes in {image_path}")
        return None
    
    # Disease detection
    lower_brown = np.array([10, 50, 50])
    upper_brown = np.array([30, 255, 255])
    
    results = []
    for box in boxes:
        x1, y1, x2, y2 = box['bbox']
        roi = hsv[y1:y2, x1:x2]
        
        disease_mask = cv2.inRange(roi, lower_brown, upper_brown)
        disease_pixels = cv2.countNonZero(disease_mask)
        
        severity = (disease_pixels / total_leaf_pixels) * 100
        
        results.append({
            'image_path': image_path,
            'class': box['class'],
            'severity': round(severity, 2),
            'disease_pixels': disease_pixels,
            'total_leaf_pixels': total_leaf_pixels,
            'bbox': str(box['bbox'])
        })
    
    return results

def process_dataset(image_folder, txt_folder, output_csv="severity_results.csv"):
    """
    Process all images in a folder and save results to CSV
    """
    # Get all images
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        image_files.extend(Path(image_folder).glob(ext))
    
    print(f"\nFound {len(image_files)} images")
    
    all_results = []
    
    # Process each image
    for img_path in image_files:
        txt_path = Path(txt_folder) / (img_path.stem + '.txt')
        
        if not txt_path.exists():
            print(f"⚠️  No txt file for {img_path.name}")
            continue
        
        print(f"Processing: {img_path.name}")
        
        results = calculate_severity(str(img_path), str(txt_path))
        
        if results:
            all_results.extend(results)
            print(f"  ✅ Added {len(results)} detections")
    
    # Save to CSV
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv(output_csv, index=False)
        print(f"\n✅ Saved {len(all_results)} results to {output_csv}")
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"Total detections: {len(df)}")
        print(f"Classes found: {sorted(df['class'].unique())}")
        print(f"Average severity: {df['severity'].mean():.2f}%")
        
        return df
    else:
        print("\n❌ No results to save")
        return None

if __name__ == '__main__':
    # Set your folders
    image_folder = "C:/Users/krish/OneDrive/Documents/astrava/images"  # Folder with all your images
    txt_folder = "C:/Users/kris/OneDrive/Documents/astrava/labels" # Folder with all your txt files

    # Process everything
    results_df = process_dataset(
        image_folder=image_folder,
        txt_folder=txt_folder,
        output_csv="severity_results.csv"
    )
