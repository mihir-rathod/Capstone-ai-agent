from config import client
from typing import Dict, Any
import json
from src.config.prompts import generate_report_prompt

def generate_report(structure: dict, context: dict, feedback: Dict[str, Any] = None) -> dict:
    """Generate structured report using Gemini with source tags"""
    # Create a copy of the structure and add source information
    modified_structure = {
        'pages': [{
            'page_number': page['page_number'],
            'tags': [{
                'id': tag['id'],
                'content': [{
                    'source': 'Gemini',
                    'title': str(tag.get('id')),
                    'data': ''
                }]
            } for tag in page['tags']]
        } for page in structure['pages']]
    }

    prompt = generate_report_prompt(modified_structure, context)

    response_text = client.generate("gemini-2.5-pro", prompt)

    try:
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            cleaned_response = response_text[json_start:json_end]
            report_json = json.loads(cleaned_response)
        else:
            raise ValueError("No JSON object found in the response.")
    except Exception as e:
        raise ValueError(f"Gemini output not valid JSON: {e}")

    return report_json