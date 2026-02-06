import pandas as pd
import joblib
import os
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

print("🧪 Initializing Unified Training Protocol...")

# 1. LOAD ALL DATASETS
files = ["master_dataset.csv", "recruitment_dataset.csv", "universal_dataset.csv", "patch_dataset.csv"]
dfs = []

for f in files:
    if os.path.exists(f):
        print(f"   🔹 Loading {f}...")
        dfs.append(pd.read_csv(f))
    else:
        print(f"   ⚠️ Warning: {f} not found. Skipping.")

if not dfs:
    print("❌ No data found! Run the generators first.")
    exit()

# 2. MERGE DATA
full_data = pd.concat(dfs, ignore_index=True)
# Shuffle the data
full_data = full_data.sample(frac=1).reset_index(drop=True)

print(f"🧠 Total Training Samples: {len(full_data)}")

# 3. CUSTOM STOP WORDS (The "Hearing Aid")
# We remove specific words from the "ignore list" so the AI pays attention to them.
my_stop_words = list(ENGLISH_STOP_WORDS)
keep_words = ['call', 'contact', 'bill', 'pay', 'system', 'fee', 'charge', 'frozen', 'tax', 'limit']
for w in keep_words:
    if w in my_stop_words: my_stop_words.remove(w)

# 4. PIPELINE
# We increase max_features because our vocabulary is getting larger (Bank + FedEx + Corporate + Tasks)
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words=my_stop_words, ngram_range=(1, 3), min_df=2, max_features=15000)),
    ('classifier', SGDClassifier(loss='modified_huber', penalty='l2', alpha=1e-5, random_state=42)) 
])

# 5. TRAIN
X_train, X_test, y_train, y_test = train_test_split(full_data['text'], full_data['label'], test_size=0.2, random_state=42)

print("🏋️‍♂️ Training the Unified Super-Brain...")
pipeline.fit(X_train, y_train)

# 6. EVALUATE
print("\n📊 UNIFIED MODEL REPORT:")
predictions = pipeline.predict(X_test)
print(classification_report(y_test, predictions, target_names=['Safe', 'Scam']))

# 7. SAVE
joblib.dump(pipeline, "scam_model.pkl")
print("✅ Unified Brain Saved to 'scam_model.pkl'")
