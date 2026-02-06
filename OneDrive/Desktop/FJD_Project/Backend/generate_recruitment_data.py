import pandas as pd
import random
from faker import Faker

fake = Faker('en_IN')
NUM_SAMPLES = 8000
data = []

print(f"👔 Generating {NUM_SAMPLES} Advanced Recruitment Scenarios...")

# --- THE "PROFESSIONAL" SCAMS (Hardest to detect) ---

def scam_offer_letter():
    company = fake.company()
    return [
        f"Dear Candidate, we are pleased to offer you the position of {fake.job()} at {company}.",
        f"Your annual CTC will be {random.randint(4, 12)} LPA.",
        "Reporting time: 9:00 AM, Monday.",
        "Mandatory: Pay a refundable security deposit of ₹2,500 for the company laptop.",
        "This amount will be refunded in your first salary.",
        "Kindly transfer via UPI to the HR manager for asset allocation.",
        "Note: Uniform charges of ₹999 are applicable for new joiners."
    ]

def scam_task_system():
    # The "Prepaid Task" or "Mall" scam
    return [
        "Welcome to the Merchant Optimization Platform.",
        "Task 1/3 complete. Your wallet balance is ₹450.",
        "To withdraw, you must complete the Premium Task.",
        "Recharge your wallet with ₹1000 to unlock high commission.",
        "Your account is frozen due to low score.",
        "Pay tax of 18% to release your frozen funds.",
        "Don't worry, this is a trusted prepaid merchant task."
    ]

def scam_data_entry():
    # The "Legal Threat" scam
    return [
        "Your QC report shows 80% accuracy only.",
        "You have failed the project terms.",
        "Pay ₹4,500 for server maintenance or we will take legal action.",
        "Our legal team will send a notice to your home address.",
        "Breach of contract penalty applies.",
        "Pay immediately to close your file."
    ]

# --- REAL JOBS (To prevent false positives) ---

def real_offer_letter():
    return [
        f"Congratulations! We are excited to have you join {fake.company()}.",
        "Please bring your PAN card and Aadhar card for verification.",
        "We do not charge any money for recruitment.",
        "Your laptop will be handed over on the first day.",
        "The joining location is our Bangalore campus.",
        "Please sign the attached offer letter via DocuSign.",
        "Medical insurance is covered by the company."
    ]

def real_rejection():
    return [
        "Thank you for your interest in the {fake.job()} role.",
        "Unfortunately, we have decided to move forward with other candidates.",
        "We will keep your CV in our database for future roles.",
        "Best of luck with your job search."
    ]

# --- GENERATOR LOOP ---

for _ in range(NUM_SAMPLES):
    label = random.choice([0, 1])
    text_block = ""
    
    if label == 1: # SCAM
        scenario = random.choice([scam_offer_letter, scam_task_system, scam_data_entry])
        lines = scenario()
        # Create a "paragraph" that looks like a real email/message
        text_block = " ".join(lines)
        
    else: # REAL
        scenario = random.choice([real_offer_letter, real_rejection])
        lines = scenario()
        text_block = " ".join(lines)

    data.append([text_block, label])

df = pd.DataFrame(data, columns=["text", "label"])
df.to_csv("recruitment_dataset.csv", index=False)
print("✅ Generated 'Corporate Mimicry' Dataset.")