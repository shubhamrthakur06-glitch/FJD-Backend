import requests
import os

# 🟢 SECURE: Get key from Environment Variables (Render/System)
# This will return None if the key is missing, so we check for that later.
API_KEY = os.getenv("GOOGLE_API_KEY") 

def list_google_models():
    # 🛡️ Safety Check: Stop immediately if no key is found
    if not API_KEY:
        print("❌ CRITICAL ERROR: 'GOOGLE_API_KEY' not found in environment variables.")
        print("   -> If running locally: Set it in your terminal or .env file.")
        print("   -> If on Render: Check your 'Environment' tab.")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("✅ CONNECTION SUCCESSFUL! Here are your available models:\n")
            
            # Filter only models that can "generateContent" (Vision/Text)
            for model in data.get('models', []):
                if "generateContent" in model['supportedGenerationMethods']:
                    print(f"   🔹 Name: {model['name']}")
                    print(f"      Version: {model['version']}")
                    print(f"      Display: {model['displayName']}")
                    print("-" * 40)
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    list_google_models()