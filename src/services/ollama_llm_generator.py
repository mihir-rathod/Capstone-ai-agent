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
You must respond ONLY with valid JSON. No explanations, no text, no markdown.
Start your response with { and end with }.
Use double quotes for all strings and keys.
No trailing commas.
Respond only with the JSON object."""
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
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()

        # Try to repair common JSON issues
        def repair_json(text):
            """Repair common JSON formatting issues from Ollama responses"""
            import re

            # Fix missing commas after string values followed by newlines and quotes
            # Pattern: "value"\n  "next_key" -> "value",\n  "next_key"
            text = re.sub(r'"\s*\n\s*"', '",\n"', text)

            # Fix missing commas after string values followed by closing braces
            # Pattern: "value"\n  } -> "value"\n  },
            text = re.sub(r'"\s*\n\s*(\}|\])', '",\n\\1', text)

            # Fix missing commas after numbers followed by quotes
            # Pattern: 123\n  "key" -> 123,\n  "key"
            text = re.sub(r'(\d+)\s*\n\s*"', '\\1,\n"', text)

            # Fix missing commas after boolean/null values
            # Pattern: true\n  "key" -> true,\n  "key"
            text = re.sub(r'(true|false|null)\s*\n\s*"', '\\1,\n"', text)

            return text

        try:
            # First try direct parsing
            report_json = json.loads(response_text)
            return report_json
        except json.JSONDecodeError as e:
            print(f"Direct JSON parsing failed: {e}")
            print("Attempting to repair JSON...")

            try:
                # Try to repair and parse
                repaired_text = repair_json(response_text)
                report_json = json.loads(repaired_text)
                print("JSON repair successful!")
                return report_json
            except json.JSONDecodeError as repair_e:
                print(f"JSON repair also failed: {repair_e}")
                print("Response text (first 500 chars):", response_text[:500])
                print("Response text (error area):", response_text[6800:6900] if len(response_text) > 6850 else "N/A")
                raise ValueError(f"Could not parse Ollama response as JSON after repair attempts: {str(e)}")

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
You must respond ONLY with valid JSON. No explanations, no text, no markdown.
Start your response with { and end with }.
Use double quotes for all strings and keys.
No trailing commas.
Respond only with the JSON object."""
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
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()

        # Try to repair common JSON issues
        def repair_json(text):
            """Repair common JSON formatting issues from Ollama responses"""
            import re

            # Fix missing commas after string values followed by newlines and quotes
            # Pattern: "value"\n  "next_key" -> "value",\n  "next_key"
            text = re.sub(r'"\s*\n\s*"', '",\n"', text)

            # Fix missing commas after string values followed by closing braces
            # Pattern: "value"\n  } -> "value"\n  },
            text = re.sub(r'"\s*\n\s*(\}|\])', '",\n\\1', text)

            # Fix missing commas after numbers followed by quotes
            # Pattern: 123\n  "key" -> 123,\n  "key"
            text = re.sub(r'(\d+)\s*\n\s*"', '\\1,\n"', text)

            # Fix missing commas after boolean/null values
            # Pattern: true\n  "key" -> true,\n  "key"
            text = re.sub(r'(true|false|null)\s*\n\s*"', '\\1,\n"', text)

            return text

        try:
            # First try direct parsing
            report_json = json.loads(response_text)
            return report_json
        except json.JSONDecodeError as e:
            print(f"Direct JSON parsing failed: {e}")
            print("Attempting to repair JSON...")

            try:
                # Try to repair and parse
                repaired_text = repair_json(response_text)
                report_json = json.loads(repaired_text)
                print("JSON repair successful!")
                return report_json
            except json.JSONDecodeError as repair_e:
                print(f"JSON repair also failed: {repair_e}")
                print("Response text (first 500 chars):", response_text[:500])
                raise ValueError(f"Could not parse Ollama response as JSON after repair attempts: {str(e)}")

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
You must respond ONLY with valid JSON. No explanations, no text, no markdown.
Start your response with { and end with }.
Use double quotes for all strings and keys.
No trailing commas.
Respond only with the JSON object."""
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
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()

        # Try to repair common JSON issues
        def repair_json(text):
            """Repair common JSON formatting issues from Ollama responses"""
            import re

            # Fix missing commas after string values followed by newlines and quotes
            # Pattern: "value"\n  "next_key" -> "value",\n  "next_key"
            text = re.sub(r'"\s*\n\s*"', '",\n"', text)

            # Fix missing commas after string values followed by closing braces
            # Pattern: "value"\n  } -> "value"\n  },
            text = re.sub(r'"\s*\n\s*(\}|\])', '",\n\\1', text)

            # Fix missing commas after numbers followed by quotes
            # Pattern: 123\n  "key" -> 123,\n  "key"
            text = re.sub(r'(\d+)\s*\n\s*"', '\\1,\n"', text)

            # Fix missing commas after boolean/null values
            # Pattern: true\n  "key" -> true,\n  "key"
            text = re.sub(r'(true|false|null)\s*\n\s*"', '\\1,\n"', text)

            return text

        try:
            # First try direct parsing
            report_json = json.loads(response_text)
            return report_json
        except json.JSONDecodeError as e:
            print(f"Direct JSON parsing failed: {e}")
            print("Attempting to repair JSON...")

            try:
                # Try to repair and parse
                repaired_text = repair_json(response_text)
                report_json = json.loads(repaired_text)
                print("JSON repair successful!")
                return report_json
            except json.JSONDecodeError as repair_e:
                print(f"JSON repair also failed: {repair_e}")
                print("Response text (first 500 chars):", response_text[:500])
                raise ValueError(f"Could not parse Ollama response as JSON after repair attempts: {str(e)}")

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
You must respond ONLY with valid JSON. No explanations, no text, no markdown.
Start your response with { and end with }.
Use double quotes for all strings and keys.
No trailing commas.
Respond only with the JSON object."""
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
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()

        # Try to repair common JSON issues
        def repair_json(text):
            """Repair common JSON formatting issues from Ollama responses"""
            import re

            # Fix missing commas after string values followed by newlines and quotes
            # Pattern: "value"\n  "next_key" -> "value",\n  "next_key"
            text = re.sub(r'"\s*\n\s*"', '",\n"', text)

            # Fix missing commas after string values followed by closing braces
            # Pattern: "value"\n  } -> "value"\n  },
            text = re.sub(r'"\s*\n\s*(\}|\])', '",\n\\1', text)

            # Fix missing commas after numbers followed by quotes
            # Pattern: 123\n  "key" -> 123,\n  "key"
            text = re.sub(r'(\d+)\s*\n\s*"', '\\1,\n"', text)

            # Fix missing commas after boolean/null values
            # Pattern: true\n  "key" -> true,\n  "key"
            text = re.sub(r'(true|false|null)\s*\n\s*"', '\\1,\n"', text)

            return text

        try:
            # First try direct parsing
            report_json = json.loads(response_text)
            return report_json
        except json.JSONDecodeError as e:
            print(f"Direct JSON parsing failed: {e}")
            print("Attempting to repair JSON...")

            try:
                # Try to repair and parse
                repaired_text = repair_json(response_text)
                report_json = json.loads(repaired_text)
                print("JSON repair successful!")
                return report_json
            except json.JSONDecodeError as repair_e:
                print(f"JSON repair also failed: {repair_e}")
                print("Response text (first 500 chars):", response_text[:500])
                raise ValueError(f"Could not parse Ollama response as JSON after repair attempts: {str(e)}")

    else:
        raise ValueError("No valid response received from Ollama")
