import streamlit as st
import tensorflow as tf
import numpy as np
import cv2
from PIL import Image, ImageChops, ImageEnhance
import os
from PIL.ExifTags import TAGS
import gdown

# --- 1. SAFE MEDIAPIPE INITIALIZATION ---
HAS_MEDIAPIPE = False
try:
    import mediapipe as mp
    from mediapipe.python.solutions import face_detection as mp_face_detection
    face_detector = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
    HAS_MEDIAPIPE = True
except Exception:
    HAS_MEDIAPIPE = False

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deepfake Defender Pro", layout="wide", page_icon="🛡️")

# --- 3. THE FORENSICS ENGINE (ELA) ---
def run_ela(image, quality=90):
    temp_file = "temp_ela_session.jpg"
    image.save(temp_file, 'JPEG', quality=quality)
    resaved = Image.open(temp_file)
    ela_map = ImageChops.difference(image, resaved)
    extrema = ela_map.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    scale = 255.0 / max_diff if max_diff != 0 else 1
    ela_map = ImageEnhance.Brightness(ela_map).enhance(scale)
    return ela_map

# --- 4. MODEL LOADING ---

@st.cache_resource
def load_ensemble():
    # 1. YOUR GOOGLE DRIVE FILE IDs
    # Get these from your Drive share links (the long string of letters/numbers)
    m1_id = '1qEdqfispNzo-gZ9R5QD9SJeMKPES6syy' 
    m2_id = '1KSCKXbPB4tEmgpE3agZm9z_OPF6VIwJo'
    
    # 2. LOCAL FILENAMES
    m1_path = 'deepfake_detector_model.h5'
    m2_path = 'pro_mobilenet_model.h5'

    # 3. AUTOMATIC DOWNLOAD LOGIC
    # Download Handmade Model if missing
    if not os.path.exists(m1_path):
        with st.spinner("Downloading Handmade AI Model... please wait."):
            url1 = f'https://drive.google.com/uc?id={m1_id}'
            gdown.download(url1, m1_path, quiet=False)

    # Download Pro Model if missing
    if not os.path.exists(m2_path):
        with st.spinner("Downloading Professional AI Model..."):
            url2 = f'https://drive.google.com/uc?id={m2_id}'
            gdown.download(url2, m2_path, quiet=False)

    # 4. LOAD THE MODELS
    m1 = tf.keras.models.load_model(m1_path)
    m2 = tf.keras.models.load_model(m2_path)
    return m1, m2

def get_metadata(image):
    # Use the official public method instead of the private underscore one
    info = image.getexif()
    if info:
        # We only want to show data that has a readable name (like 'Model' or 'Software')
        return {TAGS.get(tag, tag): value for tag, value in info.items() if tag in TAGS}
    return None
# --- 6. MAIN APP ---
# --- STEP 6: MAIN INTERFACE ---
tab1, tab2= st.tabs(["🔍 AI Face Scan", "🧪 Image Forensics"])

uploaded_file = st.file_uploader("Upload Image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img_orig = Image.open(uploaded_file).convert('RGB')
    img_array = np.array(img_orig)
    m1, m2 = load_ensemble()
    
    with tab1:
        st.header("Facial Analysis")
        
        # Safe Face Detection
        results = None
        if HAS_MEDIAPIPE:
            try: results = face_detector.process(img_array)
            except: results = None

        if results and results.detections:
            det = results.detections[0]
            bbox = det.location_data.relative_bounding_box
            h, w, _ = img_array.shape
            x, y, fw, fh = int(bbox.xmin * w), int(bbox.ymin * h), int(bbox.width * w), int(bbox.height * h)
            face_crop = img_array[max(0, y):y+fh, max(0, x):x+fw]
        else:
            face_crop = img_array

        # Prediction Logic
        processed = cv2.resize(face_crop, (224, 224)) / 255.0
        processed = np.expand_dims(processed, axis=0)
        
        score1 = m1.predict(processed)[0][0]
        score2 = m2.predict(processed)[0][0]
        ensemble_real_score = (score1 + score2) / 2

        # Display Results
        col1, col2 = st.columns(2)
        with col1:
            st.image(face_crop, caption="Analysis Target", use_container_width=True)
        
        with col2:
            if ensemble_real_score > 0.5:
                st.success(f"### RESULT: REAL")
                st.metric(label="Authenticity Score", value=f"{ensemble_real_score*100:.2f}%")
                # Add float() here
                st.progress(float(ensemble_real_score)) 
            else:
                fakeness = (1 - ensemble_real_score) * 100
                st.error(f"### RESULT: FAKE")
                st.metric(label="Threat Level (Fakeness)", value=f"{fakeness:.2f}%")
                # Add float() here and ensure it's between 0.0 and 1.0
                st.progress(float(fakeness / 100))
        report_text = f"""
        Deepfake Detection Report
        -------------------------
        Final Verdict: {'REAL' if ensemble_real_score > 0.5 else 'FAKE'}
        Confidence: {ensemble_real_score*100:.2f}%
        Handmade Model Score: {score1*100:.2f}%
        Pro Model Score: {score2*100:.2f}%
        -------------------------
        Analyzed by: Deepfake Defender Pro
        """
        st.download_button("📥 Download Forensic Report", report_text, file_name="forensic_report.txt")
   
    with tab2:
        st.header("🧪 Background Integrity (ELA)")
        
        st.markdown("""
        **What are you seeing?**
        This is an **Error Level Analysis (ELA)** map. It detects digital tampering by identifying 
        different compression levels within a single image.
        """)
        
        # 1. Generate and show the standard ELA
        st.divider()
        ela_img = run_ela(img_orig)
        st.image(ela_img, caption="Forensic Compression Map", use_container_width=True)

        # 2. ADD THE OVERLAY FEATURE HERE
        st.markdown("---")
        st.markdown("### 🔬 Advanced Forensic Overlay")
        st.write("Use the slider to blend the original image with the forensic map to pinpoint tampering.")
        
        # Slider to control how much ELA map we see vs the original image
        alpha = st.slider("Select Overlay Intensity", 0.0, 1.0, 0.5)
        
        # Convert both to RGBA so we can blend them (they must be the same format)
        orig_rgba = img_orig.convert("RGBA")
        ela_rgba = ela_img.convert("RGBA")
        
        # Create the blended heatmap
        blended = Image.blend(orig_rgba, ela_rgba, alpha)
        
        st.image(blended, caption=f"Blended View (Intensity: {alpha})", use_container_width=True)
        # Add this at the bottom of Tab 2
        st.markdown("---")
        st.markdown("### 📁 Hidden Metadata (EXIF)")
        metadata = get_metadata(img_orig)
        
        if metadata:
            # This shows the data in a nice, clean table
            st.write("Metadata found! This can reveal if software like Photoshop was used.")
            st.table(metadata)
        else:
            st.info("No EXIF metadata found. This image may have been stripped of its digital footprint.")
