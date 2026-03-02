import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env from backend directory
load_dotenv("backend/.env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Say hello in a coding style.")
    print(f"Gemini Response: {response.text}")
except Exception as e:
    print(f"Error connecting to Gemini: {e}")
