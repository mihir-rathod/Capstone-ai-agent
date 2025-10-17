import os
from dotenv import load_dotenv
import google.generativeai as genai
from src.config.settings import settings

# Load environment variables from .env file
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = settings.GOOGLE_API_KEY
if not GEMINI_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

class GeminiClient:
    @staticmethod
    def generate(model: str, prompt: str) -> str:
        """Generates content from the Gemini model."""
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(prompt)
        return response.text

# Create global reusable instance
client = GeminiClient()