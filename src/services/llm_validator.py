from src.config.config import client
from src.models.validation_schema import ValidationResult
from src.config.prompts import validate_report_prompt
from typing import Dict, Any, List
import json

def validate_report(structure: dict, report: dict) -> ValidationResult:
    """Validate the generated report against the structure and data quality requirements"""
    # Get validation prompt from prompts.py
    prompt = validate_report_prompt(structure, report)

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
