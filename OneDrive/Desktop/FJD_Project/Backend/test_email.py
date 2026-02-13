from email_validator import EmailValidator
import time

# Initialize
try:
    validator = EmailValidator()
    print("✅ Validator Loaded Successfully.")
except Exception as e:
    print(f"❌ Error loading validator: {e}")
    exit()

print("\n📧 EMAIL VALIDATOR DIAGNOSTIC TOOL (INTERACTIVE)")
print("===============================================")
print("Type 'exit' to quit at any time.\n")

while True:
    # 1. Get User Input
    email_input = input("👉 Enter Email Address to Test: ").strip()
    if email_input.lower() in ['exit', 'quit']:
        print("Exiting...")
        break

    if "@" not in email_input:
        print("⚠️ Invalid email format. Please try again.\n")
        continue

    # 2. Get Context (Optional)
    # The validator uses this to check if the domain matches the company name mentioned in text.
    print("   (Context helps detect spoofing, e.g., 'We are hiring for Amazon')")
    context_input = input("👉 Enter Email Body/Context (or press Enter to skip): ").strip()

    # 3. Run Analysis
    print(f"\n🔍 Analyzing: {email_input}...")
    time.sleep(0.5) # Dramatic pause

    try:
        score, reasons, verdict = validator.validate(email_input, context_input)

        # 4. Print Report
        print("-" * 40)
        print(f"   📊 SCORE:   {score}/100")
        print(f"   🏷️  VERDICT: {verdict}")
        
        if reasons:
            print("   ⚠️  REASONS:")
            for reason in reasons:
                print(f"      - {reason}")
        else:
            print("   ✅  REASONS: No suspicious patterns found.")
        print("-" * 40 + "\n")

    except Exception as e:
        print(f"❌ Analysis Failed: {e}\n")