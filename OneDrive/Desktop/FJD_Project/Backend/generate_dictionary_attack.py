import pandas as pd
import random

# 🎯 CONFIGURATION
NUM_SAMPLES = 20000  # Generating a massive dataset
OUTPUT_FILE = "dictionary_attack.csv"

print(f"📚 Generating {NUM_SAMPLES} Comprehensive Dictionary Attack Patterns...")

data = []

# =============================================================================
# 1. THE FINANCIAL FRAUD VOCABULARY (The "Money" Trap)
# =============================================================================
fin_verbs = [
    "pay", "deposit", "transfer", "remit", "settle", "clear", "authorize",
    "disburse", "credit", "recharge", "top-up", "balance", "equalize",
    "regularize", "validate", "authenticate", "link", "seed", "fund", "wire"
]

fin_nouns = [
    # Direct Costs
    "fee", "charge", "tax", "duty", "levy", "tariff", "premium", "token",
    "bill", "invoice", "fine", "penalty", "dues", "arrears", "debt",
    # Bureaucratic Words
    "collateral", "deposit", "security", "subscription", "membership",
    "pass", "permit", "license", "certificate", "bond", "indemnity",
    "insurance", "assurance", "guarantee", "retainer",
    # Financial States
    "liquidity", "escrow", "ledger", "balance", "shortfall", "deficit",
    "discrepancy", "variance", "limit", "cap", "threshold"
]

fin_adjectives = [
    "refundable", "mandatory", "pending", "frozen", "held", "blocked",
    "paused", "temporary", "verification", "activation", "clearance",
    "handling", "processing", "gate", "conversion", "audit", "server",
    "merchant", "gateway", "compliance", "regulatory", "administrative"
]

fin_closers = [
    "immediately", "by EOD", "instantly", "now", "urgently", "ASAP",
    "to unlock", "to release", "to unfreeze", "to withdraw", "to proceed",
    "to avoid penalty", "to avoid suspension", "before expiry",
    "via UPI", "via QR code", "via wallet", "via netbanking"
]

# =============================================================================
# 2. THE TECH & MALWARE VOCABULARY (The "Control" Trap)
# =============================================================================
tech_verbs = [
    "download", "install", "run", "open", "execute", "sideload", "update",
    "patch", "grant", "allow", "accept", "scan", "screen-share", "configure"
]

tech_nouns = [
    # Files
    "apk", "application", "file", "software", "installer", "viewer",
    "module", "plugin", "extension", "script", "bot", "config", "driver",
    # Remote Access Tools (RATs)
    "AnyDesk", "TeamViewer", "QuickSupport", "RustDesk", "RemoteDesktop",
    "screen mirroring", "remote assistant", "support tool"
]

tech_contexts = [
    "not on playstore", "sent via whatsapp", "mandatory for interview",
    "proprietary tool", "bypass security", "for attendance", "for training",
    "for verification", "server connection", "secure channel"
]

# =============================================================================
# 3. THE CRYPTO & MULE VOCABULARY (The "Laundering" Trap)
# =============================================================================
crypto_nouns = [
    "crypto", "usdt", "binance", "bitcoin", "eth", "wallet", "tether",
    "tokens", "gas fee", "network fee", "hash", "smart contract", "node"
]

mule_roles = [
    "payment processor", "transaction handler", "fund manager", "agent",
    "merchant", "operator", "arbitrage trader", "exchange partner"
]

mule_actions = [
    "keep 5%", "keep commission", "transfer remaining", "convert to",
    "receive funds", "route payment", "profit share", "daily payout"
]

# =============================================================================
# 4. THE AUTHORITY & THREAT VOCABULARY (The "Fear" Trap)
# =============================================================================
authority_nouns = [
    "Police", "Customs", "Cyber Crime", "RBI", "Income Tax", "Court",
    "Legal Notice", "Warrant", "FIR", "Challan", "Case File"
]

threat_actions = [
    "arrest", "block", "suspend", "terminate", "sue", "blackmail",
    "blacklist", "seize", "freeze", "audit", "raid"
]

# =============================================================================
# 5. THE TASK & JOB SCAM VOCABULARY (The "Greed" Trap)
# =============================================================================
task_nouns = [
    "tasks", "orders", "reviews", "likes", "scribing", "data entry",
    "typing", "captcha", "quiz", "survey", "rating"
]

task_earnings = [
    "earn daily", "part time", "work from home", "easy income",
    "guaranteed salary", "daily wage", "per page", "per like"
]

# =============================================================================
# GENERATOR ENGINE
# =============================================================================

for _ in range(NUM_SAMPLES):
    # Randomly select a scam archetype
    scam_type = random.choices(
        ["finance", "tech", "mule", "authority", "task"],
        weights=[40, 20, 15, 10, 15] # Weighted probability
    )[0]
    
    text = ""
    
    if scam_type == "finance":
        # Templates for Fee/Deposit scams
        templates = [
            f"Please {random.choice(fin_verbs)} the {random.choice(fin_adjectives)} {random.choice(fin_nouns)}.",
            f"System Alert: {random.choice(fin_nouns)} is {random.choice(fin_adjectives)}. {random.choice(fin_verbs)} {random.choice(fin_closers)}.",
            f"To {random.choice(fin_closers)}, a {random.choice(fin_nouns)} of INR {random.randint(500, 5000)} is required.",
            f"Your withdrawal is {random.choice(fin_adjectives)} due to {random.choice(fin_nouns)} mismatch. {random.choice(fin_verbs)} to resolve.",
            f"This is a {random.choice(fin_adjectives)} {random.choice(fin_nouns)}. It will be returned after process."
        ]
        text = random.choice(templates)
        
    elif scam_type == "tech":
        # Templates for Malware/RAT scams
        templates = [
            f"{random.choice(tech_verbs)} the {random.choice(tech_nouns)} {random.choice(tech_contexts)}.",
            f"For video call, {random.choice(tech_verbs)} {random.choice(tech_nouns)}. It is {random.choice(fin_adjectives)}.",
            f"Your device needs a {random.choice(tech_nouns)} to connect. {random.choice(tech_verbs)} now.",
            f"Kindly open {random.choice(tech_nouns)} and share the code for {random.choice(fin_adjectives)} check."
        ]
        text = random.choice(templates)
        
    elif scam_type == "mule":
        # Templates for Money Laundering
        templates = [
            f"Job role: {random.choice(mule_roles)}. {random.choice(mule_actions)}.",
            f"Receive money in your bank, {random.choice(mule_actions)} {random.choice(crypto_nouns)}.",
            f"Invest in {random.choice(crypto_nouns)} node and {random.choice(mule_actions)} daily.",
            f"No investment. {random.choice(mule_actions)} and {random.choice(fin_verbs)} to company wallet."
        ]
        text = random.choice(templates)
        
    elif scam_type == "authority":
        # Templates for Legal Threats
        templates = [
            f"{random.choice(authority_nouns)} Alert: Your ID is involved in illegal activity.",
            f"Pay {random.choice(fin_nouns)} or face {random.choice(threat_actions)}.",
            f"Your package is held by {random.choice(authority_nouns)}. Pay {random.choice(fin_nouns)} to avoid {random.choice(threat_actions)}.",
            f"Immediate {random.choice(fin_verbs)} required to close {random.choice(authority_nouns)} case."
        ]
        text = random.choice(templates)
        
    elif scam_type == "task":
        # Templates for Task Scams
        templates = [
            f"{random.choice(task_earnings)} by completing {random.choice(task_nouns)}.",
            f"Register now for {random.choice(task_nouns)}. {random.choice(fin_nouns)} applies.",
            f"Complete 3 {random.choice(task_nouns)} to {random.choice(fin_closers)}.",
            f"Prepaid {random.choice(task_nouns)} available. High commission guaranteed."
        ]
        text = random.choice(templates)

    data.append([text, 1]) # LABEL 1 = SCAM

# Save to CSV
df = pd.DataFrame(data, columns=["text", "label"])
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Generated {OUTPUT_FILE} with {len(df)} patterns.")