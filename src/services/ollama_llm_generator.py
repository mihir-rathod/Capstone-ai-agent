from typing import Dict, Any
import json
from ollama import Client
from dotenv import load_dotenv
from src.config.prompts import generate_report_prompt

load_dotenv()
import os

def generate_report(structure: dict, context: dict, feedback: Dict[str, Any] = None) -> dict:
    """Generate structured report using Ollama with source tags"""
    # Create a copy of the structure and add source information
    modified_structure = {
        'pages': [{
            'page_number': page['page_number'],
            'tags': [{
                'id': tag['id'],
                'title': tag.get('title', str(tag['id'])),
                'content': [{
                    'source': 'Ollama',
                    'data': ''
                }]
            } for tag in page['tags']]
        } for page in structure['pages']]
    }

    prompt = generate_report_prompt(modified_structure, context)

    # Create an Ollama client
    client = Client(host=os.getenv('OLLAMA_API_URL'))

    # Break down the prompt into structured messages for better Ollama understanding
    schema_str = json.dumps(modified_structure, indent=2)
    context_str = json.dumps(context, indent=2)
    
        # Generate response using Ollama with structured messages
    response = client.chat(model='gpt-oss:120b', messages=[
        {
            'role': 'system',
            'content': """You are an expert marketing data analyst for Marine Corps Community Services (MCCS).
Focus on generating accurate, data-driven content for each field in the report structure.
You can return data as either a single string or a list of strings for better organization.
Respond ONLY with a valid JSON object that matches the provided schema exactly."""
        },
        {
            'role': 'user',
            'content': """I need you to analyze retail marketing data and generate a report.
When appropriate, return content as a list of strings for better organization (e.g., bullet points, sequential items).
For narrative content, you can use either a single string or a list of related points.
The report must follow this exact JSON structure:

""" + schema_str
        },
        {
            'role': 'user',
            'content': """Here is the data context to use for the report:

""" + context_str
        },
        {
            'role': 'user',
            'content': """Requirements:
1. Fill in every field in the schema with relevant content
2. Use only data from the provided context
3. Format all content as strings
4. Join multi-item content with \n
5. Format dates as "Month DD, YYYY"
6. Format percentages with %% (double %)
7. Return ONLY the JSON object, no other text"""
        }
    ])
    
    # Parse the response
    if response and hasattr(response, 'message') and response.message.get('content'):
        response_text = response.message['content'].strip()
        
        # Handle potential markdown code block
        if response_text.startswith('```json'):
            response_text = response_text[7:]  # Skip ```json
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()
        
        try:
            # Find the outermost JSON object
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                cleaned_response = response_text[json_start:json_end]
                try:
                    report_json = json.loads(cleaned_response)
                    
                    # Verify the structure matches what we expect
                    if not isinstance(report_json, dict) or 'pages' not in report_json:
                        print(f"Unexpected JSON structure: {report_json.keys() if isinstance(report_json, dict) else 'not a dict'}")
                        raise ValueError("Response JSON does not match expected structure")
                    
                    return report_json
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    print("Response text:", cleaned_response[:200] + "..." if len(cleaned_response) > 200 else cleaned_response)
                    raise ValueError("Could not parse Ollama response as JSON")
            else:
                print("No JSON object found in:", response_text[:200] + "..." if len(response_text) > 200 else response_text)
                raise ValueError("No JSON object found in the response")
        except Exception as e:
            print(f"Error processing Ollama response: {e}")
            print("Raw response:", response_text[:200] + "..." if len(response_text) > 200 else response_text)
            raise ValueError(f"Failed to process Ollama response: {str(e)}")
    else:
        raise ValueError("No valid response received from Ollama")

