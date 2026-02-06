import pandas as pd
import random
from faker import Faker

fake = Faker('en_IN')
NUM_SAMPLES = 10000 # More data
data = []

print(f"🏭 Generating {NUM_SAMPLES} Mixed-Length Scenarios...")

# --- THE POISON LIST (The Incompatible Pairs) ---
# Phrases that should NEVER exist in a real job
poison_phrases = [
    "pay for gate pass", "pay for id card", "pay for laptop",
    "deposit for verification", "money for uniform", "security deposit refundable",
    "registration fee 500", "registration charges apply", "scan qr code for salary",
    "complete task and earn", "investment plan for job", "buy joining kit",
    "pay 500rs", "pay 1000rs", "pay 2000rs", "send money"
]

# Real job benefits
real_phrases = [
    "free recruitment", "company payroll", "no charges", "walk in interview",
    "face to face round", "salary credited monthly", "pf and esic provided",
    "health insurance given", "laptop provided by company", "cab facility available"
]

for _ in range(NUM_SAMPLES):
    label = random.choice([0, 1])
    text = ""
    
    if label == 1: # SCAM
        # STRATEGY 1: The "Snippet" (30% chance)
        # We feed it JUST the poison so it learns to fear these exact words.
        if random.random() < 0.3:
            text = f"{random.choice(poison_phrases)}."
        
        # STRATEGY 2: The "Hidden Poison" (70% chance)
        # Buried inside a normal looking sentence
        else:
            opener = f"Urgent hiring for {fake.job()}."
            poison = random.choice(poison_phrases)
            text = f"{opener} {poison}. Contact {fake.phone_number()}."

    else: # REAL
        # Real jobs should talk about benefits or process
        opener = f"Hiring for {fake.job()}."
        benefit = random.choice(real_phrases)
        
        text = f"{opener} {benefit}. Apply now at {fake.domain_name()}."

    data.append([text, label])

df = pd.DataFrame(data, columns=["text", "label"])
df.to_csv("big_dataset.csv", index=False)
print("✅ Generated Poison-Enhanced Data.")