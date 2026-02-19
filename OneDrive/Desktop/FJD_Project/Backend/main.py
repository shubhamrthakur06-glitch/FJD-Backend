import os
# Set TensorFlow log level to suppress oneDNN warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool # 🟢 NEW: Prevents server freezing
import asyncio                                    # 🟢 NEW: Asynchronous time delays
import io
import re
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from pypdf import PdfReader
import docx
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from PIL import Image
import time

# --- CUSTOM MODULES ---
from email_validator import EmailValidator

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BRAIN_PATH = "fjd_deep_brain.h5"
TOKENIZER_PATH = "tokenizer.pickle"

MAX_LENGTH = 120
TRUNC_TYPE = 'post'
PADDING_TYPE = 'post'

# --- INITIALIZATION LOGS ---
print("\n" + "="*40)
print("🚀 FJD BACKEND ENGINE INITIALIZING...")
print("="*40)

# Initialize Firebase
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        print("✅ Firebase: Connected.")
    except Exception as e:
        print(f"❌ Firebase Error: {e}")
db = firestore.client()

# Initialize Gemini (THE OCR ENGINE)
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("✅ Gemini OCR: Configured.")
else:
    print("❌ CRITICAL: GOOGLE_API_KEY not found. OCR will fail.")

# Initialize Tools
try:
    model = tf.keras.models.load_model(BRAIN_PATH)
    print(f"✅ Deep Brain: Loaded ({BRAIN_PATH}).")
except Exception as e:
    print(f"❌ CRITICAL: Brain Load Failed: {e}")
    model = None

try:
    with open(TOKENIZER_PATH, 'rb') as handle:
        tokenizer = pickle.load(handle)
    print(f"✅ Tokenizer: Loaded ({TOKENIZER_PATH}).")
except Exception as e:
    print(f"❌ CRITICAL: Tokenizer Load Failed: {e}")
    tokenizer = None

email_validator = EmailValidator()
print("✅ Email Validator: Ready.")
print("="*40 + "\n")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# 🛑 FATAL KEYWORDS (The "Hard Kill" List)
FATAL_KEYWORDS = [
    r"kindly\s+deposit", r"send\s+a\s+check", r"purchase\s+equipment",
    r"buy\s+from\s+vendor", r"western\s+union", r"moneygram",
    r"clearance\s+fee", r"refundable\s+deposit", r"cost\s+of\s+training"
]

# ⚠️ SUSPICIOUS KEYWORDS (The "Yellow Flag" List)
SUSPICIOUS_KEYWORDS = [
    r"telegram", r"whatsapp", r"signal\s+app", r"verify\s+your\s+identity",
    r"upload\s+id", r"ssn", r"crypto", r"bitcoin", r"wallet\s+address"
]

# ✅ WHITELIST (The "Safe Harbor" List)
WHITELIST_CONTEXT = [
    "checkr", "sterling", "hireright", "id.me",
    "background check", "pre-employment screening"
]

# --- WAKE UP ENDPOINT (NEW) ---
@app.get("/ping")
def ping_server():
    """Lightweight endpoint to wake up the Render server from cold start."""
    return {"status": "awake", "time": time.strftime('%H:%M:%S')}

# --- HELPER FUNCTIONS ---

def extract_text_from_file(file_bytes, filename):
    try:
        print(f"📄 Processing Document: {filename}")
        if filename.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + " "
            print(f"   -> Extracted {len(text)} characters from PDF.")
            return text
        elif filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(file_bytes))
            text = " ".join([p.text for p in doc.paragraphs])
            print(f"   -> Extracted {len(text)} characters from DOCX.")
            return text
        elif filename.endswith(".txt"):
            text = file_bytes.decode('utf-8')
            print(f"   -> Extracted {len(text)} characters from TXT.")
            return text
        else:
            print(f"⚠️ Unsupported file type: {filename}")
            return ""
    except Exception as e:
        print(f"❌ Document Extraction Failed: {e}")
        return ""

async def perform_ocr_with_gemini(image_bytes): # 🟢 NEW: Now Async
    print("👁️ INITIATING GEMINI OCR PROTOCOL...")
    image = Image.open(io.BytesIO(image_bytes))
    prompt = "Extract all readable text from this image exactly as it appears. Do not summarize."
    
    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
    
    for model_name in models_to_try:
        try:
            print(f"   Attempting OCR with: {model_name}...")
            model = genai.GenerativeModel(model_name)
            
            # 🟢 NEW: Push network call to background thread to avoid freezing
            response = await run_in_threadpool(model.generate_content, [prompt, image])
            
            if response.text:
                print(f"✅ OCR SUCCESS ({model_name}). Extracted {len(response.text)} characters.")
                return response.text
            else:
                 print(f"⚠️ OCR finished but returned empty text with {model_name}.")

        except Exception as e:
            print(f"❌ OCR FAILED with {model_name}: {e}")
            print("   Adding small delay before retry...")
            await asyncio.sleep(1) # 🟢 NEW: Non-blocking sleep

    print("❌❌ ALL GEMINI OCR ATTEMPTS FAILED.")
    return ""

def scan_for_keywords(text):
    print("🔎 Running Rule-Based Keyword Scan...")
    text = text.lower()
    triggers = []
    risk_score = 0
    
    is_whitelisted = any(safe in text for safe in WHITELIST_CONTEXT)
    if is_whitelisted:
        print("   🛡️ Whitelist Active: Ignoring specific suspicious triggers.")

    for pattern in FATAL_KEYWORDS:
        if re.search(pattern, text):
            found = pattern.replace(r'', '').strip()
            print(f"🚨 FATAL TRIGGER FOUND: '{found}'")
            triggers.append(f"🚨 RED FLAG: Found '{found}'")
            return 100, triggers 

    for pattern in SUSPICIOUS_KEYWORDS:
        if re.search(pattern, text):
            if "verify" in pattern and is_whitelisted:
                continue 
            
            found = pattern.replace(r'', '').strip()
            print(f"⚠️ SUSPICIOUS TRIGGER FOUND: '{found}'")
            triggers.append(f"⚠️ SUSPICIOUS: Found '{found}'")
            risk_score += 30

    score = min(risk_score, 90)
    print(f"   -> Rule-Based Score: {score}/100")
    return score, triggers

# --- API ENDPOINT ---

@app.post("/analyze")
async def analyze_evidence(
    image: UploadFile = File(None),       
    link: str = Form(None),
    document: UploadFile = File(None)
):
    print("\n" + "="*40)
    print(f"🚀 NEW ANALYSIS REQUEST RECEIVED AT {time.strftime('%H:%M:%S')}")
    print("="*40)
    
    final_score = 0
    reasons = []
    combined_text = ""

    # --- STEP 1: PROCESS SCREENSHOT ---
    if image:                             
        print("\n[INPUT 1] Processing Screenshot...")
        content = await image.read()      
        ocr_text = await perform_ocr_with_gemini(content) # 🟢 NEW: Added await
        if ocr_text:
            combined_text += ocr_text + " "
            reasons.append("✅ OCR successfully extracted text from screenshot.")
    else:
        print("\n[INPUT 1] No Screenshot provided.")

    # --- STEP 2: PROCESS DOCUMENT ---
    if document:
        print("\n[INPUT 3] Processing Document...")
        content = await document.read()
        # 🟢 NEW: Run heavy document parsing in background
        doc_text = await run_in_threadpool(extract_text_from_file, content, document.filename)
        if doc_text:
            combined_text += doc_text + " "
            reasons.append(f"✅ Extracted text from document: {document.filename}")
    else:
        print("\n[INPUT 3] No Document provided.")

    # --- STEP 3: RULE-BASED ANALYSIS ---
    print("\n[ANALYSIS] Starting Rule-Based Scan...")
    kw_score, kw_reasons = scan_for_keywords(combined_text)
    final_score = max(final_score, kw_score)
    reasons.extend(kw_reasons)

    # --- STEP 4: PROCESS LINK & EMAIL ---
    print("\n[INPUT 2] Processing Link & Emails...")
    if link:
        print(f"   🔗 Analyzing Link: {link}")

    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', combined_text)
    if email_match:
        found_email = email_match.group(0)
        print(f"   📧 Found Email Address: {found_email}")
        
        validation_context = combined_text
        if link:
            validation_context += f" Link provided: {link}"

        # 🟢 NEW: Run DNS blocking checks in background thread
        email_score, email_reasons, _ = await run_in_threadpool(email_validator.validate, found_email, validation_context)
        print(f"   -> Validator Score: {email_score}/100")
        
        if email_score == 0:
            final_score = max(final_score, 100)
            reasons.extend(email_reasons)
            print("   🚨 Email Validator triggered FATAL score.")
        elif email_score < 50:
            final_score = max(final_score, 75)
            reasons.extend(email_reasons)
        else:
            reasons.extend(email_reasons)
    else:
        print("   ℹ️ No email addresses found in text.")

    # --- STEP 5: AI BRAIN ANALYSIS ---
    print("\n[ANALYSIS] Starting AI Brain Analysis...")
    if model and tokenizer and combined_text.strip():
        seq = tokenizer.texts_to_sequences([combined_text])
        padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding=PADDING_TYPE, truncating=TRUNC_TYPE)
        
        # 🟢 NEW: Run TensorFlow prediction in background to avoid freezing
        prediction_output = await run_in_threadpool(model.predict, padded, verbose=0)
        prediction = prediction_output[0][0]
        ai_score = int(prediction * 100)
        print(f"🧠 AI RAW SCORE: {ai_score}%")

        if final_score >= 100:
            print("   -> Ignored AI score (Rule-Based FATAL trigger active).")
        elif ai_score > 90:
            final_score = max(final_score, 95)
            reasons.append("🤖 AI Model detected high-risk scam patterns.")
            print("   -> AI boosted score to High Risk.")
        elif ai_score < 10:
            if final_score < 50: 
                final_score = 5 
                reasons.append("✅ AI Context Analysis: Safe corporate language detected.")
                print("   -> AI lowered score (Safe Context).")
            else:
                 print("   -> AI score low, but existing suspicious rules prevent Safe verdict.")
    else:
        print("⚠️ Skipping AI analysis (Brain offline or empty text).")

    # --- STEP 6: FINAL VERDICT ---
    print("\n[FINALIZING] Generating Report...")
    
    if final_score > 80:
        label = "HIGH RISK"
        color = "RED"
    elif final_score > 40:
        label = "MODERATE"
        color = "YELLOW"
    else:
        label = "SAFE JOB"
        color = "GREEN"

    print(f"🏁 FINAL SCORE: {final_score} | VERDICT: {label}")
    print("="*40 + "\n")

    return {
        "score": int(final_score),       
        "label": label,                  
        "color": color,                  
        "reasons": reasons,              
        "extracted_text": combined_text[:200] + "..." if combined_text else "No readable text found." 
    }