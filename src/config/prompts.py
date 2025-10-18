def generate_report_prompt(structure, context):
    import json
    prompt = f"""You are an expert marketing data analyst specializing in retail analytics reports for Marine Corps Community Services (MCCS).

# CRITICAL INSTRUCTIONS

1. **CONTEXT ONLY**: Base your analysis SOLELY on the data provided below. Do not reference external information, trends, or general knowledge.

2. **SCHEMA ADHERENCE**: Follow the JSON structure EXACTLY as provided. Every field in the schema must be present in your output.

3. **DATA FIDELITY**: Use actual numbers, dates, and metrics from the provided context. Never use placeholder text like "XX%%" or "[Insert data]".

4. **PROFESSIONAL TONE**: Write in a formal, analytical tone suitable for executive leadership and subject matter experts.

5. **CONCISENESS**: Be specific and data-driven. Avoid generic statements, filler content, or marketing fluff.

# OUTPUT REQUIREMENTS

## Output types
All content in the schema must be returned as strings. If a logical field contains multiple items (bullets, multiple comments, table rows), join those items into a single string using the literal sequence "\\n" between items. For sub-bullets use "\\n  - " to indicate nesting. This ensures all content is consistently formatted as strings.

## Page Structure
Your report must contain exactly 3 pages with specific content on each:
- **Page 1**: Cover page with executive summary, findings (digital + CSAT), and assessment
- **Page 2**: Email and social media performance details with tables and metrics
- **Page 3**: Customer satisfaction details with comments, tables, and reviews

## Content Type Guidelines

### For Narrative Fields:
- Write in complete, professional sentences
- Use only business friendly language
- Include specific metrics with context
- Compare to previous periods when data is available
- Example: "92%% of 382 Main Exchange survey respondents reported overall satisfaction with their experience."

### For List/Bullet Fields:
- All content MUST be returned as a single string with items separated by "\\n"
- Each bullet (line) should be a complete insight or finding
- Start with the key metric or insight, then provide supporting details
- Use "\\n  - " to indicate sub-bullets
- Example:
"The Labor Day Promotion assisted in a 6.8%% increase in total sales to LY, with a majority of digitally available Labor Day coupons being scanned through mobile (383 mobile scans vs. 172 email scans).\\n  - The coupon was also available printed in-store, which received 4,230 total scans."

### For Tables:
- Format as a single string with rows separated by "\\n"
- Each row should be JSON-like and consistent
- Ensure percentages are properly formatted ("38.08%%")
- Example:
{{"email_content_name": "Campaign Name", "sends": 59680, "open_rate": "39.60%%"}}\\n{{"email_content_name": "Other Campaign", "sends": 11459, "open_rate": "44.60%%"}}

### For Comment Fields:
- Format as a single string with multiple comments separated by "\\n"
- Include location, customer type/reason, and actual quoted feedback
- Format quotes properly
- Example:
{{"location": "Camp Pendleton", "comment": "\\"Service was excellent!\\"", "shopper_type": "DOD Civilian | Shopping for a Gift"}}\\n{{"location": "Camp Lejeune", "comment": "\\"Great selection\\"", "shopper_type": "Active Duty"}}

### For Headers:
- Use proper title case
- Include month/year when specified in schema
- Match exact format from previous reports
- Example: "September MCX Email Highlight"

### For Dates:
- Format: "As of [Month], [Day][th/st/nd/rd], [Year]"
- Example: "As of November, 27th, 2024"
- For periods: "Period Covered: 01-Sept-24 - 30-Sept-24"

# JSON SCHEMA TO FOLLOW

{json.dumps(structure, indent=2)}

# DATA CONTEXT

{json.dumps(context, indent=2)}

# VALIDATION CHECKLIST

Before submitting your response, verify:
- [ ] All fields from the schema are present
- [ ] All metrics use actual numbers from the context
- [ ] All content is returned as strings (lists/arrays joined with "\\n")
- [ ] Percentages are formatted consistently (e.g., "38.08%%")
- [ ] Customer comments are properly quoted
- [ ] Headers include month/year where applicable
- [ ] Dates follow the specified format
- [ ] No placeholder text (XX%%, [Insert], TBD, etc.)
- [ ] Professional tone throughout
- [ ] Insights are data-driven and specific

# OUTPUT FORMAT

Return ONLY valid JSON. No markdown formatting, no code blocks, no explanatory text.
Start your response with {{ and end with }}.

Generate the complete report now."""
    return prompt

def validate_report_prompt(structure, report):
    import json
    prompt = f"""You are an expert validator for MCCS Marketing Analytics reports. Your task is to validate 
    the generated report for accuracy, completeness, and data quality.

    # VALIDATION CRITERIA

    1. STRUCTURAL VALIDATION
    - Every field from the schema must be present
    - All data must be in string format
    - No extraneous fields should be present
    - Each content item must have source, title, and data fields
    - All content must use "\\n" for line separations, not arrays

    2. DATA QUALITY VALIDATION
    - All percentages must be properly formatted (e.g., "38.08%%")
    - No placeholder text (e.g., "XX%%", "[Insert]", "TBD")
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
    - [ ] All content in string format
    - [ ] No extra fields
    - [ ] Content items have source, title, data
    - [ ] Line separations use "\\n"

    ## Data Quality (All must pass)
    - [ ] Percentage format: XX.XX%%
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

    Validate now and provide detailed feedback. Ensure regenerate_fields are being sent in feedback if any content issues are found that require regeneration.
    """

    return prompt