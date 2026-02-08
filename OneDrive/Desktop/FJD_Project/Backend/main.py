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
# If any of these appear, it is AUTOMATICALLY a scam.
FATAL_PATTERNS = [
    r"security\s?deposit",
    r"gate\s?pass",
    r"id\s?card\s?generation",
    r"refundable\s?fee",
    r"pay\s?for\s?training",
    r"money\s?for\s?laptop",
    r"bank\s?details.*salary",
    r"usdt",
    r"crypto",
    r"telegram",
    r"whatsapp",
    r"verify\s?your\s?identity",
    r"account\s?termination",
    r"suspend.*account",
    r"liking\s?youtube\s?videos",
    r"task\s?scam"
]

# --- LOAD RESOURCES ---
model = None
tokenizer = None
phish_blacklist = set()

print("🧠 Booting Forensic Engine...")
try:
    model = tf.keras.models.load_model(BRAIN_PATH)
    with open(TOKENIZER_PATH, 'rb') as handle:
        tokenizer = pickle.load(handle)
    print("✅ Deep Brain & Tokenizer Online.")
except Exception as e:
    print(f"❌ CRITICAL ERROR LOADING BRAIN: {e}")

if os.path.exists(PHISHTANK_PATH):
    try:
        df = pd.read_csv(PHISHTANK_PATH)
        target_col = 'text' if 'text' in df.columns else 'url'
        phish_blacklist = set(df[target_col].astype(str).str.lower())
    except: pass

email_validator = EmailValidator() 

# --- HELPER 1: DOMAIN AGE CHECKER (THE SILVER BULLET) ---
def check_domain_age(url):
    try:
        domain = urlparse(url).netloc
        print(f"🕵️‍♂️ CHECKING AGE: {domain}")
        
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        
        # Handle cases where multiple dates are returned
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        if creation_date:
            # Calculate Age in Days
            age_days = (datetime.now() - creation_date).days
            print(f"✅ Domain Age: {age_days} days")
            return age_days
    except Exception as e:
        print(f"⚠️ Age Check Failed: {e}")
        return None
    return None

# --- HELPER 2: ACTIVE RECON (BeautifulSoup) ---
def active_link_recon(url):
    print(f"🕵️‍♂️ ACTIVE SCAN: Visiting {url}...")
    
    # 1. THE WHITE LIST (Common Sense)
    SAFE_DOMAINS = [
        "google.com", "www.google.com", "linkedin.com", "www.linkedin.com",
        "microsoft.com", "www.microsoft.com", "apple.com", "www.apple.com",
        "amazon.com", "www.amazon.com", "glassdoor.com", "www.glassdoor.com",
        "indeed.com", "www.indeed.com", "naukri.com", "www.naukri.com"
    ]
    try:
        domain = urlparse(url).netloc.lower()
        if domain in SAFE_DOMAINS or f"www.{domain}" in SAFE_DOMAINS:
            return "TRUSTED_DOMAIN_OVERRIDE"
    except: pass

    # 2. THE SCRAPER
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
        }
        response = requests.get(url, headers=headers, timeout=4)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else ""
            
            # Clean text
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            clean_text = ' '.join(chunk for chunk in lines if chunk)
            
            return f"Website Title: {title}. Content: {clean_text[:800]}"
        else:
            return f"Error: Site returned status {response.status_code}"
    except Exception as e:
        return "Error: Could not reach website."

# --- HELPER 3: AI & OCR ---
def raw_gemini_ocr(image_bytes):
    if not GOOGLE_API_KEY: return None
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Extract all text exactly."}, {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}]}]}
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except: return None

async def extract_text_from_file(file: UploadFile):
    if not file: return ""
    filename = file.filename.lower()
    content = ""
    try:
        contents = await file.read()
        
        # 1. IMAGES
        if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            return raw_gemini_ocr(img_byte_arr.getvalue()) or ""
            
        # 2. PDF
        elif filename.endswith('.pdf'):
            pdf_reader = PdfReader(io.BytesIO(contents))
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text: content += text + "\n"
                
        # 3. WORD DOCS
        elif filename.endswith('.docx'):
            doc = docx.Document(io.BytesIO(contents))
            for para in doc.paragraphs:
                content += para.text + "\n"
                
        # 4. TEXT FILES (THIS WAS MISSING!) 🚨
        elif filename.endswith('.txt'):
            return contents.decode('utf-8')
            
    except Exception as e:
        print(f"❌ File Error: {e}")
    return content

def get_ai_score(text):
    if not text or not model: return 0
    try:
        seq = tokenizer.texts_to_sequences([text])
        padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding=PADDING_TYPE, truncating=TRUNC_TYPE)
        prediction = model.predict(padded, verbose=0)[0][0]
        return round(float(prediction) * 100, 2)
    except: return 50

def check_fatal_keywords(text):
    if not text: return None
    text_lower = text.lower()
    for pattern in FATAL_PATTERNS:
        if re.search(pattern, text_lower):
            return f"🚨 RED FLAG DETECTED: Found suspicious term matching '{pattern.replace(r'', '').replace(r's?', '')}'."
    return None

# --- MAIN ENDPOINT ---
@app.post("/analyze")
async def analyze_evidence(
    image: UploadFile = File(None), 
    document: UploadFile = File(None), 
    link: str = Form(None)
):
    print(f"📥 Analyzing Evidence...")
    reasons = []
    combined_text = ""
    
    # --- TRACK 1: LINK ANALYSIS (Age + Content) ---
    link_score = 0
    if link:
        clean_link = link.lower().strip()
        
        # A. Blacklist Check
        if clean_link in phish_blacklist:
            link_score = 100
            reasons.append(f"🚨 BLACKLIST MATCH: Known phishing site.")
        else:
            # B. Domain Age Check (The Silver Bullet)
            domain_age = check_domain_age(link)
            if domain_age is not None and domain_age < 30:
                link_score = 100
                reasons.append(f"🚨 FRESH DOMAIN: Website registered only {domain_age} days ago (High Risk).")
            
            # C. Content Scan
            scraped_data = active_link_recon(link)
            
            if scraped_data == "TRUSTED_DOMAIN_OVERRIDE":
                # Only trust if Age check didn't already flag it (e.g. spoofed DNS)
                if link_score < 100:
                    link_score = 0
                    reasons.append(f"✅ VERIFIED: Link is from a trusted major domain.")
                    combined_text += f" {link}"
            
            elif "Error" in scraped_data:
                link_score = max(link_score, 50)
                reasons.append("⚠️ UNVERIFIED: Website is offline or blocking connections.")
            
            else:
                combined_text += f" {scraped_data}"
                web_ai_score = get_ai_score(scraped_data)
                if web_ai_score > 80:
                    link_score = 100
                    reasons.append(f"🚨 CONTENT ALERT: Website matches scam templates.")

    # --- TRACK 2 & 3: DOCS & IMAGES ---
    doc_text = await extract_text_from_file(document)
    if doc_text:
        combined_text += f" {doc_text}"
        if get_ai_score(doc_text) > 80: reasons.append("📄 Document contains high-risk scam vocabulary.")

    img_text = await extract_text_from_file(image)
    if img_text:
        combined_text += f" {img_text}"
        if get_ai_score(img_text) > 80: reasons.append("📷 Screenshot contains high-risk scam vocabulary.")

    # --- FINAL SCORING ---
    final_score = max(link_score, get_ai_score(combined_text))

    # 🛑 VETO CHECK (The Safety Net)
    fatal_reason = check_fatal_keywords(combined_text)
    if fatal_reason:
        final_score = 100
        reasons.insert(0, fatal_reason) # Add to TOP of reasons
        print(f"🚫 VETO TRIGGERED: {fatal_reason}")
    
    # Identity & Whitelist Logic
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', combined_text)
    if email_match:
        found_email = email_match.group(0)
        email_score, email_reasons, _ = email_validator.validate(found_email, combined_text)
        if email_score < 80: 
            reasons.extend(email_reasons)
            if final_score < 100: final_score = 100
        elif email_score == 100 and final_score < 90:
             final_score = max(0, final_score - 20)

    # Confidence Calculation
    evidence_count = sum([1 for x in [image, document, link] if x is not None])
    confidence = "EXTREME" if evidence_count == 3 else "HIGH" if evidence_count == 2 else "LOW"
    
    if final_score > 80:
        label, color = "HIGH RISK", "RED"
        if not reasons: reasons.append("AI detected high-risk patterns.")
    elif final_score > 40:
        label, color = "MODERATE", "YELLOW"
        reasons.append("Analysis inconclusive.")
    else:
        label, color = "SAFE JOB", "GREEN"
        reasons.append("No active threats detected.")

    try:
        db.collection("scam_reports").add({
            "score": final_score, "reasons": reasons, "timestamp": firestore.SERVER_TIMESTAMP
        })
    except: pass

    return {
        "score": int(final_score), "label": label, "color": color,
        "extracted_text": combined_text[:200] + "...", 
        "reasons": reasons,
        "confidence": confidence
    }