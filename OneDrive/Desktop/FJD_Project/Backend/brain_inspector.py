import joblib
import pandas as pd

# Load the brain
try:
    model = joblib.load("scam_model.pkl")
    vectorizer = model.named_steps['tfidf']
    classifier = model.named_steps['classifier']
except:
    print("❌ Error: Brain not found.")
    exit()

# Get the vocabulary
feature_names = vectorizer.get_feature_names_out()
coefs = classifier.coef_[0]

# Create a dictionary for fast lookup
word_weights = {word: coef for word, coef in zip(feature_names, coefs)}

print("\n🧠 AI BRAIN SURGEON TOOL")
print("------------------------")
print("Type a word or phrase to see its 'Scam Score'.")
print("Positive (+) = SCAM  |  Negative (-) = SAFE")
print("------------------------")

while True:
    query = input("\n🔍 Inspect Word/Phrase: ").lower().strip()
    if query == 'exit': break
    
    # Check single words
    if query in word_weights:
        score = word_weights[query]
        status = "🔴 SCAM TRIGGER" if score > 0 else "🟢 SAFE SIGNAL"
        print(f"   Ref: '{query}' => Score: {score:.4f} ({status})")
    else:
        # Check if it's part of a known n-gram (phrase)
        found = False
        for word in word_weights:
            if query in word:
                print(f"   Found related concept: '{word}' => {word_weights[word]:.4f}")
                found = True
        
        if not found:
            print("   ❌ Brain has not learned this word yet.")