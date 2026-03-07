# 🌿 AgroVision - Intelligent Crop Disease Detection System

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![YOLO11](https://img.shields.io/badge/YOLO-11-success.svg)](https://github.com/ultralytics/ultralytics)
[![Roboflow](https://img.shields.io/badge/Dataset-Roboflow-purple.svg)](https://roboflow.com)
[![Flask](https://img.shields.io/badge/Flask-Backend-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)

**AgroVision** is a comprehensive, multi-modal AI system built to empower farmers and field authorities with precision agriculture tools. By analyzing crop imagery—whether from smartphones or drones—AgroVision provides pixel-level disease identification, detailed severity estimation, actionable treatment recommendations, and aggregated field health tracking.

Our ultimate goal is to bridge the gap between advanced deep learning algorithms and accessible farming tools, ensuring that farmers can secure their yields with minimal friction, regardless of language barriers or technical expertise.

---

## 🚀 What We Are Doing

AgroVision serves multiple facets of the agricultural monitoring pipeline:

1. **Farmer Portal & Web Dashboard:** An intuitive web application built with Flask and Vanilla JS/CSS outlining a diagnostic flow. Users can upload crop leaf images to receive immediate YOLO-powered bounded-box tracking, dynamic severity scoring (powered by advanced HSV masking techniques in OpenCV), and immediate agronomist-verified treatment plans.
2. **Field Health Overlay (Drone Dashboard):** For large-scale precision agriculture, AgroVision processes bulk imagery (often captured via drones). It synthesizes the data into visual heatmap overlays that highlight "hotspots" of high disease severity across different crop areas, allowing agronomists to identify critically infected field sectors swiftly.
3. **Multilingual Telegram Assistant (`@AgraVision_bot`):** Accessibility is key. We have built an integrated Telegram Bot capable of accepting field images from farmers via chat. The bot analyzes the crop, extracts severity and treatment steps, and provides responses via **translated text and Edge-TTS voice audio** in **8 Indian languages** (English, Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, and Bengali).

---

## ✨ Key Features & Technical Capabilities

* **Multi-Crop Support (21 Classes):** We accurately identify specific diseases affecting **Rice, Cotton, Tomato, and Wheat**, as well as accurately classifying healthy leaves.
* **Precise AI Object Detection:** Utilizing a custom-trained **YOLO11** model, AgroVision detects intricate signs of crop illness and establishes accurate bounding boxes even under varied lighting conditions.
* **Computer Vision Severity Scoring:** Once a diseased spot is located by YOLO, internal logic uses precise OpenCV color-space (HSV) masks to quantify the exact ratio of the discolored disease pixels relative to the total leaf surface, providing an exact `Severity %`.
* **Tailored Actionable Insights:** A robust recommendation engine maps detected diseases to clear, practical treatment methods, fertilizer recommendations, and preventative measures. All treatments refer to trusted agricultural sources.
* **Accessible Voice Reports:** The seamless integration of Google Translate and Microsoft Edge TTS provides spoken-word agricultural assistance to farmers right on their standard messaging apps.

---

## 📊 Datasets Used

The models are trained using comprehensive, high-quality datasets for multiple crop types hosted on Roboflow:

| Crop | Dataset Link |
| :---: | :--- |
| 🌾 **Rice** | [Rice Disease Dataset](https://universe.roboflow.com/deep-learning-q7eui/rice-disease-eq1pq/) |
| ☁️ **Cotton** | [Cotton Disease Detection](https://universe.roboflow.com/disease-detection-wounm/cotton-disease-detection-xevxs/) |
| 🍅 **Tomato** | [Tomato Crop Disease](https://universe.roboflow.com/aryan-rajvanshi-xvuyg/crop-disease-axhjj/) |
| 🌾 **Wheat** | [Wheat Disease Dataset](https://universe.roboflow.com/wheatdisease/wheat-disease-efcmq/) |

---

## 📁 Project Resources

- ☁️ **Google Drive Workspace:** [Access Project Files, Models, & Data](https://drive.google.com/drive/folders/1Y2sDvTgUGfcGdzWJXKjaM3DWuNGc3YeN?usp=drive_link)
- 💬 **Telegram Bot Interface:** Start chatting with the bot globally via [@AgraVision_bot](https://t.me/AgraVision_bot)

---

## 🛠️ Architecture Overview

- **`app.py`**: The core Flask backend routing Web Dashboard API calls (`/predict`, `/generate_heatmap`) directly to inference logic.
- **`models/best.pt`**: Our optimized YOLOv11 weights for crop disease identification.
- **`modules/`**:
  - `severity.py`: Post-processing computer vision algorithms to isolate brown/disease pixels against green/leaf background pixels to compute quantifiable severity levels.
  - `recommendation.py`: Intelligent lookup system mapping YOLO class detections to verified agricultural solutions.
- **`scripts/bot.py`**: The asynchronous Telegram bot logic operating on `python-telegram-bot`, capable of edge translation and voice synthesis.
- **`templates/` & `static/`**: High-fidelity frontend design ensuring a smooth Farmer Portal experience.

---

*Built with ❤️ by Team Tomato Chutney.*
