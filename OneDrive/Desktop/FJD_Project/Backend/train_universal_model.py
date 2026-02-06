import pandas as pd
import joblib
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

print("📚 Loading Universal Dataset...")
try:
    data = pd.read_csv("universal_dataset.csv")
except FileNotFoundError:
    print("❌ Error: Run generate_multipurpose_data.py first!")
    exit()

# We remove 'call' and 'contact' from stop words because scammers say "Call this number"
my_stop_words = list(ENGLISH_STOP_WORDS)
for w in ['call', 'contact', 'bill', 'pay', 'system']:
    if w in my_stop_words: my_stop_words.remove(w)

print(f"🧠 Training on {len(data)} samples...")

# Split data to test accuracy later
X_train, X_test, y_train, y_test = train_test_split(data['text'], data['label'], test_size=0.2, random_state=42)

pipeline = Pipeline([
    # TfidfVectorizer converts text to numbers
    # ngram_range=(1, 3) captures: "Pay", "Pay Duty", "Pay Duty Taxes"
    ('tfidf', TfidfVectorizer(stop_words=my_stop_words, ngram_range=(1, 3), min_df=2, max_features=10000)),
    
    # SGDClassifier is a linear SVM (Aggressive and Fast)
    ('classifier', SGDClassifier(loss='modified_huber', random_state=42)) 
])

print("🏋️‍♂️ Training the brain...")
pipeline.fit(X_train, y_train)

# Test the brain immediately
print("\n🔍 EVALUATION REPORT:")
predictions = pipeline.predict(X_test)
print(classification_report(y_test, predictions, target_names=['Safe', 'Scam']))

# Save the brain
joblib.dump(pipeline, "scam_model.pkl")
print("💾 Brain Saved to 'scam_model.pkl'")

# --- DEBUG: Show what it learned ---
print("\n🔥 TOP 10 SCAM INDICATORS:")
vectorizer = pipeline.named_steps['tfidf']
classifier = pipeline.named_steps['classifier']
feature_names = vectorizer.get_feature_names_out()
coefs = classifier.coef_[0]
top_positive = np.argsort(coefs)[-10:]
for i in top_positive[::-1]:
    print(f"   ⚠️ {feature_names[i]}: {coefs[i]:.2f}")