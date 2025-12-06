import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions


# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file. Please set it in .env")

genai.configure(api_key=GEMINI_API_KEY)

# ✅ Wrapper class for easy usage with retry logic
class GeminiClient:
    # Retry configuration
    MAX_RETRIES = 3
    INITIAL_DELAY = 60  # seconds to wait on rate limit
    
    @staticmethod
    def generate(model: str, prompt: str) -> str:
        """
        Generates content from the Gemini model with retry logic for rate limits.
        """
        model_instance = genai.GenerativeModel(model)
        
        for attempt in range(GeminiClient.MAX_RETRIES):
            try:
                response = model_instance.generate_content(prompt)
                return response.text
                
            except google_exceptions.ResourceExhausted as e:
                # Rate limit error (429)
                if attempt < GeminiClient.MAX_RETRIES - 1:
                    delay = GeminiClient.INITIAL_DELAY * (2 ** attempt)  # Exponential backoff
                    print(f"[Gemini] Rate limit hit. Waiting {delay} seconds before retry {attempt + 2}/{GeminiClient.MAX_RETRIES}...")
                    time.sleep(delay)
                else:
                    print(f"[Gemini] Rate limit exceeded after {GeminiClient.MAX_RETRIES} retries")
                    raise
                    
            except Exception as e:
                # For other errors, check if it's a rate limit error by message
                error_msg = str(e).lower()
                if "429" in str(e) or "quota" in error_msg or "rate" in error_msg:
                    if attempt < GeminiClient.MAX_RETRIES - 1:
                        delay = GeminiClient.INITIAL_DELAY * (2 ** attempt)
                        print(f"[Gemini] Rate limit detected. Waiting {delay} seconds before retry {attempt + 2}/{GeminiClient.MAX_RETRIES}...")
                        time.sleep(delay)
                    else:
                        print(f"[Gemini] Rate limit exceeded after {GeminiClient.MAX_RETRIES} retries")
                        raise
                else:
                    # Non-rate-limit error, raise immediately
                    raise
        
        # Should not reach here, but just in case
        raise Exception("Failed to generate content after retries")

# Create global reusable instance
client = GeminiClient()