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
from bs4 import BeautifulSoup # <--- NEW RECON TOOL

# --- CONFIGURATION ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
BRAIN_PATH = "fjd_deep_brain.h5"
TOKENIZER_PATH = "tokenizer.pickle"
PHISHTANK_PATH = "phishtank_urls.csv"

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

print("🧠 Booting Forensic Engine (with Active Recon)...")

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
    except Exception as e:
        pass

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
        print(f"❌ File Error: {e}")
    return content

def get_ai_score(text):
    if not text or not model or not tokenizer: return 0
    try:
        seq = tokenizer.texts_to_sequences([text])
        padded = pad_sequences(seq, maxlen=MAX_LENGTH, padding=PADDING_TYPE, truncating=TRUNC_TYPE)
        prediction = model.predict(padded, verbose=0)[0][0]
        return round(float(prediction) * 100, 2)
    except:
        return 50

# --- NEW: ACTIVE LINK RECON ---
def active_link_recon(url):
    """Visits the URL, scrapes the content, and returns extracted text."""
    try:
        # Pretend to be an iPhone to bypass basic bot-blockers
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
        }
        print(f"🕵️‍♂️ Deploying Active Recon on: {url}")
        
        # Timeout after 5 seconds so the app doesn't freeze forever
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract the Title
            title = soup.title.string if soup.title else ""
            
            # Extract paragraphs
            paragraphs = soup.find_all('p')
            body_text = " ".join([p.get_text() for p in paragraphs])
            
            # Combine it
            scraped_text = f"Website Title: {title}. Content: {body_text}"
            
            # Clean up whitespace
            scraped_text = " ".join(scraped_text.split())
            
            print(f"✅ Recon Successful. Extracted {len(scraped_text)} characters.")
            return scraped_text[:1000] # Return first 1000 chars to avoid overloading the Brain
        else:
            print(f"⚠️ Recon Failed. Site returned status: {response.status_code}")
            return f"Error: Site returned status {response.status_code}"
            
    except Exception as e:
        print(f"❌ Recon Failed (Site down or blocked): {e}")
        return "Error: Could not reach the website."

# --- MAIN ENDPOINT ---
@app.post("/analyze")
async def analyze_evidence(
    image: UploadFile = File(None), 
    document: UploadFile = File(None), 
    link: str = Form(None)
):
    print("📥 Commencing Triple-Threat Analysis...")
    reasons = []
    combined_text = ""
    
    # --- TRACK 1: THE RECON TRACK (LINK) ---
    link_score = 0
    if link:
        clean_link = link.lower().strip()
        
        # 1. Check PhishTank Database
        if clean_link in phish_blacklist:
            link_score = 100
            reasons.append(f"🚨 BLACKLIST: Link '{link}' is a verified phishing site.")
        else:
            # 2. Deploy Active Recon
            scraped_content = active_link_recon(link)
            
            if "Error:" in scraped_content:
                reasons.append("⚠️ SUSPICIOUS LINK: The provided website is offline or blocking forensic analysis.")
                # We bump the score slightly if the site is hiding
                link_score = 60 
            else:
                # 3. Feed the Scraped HTML directly to the Brain
                link_score = get_ai_score(scraped_content)
                if link_score > 80:
                    reasons.append("🚨 ACTIVE RECON: The website's hidden content matches known scam profiles.")
                elif link_score < 40:
                    reasons.append("✅ ACTIVE RECON: The website's content appears legitimate.")
                
                # Add the scraped text to the combined evidence pile
                combined_text += f" [Scraped from Link: {scraped_content}] "

    # --- TRACK 2: DOCUMENT ---
    doc_text = await extract_text_from_file(document)
    doc_score = get_ai_score(doc_text)
    if doc_text:
        combined_text += f" [Doc: {doc_text}] "
        if doc_score > 80: reasons.append("📄 Deep Scan: Document contains high-risk scam vocabulary.")

    # --- TRACK 3: IMAGE ---
    img_text = await extract_text_from_file(image)
    img_score = get_ai_score(img_text)
    if img_text:
        combined_text += f" [Image: {img_text}] "
        if img_score > 80: reasons.append("📷 Deep Scan: Screenshot contains high-risk scam vocabulary.")

    # --- THE JURY (Aggregation) ---
    final_score = max(link_score, doc_score, img_score)
    
    email_score = 50 
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', combined_text)
    if email_match:
        found_email = email_match.group(0)
        email_score, email_reasons, _ = email_validator.validate(found_email, combined_text)
        if email_score < 80: 
            reasons.extend(email_reasons)
            if final_score < 100:
                final_score = 100
                reasons.append("🚨 IDENTITY: Fake/Free Email Address Overrides Safe Text.")
        elif email_score == 100: 
            reasons.append(f"✅ IDENTITY: Verified Sender ({found_email})")
            if final_score < 90: 
                final_score = max(0, final_score - 20)
                reasons.append("🛡️ Trusted Sender lowers overall risk.")

    evidence_count = sum([1 for x in [image, document, link] if x is not None])
    confidence_level = "LOW"
    if evidence_count == 3: confidence_level = "EXTREME"
    elif evidence_count == 2: confidence_level = "HIGH"
    
    if final_score > 80:
        label, color = "HIGH RISK", "RED"
        if not reasons: reasons.append(f"AI Brain detected scam patterns (Confidence: {confidence_level}).")
    elif final_score > 40:
        label, color = "MODERATE", "YELLOW"
        reasons.append(f"Analysis is inconclusive. (Confidence: {confidence_level}).")
    else:
        label, color = "SAFE JOB", "GREEN"
        reasons.append(f"No active threats detected. (Confidence: {confidence_level}).")

    return {
        "score": int(final_score), "label": label, "color": color,
        "extracted_text": combined_text[:300] + "...", 
        "reasons": reasons,
        "confidence": confidence_level
    }