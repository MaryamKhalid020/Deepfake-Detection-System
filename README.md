# 🛡️ Dual-Defense Deepfake Detection Suite

A high-accuracy security tool designed to detect AI-generated faces and background manipulations. 

## 🚀 Overview
This project addresses the growing threat of deepfakes by using a **Dual-Defense Architecture**. Unlike standard detectors, this system analyzes both the **facial features** (using Deep Learning) and the **image integrity** (using Digital Forensics).

## 🛠️ Key Features
* **Ensemble AI Model:** Combines a custom-built CNN with a pre-trained **MobileNetV2** (Transfer Learning) for 95%+ detection accuracy.
* **Automatic Face Cropping:** Uses **MediaPipe** to isolate faces and remove background noise for cleaner analysis.
* **Image Forensics (ELA):** Implements **Error Level Analysis** to detect "Photoshopped" or AI-generated backgrounds that the facial model might miss.
* **Interactive Web Dashboard:** A user-friendly interface built with **Streamlit**.

## 📊 Performance
* **Dataset:** Trained on the 140K Real/Fake Faces dataset.
* **Validation Accuracy:** ~92.5% (Handmade) | ~95%+ (Ensemble).
* **Inference Speed:** < 1 second per image.

## 💻 Tech Stack
* **Language:** Python
* **AI Frameworks:** TensorFlow / Keras
* **Computer Vision:** OpenCV, MediaPipe
* **Web App:** Streamlit
* **Forensics:** PIL (Pillow)

## 📋 Installation & Usage
1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/Deepfake-Detection-System.git](https://github.com/YOUR_USERNAME/Deepfake-Detection-System.git)
