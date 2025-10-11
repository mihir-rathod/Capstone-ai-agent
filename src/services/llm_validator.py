from config import client
from src.models.validation_schema import ValidationResult
import json

def validate_report(structure: dict, report: dict) -> ValidationResult:
    """Validate the generated report against the structure"""
    prompt = f"""
    You are a JSON validator.
    Validate whether the following report matches the provided structure
    and is logically consistent.

    Structure:
    {json.dumps(structure, indent=2)}

    Report:
    {json.dumps(report, indent=2)}

    Respond ONLY in this JSON format:
    {{
      "is_valid": true or false,
      "message": "<brief reason>"
    }}
    """

    response = client.generate("gemini-2.5-flash",prompt)

    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            cleaned_response = response[json_start:json_end]
            result = json.loads(cleaned_response)
            return ValidationResult(**result)
        else:
            raise ValueError("No JSON object found in the response.")
    except Exception:
        return ValidationResult(is_valid=False, message="Invalid JSON response from Gemini validator")
