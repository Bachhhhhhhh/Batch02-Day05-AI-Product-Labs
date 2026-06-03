import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.chat_service import process_gemini_ai, process_openai_ai

print("Testing Gemini API...")
try:
    res = process_gemini_ai("tôi bị ho và sổ mũi")
    print("Gemini Result:")
    print(res)
except Exception as e:
    print(f"Gemini Exception: {e}")

print("---------------------------------")
print("Testing OpenAI API...")
try:
    res = process_openai_ai("tôi bị ho và sổ mũi")
    print("OpenAI Result:")
    print(res)
except Exception as e:
    print(f"OpenAI Exception: {e}")
