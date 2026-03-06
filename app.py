import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template
import base64
from ultralytics import YOLO
import sys

# Import custom modules
try:
    from modules.severity import calculate_severity_from_boxes
    from modules.recommendation import recommend
except ImportError as e:
    print(f"Warning: Could not import custom modules: {e}")
    # Will define a dummy if needed, but assuming they will be present

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max upload

# Patch torch.load for PyTorch 2.6+ to fix older weights loading
import torch
import functools
original_load = torch.load
def safe_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_load(*args, **kwargs)
torch.load = safe_load

# Load YOLO model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'best.pt')
try:
    model = YOLO(MODEL_PATH)
    print("YOLO model loaded successfully!")
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    model = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        try:
            # Read image
            in_memory_file = file.read()
            nparr = np.frombuffer(in_memory_file, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return jsonify({'error': 'Invalid image format'}), 400

            # 1. Run inference
            if model is None:
                return jsonify({'error': 'Model not loaded'}), 500
                
            results = model.predict(source=img, save=False, conf=0.25) # Adjust conf if needed
            result = results[0]
            
            # Format boxes for severity calculation
            # format needed: [{'class': int, 'bbox': [x1, y1, x2, y2]}, ...]
            boxes_formatted = []
            
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                cls_id = int(box.cls[0].item())
                boxes_formatted.append({
                    'class': cls_id,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })

            # 2. Calculate Severity
            severity_results = calculate_severity_from_boxes(img, boxes_formatted)
            
            final_predictions = []
            names = result.names # class map
            
            if severity_results is None:
                severity_results = []
                
            for i, box_info in enumerate(boxes_formatted):
                cls_id = box_info['class']
                cls_name = names.get(cls_id, f"class_{cls_id}")
                
                # Find corresponding severity 
                # (Assuming order is preserved or we map by index/bbox)
                severity_score = 0.0
                if i < len(severity_results):
                    severity_score = severity_results[i].get('severity', 0.0)
                
                # 3. Get Recommendation
                rec_data = recommend(cls_name)
                
                final_predictions.append({
                    'class_id': int(cls_id),
                    'class_name': str(cls_name),
                    'bbox': box_info['bbox'],
                    'severity': float(severity_score),
                    'recommendation': str(rec_data.get('recommendation', 'Consult agronomist.')),
                    'source': str(rec_data.get('source', ''))
                })
                
                # Draw bounding box on image
                x1, y1, x2, y2 = box_info['bbox']
                color = (0, 0, 255) if "healthy" not in cls_name.lower() else (0, 255, 0)
                # Ensure x1, y1, x2, y2 are ints
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                
                # Dynamic text sizing
                height, width = img.shape[:2]
                font_scale = min(width, height) / 1000.0
                thickness = max(1, int(font_scale * 2))
                
                label = f"{cls_name} ({severity_score:.1f}%)"
                (label_width, label_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                cv2.rectangle(img, (x1, y1 - label_height - baseline - 5), (x1 + label_width, y1), color, -1)
                cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

            # Convert processed image to base64
            _, buffer = cv2.imencode('.jpg', img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            return jsonify({
                'success': True,
                'image': f'data:image/jpeg;base64,{img_base64}',
                'predictions': final_predictions
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
