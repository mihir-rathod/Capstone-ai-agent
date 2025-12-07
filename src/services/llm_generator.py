from config import client
from typing import Dict, Any, List, Union
import json
import re
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

def repair_json_response(text):
    """Robust JSON repair for common LLM formatting issues"""
    
    # Step 1: Remove any non-JSON content before/after the JSON object
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]
    
    # Step 2: Remove control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Step 3: Handle trailing commas - multiple passes
    for _ in range(10):
        text = re.sub(r',(\s*[\]\}])', r'\1', text)
    
    # Step 4: Handle missing commas between elements
    text = re.sub(r'"\s*\n\s*"', '",\n"', text)
    text = re.sub(r'(\}|\])\s*\n\s*(\{|\[|")', r'\1,\n\2', text)
    text = re.sub(r'(\d+)\s*\n\s*"', r'\1,\n"', text)
    text = re.sub(r'(true|false|null)\s*\n\s*"', r'\1,\n"', text)
    
    # Step 5: Handle truncated JSON
    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')
    
    if open_braces > 0:
        text = text.rstrip().rstrip(',') + '}' * open_braces
    if open_brackets > 0:
        text = text.rstrip().rstrip(',') + ']' * open_brackets
    
    # Step 6: Remove double commas
    text = re.sub(r',\s*,', ',', text)
    
    return text

def try_parse_json_with_recovery(text):
    """Try multiple strategies to parse JSON"""
    strategies = []
    
    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        strategies.append(("direct", str(e)))
    
    # Strategy 2: Basic repair
    try:
        repaired = repair_json_response(text)
        return json.loads(repaired)
    except json.JSONDecodeError as e:
        strategies.append(("basic_repair", str(e)))
    
    # Strategy 3: Collapse newlines then repair
    try:
        collapsed = re.sub(r'\n\s*', ' ', text)
        collapsed = repair_json_response(collapsed)
        return json.loads(collapsed)
    except json.JSONDecodeError as e:
        strategies.append(("collapse_newlines", str(e)))
    
    # Strategy 4: Binary search for valid JSON
    try:
        first_brace = text.find('{')
        if first_brace != -1:
            for end_pos in range(len(text), first_brace + 100, -100):
                try:
                    substring = text[first_brace:end_pos]
                    open_braces = substring.count('{') - substring.count('}')
                    open_brackets = substring.count('[') - substring.count(']')
                    substring = substring.rstrip().rstrip(',')
                    substring += ']' * max(0, open_brackets) + '}' * max(0, open_braces)
                    result = json.loads(substring)
                    if result:
                        return result
                except:
                    continue
    except Exception as e:
        strategies.append(("binary_search", str(e)))
    
    # All strategies failed
    error_msg = "; ".join([f"{s[0]}: {s[1][:50]}" for s in strategies])
    raise json.JSONDecodeError(f"All JSON recovery strategies failed: {error_msg}", text, 0)

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

    response_text = client.generate("gemini-2.5-flash", prompt)

    try:
        return try_parse_json_with_recovery(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini output not valid JSON: {e}")

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

    response_text = client.generate("gemini-2.5-flash", prompt)

    try:
        return try_parse_json_with_recovery(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini output not valid JSON: {e}")

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

    response_text = client.generate("gemini-2.5-flash", prompt)

    try:
        return try_parse_json_with_recovery(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini output not valid JSON: {e}")

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

    response_text = client.generate("gemini-2.5-flash", prompt)

    try:
        return try_parse_json_with_recovery(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini output not valid JSON: {e}")

