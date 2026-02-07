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
from pypdf import PdfReader
import docx
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

print("🧠 Booting Universal Neural Network...")
try:
    model = tf.keras.models.load_model(BRAIN_PATH)
    with open(TOKENIZER_PATH, 'rb') as handle:
        tokenizer = pickle.load(handle)
    print("✅ Deep Brain & Tokenizer Online.")
except Exception as e:
    print(f"❌ CRITICAL ERROR LOADING BRAIN: {e}")

email_validator = EmailValidator() 

# --- HELPER: VETO KEYWORDS ---
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

# --- HELPER: GEMINI OCR (Images) ---
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

# --- NEW HELPER: UNIVERSAL TEXT EXTRACTOR ---
async def extract_text_from_file(file: UploadFile):
    filename = file.filename.lower()
    content = ""
    
    try:
        # 1. IMAGES (JPG, PNG, JPEG)
        if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            print("📷 Detected Image File")
            contents = await file.read()
            # Convert to RGB to be safe
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            return raw_gemini_ocr(img_byte_arr.getvalue())

        # 2. PDF DOCUMENTS
        elif filename.endswith('.pdf'):
            print("📄 Detected PDF Document")
            contents = await file.read()
            pdf_reader = PdfReader(io.BytesIO(contents))
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text: content += text + "\n"
            return content

        # 3. WORD DOCUMENTS (.docx)
        elif filename.endswith('.docx'):
            print("📝 Detected Word Document")
            contents = await file.read()
            doc = docx.Document(io.BytesIO(contents))
            for para in doc.paragraphs:
                content += para.text + "\n"
            return content
            
        # 4. TEXT FILES (.txt)
        elif filename.endswith('.txt'):
            print("📜 Detected Text File")
            contents = await file.read()
            return contents.decode('utf-8')
            
    except Exception as e:
        print(f"❌ Extraction Error: {e}")
        return None
    
    return content if content else None

# --- MAIN API ENDPOINT ---
@app.post("/analyze")
async def analyze_evidence(file: UploadFile = File(...)):
    print(f"📥 Received Evidence: {file.filename}")
    reasons = []
    
    # 1. EXTRACT TEXT (Universal)
    extracted_text = await extract_text_from_file(file)
    
    if not extracted_text:
        return {"score": 0, "label": "UNREADABLE", "color": "GRAY", "extracted_text": "", "reasons": ["File format not supported or empty."]}

    print(f"📝 Extracted ({len(extracted_text)} chars): {extracted_text[:100]}...")

    # 2. LINK SCANNER (New!)
    # Find links like http://bit.ly/scam or www.fake-job.com
    urls = re.findall(r'(https?://\S+|www\.\S+)', extracted_text)
    if urls:
        print(f"🔗 Found {len(urls)} links in document.")
        # We append links to the text so the AI notices them explicitly
        extracted_text += " " + " ".join(urls)

    # 3. DEEP LEARNING ANALYSIS
    text_score = 0
    if model and tokenizer:
        try:
            seq = tokenizer.texts_to_sequences([extracted_text])
            padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding=PADDING_TYPE, truncating=TRUNC_TYPE)
            prediction = model.predict(padded, verbose=0)[0][0]
            text_score = round(float(prediction) * 100, 2)
            print(f"🧠 Deep Learning Score: {text_score}%")
        except Exception as e:
            print(f"⚠️ Model Error: {e}")
            text_score = 50 

    # 4. VETO CHECK
    is_fatal_keyword, trigger = check_veto(extracted_text)
    if is_fatal_keyword:
        reasons.append(f"🚩 Fatal Keyword: '{trigger}'")

    # 5. IDENTITY CHECK
    # Fix: Default to 50 (Neutral) if no email found
    email_score = 50 
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', extracted_text)
    if email_match:
        found_email = email_match.group(0)
        email_score, email_reasons, _ = email_validator.validate(found_email, extracted_text)
        if email_score < 80: reasons.extend(email_reasons)
        elif email_score == 100: reasons.append(f"✅ Verified Sender: {found_email}")

    # 6. FINAL SCORING
    final_score = text_score
    
    if email_score == 0:
        final_score = 100
        reasons.insert(0, "🚨 IDENTITY ALERT: Fake/Free Email Address.")
    elif email_score < 50 and text_score > 50:
        final_score = 100
        reasons.insert(0, "🚨 DOUBLE THREAT: Suspicious Text + Unverified Email.")
    elif email_score > 80 and text_score > 60:
        final_score = text_score - 20 
        reasons.append("🛡️ Trusted Sender lowers risk.")
        
    if is_fatal_keyword: final_score = 100
    
    # URL Penalty: If AI is suspicious AND there are links, boost risk
    if text_score > 70 and urls:
        reasons.append("⚠️ Suspicious links detected in document.")

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
            "filename": file.filename, "timestamp": firestore.SERVER_TIMESTAMP
        })
    except: pass

    return {
        "score": int(final_score), "label": label, "color": color,
        "extracted_text": extracted_text[:300], "reasons": reasons
    }