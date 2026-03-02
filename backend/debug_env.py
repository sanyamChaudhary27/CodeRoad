import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_env():
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Current Working Directory: {os.getcwd()}")
    
    try:
        import google.generativeai as genai
        print("google-generativeai is INSTALLED")
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            
        if api_key:
            print(f"GEMINI_API_KEY found (starts with {api_key[:5]}...)")
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content("Say hello in one word.")
                print(f"Gemini Test Response: {response.text.strip()}")
            except Exception as e:
                print(f"Gemini API test FAILED: {e}")
        else:
            print("GEMINI_API_KEY NOT FOUND in environment or .env")
            
    except ImportError:
        print("google-generativeai is NOT INSTALLED")

if __name__ == "__main__":
    check_env()
