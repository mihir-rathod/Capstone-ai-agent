from database.db_connection import DatabaseConnection
from ai.gemini_client import GeminiAI
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize database connection
    db = DatabaseConnection()
    connection = db.get_connection()
    
    if connection and connection.is_connected():
        # Initialize Gemini AI
        try:
            ai_client = GeminiAI()
            
            # Example: Generate a response
            response = ai_client.generate_response("Hello, what can you help me with today?")
            print("AI Response:", response)
            
            # Here you can add your main application logic
            # For example:
            # - Process AI responses
            # - Store results in the database
            # - Handle user interactions
            
        except Exception as e:
            print(f"Error in main application: {e}")
        finally:
            # Close database connection
            db.close_connection()

if __name__ == "__main__":
    main()