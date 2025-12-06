from typing import Dict, Any
import json
from ollama import Client
from dotenv import load_dotenv
from src.config.prompts import (
    generate_report_prompt,
    generate_retail_data_report_prompt,
    generate_email_performance_report_prompt,
    generate_social_media_data_report_prompt
)

load_dotenv()
import os
import re

def repair_json_response(text):
    """Robust JSON repair for common LLM formatting issues"""
    
    # Step 1: Remove any non-JSON content before/after the JSON object
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]
    
    # Step 2: Remove control characters (except newlines and tabs for now)
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

def fix_unescaped_quotes_in_strings(text):
    """Try to fix unescaped quotes within JSON string values"""
    result = []
    in_string = False
    escape_next = False
    
    for i, char in enumerate(text):
        if escape_next:
            result.append(char)
            escape_next = False
            continue
            
        if char == '\\':
            result.append(char)
            escape_next = True
            continue
            
        if char == '"':
            if not in_string:
                in_string = True
                result.append(char)
            else:
                # Check if this quote ends the string or is embedded
                # Look ahead to see if next non-whitespace is : , } ]
                rest = text[i+1:].lstrip()
                if rest and rest[0] in ':,}]':
                    # This is a closing quote
                    in_string = False
                    result.append(char)
                else:
                    # This might be an embedded quote - escape it
                    result.append('\\"')
        else:
            result.append(char)
    
    return ''.join(result)

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
    
    # Strategy 3: Fix unescaped quotes then repair
    try:
        fixed_quotes = fix_unescaped_quotes_in_strings(text)
        repaired = repair_json_response(fixed_quotes)
        return json.loads(repaired)
    except json.JSONDecodeError as e:
        strategies.append(("fix_quotes", str(e)))
    
    # Strategy 4: Remove all newlines within strings (collapse to single line)
    try:
        # Replace newlines that are inside strings with spaces
        collapsed = re.sub(r'\n\s*', ' ', text)
        collapsed = repair_json_response(collapsed)
        return json.loads(collapsed)
    except json.JSONDecodeError as e:
        strategies.append(("collapse_newlines", str(e)))
    
    # Strategy 5: Binary search to find valid JSON prefix
    try:
        first_brace = text.find('{')
        if first_brace != -1:
            # Try progressively shorter substrings
            for end_pos in range(len(text), first_brace + 100, -100):
                try:
                    substring = text[first_brace:end_pos]
                    # Close any open structures
                    open_braces = substring.count('{') - substring.count('}')
                    open_brackets = substring.count('[') - substring.count(']')
                    substring = substring.rstrip().rstrip(',')
                    substring += ']' * max(0, open_brackets) + '}' * max(0, open_braces)
                    result = json.loads(substring)
                    if result:  # If we got something valid, return it
                        return result
                except:
                    continue
    except Exception as e:
        strategies.append(("binary_search", str(e)))
    
    # Strategy 6: Try using ast.literal_eval as last resort for simpler structures
    try:
        import ast
        # Replace JSON booleans/null with Python equivalents
        py_text = text.replace('true', 'True').replace('false', 'False').replace('null', 'None')
        result = ast.literal_eval(py_text)
        # Convert back to JSON-compatible format
        return json.loads(json.dumps(result))
    except Exception as e:
        strategies.append(("ast_eval", str(e)))
    
    # All strategies failed
    error_msg = "; ".join([f"{s[0]}: {s[1][:50]}" for s in strategies])  # Truncate error messages
    raise json.JSONDecodeError(f"All JSON recovery strategies failed: {error_msg}", text, 0)

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
                    'data': []
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

CRITICAL JSON REQUIREMENTS - FOLLOW EXACTLY:
1. Respond ONLY with a valid JSON object - no explanations, no markdown, no code blocks
2. Start with { and end with }
3. Use double quotes (") for ALL strings and keys
4. NO trailing commas - never put a comma before } or ]
5. Escape quotes inside strings with backslash: \"
6. Keep string values SHORT - max 200 characters per string
7. Do NOT use newlines inside string values
8. Do NOT use special characters like tabs or backslashes (except for escaping)
9. Ensure every { has a matching } and every [ has a matching ]
10. Verify your JSON is valid before responding"""
        },
        {
            'role': 'user',
            'content': """I need you to analyze retail marketing data and generate a report.
When appropriate, return content as a list of strings for better organization (e.g., bullet points, sequential items).
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
        if response_text.startswith('```'):
            response_text = response_text[3:]  # Skip ```
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()

        try:
            return try_parse_json_with_recovery(response_text)
        except json.JSONDecodeError as e:
            print(f"All JSON recovery attempts failed: {e}")
            print("Response text (first 500 chars):", response_text[:500])
            raise ValueError(f"Could not parse Ollama response as JSON: {str(e)}")

    else:
        raise ValueError("No valid response received from Ollama")

def generate_retail_data_report(structure: dict, context: dict, feedback: Dict[str, Any] = None) -> dict:
    """Generate retail data report using Ollama with source tags"""
    # Create a copy of the structure and add source information
    modified_structure = {
        'pages': [{
            'page_number': page['page_number'],
            'tags': [{
                'id': tag['id'],
                'title': tag.get('title', str(tag['id'])),
                'content': [{
                    'source': 'Ollama',
                    'data': []
                }]
            } for tag in page['tags']]
        } for page in structure['pages']]
    }

    prompt = generate_retail_data_report_prompt(modified_structure, context)

    # Create an Ollama client
    client = Client(host=os.getenv('OLLAMA_API_URL'))

    # Break down the prompt into structured messages for better Ollama understanding
    schema_str = json.dumps(modified_structure, indent=2)
    context_str = json.dumps(context, indent=2)

    # Generate response using Ollama with structured messages
    response = client.chat(model='gpt-oss:120b', messages=[
        {
            'role': 'system',
            'content': """You are an expert retail data analyst for Marine Corps Community Services (MCCS).

CRITICAL JSON REQUIREMENTS - FOLLOW EXACTLY:
1. Respond ONLY with a valid JSON object - no explanations, no markdown, no code blocks
2. Start with { and end with }
3. Use double quotes (") for ALL strings and keys
4. NO trailing commas - never put a comma before } or ]
5. Escape quotes inside strings with backslash: \"
6. Keep string values SHORT - max 200 characters per string
7. Do NOT use newlines inside string values
8. Do NOT use special characters like tabs or backslashes (except for escaping)
9. Ensure every { has a matching } and every [ has a matching ]
10. Verify your JSON is valid before responding"""
        },
        {
            'role': 'user',
            'content': """I need you to analyze retail sales data and generate a comprehensive report.
Create meaningful content for every field based on the available data and logical inferences.
The report must follow this exact JSON structure:

""" + schema_str
        },
        {
            'role': 'user',
            'content': """Here is the retail data context to use for the report:

""" + context_str
        },
        {
            'role': 'user',
            'content': """Requirements:
1. Fill in EVERY field in the schema with meaningful, comprehensive content
2. Generate content based on available data, trends, and logical inferences
3. Use "No data available" only when genuinely impossible to populate a field
4. Always provide appropriate headers and titles
5. Format all content as strings, join multiple items with \n
6. Include specific metrics, dates, and context from the data
7. Return ONLY the JSON object, no other text

CRITICAL JSON FORMATTING REQUIREMENTS:
- Start your response with { and end with }
- Use proper JSON syntax with commas between fields
- Escape quotes properly in strings
- Do not include any text before or after the JSON object
- Ensure all brackets and braces are properly matched"""
        }
    ])

    # Parse the response
    if response and hasattr(response, 'message') and response.message.get('content'):
        response_text = response.message['content'].strip()

        # Handle potential markdown code block
        if response_text.startswith('```json'):
            response_text = response_text[7:]  # Skip ```json
        if response_text.startswith('```'):
            response_text = response_text[3:]  # Skip ```
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()

        try:
            return try_parse_json_with_recovery(response_text)
        except json.JSONDecodeError as e:
            print(f"All JSON recovery attempts failed: {e}")
            print("Response text (first 500 chars):", response_text[:500])
            raise ValueError(f"Could not parse Ollama response as JSON: {str(e)}")

    else:
        raise ValueError("No valid response received from Ollama")

def generate_email_performance_report(structure: dict, context: dict, feedback: Dict[str, Any] = None) -> dict:
    """Generate email performance report using Ollama with source tags"""
    # Create a copy of the structure and add source information
    modified_structure = {
        'pages': [{
            'page_number': page['page_number'],
            'tags': [{
                'id': tag['id'],
                'title': tag.get('title', str(tag['id'])),
                'content': [{
                    'source': 'Ollama',
                    'data': []
                }]
            } for tag in page['tags']]
        } for page in structure['pages']]
    }

    prompt = generate_email_performance_report_prompt(modified_structure, context)

    # Create an Ollama client
    client = Client(host=os.getenv('OLLAMA_API_URL'))

    # Break down the prompt into structured messages for better Ollama understanding
    schema_str = json.dumps(modified_structure, indent=2)
    context_str = json.dumps(context, indent=2)

    # Generate response using Ollama with structured messages
    response = client.chat(model='gpt-oss:120b', messages=[
        {
            'role': 'system',
            'content': """You are an expert email marketing analyst for Marine Corps Community Services (MCCS).

CRITICAL JSON REQUIREMENTS - FOLLOW EXACTLY:
1. Respond ONLY with a valid JSON object - no explanations, no markdown, no code blocks
2. Start with { and end with }
3. Use double quotes (") for ALL strings and keys
4. NO trailing commas - never put a comma before } or ]
5. Escape quotes inside strings with backslash: \"
6. Keep string values SHORT - max 200 characters per string
7. Do NOT use newlines inside string values
8. Do NOT use special characters like tabs or backslashes (except for escaping)
9. Ensure every { has a matching } and every [ has a matching ]
10. Verify your JSON is valid before responding"""
        },
        {
            'role': 'user',
            'content': """I need you to analyze email marketing performance data and generate a comprehensive report.
Create meaningful content for every field based on the available data and logical inferences.
The report must follow this exact JSON structure:

""" + schema_str
        },
        {
            'role': 'user',
            'content': """Here is the email performance data context to use for the report:

""" + context_str
        },
        {
            'role': 'user',
            'content': """Requirements:
1. Fill in EVERY field in the schema with meaningful, comprehensive content
2. Generate content based on available data, trends, and logical inferences
3. Use "No data available" only when genuinely impossible to populate a field
4. Always provide appropriate headers and titles
5. Format all content as strings, join multiple items with \n
6. Include specific metrics, dates, and context from the data
7. Return ONLY the JSON object, no other text

CRITICAL JSON FORMATTING REQUIREMENTS:
- Start your response with { and end with }
- Use proper JSON syntax with commas between fields
- Escape quotes properly in strings
- Do not include any text before or after the JSON object
- Ensure all brackets and braces are properly matched"""
        }
    ])

    # Parse the response
    if response and hasattr(response, 'message') and response.message.get('content'):
        response_text = response.message['content'].strip()

        # Handle potential markdown code block
        if response_text.startswith('```json'):
            response_text = response_text[7:]  # Skip ```json
        if response_text.startswith('```'):
            response_text = response_text[3:]  # Skip ```
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()

        try:
            return try_parse_json_with_recovery(response_text)
        except json.JSONDecodeError as e:
            print(f"All JSON recovery attempts failed: {e}")
            print("Response text (first 500 chars):", response_text[:500])
            raise ValueError(f"Could not parse Ollama response as JSON: {str(e)}")

    else:
        raise ValueError("No valid response received from Ollama")

def generate_social_media_data_report(structure: dict, context: dict, feedback: Dict[str, Any] = None) -> dict:
    """Generate social media data report using Ollama with source tags"""
    # Create a copy of the structure and add source information
    modified_structure = {
        'pages': [{
            'page_number': page['page_number'],
            'tags': [{
                'id': tag['id'],
                'title': tag.get('title', str(tag['id'])),
                'content': [{
                    'source': 'Ollama',
                    'data': []
                }]
            } for tag in page['tags']]
        } for page in structure['pages']]
    }

    prompt = generate_social_media_data_report_prompt(modified_structure, context)

    # Create an Ollama client
    client = Client(host=os.getenv('OLLAMA_API_URL'))

    # Break down the prompt into structured messages for better Ollama understanding
    schema_str = json.dumps(modified_structure, indent=2)
    context_str = json.dumps(context, indent=2)

    # Generate response using Ollama with structured messages
    response = client.chat(model='gpt-oss:120b', messages=[
        {
            'role': 'system',
            'content': """You are an expert social media analyst for Marine Corps Community Services (MCCS).

CRITICAL JSON REQUIREMENTS - FOLLOW EXACTLY:
1. Respond ONLY with a valid JSON object - no explanations, no markdown, no code blocks
2. Start with { and end with }
3. Use double quotes (") for ALL strings and keys
4. NO trailing commas - never put a comma before } or ]
5. Escape quotes inside strings with backslash: \"
6. Keep string values SHORT - max 200 characters per string
7. Do NOT use newlines inside string values
8. Do NOT use special characters like tabs or backslashes (except for escaping)
9. Ensure every { has a matching } and every [ has a matching ]
10. Verify your JSON is valid before responding"""
        },
        {
            'role': 'user',
            'content': """I need you to analyze social media performance data and generate a comprehensive report.
Create meaningful content for every field based on the available data and logical inferences.
The report must follow this exact JSON structure:

""" + schema_str
        },
        {
            'role': 'user',
            'content': """Here is the social media data context to use for the report:

""" + context_str
        },
        {
            'role': 'user',
            'content': """Requirements:
1. Fill in EVERY field in the schema with meaningful, comprehensive content
2. Generate content based on available data, trends, and logical inferences
3. Use "No data available" only when genuinely impossible to populate a field
4. Always provide appropriate headers and titles
5. Format all content as strings, join multiple items with \n
6. Include specific metrics, dates, and context from the data
7. Return ONLY the JSON object, no other text

CRITICAL JSON FORMATTING REQUIREMENTS:
- Start your response with { and end with }
- Use proper JSON syntax with commas between fields
- Escape quotes properly in strings
- Do not include any text before or after the JSON object
- Ensure all brackets and braces are properly matched"""
        }
    ])

    # Parse the response
    if response and hasattr(response, 'message') and response.message.get('content'):
        response_text = response.message['content'].strip()

        # Handle potential markdown code block
        if response_text.startswith('```json'):
            response_text = response_text[7:]  # Skip ```json
        if response_text.startswith('```'):
            response_text = response_text[3:]  # Skip ```
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()

        try:
            return try_parse_json_with_recovery(response_text)
        except json.JSONDecodeError as e:
            print(f"All JSON recovery attempts failed: {e}")
            print("Response text (first 500 chars):", response_text[:500])
            raise ValueError(f"Could not parse Ollama response as JSON: {str(e)}")

    else:
        raise ValueError("No valid response received from Ollama")
