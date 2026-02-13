from fastapi import FastAPI, UploadFile, File, Form
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' 
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

# --- NEW IMPORTS ---
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import whois
from datetime import datetime

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BRAIN_PATH = "fjd_deep_brain.h5"
TOKENIZER_PATH = "tokenizer.pickle"
PHISHTANK_PATH = "phishtank_urls.csv"

MAX_LENGTH = 120
TRUNC_TYPE = 'post'
PADDING_TYPE = 'post'

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    except: pass
db = firestore.client()

app = FastAPI()

# 🛑 FATAL KEYWORDS (The "Hard Kill" List)
# If any of these appear, it is AUTOMATICALLY a scam (Override AI).
FATAL_KEYWORDS = [
    r"kindly\s+deposit",
    r"send\s+a\s+check",
    r"purchase\s+equipment",
    r"buy\s+from\s+vendor",
    r"western\s+union",
    r"moneygram",
    r"cash\s+app",
    r"steam\s+card",
    r"apple\s+gift\s+card",
    r"clearance\s+fee",
    r"refundable\s+deposit",
    r"cost\s+of\s+training",
    r"bank\s+login"
]

# ⚠️ SUSPICIOUS KEYWORDS (The "Yellow Flag" List)
# These increase risk but don't auto-ban (unless context is bad).
SUSPICIOUS_KEYWORDS = [
    r"telegram",
    r"whatsapp",
    r"signal\s+app",
    r"verify\s+your\s+identity",  # <--- This was killing your test
    r"upload\s+id",
    r"ssn",
    r"credit\s+score",
    r"crypto",
    r"bitcoin",
    r"usdt",
    r"wallet\s+address"
]

# ✅ WHITELIST (The "Safe Harbor" List)
# If these exist, ignore specific Suspicious Keywords.
WHITELIST_CONTEXT = [
    "checkr",
    "sterling",
    "hireright",
    "id.me",
    "fadv",
    "first advantage",
    "background check",
    "pre-employment screening"
]

# Initialize Tools
try:
    model = tf.keras.models.load_model(BRAIN_PATH)
    print("✅ DEEP BRAIN LOADED.")
except:
    print("❌ BRAIN NOT FOUND.")
    model = None

try:
    with open(TOKENIZER_PATH, 'rb') as handle:
        tokenizer = pickle.load(handle)
    print("✅ TOKENIZER LOADED.")
except:
    print("❌ TOKENIZER NOT FOUND.")
    tokenizer = None

email_validator = EmailValidator()

# --- HELPER FUNCTIONS ---

def extract_text_from_file(file_bytes, filename):
    try:
        if filename.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + " "
            return text
        elif filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(file_bytes))
            return " ".join([p.text for p in doc.paragraphs])
        elif filename.endswith(".txt"):
            return file_bytes.decode('utf-8')
        else:
            return ""
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""

def scan_for_keywords(text):
    text = text.lower()
    triggers = []
    
    # Check Whitelist First
    is_whitelisted = any(safe in text for safe in WHITELIST_CONTEXT)
    
    # 1. FATAL CHECKS
    for pattern in FATAL_KEYWORDS:
        if re.search(pattern, text):
            triggers.append(f"🚨 RED FLAG: Found '{pattern.replace(r'', '').strip()}'")
            return 100, triggers # Instant Kill

    # 2. SUSPICIOUS CHECKS
    risk_score = 0
    for pattern in SUSPICIOUS_KEYWORDS:
        if re.search(pattern, text):
            # The Fix: Ignore "Verify Identity" if Whitelisted
            if "verify" in pattern and is_whitelisted:
                continue 
            
            triggers.append(f"⚠️ SUSPICIOUS: Found '{pattern.replace(r'', '').strip()}'")
            risk_score += 30

    return min(risk_score, 90), triggers

def analyze_link(url):
    """
    Checks if a URL is in the PhishTank database.
    """
    try:
        df = pd.read_csv(PHISHTANK_PATH)
        if url in df['url'].values:
            return 100, [f"🚫 MALICIOUS LINK: {url} is a known phishing site."]
    except:
        pass # If DB missing, skip
    return 0, []

# --- API ENDPOINT ---

@app.post("/analyze")
async def analyze_evidence(
    screenshot_text: str = Form(None),
    link: str = Form(None),
    document: UploadFile = File(None)
):
    print("🚀 ANALYZING EVIDENCE...")
    
    final_score = 0
    reasons = []
    combined_text = ""

    # 1. PROCESS TEXT SOURCES
    if screenshot_text:
        combined_text += screenshot_text + " "
    
    if document:
        content = await document.read()
        doc_text = extract_text_from_file(content, document.filename)
        combined_text += doc_text + " "

    # 2. KEYWORD SCAN (Rule-Based)
    kw_score, kw_reasons = scan_for_keywords(combined_text)
    final_score = max(final_score, kw_score)
    reasons.extend(kw_reasons)

    # 3. LINK ANALYSIS
    if link:
        link_score, link_reasons = analyze_link(link)
        final_score = max(final_score, link_score)
        reasons.extend(link_reasons)

    # 4. EMAIL ANALYSIS (The Missing Piece)
    # Extract email from text using regex
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', combined_text)
    if email_match:
        found_email = email_match.group(0)
        print(f"📧 FOUND EMAIL: {found_email}")
        
        # Call Validator
        email_score, email_reasons, _ = email_validator.validate(found_email, combined_text)
        
        # If Validator screams SCAM (Score 0), we boost risk
        if email_score == 0:
            final_score = max(final_score, 100)
            reasons.extend(email_reasons)
        elif email_score < 50:
            final_score = max(final_score, 75)
            reasons.extend(email_reasons)
        else:
            # If Valid, we note it but don't change risk yet
            reasons.extend(email_reasons)

    # 5. AI BRAIN ANALYSIS (The Deep Learning)
    if model and tokenizer and combined_text.strip():
        # Preprocess
        seq = tokenizer.texts_to_sequences([combined_text])
        padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding=PADDING_TYPE, truncating=TRUNC_TYPE)
        
        # Predict
        prediction = model.predict(padded)[0][0]
        ai_score = int(prediction * 100)
        
        print(f"🧠 AI RAW SCORE: {ai_score}%")

        # FUSION LOGIC (Brain vs Rules)
        if final_score >= 100:
            # Rules say FATAL -> Keep FATAL (Brain ignored)
            pass 
        elif ai_score > 90:
            # Brain says SCAM -> Boost Score
            final_score = max(final_score, 95)
            reasons.append("🤖 AI Model detected high-risk scam patterns.")
        elif ai_score < 10:
            # Brain says SAFE -> Lower Score (only if no Fatal Rules)
            if final_score < 50: 
                final_score = 5 # Trust the Brain
                reasons.append("✅ AI Context Analysis: Safe corporate language detected.")

    # 6. FINAL VERDICT
    if final_score > 80:
        verdict = "HIGH RISK"
        color = "RED"
    elif final_score > 40:
        verdict = "SUSPICIOUS"
        color = "YELLOW"
    else:
        verdict = "SAFE"
        color = "GREEN"

    return {
        "risk_score": final_score,
        "verdict": verdict,
        "reasons": reasons,
        "raw_text_analyzed": combined_text[:100] + "..."
    }