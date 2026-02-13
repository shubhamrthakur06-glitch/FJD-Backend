import requests
import time
import io
import os

# 🔧 CONFIGURATION
# API_URL = "http://127.0.0.1:8000"       # Local
API_URL = "https://fjd-brain.onrender.com" # Live

# --- STATE (Holds your evidence before sending) ---
evidence = {
    "image_text": None,
    "doc_text": None,
    "link_url": None
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print("📱 FJD APP SIMULATOR (DEV CONSOLE)")
    print("==================================")
    print("Staged Evidence:")
    
    # Show what is currently loaded
    img_status = "✅ Loaded" if evidence['image_text'] else "❌ Empty"
    link_status = f"✅ {evidence['link_url']}" if evidence['link_url'] else "❌ Empty"
    doc_status = "✅ Loaded" if evidence['doc_text'] else "❌ Empty"
    
    print(f"  [1] 🖼️  Screenshot Text:  {img_status}")
    print(f"  [2] 🌐 Link URL:         {link_status}")
    print(f"  [3] 📄 Document Text:    {doc_status}")
    print("----------------------------------")

def run_analysis():
    print("\n🚀 SENDING DATA TO FORENSIC ENGINE...")
    
    # Prepare the Multipart Data
    files = {}
    data = {}
    
    # 1. Simulate Image (Send text as a .txt file labeled 'image')
    # The backend now accepts .txt, so this bypasses OCR and tests the Brain directly.
    if evidence['image_text']:
        f = io.BytesIO(evidence['image_text'].encode('utf-8'))
        files['image'] = ('simulated_screenshot.txt', f, 'text/plain')
        
    # 2. Simulate Document
    if evidence['doc_text']:
        f = io.BytesIO(evidence['doc_text'].encode('utf-8'))
        files['document'] = ('simulated_contract.txt', f, 'text/plain')
        
    # 3. Add Link
    if evidence['link_url']:
        data['link'] = evidence['link_url']
        
    if not files and not data:
        print("⚠️  No evidence staged! Please add something first.")
        input("Press Enter...")
        return

    start_time = time.time()
    try:
        # Mimic the App's POST request
        response = requests.post(f"{API_URL}/analyze", files=files, data=data)
        duration = round(time.time() - start_time, 2)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ ANALYSIS COMPLETE ({duration}s)")
            print("==================================")
            
            # 🎨 Visual Score
            score = result['score']
            bar = "█" * (score // 5) + "░" * ((100 - score) // 5)
            color_icon = "🔴" if result['color'] == "RED" else "🟢" if result['color'] == "GREEN" else "🟡"
            
            print(f"{color_icon} RISK SCORE: {score}%")
            print(f"   [{bar}]")
            print(f"🏷️  VERDICT:  {result['label']}")
            print(f"🤖 CONFIDENCE: {result['confidence']}")
            print("\n🧐 DETECTED THREATS:")
            if result['reasons']:
                for r in result['reasons']:
                    print(f"   - {r}")
            else:
                print("   - No active threats found.")
                
            print("\n📝 EXTRACTED CONTEXT (What the AI saw):")
            print(f"   \"{result['extracted_text'][:150]}...\"")
            
        else:
            print(f"\n❌ SERVER ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n💥 CONNECTION ERROR: {e}")
        
    input("\nPress Enter to continue...")

# --- MAIN LOOP ---
while True:
    print_header()
    print("Actions:")
    print("  [4] 🚀 RUN ANALYSIS")
    print("  [5] 🧹 Clear All Evidence")
    print("  [6] 🚪 Exit")
    
    choice = input("\nSelect Option > ")
    
    if choice == '1':
        print("\n--- PASTE SCREENSHOT TEXT (One line) ---")
        evidence['image_text'] = input("> ")
    elif choice == '2':
        print("\n--- PASTE LINK URL ---")
        evidence['link_url'] = input("> ")
    elif choice == '3':
        print("\n--- PASTE DOCUMENT TEXT (One line) ---")
        evidence['doc_text'] = input("> ")
    elif choice == '4':
        run_analysis()
    elif choice == '5':
        evidence = {"image_text": None, "doc_text": None, "link_url": None}
    elif choice == '6':
        break