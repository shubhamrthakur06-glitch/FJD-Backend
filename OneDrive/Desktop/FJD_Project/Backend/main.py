from fastapi import FastAPI, UploadFile, File, Form
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' # Silence warnings
import io
import base64
import requests
import re
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from PIL import Image
from pypdf import PdfReader
import docx
import firebase_admin
from firebase_admin import credentials, firestore
from email_validator import EmailValidator

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BRAIN_PATH = "fjd_deep_brain.h5"
TOKENIZER_PATH = "tokenizer.pickle"
PHISHTANK_PATH = "phishtank_urls.csv"

# Deep Learning Constants
MAX_LENGTH = 120
TRUNC_TYPE = 'post'
PADDING_TYPE = 'post'

# Initialize Firebase
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    except:
        pass
db = firestore.client()

app = FastAPI()

# --- LOAD RESOURCES ---
model = None
tokenizer = None
phish_blacklist = set()

print("🧠 Booting Forensic Engine...")

# 1. Load Brain
try:
    model = tf.keras.models.load_model(BRAIN_PATH)
    with open(TOKENIZER_PATH, 'rb') as handle:
        tokenizer = pickle.load(handle)
    print("✅ Deep Brain & Tokenizer Online.")
except Exception as e:
    print(f"❌ CRITICAL ERROR LOADING BRAIN: {e}")

# 2. Load PhishTank (Blacklist)
if os.path.exists(PHISHTANK_PATH):
    try:
        df = pd.read_csv(PHISHTANK_PATH)
        # Assuming column 'text' or 'url' holds the link
        target_col = 'text' if 'text' in df.columns else 'url'
        phish_blacklist = set(df[target_col].astype(str).str.lower())
        print(f"✅ PhishTank Loaded: {len(phish_blacklist)} known threats.")
    except Exception as e:
        print(f"⚠️ PhishTank Load Failed: {e}")
else:
    print("⚠️ PhishTank CSV not found. Link blacklist disabled.")

email_validator = EmailValidator() 

# --- HELPER: TEXT EXTRACTION ---
def raw_gemini_ocr(image_bytes):
    if not GOOGLE_API_KEY: return None
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    ]
    payload = {"contents": [{"parts": [{"text": "Extract all text exactly."}, {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}]}]}
    
    for url in endpoints:
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except: continue
    return None

async def extract_text_from_file(file: UploadFile):
    if not file: return ""
    filename = file.filename.lower()
    content = ""
    try:
        contents = await file.read()
        if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            return raw_gemini_ocr(img_byte_arr.getvalue()) or ""
        elif filename.endswith('.pdf'):
            pdf_reader = PdfReader(io.BytesIO(contents))
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text: content += text + "\n"
        elif filename.endswith('.docx'):
            doc = docx.Document(io.BytesIO(contents))
            for para in doc.paragraphs:
                content += para.text + "\n"
        elif filename.endswith('.txt'):
            return contents.decode('utf-8')
    except Exception as e:
        print(f"❌ File Error ({filename}): {e}")
    return content

# --- HELPER: AI PREDICTION ---
def get_ai_score(text):
    if not text or not model or not tokenizer: return 0
    try:
        seq = tokenizer.texts_to_sequences([text])
        padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding=PADDING_TYPE, truncating=TRUNC_TYPE)
        prediction = model.predict(padded, verbose=0)[0][0]
        return round(float(prediction) * 100, 2)
    except:
        return 50

# --- MAIN ENDPOINT: TRIPLE THREAT ANALYSIS ---
@app.post("/analyze")
async def analyze_evidence(
    image: UploadFile = File(None), 
    document: UploadFile = File(None), 
    link: str = Form(None)
):
    print(f"📥 Received Evidence - Image: {image is not None}, Doc: {document is not None}, Link: {link is not None}")
    
    reasons = []
    combined_text = ""
    
    # --- TRACK 1: LINK ANALYSIS ---
    link_score = 0
    if link:
        # Check Blacklist
        clean_link = link.lower().strip()
        if clean_link in phish_blacklist:
            link_score = 100
            reasons.append(f"🚨 BLACKLIST MATCH: Link '{link}' is a known phishing site.")
        else:
            # Check AI on the link text itself (e.g. "secure-login-update")
            link_score = get_ai_score(link)
            if link_score > 80:
                reasons.append("⚠️ Suspicious URL pattern detected.")
        
        combined_text += f" {link}"

    # --- TRACK 2: DOCUMENT ANALYSIS ---
    doc_text = await extract_text_from_file(document)
    doc_score = get_ai_score(doc_text)
    if doc_text:
        combined_text += f" {doc_text}"
        if doc_score > 80: reasons.append("📄 Document contains high-risk scam vocabulary.")

    # --- TRACK 3: IMAGE ANALYSIS ---
    img_text = await extract_text_from_file(image)
    img_score = get_ai_score(img_text)
    if img_text:
        combined_text += f" {img_text}"
        if img_score > 80: reasons.append("📷 Screenshot contains high-risk scam vocabulary.")

    # --- AGGREGATION LOGIC (THE JURY) ---
    
    # 1. The "Poison Drop" Rule: Max score wins
    final_score = max(link_score, doc_score, img_score)
    
    # 2. Identity Check (on combined text)
    email_score = 50 
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', combined_text)
    if email_match:
        found_email = email_match.group(0)
        email_score, email_reasons, _ = email_validator.validate(found_email, combined_text)
        if email_score < 80: 
            reasons.extend(email_reasons)
            # If identity is fake, force score to 100
            if final_score < 100:
                final_score = 100
                reasons.append("🚨 IDENTITY ALERT: Fake/Free Email Address Overrides Safe Text.")
        elif email_score == 100: 
            reasons.append(f"✅ Verified Sender: {found_email}")
            # Identity Shield (Only lowers score if text isn't CRITICAL)
            if final_score < 90: 
                final_score = max(0, final_score - 20)
                reasons.append("🛡️ Trusted Sender lowers risk.")

    # 3. Confidence Calculation
    evidence_count = sum([1 for x in [image, document, link] if x is not None])
    confidence_level = "LOW"
    if evidence_count == 3: confidence_level = "EXTREME"
    elif evidence_count == 2: confidence_level = "HIGH"
    
    if final_score > 80:
        label, color = "HIGH RISK", "RED"
        if not reasons: reasons.append(f"AI Brain detected scam patterns (Confidence: {confidence_level}).")
    elif final_score > 40:
        label, color = "MODERATE", "YELLOW"
        reasons.append(f"Analysis is inconclusive. More evidence recommended (Confidence: {confidence_level}).")
    else:
        label, color = "SAFE JOB", "GREEN"
        reasons.append(f"No active threats detected in provided evidence (Confidence: {confidence_level}).")

    # 4. Save to DB
    try:
        db.collection("scam_reports").add({
            "score": final_score, "reasons": reasons, "confidence": confidence_level,
            "has_image": image is not None, "has_doc": document is not None, "has_link": link is not None,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
    except: pass

    return {
        "score": int(final_score), "label": label, "color": color,
        "extracted_text": combined_text[:200] + "...", 
        "reasons": reasons,
        "confidence": confidence_level
    }