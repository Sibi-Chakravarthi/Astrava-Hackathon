import os
import sys
import cv2
import numpy as np
import torch
import edge_tts
from deep_translator import GoogleTranslator
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
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

# In-memory storage for user language preferences.
# Key: User ID (int), Value: Language Code (str)
user_languages = {}

# Supported languages and their corresponding Google translate code and Edge-TTS voice
LANGUAGES = {
    "en": {"name": "English", "tts_voice": "en-US-JennyNeural"},
    "hi": {"name": "Hindi", "tts_voice": "hi-IN-SwaraNeural"},
    "ta": {"name": "Tamil", "tts_voice": "ta-IN-PallaviNeural"},
    "te": {"name": "Telugu", "tts_voice": "te-IN-ShrutiNeural"},
    "kn": {"name": "Kannada", "tts_voice": "kn-IN-SapnaNeural"},
    "ml": {"name": "Malayalam", "tts_voice": "ml-IN-SobhanaNeural"},
    "mr": {"name": "Marathi", "tts_voice": "mr-IN-AarohiNeural"},
    "bn": {"name": "Bengali", "tts_voice": "bn-IN-TanishaaNeural"}
}

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
    # Create an inline keyboard with the supported languages
    keyboard = []
    row = []
    for lang_code, lang_info in LANGUAGES.items():
        row.append(InlineKeyboardButton(lang_info["name"], callback_data=f"lang_{lang_code}"))
        if len(row) == 2: # 2 buttons per row
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome to the Agricultural Assistant!\n\n"
        "Please select your preferred language:",
        reply_markup=reply_markup
    )

# Callback handler for language selection
async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data.startswith("lang_"):
        lang_code = data.split("_")[1]
        
        # Store preference
        user_languages[user_id] = lang_code
        lang_name = LANGUAGES[lang_code]["name"]
        
        # Translate the confirmation message if it's not English
        confirm_msg = f"Language set to {lang_name}. Please send me an image of a crop leaf."
        if lang_code != "en":
            try:
                translator = GoogleTranslator(source='en', target=lang_code)
                confirm_msg = translator.translate(confirm_msg)
            except Exception as e:
                print(f"Failed to translate confirmation: {e}")
                
        await query.edit_message_text(text=confirm_msg)

# Handle text / non-image messages
async def handle_non_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang_code = user_languages.get(user_id, "en") # Default to english
    
    msg = "I can only process images! Please send me an image of a crop leaf so I can analyze it."
    if lang_code != "en":
        try:
             translator = GoogleTranslator(source='en', target=lang_code)
             msg = translator.translate(msg)
        except Exception:
             pass
             
    await update.message.reply_text(msg)

# Handle incoming images
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if model is None:
        await update.message.reply_text("Sorry, the detection model is not loaded correctly. Please contact the administrator.")
        return

    user_id = update.effective_user.id
    lang_code = user_languages.get(user_id, "en") # English by default

    # Prepare localized loading message
    processing_txt = "Processing your image, please wait..."
    if lang_code != "en":
         try:
             translator = GoogleTranslator(source='en', target=lang_code)
             processing_txt = translator.translate(processing_txt)
         except Exception:
             pass

    processing_msg = await update.message.reply_text(processing_txt)

    try:
        # 1. Download the image
        photo_file = await update.message.photo[-1].get_file()
        image_path = f"temp_image_{update.message.message_id}.jpg"
        audio_path = f"temp_voice_{update.message.message_id}.mp3"
        await photo_file.download_to_drive(image_path)

        # 2. Read the image and run inference
        img = cv2.imread(image_path)
        if img is None:
            err_msg = "Sorry, I couldn't read the image. Please try sending it again."
            if lang_code != "en": err_msg = GoogleTranslator(source='en', target=lang_code).translate(err_msg)
            await processing_msg.edit_text(err_msg)
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
            err_msg = "I couldn't detect any specific crop diseases in this image. The plant might be healthy, or the image may be too blurry."
            if lang_code != "en": err_msg = GoogleTranslator(source='en', target=lang_code).translate(err_msg)
            await processing_msg.edit_text(err_msg)
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
        
        # Translate main text if necessary
        if lang_code != "en":
            try:
                # We translate the full English response into the selected language
                translator = GoogleTranslator(source='en', target=lang_code)
                translated_text = translator.translate(final_text)
                final_text = translated_text
            except Exception as e:
                print(f"Translation failed: {e}")

        # 6. Generate Voice Data
        gen_voice_msg = "Generating a voice response..."
        if lang_code != "en": gen_voice_msg = GoogleTranslator(source='en', target=lang_code).translate(gen_voice_msg)
        await processing_msg.edit_text(gen_voice_msg)
        
        # Lookup the appropriate localized voice for the chosen language
        voice_model = LANGUAGES.get(lang_code, LANGUAGES["en"])["tts_voice"]
        
        communicate = edge_tts.Communicate(final_text, voice_model)
        await communicate.save(audio_path)

        # 7. Send the text and voice back to the user
        await processing_msg.delete()
        await update.message.reply_text(final_text)
        with open(audio_path, 'rb') as audio_file:
            await update.message.reply_voice(voice=audio_file)

    except Exception as e:
        print(f"Error processing image: {e}")
        err_msg = "Sorry, an error occurred while processing the image."
        try:
             if lang_code != "en": err_msg = GoogleTranslator(source='en', target=lang_code).translate(err_msg)
        except Exception: pass
        await processing_msg.edit_text(err_msg)
    finally:
        # Cleanup temp files
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(language_callback))
# Handler for images
app.add_handler(MessageHandler(filters.PHOTO, handle_image))
# Handler for anything else (text, documents, etc) that is not a command
app.add_handler(MessageHandler((~filters.PHOTO) & (~filters.COMMAND), handle_non_image))

print("Bot is running...")
if __name__ == '__main__':
    app.run_polling()