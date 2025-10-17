import os
from dotenv import load_dotenv
from ollama import Client

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv('OLLAMA_API_KEY')

# Check if the API key is set
if not api_key:
    raise ValueError("OLLAMA_API_KEY is not set in the environment variables.")

# Create the client
client = Client(
    host="https://ollama.com",
    headers={'Authorization': f'Bearer {api_key}'}
)

messages = [
    {
        'role': 'user',
        'content': 'Why is the sky blue?',
    },
]

# Stream and print the response
for part in client.chat('gpt-oss:120b', messages=messages, stream=True):
    print(part['message']['content'], end='', flush=True)
