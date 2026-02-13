from email_validator import EmailValidator

# Initialize
validator = EmailValidator()

print("📧 EMAIL VALIDATOR DIAGNOSTIC TOOL")
print("==================================")

# 🧪 TEST CASE 1: The "Gmail CEO" (Scam)
email1 = "ceo.recruitment.team@gmail.com"
context1 = "I am the CEO. Reply to my personal email."
print(f"\n[Test 1] Analyzing: {email1}")
score, reasons, verdict = validator.validate(email1, context1)
print(f"   Score: {score}/100")
print(f"   Verdict: {verdict}")
print(f"   Reasons: {reasons}")

# 🧪 TEST CASE 2: The "Real Recruiter" (Safe)
email2 = "sarah.jones@microsoft.com"
context2 = "Please schedule a time on my calendar."
print(f"\n[Test 2] Analyzing: {email2}")
score, reasons, verdict = validator.validate(email2, context2)
print(f"   Score: {score}/100")
print(f"   Verdict: {verdict}")
print(f"   Reasons: {reasons}")

# 🧪 TEST CASE 3: The "Typosquatting" (Scam)
email3 = "hr@amazonn-jobs.com"
context3 = "We are hiring for Amazon Fulfillment."
print(f"\n[Test 3] Analyzing: {email3}")
score, reasons, verdict = validator.validate(email3, context3)
print(f"   Score: {score}/100")
print(f"   Verdict: {verdict}")
print(f"   Reasons: {reasons}")

print("\n==================================")