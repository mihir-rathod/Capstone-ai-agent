from src.config.config import client
from src.models.validation_schema import ValidationResult
from typing import Dict, Any, List
import json

def validate_report(structure: dict, report: dict) -> ValidationResult:
    """Validate the generated report against the structure and data quality requirements"""
    prompt = f"""You are an expert validator for MCCS Marketing Analytics reports. Your task is to validate 
    the generated report for accuracy, completeness, and data quality.

    # VALIDATION CRITERIA

    1. STRUCTURAL VALIDATION
    - Every field from the schema must be present
    - All data types must match schema requirements
    - No extraneous fields should be present

    2. DATA QUALITY VALIDATION
    - All percentages must be properly formatted (e.g., "38.08%")
    - No placeholder text (e.g., "XX%", "[Insert]", "TBD")
    - Tables must have consistent column names
    - Customer comments must be properly quoted
    - Dates must follow format: "As of [Month], [Day][th/st/nd/rd], [Year]"

    3. CONTENT VALIDATION
    - All metrics must use actual numbers from the data
    - Insights must be specific and data-driven
    - Language must be professional and formal
    - Headers must include month/year where specified
    - Tables must have consistent formatting

    If some of the fields are empty, ignore them for validation purposes.
    # REPORT TO VALIDATE

    Structure Schema:
    {json.dumps(structure, indent=2)}

    Generated Report:
    {json.dumps(report, indent=2)}

    # VALIDATION PROCESS

    1. Check each section against the checklist below
    2. For any failures, provide specific details about what is wrong
    3. For structural issues, indicate exactly which fields are problematic
    4. For data quality issues, provide examples of the incorrect values
    5. Suggest specific fixes for each issue found

    Respond with a JSON object in this format:
    {{
        "is_valid": boolean,
        "validation_results": {{
            "structure": {{
                "passed": boolean,
                "issues": [{{
                    "field": "field_name",
                    "issue": "description",
                    "fix": "suggested_fix"
                }}]
            }},
            "data_quality": {{
                "passed": boolean,
                "issues": [{{
                    "field": "field_name",
                    "issue": "description",
                    "fix": "suggested_fix"
                }}]
            }},
            "content": {{
                "passed": boolean,
                "issues": [{{
                    "field": "field_name",
                    "issue": "description",
                    "fix": "suggested_fix"
                }}]
            }}
        }},
        "summary": "Brief overall assessment",
        "regeneration_required": boolean,
        "regenerate_fields": ["field1", "field2"]  // Only fields needing regeneration
    }}

    # DETAILED CHECKLIST

    ## Structure (All must pass)
    - [ ] All required fields present
    - [ ] Correct data types used
    - [ ] No extra fields
    - [ ] Lists have minimum items
    - [ ] Nested structures complete

    ## Data Quality (All must pass)
    - [ ] Percentage format: XX.XX%
    - [ ] No placeholder text
    - [ ] Consistent table columns
    - [ ] Proper quote formatting
    - [ ] Valid date formats
    - [ ] Table row consistency
    - [ ] Number formatting

    ## Content Quality (All must pass)
    - [ ] Data-driven insights
    - [ ] Professional language
    - [ ] Correct headers
    - [ ] Metric accuracy
    - [ ] Logical consistency
    - [ ] Complete sentences
    - [ ] Context provided

    Validate now and provide detailed feedback.
    """

    try:
        response = client.generate("gemini-2.5-flash", prompt)
        
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            cleaned_response = response[json_start:json_end]
            validation_result = json.loads(cleaned_response)
            
            # Convert to simple ValidationResult for API response
            is_valid = validation_result.get('is_valid', False)
            
            # If invalid, construct detailed message with source context
            if not is_valid:
                message_parts = []
                # Add source context if available
                if 'source' in validation_result:
                    message_parts.append(f"Source: {validation_result['source']}")
                
                # Add structural issues
                struct_issues = validation_result.get('validation_results', {}).get('structure', {}).get('issues', [])
                for issue in struct_issues:
                    message_parts.append(f"Structure ({issue['field']}): {issue['issue']}")
                
                # Add data quality issues
                quality_issues = validation_result.get('validation_results', {}).get('data_quality', {}).get('issues', [])
                for issue in quality_issues:
                    message_parts.append(f"Quality ({issue['field']}): {issue['issue']}")
                
                # Add content issues
                content_issues = validation_result.get('validation_results', {}).get('content', {}).get('issues', [])
                for issue in content_issues:
                    message_parts.append(f"Content ({issue['field']}): {issue['issue']}")
                
                # Add regeneration guidance
                if validation_result.get('regeneration_required', False):
                    fields = validation_result.get('regenerate_fields', [])
                    message_parts.append(f"Please regenerate the following fields: {', '.join(fields)}")
                
                message = " | ".join(message_parts)
            else:
                message = validation_result.get('summary', "Report validation passed")
            
            return ValidationResult(is_valid=is_valid, message=message)
            
        else:
            return ValidationResult(
                is_valid=False,
                message="No valid JSON found in validation response"
            )
            
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            message=f"Validation error: {str(e)}"
        )
