import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# เช็ค API Key
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {bool(api_key)}")
if api_key:
    print(f"First 10 chars: {api_key[:10]}...")

# ทดสอบ Gemini
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-1.5-pro')  # เพิ่ม models/
    response = model.generate_content("Say hello")
    print("✅ SUCCESS! Gemini works!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {e}")