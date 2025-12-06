from src.config.config import client
from src.models.validation_schema import ValidationResult, DetailedValidationResult, ValidationResults, ValidationSection, ValidationIssue
from src.config.prompts import (
    validate_report_prompt,
    validate_retail_data_report_prompt,
    validate_email_performance_report_prompt,
    validate_social_media_data_report_prompt
)
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

def validate_retail_data_report(structure: dict, report: dict) -> ValidationResult:
    """Validate the generated retail data report"""
    prompt = validate_retail_data_report_prompt(structure, report)

    try:
        response = client.generate("gemini-2.5-flash", prompt)

        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            cleaned_response = response[json_start:json_end]
            validation_result = json.loads(cleaned_response)

            is_valid = validation_result.get('is_valid', False)

            # Create detailed validation result
            detailed_result = None
            if not is_valid:
                # Parse validation results into proper schema objects
                validation_results_data = validation_result.get('validation_results', {})

                # Create ValidationSection objects
                structure_section = ValidationSection(
                    passed=validation_results_data.get('structure', {}).get('passed', False),
                    issues=[
                        ValidationIssue(field=issue['field'], issue=issue['issue'], fix=issue['fix'])
                        for issue in validation_results_data.get('structure', {}).get('issues', [])
                    ]
                )

                data_quality_section = ValidationSection(
                    passed=validation_results_data.get('data_quality', {}).get('passed', False),
                    issues=[
                        ValidationIssue(field=issue['field'], issue=issue['issue'], fix=issue['fix'])
                        for issue in validation_results_data.get('data_quality', {}).get('issues', [])
                    ]
                )

                content_section = ValidationSection(
                    passed=validation_results_data.get('content', {}).get('passed', False),
                    issues=[
                        ValidationIssue(field=issue['field'], issue=issue['issue'], fix=issue['fix'])
                        for issue in validation_results_data.get('content', {}).get('issues', [])
                    ]
                )

                validation_results_obj = ValidationResults(
                    structure=structure_section,
                    data_quality=data_quality_section,
                    content=content_section
                )

                detailed_result = DetailedValidationResult(
                    is_valid=is_valid,
                    validation_results=validation_results_obj,
                    summary=validation_result.get('summary', "Validation completed"),
                    regeneration_required=validation_result.get('regeneration_required', False),
                    regenerate_fields=validation_result.get('regenerate_fields', [])
                )

                # Create message for backward compatibility
                message_parts = []
                if 'source' in validation_result:
                    message_parts.append(f"Source: {validation_result['source']}")

                for issue in structure_section.issues:
                    message_parts.append(f"Structure ({issue.field}): {issue.issue}")

                for issue in data_quality_section.issues:
                    message_parts.append(f"Quality ({issue.field}): {issue.issue}")

                for issue in content_section.issues:
                    message_parts.append(f"Content ({issue.field}): {issue.issue}")

                if detailed_result.regeneration_required:
                    message_parts.append(f"Please regenerate the following fields: {', '.join(detailed_result.regenerate_fields)}")

                message = " | ".join(message_parts)
            else:
                message = validation_result.get('summary', "Retail report validation passed")

            return ValidationResult(
                is_valid=is_valid,
                message=message,
                detailed_results=detailed_result
            )

        else:
            return ValidationResult(
                is_valid=False,
                message="No valid JSON found in retail validation response"
            )

    except Exception as e:
        return ValidationResult(
            is_valid=False,
            message=f"Retail validation error: {str(e)}"
        )

def validate_email_performance_report(structure: dict, report: dict) -> ValidationResult:
    """Validate the generated email performance report"""
    prompt = validate_email_performance_report_prompt(structure, report)

    try:
        response = client.generate("gemini-2.5-flash", prompt)

        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            cleaned_response = response[json_start:json_end]
            validation_result = json.loads(cleaned_response)

            is_valid = validation_result.get('is_valid', False)

            # Create detailed validation result
            detailed_result = None
            if not is_valid:
                # Parse validation results into proper schema objects
                validation_results_data = validation_result.get('validation_results', {})

                # Create ValidationSection objects
                structure_section = ValidationSection(
                    passed=validation_results_data.get('structure', {}).get('passed', False),
                    issues=[
                        ValidationIssue(field=issue['field'], issue=issue['issue'], fix=issue['fix'])
                        for issue in validation_results_data.get('structure', {}).get('issues', [])
                    ]
                )

                data_quality_section = ValidationSection(
                    passed=validation_results_data.get('data_quality', {}).get('passed', False),
                    issues=[
                        ValidationIssue(field=issue['field'], issue=issue['issue'], fix=issue['fix'])
                        for issue in validation_results_data.get('data_quality', {}).get('issues', [])
                    ]
                )

                content_section = ValidationSection(
                    passed=validation_results_data.get('content', {}).get('passed', False),
                    issues=[
                        ValidationIssue(field=issue['field'], issue=issue['issue'], fix=issue['fix'])
                        for issue in validation_results_data.get('content', {}).get('issues', [])
                    ]
                )

                validation_results_obj = ValidationResults(
                    structure=structure_section,
                    data_quality=data_quality_section,
                    content=content_section
                )

                detailed_result = DetailedValidationResult(
                    is_valid=is_valid,
                    validation_results=validation_results_obj,
                    summary=validation_result.get('summary', "Validation completed"),
                    regeneration_required=validation_result.get('regeneration_required', False),
                    regenerate_fields=validation_result.get('regenerate_fields', [])
                )

                # Create message for backward compatibility
                message_parts = []
                if 'source' in validation_result:
                    message_parts.append(f"Source: {validation_result['source']}")

                for issue in structure_section.issues:
                    message_parts.append(f"Structure ({issue.field}): {issue.issue}")

                for issue in data_quality_section.issues:
                    message_parts.append(f"Quality ({issue.field}): {issue.issue}")

                for issue in content_section.issues:
                    message_parts.append(f"Content ({issue.field}): {issue.issue}")

                if detailed_result.regeneration_required:
                    message_parts.append(f"Please regenerate the following fields: {', '.join(detailed_result.regenerate_fields)}")

                message = " | ".join(message_parts)
            else:
                message = validation_result.get('summary', "Email performance report validation passed")

            return ValidationResult(
                is_valid=is_valid,
                message=message,
                detailed_results=detailed_result
            )

        else:
            return ValidationResult(
                is_valid=False,
                message="No valid JSON found in email validation response"
            )

    except Exception as e:
        return ValidationResult(
            is_valid=False,
            message=f"Email validation error: {str(e)}"
        )

def validate_social_media_data_report(structure: dict, report: dict) -> ValidationResult:
    """Validate the generated social media data report"""
    prompt = validate_social_media_data_report_prompt(structure, report)

    try:
        response = client.generate("gemini-2.5-flash", prompt)

        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            cleaned_response = response[json_start:json_end]
            validation_result = json.loads(cleaned_response)

            is_valid = validation_result.get('is_valid', False)

            # Create detailed validation result
            detailed_result = None
            if not is_valid:
                # Parse validation results into proper schema objects
                validation_results_data = validation_result.get('validation_results', {})

                # Create ValidationSection objects
                structure_section = ValidationSection(
                    passed=validation_results_data.get('structure', {}).get('passed', False),
                    issues=[
                        ValidationIssue(field=issue['field'], issue=issue['issue'], fix=issue['fix'])
                        for issue in validation_results_data.get('structure', {}).get('issues', [])
                    ]
                )

                data_quality_section = ValidationSection(
                    passed=validation_results_data.get('data_quality', {}).get('passed', False),
                    issues=[
                        ValidationIssue(field=issue['field'], issue=issue['issue'], fix=issue['fix'])
                        for issue in validation_results_data.get('data_quality', {}).get('issues', [])
                    ]
                )

                content_section = ValidationSection(
                    passed=validation_results_data.get('content', {}).get('passed', False),
                    issues=[
                        ValidationIssue(field=issue['field'], issue=issue['issue'], fix=issue['fix'])
                        for issue in validation_results_data.get('content', {}).get('issues', [])
                    ]
                )

                validation_results_obj = ValidationResults(
                    structure=structure_section,
                    data_quality=data_quality_section,
                    content=content_section
                )

                detailed_result = DetailedValidationResult(
                    is_valid=is_valid,
                    validation_results=validation_results_obj,
                    summary=validation_result.get('summary', "Validation completed"),
                    regeneration_required=validation_result.get('regeneration_required', False),
                    regenerate_fields=validation_result.get('regenerate_fields', [])
                )

                # Create message for backward compatibility
                message_parts = []
                if 'source' in validation_result:
                    message_parts.append(f"Source: {validation_result['source']}")

                for issue in structure_section.issues:
                    message_parts.append(f"Structure ({issue.field}): {issue.issue}")

                for issue in data_quality_section.issues:
                    message_parts.append(f"Quality ({issue.field}): {issue.issue}")

                for issue in content_section.issues:
                    message_parts.append(f"Content ({issue.field}): {issue.issue}")

                if detailed_result.regeneration_required:
                    message_parts.append(f"Please regenerate the following fields: {', '.join(detailed_result.regenerate_fields)}")

                message = " | ".join(message_parts)
            else:
                message = validation_result.get('summary', "Social media report validation passed")

            return ValidationResult(
                is_valid=is_valid,
                message=message,
                detailed_results=detailed_result
            )

        else:
            return ValidationResult(
                is_valid=False,
                message="No valid JSON found in social media validation response"
            )

    except Exception as e:
        return ValidationResult(
            is_valid=False,
            message=f"Social media validation error: {str(e)}"
        )
