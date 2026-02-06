import pandas as pd
import random
from faker import Faker

fake = Faker('en_IN')
NUM_SAMPLES = 4000
data = []

print(f"🩹 Generating {NUM_SAMPLES} Surgical Patch Data...")

# --- 1. TEACHING IT "BANK INFO" IS OKAY FOR SALARY ---
def safe_onboarding():
    return [
        "Please bring a cancelled cheque for salary account creation.",
        "Submit your PAN card copy and Aadhar for background verification.",
        "We need your bank details to process the monthly payroll.",
        "HR will collect your documents for the provident fund (PF) setup.",
        "This is for your employee file and salary credit only."
    ]

# --- 2. TEACHING IT "URGENCY" IS OKAY FOR WALKINS ---
def safe_urgency():
    return [
        f"Urgent requirement for {fake.job()}. Walk-in interview today.",
        "Immediate joiners required. Spot offer letter.",
        "Drive for freshers. Bring original documents for verification only.",
        "Hiring aggressively for sales role. No fees. Direct company payroll.",
        "Emergency opening. Face to face interview at our office."
    ]

# --- 3. TEACHING IT "FROZEN/TASK" IS DEADLY ---
def deadly_task_scam():
    return [
        "Your account is frozen. Pay tax to withdraw funds.",
        "Complete the optimization task to unfreeze your wallet.",
        "Merchant error. Deposit 50% to reclaim your commission.",
        "System paused. You must recharge to finish the last order.",
        "Premium task allocated. High return but requires deposit."
    ]

for _ in range(NUM_SAMPLES):
    # Equal chance of generating one of these 3 specific scenarios
    choice = random.choice(["safe_bank", "safe_urgent", "deadly_task"])
    
    if choice == "safe_bank":
        text = " ".join(safe_onboarding())
        label = 0 # SAFE
    elif choice == "safe_urgent":
        text = " ".join(safe_urgency())
        label = 0 # SAFE
    else:
        text = " ".join(deadly_task_scam())
        label = 1 # SCAM

    data.append([text, label])

df = pd.DataFrame(data, columns=["text", "label"])
df.to_csv("patch_dataset.csv", index=False)
print("✅ Patch Data Generated. Now re-train.")