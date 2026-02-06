import pandas as pd
import random
from faker import Faker

fake = Faker('en_IN') # Use Indian English for realistic local contexts
NUM_SAMPLES = 15000   # We need a LOT of data to make it smart
data = []

print(f"🧠 Generating {NUM_SAMPLES} General Scam & Safe Conversations...")

# --- SCAM SCENARIOS ---

def scam_delivery():
    # Matches your FedEx screenshot pattern
    links = ["http://bit.ly/23", "www.bpoint.com.au", "fedex-customs-pay.com", "delivery-fee.in"]
    return [
        f"FedEx: Shipment #{random.randint(1000,9999)} requires urgent Duty and Taxes payment.",
        f"Your parcel is on hold. Pay {random.randint(100,500)}rs to release.",
        f"Customs duty pending. Click link to pay: {random.choice(links)}",
        "BlueDart: Address incomplete. Update here or parcel will be returned.",
        "IndiaPost: Your package delivery failed. Reschedule here."
    ]

def scam_job_chat():
    # Chat based job scams
    return [
        "Hello dear, do you want part time job?",
        "Earn 3000-5000 daily by liking YouTube videos.",
        "Kindly message me on Telegram for job details.",
        "No interview required. Direct joining. Just pay registration fee.",
        "Hiring for back office. Send 500rs for ID card generation."
    ]

def scam_bank_kyc():
    return [
        f"Dear Customer, your {fake.credit_card_provider()} account is blocked.",
        "PAN Card update required. Click link to verify KYC.",
        "Your SBI points will expire today. Redeem now at http://fake-bank.com",
        "Electricity bill unpaid. Power will be cut tonight. Call this number."
    ]

# --- SAFE SCENARIOS ---

def safe_delivery():
    return [
        f"Your order #{random.randint(1000,9999)} has been delivered.",
        "Amazon: Your package is out for delivery with agent Ravi.",
        "OTP for delivery is 4567. Do not share with anyone.",
        "Your Zomato order is picked up.",
        "Flipkart: Refund of 500rs processed to your source account."
    ]

def safe_chat():
    return [
        "Hey, are we meeting today?",
        "Please send the files by evening.",
        "Happy birthday! Have a great year ahead.",
        "Can you call me when you are free?",
        "The meeting link is on Google Meet."
    ]

# --- GENERATOR LOOP ---

for _ in range(NUM_SAMPLES):
    label = random.choice([0, 1])
    text = ""
    
    if label == 1: # SCAM
        scenario = random.choice([scam_delivery, scam_job_chat, scam_bank_kyc])
        # Pick 2-3 sentences to form a "message"
        lines = scenario()
        text = " ".join(random.sample(lines, k=random.randint(1, 2)))
        
        # Inject specific trigger words from your "Fatal List" to reinforce them
        if random.random() < 0.3:
            text += f" Contact via WhatsApp."
            
    else: # SAFE
        scenario = random.choice([safe_delivery, safe_chat])
        lines = scenario()
        text = " ".join(random.sample(lines, k=random.randint(1, 2)))

    data.append([text, label])

# Save to CSV
df = pd.DataFrame(data, columns=["text", "label"])
df.to_csv("universal_dataset.csv", index=False)
print("✅ Universal Dataset Generated.")