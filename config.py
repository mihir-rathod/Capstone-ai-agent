import os
from dotenv import load_dotenv
import google.generativeai as genai


# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file. Please set it in .env")

genai.configure(api_key=GEMINI_API_KEY)

# ✅ Wrapper class for easy usage
class GeminiClient:
    @staticmethod
    def generate(model: str, prompt: str) -> str:
        """
        Generates content from the Gemini model.
        """
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(prompt)
        return response.text

# Create global reusable instance
client = GeminiClient()