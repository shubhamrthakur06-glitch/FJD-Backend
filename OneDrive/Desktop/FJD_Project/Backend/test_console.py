import joblib
import re
import os

MODEL_PATH = "scam_model.pkl"

# --- UPDATED FATAL LIST (Syncs with Generator) ---
FATAL_KEYWORDS = [
    "registration fee", "security deposit", "refundable amount", 
    "pay for laptop", "id card", "gate pass", "scan qr code", 
    "bank otp", "processing fee", "money for kit",
    "buy connection", "investment required", "uniform charge",
    "refundable", "google map rating", "telegram", "whatsapp"
]

SAFE_CONTEXT = ["no", "never", "zero", "without", "fraud", "fake", "scam", "avoid", "beware"]

def check_veto(text):
    text_lower = text.lower()
    sentences = re.split(r'[.!?]', text_lower)
    for sentence in sentences:
        for fatal in FATAL_KEYWORDS:
            if fatal in sentence:
                is_safe = False
                for safe_word in SAFE_CONTEXT:
                    if safe_word in sentence:
                        is_safe = True
                        break
                if not is_safe:
                    return True, fatal
    return False, None

def load_brain():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)

def main():
    print("🕵️‍♂️ FJD Forensic Console 2.0")
    model = load_brain()
    if not model: return

    while True:
        print("\n" + "="*40)
        user_input = input("📝 Enter text: ")
        if user_input == 'exit': break

        is_fatal, trigger = check_veto(user_input)
        
        # Get AI Score
        ai_prob = model.predict_proba([user_input])[0][1]
        ai_score = round(ai_prob * 100, 2)

        final_score = ai_score
        status = "SAFE"
        
        if is_fatal:
            final_score = 100.0
            status = f"🔴 FATAL (Trigger: {trigger})"
        elif ai_score > 75:
            status = "🟠 HIGH RISK"
        elif ai_score > 40:
            status = "🟡 MODERATE"
        else:
            status = "🟢 SAFE"

        print(f"📊 REPORT | Veto: {trigger if is_fatal else 'PASS'} | AI: {ai_score}% | FINAL: {status}")

if __name__ == "__main__":
    main()