from fastapi import FastAPI, UploadFile, File
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' # Silence warnings
import io
import base64
import requests
import re
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore
from email_validator import EmailValidator

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BRAIN_PATH = "fjd_deep_brain.h5"
TOKENIZER_PATH = "tokenizer.pickle"

# Deep Learning Constants (MUST MATCH TRAINING)
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

# --- LOAD THE DEEP MIND ---
model = None
tokenizer = None

print("🧠 Booting Neural Network...")
try:
    model = tf.keras.models.load_model(BRAIN_PATH)
    with open(TOKENIZER_PATH, 'rb') as handle:
        tokenizer = pickle.load(handle)
    print("✅ Deep Brain & Tokenizer Online.")
except Exception as e:
    print(f"❌ CRITICAL ERROR LOADING BRAIN: {e}")

email_validator = EmailValidator() 

# --- HELPER: VETO KEYWORDS (The Fail-Safe) ---
FATAL_KEYWORDS = [
    "pay for gate pass", "pay for id card", "pay for laptop",
    "deposit for verification", "money for uniform", "security deposit",
    "registration fee", "frozen wallet", "tax to withdraw", 
    "merchant task", "anydesk", "teamviewer"
]

SAFE_CONTEXT = ["no", "never", "zero", "fake", "scam", "fraud", "beware", "avoid"]

def check_veto(text):
    text_lower = text.lower()
    for fatal in FATAL_KEYWORDS:
        if fatal in text_lower:
            is_safe = False
            for safe in SAFE_CONTEXT:
                if safe in text_lower:
                    is_safe = True
                    break
            if not is_safe:
                return True, fatal
    return False, None

# --- HELPER: GEMINI OCR ---
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

# --- MAIN API ENDPOINT ---
@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    print(f"📥 Received Image: {file.filename}")
    reasons = []
    
    # 1. READ IMAGE
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        image_bytes = img_byte_arr.getvalue()
    except:
        return {"score": 0, "label": "ERROR", "color": "GRAY", "extracted_text": "", "reasons": ["Image corrupt"]}

    # 2. EXTRACT TEXT
    extracted_text = raw_gemini_ocr(image_bytes)
    if not extracted_text:
        return {"score": 0, "label": "OCR ERROR", "color": "GRAY", "extracted_text": "", "reasons": ["Text unreadable"]}

    print(f"📝 Extracted: {extracted_text[:50]}...")

    # 3. DEEP LEARNING ANALYSIS
    text_score = 0
    if model and tokenizer:
        try:
            # Convert text to numbers
            seq = tokenizer.texts_to_sequences([extracted_text])
            padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding=PADDING_TYPE, truncating=TRUNC_TYPE)
            # Predict
            prediction = model.predict(padded, verbose=0)[0][0]
            text_score = round(float(prediction) * 100, 2)
            print(f"🧠 Deep Learning Score: {text_score}%")
        except Exception as e:
            print(f"⚠️ Model Error: {e}")
            text_score = 50 # Fallback

    # 4. VETO CHECK
    is_fatal_keyword, trigger = check_veto(extracted_text)
    if is_fatal_keyword:
        reasons.append(f"🚩 Fatal Keyword: '{trigger}'")

    # 5. IDENTITY ANALYSIS (The Detective)
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', extracted_text)
    
    # 🛑 FIX: Default to 50 (Neutral), NOT 100 (Trusted)
    # If there is no email, we shouldn't vouch for them.
    email_score = 50 
    email_verdict = "N/A"
    
    if email_match:
        found_email = email_match.group(0)
        email_score, email_reasons, email_verdict = email_validator.validate(found_email, extracted_text)
        
        if email_score < 80:
            reasons.extend(email_reasons)
        elif email_score == 100:
            reasons.append(f"✅ Verified Sender: {found_email}")
    else:
        # If no email is found, we don't add reasons, but we keep score at 50
        pass 

    # 5. THE VETO PROTOCOL (Combining Scores)
    final_score = text_score
    
    # Rule 1: The "Wolf" (Text Safe, Email Fake)
    if email_score == 0:
        final_score = 100
        reasons.insert(0, "🚨 IDENTITY ALERT: Fake/Free Email Address detected.")
        
    # Rule 2: The "Sus" (Text Risky, Email Bad)
    elif email_score < 50 and text_score > 50:
        final_score = 100
        reasons.insert(0, "🚨 DOUBLE THREAT: Suspicious Text + Unverified Email.")
        
    # Rule 3: The "Verified" (Text Risky, Email Real)
    # 🛑 FIX: Only shield if score is strictly GREATER than 80 (Verified)
    elif email_score > 80 and text_score > 60:
        final_score = text_score - 20 
        reasons.append("🛡️ IDENTITY SHIELD: Verified Sender lowers risk.")
        
    if is_fatal_keyword: final_score = 100

    final_score = max(0, min(100, final_score))
    
    if final_score > 80:
        label, color = "HIGH RISK", "RED"
        if not reasons: reasons.append("Deep AI detected high-risk scam patterns.")
    elif final_score > 40:
        label, color = "MODERATE", "YELLOW"
        if not reasons: reasons.append("Content is ambiguous. Proceed with caution.")
    else:
        label, color = "SAFE JOB", "GREEN"
        if not reasons: reasons.append("No threats detected.")

    # 7. SAVE TO DB
    try:
        db.collection("scam_reports").add({
            "text": extracted_text, "score": final_score, "reasons": reasons, 
            "timestamp": firestore.SERVER_TIMESTAMP
        })
    except: pass

    return {
        "score": int(final_score), "label": label, "color": color,
        "extracted_text": extracted_text[:300], "reasons": reasons
    }