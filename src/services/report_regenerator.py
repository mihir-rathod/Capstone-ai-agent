from typing import Dict, Any, Optional
from src.models.validation_schema import DetailedValidationResult, ValidationResult
import json

class ReportRegenerator:
    def __init__(self, structure: dict, context: dict, original_report: dict):
        self.structure = structure
        self.context = context
        self.original_report = original_report
        
    def create_regeneration_prompt(self, validation_result: DetailedValidationResult, previous_attempts: list = None) -> str:
        """
        Create a prompt for regenerating specific parts of the report, incorporating feedback from previous attempts
        """
        fields_to_fix = validation_result.regenerate_fields
        issues_by_field = self._get_issues_by_field(validation_result)
        
        # Build history of previous attempts if available
        previous_attempts_summary = self._format_previous_attempts(previous_attempts) if previous_attempts else ""
        
        prompt = f"""You are tasked with regenerating specific parts of an MCCS Marketing Analytics report 
        that were found to be inaccurate or invalid. This is attempt {len(previous_attempts) + 1 if previous_attempts else 1} 
        out of 3 maximum attempts. Focus ONLY on fixing the identified issues while maintaining the accuracy 
        of the rest of the report.

        {previous_attempts_summary}

        # ORIGINAL REPORT
        {json.dumps(self.original_report, indent=2)}

        # FIELDS TO REGENERATE
        The following fields need to be fixed:
        {self._format_fields_with_issues(fields_to_fix, issues_by_field)}

        # REQUIRED STRUCTURE
        {json.dumps(self.structure, indent=2)}

        # CONTEXT DATA
        {json.dumps(self.context, indent=2)}

        # INSTRUCTIONS

        1. Regenerate ONLY the specified fields
        2. Ensure the new content fixes the identified issues
        3. Maintain consistency with the rest of the report
        4. Follow all formatting and data quality requirements
        5. Use the exact same structure as the original report
        6. Ensure all numbers and metrics are accurate
        7. Preserve any correct insights from the original report

        Return the complete report with the regenerated sections in valid JSON format.
        Keep all other sections exactly as they were in the original report.
        """
        
        return prompt
        
    def _get_issues_by_field(self, validation_result: DetailedValidationResult) -> Dict[str, list]:
        """
        Organize validation issues by field
        """
        issues_by_field = {}
        
        # Get issues from all validation sections
        for section in [validation_result.validation_results.structure,
                       validation_result.validation_results.data_quality,
                       validation_result.validation_results.content]:
            for issue in section.issues:
                if issue.field not in issues_by_field:
                    issues_by_field[issue.field] = []
                issues_by_field[issue.field].append({
                    "issue": issue.issue,
                    "fix": issue.fix
                })
                
        return issues_by_field
        
    def _format_fields_with_issues(self, fields: list, issues_by_field: Dict[str, list]) -> str:
        """
        Format fields and their issues for the prompt
        """
        formatted = []
        for field in fields:
            field_issues = issues_by_field.get(field, [])
            issues_text = "\n".join([f"    - Issue: {i['issue']}\n      Fix: {i['fix']}" 
                                   for i in field_issues])
            formatted.append(f"""
            Field: {field}
            Current Value: {json.dumps(self.original_report.get(field, ""), indent=2)}
            Issues:
            {issues_text}
            """)
            
        return "\n".join(formatted)
        
    def _format_previous_attempts(self, previous_attempts: list) -> str:
        """
        Format history of previous regeneration attempts
        """
        if not previous_attempts:
            return ""
            
        history = ["# PREVIOUS REGENERATION ATTEMPTS\n"]
        
        for attempt in previous_attempts:
            history.append(f"""
            Attempt {attempt['attempt']}:
            Fields Attempted: {', '.join(attempt['fields_regenerated'])}
            Issues Found:
            """)
            
            # Add issues from each validation section
            for section, details in attempt['issues'].items():
                if details['issues']:
                    history.append(f"  {section.title()} Issues:")
                    for issue in details['issues']:
                        history.append(f"    - Field: {issue['field']}")
                        history.append(f"      Problem: {issue['issue']}")
                        
            history.append("\n")  # Add spacing between attempts
            
        history.append("""
        IMPORTANT: Review the previous attempt history above to avoid repeating the same issues.
        Focus on generating content that addresses all previous validation failures.
        """)
        
        return "\n".join(history)