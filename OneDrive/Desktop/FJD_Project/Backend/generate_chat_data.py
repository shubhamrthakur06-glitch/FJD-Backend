import pandas as pd
import random
from faker import Faker

fake = Faker('en_IN')
NUM_SAMPLES = 6000
data = []

print(f"💬 Simulating {NUM_SAMPLES} Chat Logs (WhatsApp/Telegram)...")

# --- SCAM CONVERSATION PATTERNS ---
scam_openers = [
    "Hello dear", "Hi sir", "Are you looking for part time job?", 
    "Greetings from Amazon hiring team", "Part time wfh available"
]

scam_tactics = [
    "kindly message our HR on Telegram", 
    "complete 3 tasks to get payment", 
    "pay security deposit of 500rs refundable", 
    "your wallet is frozen pay tax to withdraw", 
    "download this app and register", 
    "send screenshot of payment",
    "just like youtube videos and earn"
]

scam_closers = [
    "limited seats", "hurry up", "offer expires soon", 
    "dont worry it is trusted company", "100% genuine process"
]

# --- REAL CONVERSATION PATTERNS ---
real_openers = [
    "Hi, I saw your application on LinkedIn", 
    "Hello, regarding the Python Developer role", 
    "Are you available for a call?", 
    "Your interview is scheduled"
]

real_tactics = [
    "can you send your updated CV?", 
    "please share your portfolio link", 
    "the office is located in Bangalore", 
    "we offer health insurance and PF", 
    "process involves 3 rounds of interview", 
    "no fees are charged for recruitment"
]

real_closers = [
    "let us know your availability", "thanks for your time", 
    "regards, HR Team", "check your email for invite"
]

for _ in range(NUM_SAMPLES):
    label = random.choice([0, 1])
    conversation = ""
    
    if label == 1: # SCAM CHAT
        # Simulate a messy chat structure
        p1 = random.choice(scam_openers)
        p2 = "Yes I am interested" # User reply simulation
        p3 = random.choice(scam_tactics)
        p4 = "Is there any fee?" # User suspicion
        p5 = random.choice(scam_closers)
        
        # Combine into a "screenshot text" format
        conversation = f"Unknown: {p1}\nMe: {p2}\nUnknown: {p3}\nMe: {p4}\nUnknown: {p5}"
        
    else: # REAL CHAT
        p1 = random.choice(real_openers)
        p2 = "Yes, what is the process?"
        p3 = random.choice(real_tactics)
        p4 = "Okay I will send it."
        p5 = random.choice(real_closers)
        
        conversation = f"HR: {p1}\nMe: {p2}\nHR: {p3}\nMe: {p4}\nHR: {p5}"

    data.append([conversation, label])

# Save specifically as chat data
df = pd.DataFrame(data, columns=["text", "label"])
df.to_csv("chat_dataset.csv", index=False)
print("✅ Chat Simulation Complete.")