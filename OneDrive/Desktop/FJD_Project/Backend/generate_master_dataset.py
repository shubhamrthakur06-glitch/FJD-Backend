import pandas as pd
import random
from faker import Faker

fake = Faker('en_IN')
NUM_SAMPLES = 12000 # Increased size
data = []

print(f"🧠 Generating {NUM_SAMPLES} Forensic Conversation Logs (V2)...")

# --- NEW: SMS / DELIVERY SCAMS (The "Boring" but Dangerous ones) ---
def scenario_sms_delivery():
    tracking = random.randint(100000, 999999)
    amount = random.choice(['45.00', '120.00', '216.21', '500'])
    return [
        f"FedEx: Shipment #{tracking} requires urgent Duty and Taxes.",
        f"Payment of {amount} is pending before delivery.",
        "Please pay today to avoid return.",
        f"Click link: https://www.bpoint.com.au/pay/{fake.slug()}",
        "If unpaid, legal action will be taken.",
        "Update your address immediately via this link.",
        "Your package is on hold at the warehouse."
    ]

def scenario_bank_alert():
    return [
        f"Dear Customer, your {fake.credit_card_provider()} card is blocked.",
        "KYC verification is pending.",
        "Click here to update PAN card immediately.",
        "Your account will be debited 5000rs for non-maintenance.",
        "Refund approved. Click to claim.",
        "HDFC Alert: Your Netbanking is disabled.",
        "Visit http://bit.ly/kyc-update now."
    ]

# --- EXISTING SCENARIOS (Retained) ---
def scenario_youtube_task():
    return [
        "Hello dear, part time job available.",
        "Just like YouTube videos and earn daily.",
        "First task completed. You earned 150rs.",
        "Now join Premium Group for big profit.",
        "Pay 1000rs security deposit refundable.",
        "This is prepaid task merchant task."
    ]

def scenario_fedex_police():
    return [
        "This is Mumbai Customs.",
        "Parcel seized with illegal passports and drugs.",
        "Transfer penalty to avoid arrest warrant.",
        "Skype verification mandatory."
    ]

def scenario_gate_pass():
    return [
        f"Interview at {fake.company()} confirmed.",
        "Pay 500rs for Gate Pass generation.",
        "Refundable after interview.",
        "Scan QR code sent to you."
    ]

# --- REAL SCENARIOS (Safety Control) ---
def scenario_real_sms():
    otp = random.randint(1000,9999)
    return [
        f"Your OTP for login is {otp}. Do not share it.",
        f"Amazon: Your package will be delivered today.",
        "Your SIP installment of 5000rs was successful.",
        "Credited: 25,000rs salary for Feb.",
        "Appointment confirmed with Dr. Sharma."
    ]

def scenario_real_chat():
    return [
        "Hi, are you available for a meeting?",
        "Please send the report by EOD.",
        "Happy birthday! Enjoy your day.",
        "Can you send me the location?"
    ]

# --- ASSEMBLER ---
for _ in range(NUM_SAMPLES):
    label = random.choice([0, 1])
    conversation_lines = []
    
    if label == 1: # SCAM
        scenario = random.choice([
            scenario_sms_delivery, scenario_bank_alert, 
            scenario_youtube_task, scenario_fedex_police, scenario_gate_pass
        ])
        lines = scenario()
    else: # REAL
        scenario = random.choice([scenario_real_sms, scenario_real_chat])
        lines = scenario()

    # Create random snippets
    if len(lines) > 2:
        start = random.randint(0, len(lines) - 2)
        text_block = "\n".join(lines[start : start + 3])
    else:
        text_block = "\n".join(lines)
        
    data.append([text_block, label])

df = pd.DataFrame(data, columns=["text", "label"])
df.to_csv("master_dataset.csv", index=False)
print("✅ Generated V2 Dataset (Includes SMS & Links).")