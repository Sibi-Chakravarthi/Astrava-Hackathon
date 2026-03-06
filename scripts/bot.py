import os
import sys
import cv2
import numpy as np
import torch
import edge_tts
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from ultralytics import YOLO

# Add parent directory to path so we can import custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from modules.severity import calculate_severity_from_boxes
    from modules.recommendation import recommend
except ImportError as e:
    print(f"Error importing modules: {e}")

# Patch torch.load for PyTorch 2.6+ to keep old weights loading
original_load = torch.load
def safe_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_load(*args, **kwargs)
torch.load = safe_load

TOKEN = "8681921369:AAE5wqwkHiNa4qfaJ5s6_czipZvln8QcZE4"

# Load YOLO model
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'best.pt')
try:
    model = YOLO(MODEL_PATH)
    print("YOLO model loaded successfully!")
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    model = None

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey! I'm your agricultural assistant. Please send me an image of a crop leaf, and I'll analyze it for diseases and provide recommendations.")

# Handle text / non-image messages
async def handle_non_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I can only process images! Please send me an image of a crop leaf so I can analyze it.")

# Handle incoming images
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if model is None:
        await update.message.reply_text("Sorry, the detection model is not loaded correctly. Please contact the administrator.")
        return

    # Inform the user that processing has started
    processing_msg = await update.message.reply_text("Processing your image, please wait...")

    try:
        # 1. Download the image
        photo_file = await update.message.photo[-1].get_file()
        image_path = f"temp_image_{update.message.message_id}.jpg"
        audio_path = f"temp_voice_{update.message.message_id}.mp3"
        await photo_file.download_to_drive(image_path)

        # 2. Read the image and run inference
        img = cv2.imread(image_path)
        if img is None:
            await processing_msg.edit_text("Sorry, I couldn't read the image. Please try sending it again.")
            if os.path.exists(image_path): os.remove(image_path)
            return

        results = model.predict(source=img, save=False, conf=0.25)
        result = results[0]

        # 3. Format boxes for severity calculation
        boxes_formatted = []
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            cls_id = int(box.cls[0].item())
            boxes_formatted.append({
                'class': cls_id,
                'bbox': [int(x1), int(y1), int(x2), int(y2)]
            })

        if not boxes_formatted:
            await processing_msg.edit_text("I couldn't detect any specific crop diseases in this image. The plant might be healthy, or the image may be too blurry.")
            if os.path.exists(image_path): os.remove(image_path)
            return

        # 4. Calculate severity
        severity_results = calculate_severity_from_boxes(img, boxes_formatted)
        if severity_results is None:
            severity_results = []

        names = result.names # Class id to name mapping
        
        # 5. Build text response
        detected_issues = []
        for i, box_info in enumerate(boxes_formatted):
            cls_name = names.get(box_info['class'], f"class_{box_info['class']}")
            severity_score = 0.0
            if i < len(severity_results):
                 severity_score = severity_results[i].get('severity', 0.0)
            
            # Formulate readable disease name
            disease_readable = cls_name.replace('_', ' ').title()
            
            # Get Recommendation
            rec_data = recommend(cls_name)
            rec_text = rec_data.get('recommendation', 'Please consult a local agronomist.')

            if "healthy" in cls_name.lower():
                detected_issues.append(f"The leaf appears to be a {disease_readable}.")
            else:
                detected_issues.append(f"I detected {disease_readable} with a severity of {severity_score:.1f} percent. Recommendation: {rec_text}")

        # Remove duplicates while maintaining order
        unique_issues = list(dict.fromkeys(detected_issues))
        final_text = " ".join(unique_issues)
        
        # 6. Generate Voice Data
        await processing_msg.edit_text("Generating a voice response...")
        # Use an expressive and clear edge-tts voice
        communicate = edge_tts.Communicate(final_text, "en-US-JennyNeural")
        await communicate.save(audio_path)

        # 7. Send the voice back to the user
        await processing_msg.delete()
        with open(audio_path, 'rb') as audio_file:
            await update.message.reply_voice(voice=audio_file)

    except Exception as e:
        print(f"Error processing image: {e}")
        await processing_msg.edit_text("Sorry, an error occurred while processing the image.")
    finally:
        # Cleanup temp files
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
# Handler for images
app.add_handler(MessageHandler(filters.PHOTO, handle_image))
# Handler for anything else (text, documents, etc) that is not a command
app.add_handler(MessageHandler((~filters.PHOTO) & (~filters.COMMAND), handle_non_image))

print("Bot is running...")
if __name__ == '__main__':
    app.run_polling()