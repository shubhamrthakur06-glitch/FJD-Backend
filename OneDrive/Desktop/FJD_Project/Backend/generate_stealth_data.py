import pandas as pd
import random
from faker import Faker

fake = Faker('en_IN')
NUM_SAMPLES = 3000
data = []

print(f"🥷 Generating {NUM_SAMPLES} Stealth Synonym Scams...")

# --- 1. THE "COLLATERAL" SWAP (Replaces 'Security Deposit') ---
def scam_collateral():
    return [
        "To receive the company laptop, you must pay a refundable collateral of 3000 INR.",
        "Asset insurance is mandatory for remote work. This collateral is returned in your first salary.",
        "Please transfer the indemnity bond amount to the HR UPI.",
        "A cautionary deposit is required to secure your hardware shipment.",
        "This is not a fee, it is a refundable asset protection charge."
    ]

# --- 2. THE "LEDGER" SWAP (Replaces 'Frozen/Recharge') ---
def scam_ledger():
    return [
        "Your account is paused due to a ledger mismatch.",
        "To resume tasks, you must balance the ledger by adding 500 credits.",
        "Merchant audit pending. Settle the difference to release your withdrawal.",
        "Your working status is on hold. Clear the negative balance immediately.",
        "System limit exceeded. add funds to equalize the merchant order value."
    ]

# --- 3. THE "DUTY" SWAP (Replaces 'Tax/Customs') ---
def scam_duty():
    return [
        "Shipment held at customs. Pay the outstanding duty to release.",
        "Clearance charges are pending for your package.",
        "Settlement of 450 INR is required for the delivery to proceed.",
        "Avoid return to sender by paying the import tariff today.",
        "Your consignment is stuck at the hub. Settle dues via the link."
    ]

for _ in range(NUM_SAMPLES):
    # 100% SCAM DATA (We need to hammer this home)
    label = 1 
    scenario = random.choice([scam_collateral, scam_ledger, scam_duty])
    lines = scenario()
    # Randomly pick 2-3 lines to make a paragraph
    text = " ".join(random.sample(lines, k=random.randint(1, 3)))
    data.append([text, label])

df = pd.DataFrame(data, columns=["text", "label"])
df.to_csv("stealth_dataset.csv", index=False)
print("✅ Stealth Data Generated.")