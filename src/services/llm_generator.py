from config import client
from typing import Dict, Any, List, Union
import json
from src.config.prompts import (
    generate_report_prompt,
    generate_retail_data_report_prompt,
    generate_email_performance_report_prompt,
    generate_social_media_data_report_prompt
)

def format_content(data: Union[str, List[str]]) -> Union[str, List[str]]:
    """Helper function to properly format content"""
    if isinstance(data, list):
        return [str(item).strip() for item in data if item]
    return str(data).strip()

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
                    'data': []  # Initialize as empty list to support both string and list formats
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

def generate_retail_data_report(structure: dict, context: dict, feedback: Dict[str, Any] = None) -> dict:
    """Generate retail data report using Gemini with source tags"""
    # Create a copy of the structure and add source information
    modified_structure = {
        'pages': [{
            'page_number': page['page_number'],
            'tags': [{
                'id': tag['id'],
                'content': [{
                    'source': 'Gemini',
                    'title': str(tag.get('id')),
                    'data': []  # Initialize as empty list to support both string and list formats
                }]
            } for tag in page['tags']]
        } for page in structure['pages']]
    }

    prompt = generate_retail_data_report_prompt(modified_structure, context)

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

def generate_email_performance_report(structure: dict, context: dict, feedback: Dict[str, Any] = None) -> dict:
    """Generate email performance report using Gemini with source tags"""
    # Create a copy of the structure and add source information
    modified_structure = {
        'pages': [{
            'page_number': page['page_number'],
            'tags': [{
                'id': tag['id'],
                'content': [{
                    'source': 'Gemini',
                    'title': str(tag.get('id')),
                    'data': []  # Initialize as empty list to support both string and list formats
                }]
            } for tag in page['tags']]
        } for page in structure['pages']]
    }

    prompt = generate_email_performance_report_prompt(modified_structure, context)

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

def generate_social_media_data_report(structure: dict, context: dict, feedback: Dict[str, Any] = None) -> dict:
    """Generate social media data report using Gemini with source tags"""
    # Create a copy of the structure and add source information
    modified_structure = {
        'pages': [{
            'page_number': page['page_number'],
            'tags': [{
                'id': tag['id'],
                'content': [{
                    'source': 'Gemini',
                    'title': str(tag.get('id')),
                    'data': []  # Initialize as empty list to support both string and list formats
                }]
            } for tag in page['tags']]
        } for page in structure['pages']]
    }

    prompt = generate_social_media_data_report_prompt(modified_structure, context)

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
