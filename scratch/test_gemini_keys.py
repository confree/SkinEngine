import google.generativeai as genai
import os
from dotenv import load_dotenv

def test_key(api_key):
    print(f"Testing key: {api_key[:10]}...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hi")
        print(f"✅ Success: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    # 1. Test .env key
    # load_dotenv()
    env_key = "AIzaSyBmCaxvLjWCD0BSEUsQ6Yt7Ha22n33gmXw"
    test_key(env_key)
    
    # 2. Test hardcoded key
    hardcoded_key = "AIzaSyD1MVFUZux4oHnk8hEimxgwFqKq7EaOENU"
    test_key(hardcoded_key)
