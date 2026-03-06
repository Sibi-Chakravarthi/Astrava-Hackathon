# =============================================================================
# AgraVision — Multi-Crop Disease Detection API
# Flask backend for drone-based crop disease detection system
# =============================================================================

import os
import uuid
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Our modules
from severity import analyze_severity, generate_field_heatmap
from recommendations import get_recommendation, get_all_diseases

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Global model variable — loaded once at startup
model = None
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'best.pt')


def load_model():
    """Load the YOLOv11 classification model."""
    global model
    try:
        from ultralytics import YOLO
        if os.path.exists(MODEL_PATH):
            model = YOLO(MODEL_PATH)
            print(f"[OK] Model loaded from {MODEL_PATH}")
        else:
            print(f"[WARN] Model not found at {MODEL_PATH}")
            print("   Place your trained best.pt in the project root.")
            print("   Running in DEMO MODE with simulated predictions")
            model = None
    except Exception as e:
        print(f"[ERR] Error loading model: {e}")
        model = None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def predict_disease(image_path):
    """
    Run disease detection on an image.
    Returns: (dominant_class, confidence, detections_list)
    detections_list contains all detected objects with bboxes.
    """
    if model is not None:
        # Real model inference — OBJECT DETECTION
        results = model.predict(source=image_path, verbose=False, conf=0.25)
        result = results[0]
        boxes = result.boxes

        if len(boxes) == 0:
            return "unknown", 0.0, [{"class": "No disease detected", "confidence": 0}]

        # Collect all detections
        detections = []
        class_counts = {}
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = result.names[cls_id]
            xyxy = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

            detections.append({
                "class": class_name,
                "confidence": round(conf * 100, 1),
                "bbox": [round(c, 1) for c in xyxy]
            })

            if class_name not in class_counts:
                class_counts[class_name] = {"count": 0, "total_conf": 0}
            class_counts[class_name]["count"] += 1
            class_counts[class_name]["total_conf"] += conf

        # Find dominant disease (most frequent, highest avg confidence)
        dominant = max(class_counts.items(),
                       key=lambda x: (x[1]["count"], x[1]["total_conf"] / x[1]["count"]))
        dominant_class = dominant[0]
        dominant_conf = dominant[1]["total_conf"] / dominant[1]["count"]

        # Build top-N summary sorted by count then confidence
        top5 = []
        for cls_name, info in sorted(class_counts.items(),
                                      key=lambda x: (x[1]["count"], x[1]["total_conf"]),
                                      reverse=True)[:5]:
            avg_conf = info["total_conf"] / info["count"]
            top5.append({
                "class": cls_name,
                "confidence": round(avg_conf * 100, 1),
                "count": info["count"]
            })

        return dominant_class, dominant_conf, top5
    else:
        # Demo mode — simulate detection with actual 23-class dataset labels
        import random
        demo_classes = [
            "cotton_bacterial_blight", "cotton_leaf_curl_virus", "cotton_grey_mildew",
            "cotton_healthy", "cotton_alternaria_leaf_spot", "cotton_wilt",
            "rice_grain_discoloration", "rice_leaf_blight", "rice_pesticide_residue", "rice_blast",
            "tomato_early_blight", "tomato_septoria_leaf_spot", "tomato_healthy",
            "tomato_bacterial_spot", "tomato_late_blight", "tomato_mosaic_virus",
            "tomato_yellow_leaf_curl_virus", "tomato_leaf_mold", "tomato_spider_mite",
            "wheat_powdery_mildew", "wheat_septoria_leaf_blotch", "wheat_stem_rust", "wheat_yellow_rust"
        ]
        chosen = random.choice(demo_classes)
        conf = random.uniform(0.75, 0.98)
        top5 = [{"class": chosen, "confidence": round(conf * 100, 1)}]
        others = random.sample([c for c in demo_classes if c != chosen], 4)
        for o in others:
            c = random.uniform(0.01, 0.15)
            top5.append({"class": o, "confidence": round(c * 100, 1)})
        top5.sort(key=lambda x: x["confidence"], reverse=True)
        return chosen, conf, top5


# ============================================================================
#  ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main dashboard."""
    return send_from_directory('static', 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check."""
    return jsonify({
        "status": "online",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH,
        "timestamp": datetime.now().isoformat(),
        "supported_crops": ["rice", "wheat", "cotton", "tomato"],
        "total_diseases": len(get_all_diseases())
    })


@app.route('/api/diseases', methods=['GET'])
def list_diseases():
    """List all supported diseases."""
    return jsonify({"diseases": get_all_diseases()})


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Upload a single image for disease prediction.
    Returns disease classification + severity analysis + recommendations.
    """
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided. Use 'image' form field."}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}"}), 400
    
    # Save uploaded file
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        start_time = time.time()
        
        # 1. Run disease classification
        disease_class, confidence, top5 = predict_disease(filepath)
        
        # 2. Run severity analysis
        severity_result = analyze_severity(image_path=filepath)
        
        # 3. Get recommendations
        recommendation = get_recommendation(disease_class, severity_result['severity_percent'])
        
        inference_time = round(time.time() - start_time, 3)
        
        response = {
            "success": True,
            "prediction": {
                "disease_class": disease_class,
                "confidence": round(confidence * 100, 1),
                "top5": top5
            },
            "severity": {
                "percent": severity_result['severity_percent'],
                "label": severity_result['severity_label'],
                "healthy_percent": severity_result['healthy_percent'],
                "heatmap": severity_result['heatmap_base64'],
                "annotated": severity_result['annotated_base64']
            },
            "recommendation": recommendation,
            "metadata": {
                "filename": file.filename,
                "inference_time_seconds": inference_time,
                "model_loaded": model is not None,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500
    finally:
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route('/api/analyze-field', methods=['POST'])
def analyze_field():
    """
    Upload multiple images for field-level analysis.
    Returns individual predictions + composite field heatmap.
    """
    if 'images' not in request.files:
        return jsonify({"error": "No images provided. Use 'images' form field with multiple files."}), 400
    
    files = request.files.getlist('images')
    if len(files) == 0:
        return jsonify({"error": "No files selected"}), 400
    
    results = []
    severity_data = []
    saved_files = []
    
    try:
        start_time = time.time()
        
        for file in files:
            if file.filename == '' or not allowed_file(file.filename):
                continue
            
            # Save file
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_files.append(filepath)
            
            # Predict
            disease_class, confidence, top5 = predict_disease(filepath)
            severity_result = analyze_severity(image_path=filepath)
            recommendation = get_recommendation(disease_class, severity_result['severity_percent'])
            
            results.append({
                "filename": file.filename,
                "prediction": {
                    "disease_class": disease_class,
                    "confidence": round(confidence * 100, 1),
                },
                "severity": {
                    "percent": severity_result['severity_percent'],
                    "label": severity_result['severity_label'],
                },
                "recommendation": recommendation
            })
            
            severity_data.append({
                "severity_percent": severity_result['severity_percent']
            })
        
        # Generate field-level heatmap
        field_heatmap = generate_field_heatmap(severity_data)
        
        # Calculate field-level stats
        if severity_data:
            severities = [s['severity_percent'] for s in severity_data]
            field_stats = {
                "total_zones": len(severity_data),
                "average_severity": round(sum(severities) / len(severities), 1),
                "max_severity": round(max(severities), 1),
                "min_severity": round(min(severities), 1),
                "critical_zones": sum(1 for s in severities if s > 55),
                "healthy_zones": sum(1 for s in severities if s < 10),
            }
        else:
            field_stats = {}
        
        total_time = round(time.time() - start_time, 3)
        
        return jsonify({
            "success": True,
            "field_heatmap": field_heatmap,
            "field_stats": field_stats,
            "zone_results": results,
            "metadata": {
                "total_images": len(results),
                "total_time_seconds": total_time,
                "model_loaded": model is not None,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500
    finally:
        # Clean up
        for fp in saved_files:
            if os.path.exists(fp):
                os.remove(fp)


# ============================================================================
#  MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("  AgraVision -- Multi-Crop Disease Detection System")
    print("=" * 60)
    load_model()
    print(f"\n[*] Starting server at http://localhost:5000")
    print(f"[*] Dashboard: http://localhost:5000")
    print(f"[*] API Health: http://localhost:5000/api/health\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
