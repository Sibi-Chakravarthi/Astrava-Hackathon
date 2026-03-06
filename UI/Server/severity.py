# =============================================================================
# Pixel-Based Severity Analysis for Crop Disease
# Uses OpenCV color segmentation to estimate diseased area percentage
# =============================================================================

import cv2
import numpy as np
import base64
from io import BytesIO


def analyze_severity(image_path: str = None, image_bytes: bytes = None) -> dict:
    """
    Analyze disease severity from an image using color segmentation.
    Detects brown/yellow/black diseased regions vs healthy green tissue.
    
    Args:
        image_path: Path to the image file
        image_bytes: Raw image bytes (alternative to image_path)
    
    Returns:
        dict with severity_percent, heatmap_base64, and analysis details
    """
    # Load image
    if image_bytes is not None:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    elif image_path is not None:
        img = cv2.imread(image_path)
    else:
        raise ValueError("Provide either image_path or image_bytes")

    if img is None:
        return {"severity_percent": 0, "error": "Could not load image"}

    # Resize for consistent analysis
    h, w = img.shape[:2]
    max_dim = 640
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    # Convert to HSV for color-based segmentation
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # --- Define color masks ---
    
    # Healthy green tissue
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([90, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Diseased regions: brown/tan spots
    lower_brown = np.array([8, 40, 40])
    upper_brown = np.array([25, 255, 200])
    brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
    
    # Diseased regions: yellow/chlorosis
    lower_yellow = np.array([15, 80, 100])
    upper_yellow = np.array([35, 255, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Diseased regions: dark/necrotic spots
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, 60])
    dark_mask = cv2.inRange(hsv, lower_dark, upper_dark)
    
    # Combine diseased masks
    diseased_mask = cv2.bitwise_or(brown_mask, yellow_mask)
    diseased_mask = cv2.bitwise_or(diseased_mask, dark_mask)
    
    # Plant tissue mask (green + diseased = total plant area)
    plant_mask = cv2.bitwise_or(green_mask, diseased_mask)
    
    # Morphological operations to clean up masks
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    plant_mask = cv2.morphologyEx(plant_mask, cv2.MORPH_CLOSE, kernel)
    diseased_mask = cv2.morphologyEx(diseased_mask, cv2.MORPH_CLOSE, kernel)
    
    # Calculate areas
    total_plant_pixels = cv2.countNonZero(plant_mask)
    diseased_pixels = cv2.countNonZero(diseased_mask)
    
    # Avoid division by zero
    if total_plant_pixels == 0:
        severity_percent = 0
    else:
        severity_percent = (diseased_pixels / total_plant_pixels) * 100
        severity_percent = min(severity_percent, 100)
    
    # Generate severity heatmap overlay
    heatmap = _generate_heatmap(img, diseased_mask, green_mask)
    heatmap_b64 = _image_to_base64(heatmap)
    
    # Generate annotated image
    annotated = _generate_annotated(img, diseased_mask, severity_percent)
    annotated_b64 = _image_to_base64(annotated)
    
    return {
        "severity_percent": round(severity_percent, 1),
        "healthy_percent": round(100 - severity_percent, 1) if total_plant_pixels > 0 else 0,
        "total_plant_pixels": int(total_plant_pixels),
        "diseased_pixels": int(diseased_pixels),
        "heatmap_base64": heatmap_b64,
        "annotated_base64": annotated_b64,
        "severity_label": _severity_label(severity_percent)
    }


def _generate_heatmap(original, diseased_mask, healthy_mask):
    """Generate a color-coded heatmap overlay showing disease distribution."""
    # Create overlay
    overlay = original.copy()
    
    # Color healthy areas green (semi-transparent)
    green_overlay = np.zeros_like(original)
    green_overlay[healthy_mask > 0] = [0, 200, 0]  # Green
    
    # Color diseased areas on a gradient (yellow → orange → red)
    # Use distance transform for intensity gradient
    if cv2.countNonZero(diseased_mask) > 0:
        # Create heat gradient based on local disease density
        blurred = cv2.GaussianBlur(diseased_mask.astype(np.float32), (31, 31), 0)
        blurred_norm = cv2.normalize(blurred, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Apply colormap (COLORMAP_JET: blue=low, red=high)
        heat_colored = cv2.applyColorMap(blurred_norm, cv2.COLORMAP_JET)
        
        # Only apply where disease exists
        disease_heat = np.zeros_like(original)
        disease_heat[diseased_mask > 0] = heat_colored[diseased_mask > 0]
        
        # Blend
        overlay = cv2.addWeighted(original, 0.5, green_overlay, 0.3, 0)
        overlay = cv2.addWeighted(overlay, 0.7, disease_heat, 0.5, 0)
    else:
        overlay = cv2.addWeighted(original, 0.6, green_overlay, 0.4, 0)
    
    return overlay


def _generate_annotated(original, diseased_mask, severity):
    """Generate annotated image with contours around diseased areas."""
    annotated = original.copy()
    
    # Find contours of diseased regions
    contours, _ = cv2.findContours(diseased_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw contours
    color = (0, 0, 255) if severity > 50 else (0, 165, 255) if severity > 25 else (0, 255, 255)
    cv2.drawContours(annotated, contours, -1, color, 2)
    
    # Add severity text
    label = f"Severity: {severity:.1f}%"
    h, w = annotated.shape[:2]
    cv2.rectangle(annotated, (5, 5), (280, 45), (0, 0, 0), -1)
    cv2.putText(annotated, label, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    
    return annotated


def _image_to_base64(img):
    """Convert OpenCV image to base64 string."""
    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(buffer).decode('utf-8')


def _severity_label(percent):
    """Convert percentage to severity label."""
    if percent < 10:
        return "minimal"
    elif percent < 25:
        return "low"
    elif percent < 55:
        return "moderate"
    elif percent < 80:
        return "high"
    else:
        return "critical"


def generate_field_heatmap(image_analyses: list, grid_cols: int = 4) -> str:
    """
    Generate a field-level heatmap from multiple image analyses.
    Creates a grid showing severity across different areas of the field.
    
    Args:
        image_analyses: List of dicts with 'severity_percent' and optional 'position'
        grid_cols: Number of columns in the grid
    
    Returns:
        Base64 encoded field heatmap image
    """
    n = len(image_analyses)
    if n == 0:
        return ""
    
    grid_rows = (n + grid_cols - 1) // grid_cols
    cell_size = 120
    padding = 4
    
    img_w = grid_cols * (cell_size + padding) + padding
    img_h = grid_rows * (cell_size + padding) + padding + 60  # Extra space for legend
    
    # Create white background
    field_map = np.ones((img_h, img_w, 3), dtype=np.uint8) * 30  # Dark background
    
    for idx, analysis in enumerate(image_analyses):
        row = idx // grid_cols
        col = idx % grid_cols
        
        x = col * (cell_size + padding) + padding
        y = row * (cell_size + padding) + padding
        
        severity = analysis.get("severity_percent", 0)
        color = _severity_to_color(severity)
        
        # Draw cell
        cv2.rectangle(field_map, (x, y), (x + cell_size, y + cell_size), color, -1)
        cv2.rectangle(field_map, (x, y), (x + cell_size, y + cell_size), (60, 60, 60), 1)
        
        # Add severity text
        text = f"{severity:.0f}%"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = x + (cell_size - text_size[0]) // 2
        text_y = y + (cell_size + text_size[1]) // 2
        cv2.putText(field_map, text, (text_x, text_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Add zone label
        zone_text = f"Zone {idx + 1}"
        zone_size = cv2.getTextSize(zone_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
        zone_x = x + (cell_size - zone_size[0]) // 2
        cv2.putText(field_map, zone_text, (zone_x, y + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # Add legend at bottom
    legend_y = grid_rows * (cell_size + padding) + padding + 10
    legend_items = [
        ("Healthy", (0, 180, 0)), ("Low", (0, 220, 220)),
        ("Moderate", (0, 140, 255)), ("High", (0, 60, 255)), ("Critical", (0, 0, 200))
    ]
    legend_x = padding
    for label, color in legend_items:
        cv2.rectangle(field_map, (legend_x, legend_y), (legend_x + 15, legend_y + 15), color, -1)
        cv2.putText(field_map, label, (legend_x + 20, legend_y + 13),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
        legend_x += 90
    
    return _image_to_base64(field_map)


def _severity_to_color(severity):
    """Convert severity percentage to BGR color for heatmap."""
    if severity < 10:
        return (0, 180, 0)        # Green - healthy
    elif severity < 25:
        return (0, 220, 220)      # Yellow - low
    elif severity < 55:
        return (0, 140, 255)      # Orange - moderate
    elif severity < 80:
        return (0, 60, 255)       # Red-orange - high
    else:
        return (0, 0, 200)        # Red - critical
