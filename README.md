# 🌿 AI Crop Disease Detection System

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![YOLO11](https://img.shields.io/badge/YOLO-11-success.svg)](https://github.com/ultralytics/ultralytics)
[![Roboflow](https://img.shields.io/badge/Dataset-Roboflow-purple.svg)](https://roboflow.com)

A comprehensive AI system designed for detecting and analyzing crop diseases from drone imagery. By leveraging advanced instance segmentation (YOLO11-seg), this project enables precision agriculture through pixel-level disease identification, detailed affected area calculations, automated fertilizer recommendations, and temporal health trend analysis.

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

---

## 🚀 Key Features

* **Multi-Crop Support:** Advanced detection across Rice, Cotton, Tomato, and Wheat.
* **Instance Segmentation:** Powered by YOLO11-Seg for precise, pixel-level disease mapping and severity estimation.
* **Drone Data Pipeline:** Complete pipeline from drone imagery acquisition to farmer-facing dashboard insights.
* **Geofencing & Mapping:** Unity C# module for precise field boundaries and georeferenced disease tracking.
* **Actionable Insights:** Calculates affected area percentages and provides tailored fertilizer recommendations.
