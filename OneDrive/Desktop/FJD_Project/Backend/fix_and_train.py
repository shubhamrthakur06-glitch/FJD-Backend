import pandas as pd
import joblib
import random
import re
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

print("🧹 STARTING PHASE 11: FULL DATASET MERGE & SANITIZATION...")

# --- 1. THE CLEANING FUNCTION (The "Blindfold") ---
def clean_text(text):
    text = str(text)
    # 1. Remove the "Cheat Codes" (Prefixes)
    # The AI was just looking for "Unknown:" vs "HR:" labels. We remove them.
    text = text.replace("Unknown:", "").replace("HR:", "").replace("Me:", "")
    text = text.replace("Admin:", "").replace("Support:", "").replace("Mentor:", "")
    
    # 2. Normalize whitespace (remove newlines from chat blocks)
    text = text.replace("\n", " ").strip()
    
    # 3. Remove multiple spaces
    text = re.sub(' +', ' ', text)
    return text

# --- 2. LOAD ALL 7 DATASETS ---
files = [
    "dataset.csv",
    "chat_dataset.csv",
    "big_dataset.csv",
    "master_dataset.csv",
    "recruitment_dataset.csv",
    "universal_dataset.csv",
    "patch_dataset.csv",
    "stealth_dataset.csv",
    "dictionary_attack.csv"   # <--- THE NEW WEAPON
]

dfs = []
total_loaded = 0

for f in files:
    try:
        df = pd.read_csv(f)
        # Apply the cleaning immediately
        df['text'] = df['text'].apply(clean_text)
        dfs.append(df)
        print(f"   🔹 Loaded & Sanitized: {f} ({len(df)} rows)")
        total_loaded += len(df)
    except FileNotFoundError:
        print(f"   ⚠️ Skipping {f} (Not found)")
    except Exception as e:
        print(f"   ❌ Error loading {f}: {e}")

if not dfs:
    print("❌ Critical Error: No data loaded. Exiting.")
    exit()

# --- 3. INJECT "STARTUP INOCULATION" (The Anti-Paranoia Fix) ---
# This teaches the AI that "Urgency" and "High Growth" are not always scams.
print("   💉 Injecting 'Startup & Sales' Inoculation Data...")

startup_phrases = [
    "We are a high growth startup moving very fast.",
    "Need immediate joiners who can start coding on Day 1.",
    "No formal HR process yet, we just vibe and code.",
    "Equity and salary discussion after the hackathon.",
    "Looking for rockstars to crush our Q3 targets.",
    "Urgent requirement for sales executives. Walk-in today.",
    "Bring your laptop and show us what you can build.",
    "Hiring aggressively for the new Bangalore office.",
    "Spot offer for immediate joiners. Bring original docs.",
    "Founder's office role. High pressure, high reward."
]

# Generate 2500 safe samples to balance the fear
inoculation_data = []
for _ in range(2500): 
    # Combine 2 random phrases to make a sentence
    text = " ".join(random.sample(startup_phrases, k=2))
    inoculation_data.append([text, 0]) # Label 0 = SAFE

df_inoculation = pd.DataFrame(inoculation_data, columns=["text", "label"])
dfs.append(df_inoculation)

# --- 4. MERGE EVERYTHING ---
full_data = pd.concat(dfs, ignore_index=True)
full_data = full_data.sample(frac=1).reset_index(drop=True) # Shuffle randomly

print(f"🧠 TRAINING BRAIN ON {len(full_data)} CLEANED SAMPLES...")

# --- 5. SMART VOCABULARY SETUP ---
# We remove specific words from the "Ignore List" (Stop Words)
# so the AI pays attention to them.
my_stop_words = list(ENGLISH_STOP_WORDS)
important_words = ['call', 'contact', 'pay', 'paid', 'fee', 'money', 'urgent', 'immediate', 'bill', 'frozen']
for w in important_words:
    if w in my_stop_words: my_stop_words.remove(w)

pipeline = Pipeline([
    # TfidfVectorizer: Converts text to math
    # ngram_range=(1, 3): Reads "gate pass fee" as one concept, not 3 words.
    # max_features=25000: Increased vocabulary size for the huge dataset.
    ('tfidf', TfidfVectorizer(stop_words=my_stop_words, ngram_range=(1, 3), min_df=2, max_features=25000)),
    
    # SGDClassifier: The "Wolf". Fast, aggressive, hard boundaries.
    ('classifier', SGDClassifier(loss='modified_huber', penalty='l2', alpha=1e-5, random_state=42, max_iter=1000)) 
])

# --- 6. TRAIN & EVALUATE ---
X_train, X_test, y_train, y_test = train_test_split(full_data['text'], full_data['label'], test_size=0.15, random_state=42)

pipeline.fit(X_train, y_train)

print("\n📊 PHASE 11 REPORT CARD:")
predictions = pipeline.predict(X_test)
print(classification_report(y_test, predictions, target_names=['Safe', 'Scam']))

# --- 7. SAVE ---
joblib.dump(pipeline, "scam_model.pkl")
print("✅ FINAL BRAIN SAVED (Prefix-Free & Inoculated).")
