import pandas as pd
import joblib
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

print("📚 Loading V2 Dataset...")
data = pd.read_csv("master_dataset.csv")

# We remove 'call' and 'system' from stop words so the AI "hears" them.
custom_stop_words = list(ENGLISH_STOP_WORDS)
keep_words = ['call', 'system', 'bill', 'pay', 'name', 'click', 'link']
for word in keep_words:
    if word in custom_stop_words:
        custom_stop_words.remove(word)

print(f"🧠 Training on {len(data)} samples...")

X_train, X_test, y_train, y_test = train_test_split(data['text'], data['label'], test_size=0.2, random_state=42)

pipeline = Pipeline([
    # ngram_range=(1, 3) captures "click this link" or "urgent duty taxes"
    ('tfidf', TfidfVectorizer(stop_words=custom_stop_words, ngram_range=(1, 3), min_df=2, max_features=60000)),
    ('classifier', SGDClassifier(loss='modified_huber', penalty='l2', alpha=1e-5, random_state=42, max_iter=2000)) 
])

print("🏋️‍♂️ Training V2 Brain...")
pipeline.fit(X_train, y_train)

# --- REPORT ---
print("\n📊 SCORECARD:")
predictions = pipeline.predict(X_test)
print(classification_report(y_test, predictions, target_names=['Safe', 'Scam']))

joblib.dump(pipeline, "scam_model.pkl")
print("💾 V2 Brain Saved.")

# --- TOP TRIGGERS ---
print("\n🔍 TOP 15 SCAM SIGNALS:")
vectorizer = pipeline.named_steps['tfidf']
classifier = pipeline.named_steps['classifier']
feature_names = vectorizer.get_feature_names_out()
coefs = classifier.coef_[0]

top_positive = np.argsort(coefs)[-15:]
for i in top_positive[::-1]:
    print(f"   🔥 {feature_names[i]}: {coefs[i]:.2f}")