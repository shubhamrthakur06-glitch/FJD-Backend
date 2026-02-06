import joblib
import pandas as pd
from email_validator import EmailValidator

# 1. Load the Text Brain
print("🧠 Loading Text Brain...")
try:
    model = joblib.load("scam_model.pkl")
    print("✅ Brain Loaded.")
except:
    print("❌ Error: scam_model.pkl not found. Train it first!")
    exit()

# 2. Load the Email Detective
print("🕵️ Loading Email Validator...")
validator = EmailValidator()
print("✅ Detective Ready.")

print("\n🧪 INTEGRATED FORENSIC LAB (Veto Protocol Active)")
print("--------------------------------------------------")

while True:
    print("\n--------------------------------------------------")
    # Step A: Get Inputs
    email_input = input("📧 Enter Sender Email (or 'exit'): ").strip()
    if email_input.lower() == 'exit': break
    
    text_input = input("📝 Paste Chat/Text: ").strip()
    
    # Step B: Analyze Text (The Brain)
    text_prediction = model.predict([text_input])[0]
    text_prob = model.predict_proba([text_input])[0][1] * 100 # % chance of scam
    
    # Step C: Analyze Email (The Detective)
    email_score, email_reasons, email_verdict = validator.validate(email_input, text_input)
    
    # Step D: THE VETO PROTOCOL (Combining the scores)
    final_risk = text_prob
    override_msg = ""

    # Rule 1: The "Wolf" (Text Safe, Email Fake)
    if email_score == 0: 
        final_risk = 100.0
        override_msg = "🚨 IDENTITY OVERRIDE: Fake Email detected. Marked as FATAL."
    
    # Rule 2: The "Sus" (Text Suspicious, Email Bad)
    elif email_score < 50 and text_prob > 50:
        final_risk = 100.0
        override_msg = "🚨 CONFIRMATION: Risky Text + Bad Email = FATAL."

    # Rule 3: The "Verified" (Text Risky, Email Real)
    # If Email is 100% Trusted, we give the user the benefit of the doubt
    elif email_score >= 80 and text_prob > 60:
        final_risk = text_prob - 20 # Lower the risk slightly
        override_msg = "🛡️ IDENTITY SHIELD: Verified Sender. Risk lowered."

    # Final Formatting
    final_risk = max(0, min(100, final_risk)) # Cap at 0-100
    
    if final_risk > 80:
        status = "🔴 HIGH RISK (SCAM)"
    elif final_risk > 40:
        status = "🟡 MODERATE (WARNING)"
    else:
        status = "🟢 SAFE"

    # Step E: The Report
    print(f"\n📊 FINAL ANALYSIS REPORT")
    print(f"   -----------------------")
    print(f"   🧠 Text Analysis:   {text_prob:.2f}% Risk")
    print(f"   🕵️ Identity Check:  {email_verdict} (Trust Score: {email_score}/100)")
    for reason in email_reasons:
        print(f"      - {reason}")
    
    if override_msg:
        print(f"   ⚠️ {override_msg}")
        
    print(f"   -----------------------")
    print(f"   🎯 FINAL VERDICT:   {status} ({final_risk:.2f}%)")