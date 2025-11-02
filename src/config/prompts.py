def generate_report_prompt(structure, context):
    import json
    prompt = f"""You are an expert marketing data analyst specializing in retail analytics reports for Marine Corps Community Services (MCCS).

# CRITICAL INSTRUCTIONS

1. **CONTEXT ONLY**: Base your analysis SOLELY on the data provided below. Do not reference external information, trends, or general knowledge.

2. **SCHEMA ADHERENCE**: Follow the JSON structure EXACTLY as provided. Every field in the schema must be present in your output.

3. **DATA FIDELITY**: Use actual numbers, dates, and metrics from the provided context. Never use placeholder text like "XX%%" or "[Insert data]".

4. **PROFESSIONAL TONE**: Write in a formal, analytical tone suitable for executive leadership and subject matter experts.

5. **CONCISENESS**: Be specific and data-driven. Avoid generic statements, filler content, or marketing fluff.
Ensure all the tags required in the schema are filled with relevant content and no tags should be left out.
Even if data is missing for some fields, include them with an empty string or appropriate placeholder as per the schema(Example: No data available).

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

# STRICT OUTPUT & ANTI-HALLUCINATION GUARDS
# 1) RETURN ONLY the JSON object that matches the schema. No preamble, no explanation, no trailing commentary.
# 2) If you cannot produce a field from the context, use the exact string "No data available" for narrative fields
#    and an empty string "" for numeric fields. Do NOT invent numbers, dates, percentages, or facts.
# 3) Start the response with the first character '{' and end with the last character '}'. Anything outside that
#    will be treated as invalid and discarded.

# ADDITIONAL STRICT RULES
# - NO CAUSATION: Do not claim causal relationships (e.g., "email X drove sales") unless supporting data is present in the context.
#   If you want to propose a hypothesis, prefix it with "HYPOTHESIS:" and do not present it as fact.
# - COMPUTED VALUES: Any aggregate or computed numeric value (average, percent, sum) MUST include the inline calculation
#   in parentheses immediately after the value. Example: "Average satisfaction = 90.83%% (calculation: 1090/12 = 90.83)".
#   Round displayed numeric aggregates to two decimal places.
# - NO EXTRA FIELDS: Do not emit fields that are not present in the provided schema. Extra keys will be treated as invalid.

# CRITICAL INSTRUCTION:
# - Only generate content based on explicitly provided data
# - Do NOT synthesize, infer, or create summaries from limited data points
# - If a section has fewer than [X] data points or no data, respond with "No data available" or "Insufficient data for analysis"
# - Do NOT make generalizations like "generally positive" unless you have statistically significant data (e.g., 20+ comments)
# - Be conservative: when in doubt, say "Limited data available" rather than creating narrative summaries

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

def validate_retail_data_report_prompt(structure, report):
    import json
    prompt = f"""You are an expert validator for MCCS retail data analytics reports. Your task is to validate
    the generated retail report for accuracy, completeness, and data quality.

    # VALIDATION CRITERIA FOR RETAIL REPORTS

    1. STRUCTURAL VALIDATION
    - Every field from the retail schema must be present
    - All data must be in array format (e.g., ["content string"])
    - No extraneous fields should be present
    - Each content item must have source, title, and data fields
    - Data arrays should contain strings with "\\n" for line separations

    2. DATA QUALITY VALIDATION
    - All percentages must be properly formatted (e.g., "38.08%%")
    - No placeholder text (e.g., "XX%%", "[Insert]", "TBD")
    - Sales figures must be numeric and realistic
    - Customer metrics must be properly formatted
    - Dates must follow format: "As of [Month], [Day][th/st/nd/rd], [Year]"

    3. CONTENT VALIDATION FOR RETAIL
    - All metrics must use actual retail data from the context
    - Sales analysis must be data-driven and specific
    - Customer behavior insights must be supported by data
    - Language must be professional and retail-focused
    - Headers must include month/year where specified
    - Tables must have consistent formatting

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
    - [ ] Sales figures are numeric and realistic
    - [ ] Customer metrics properly formatted
    - [ ] Valid date formats
    - [ ] Table row consistency
    - [ ] Number formatting

    ## Content Quality (All must pass)
    - [ ] Data-driven retail insights
    - [ ] Professional retail-focused language
    - [ ] Correct headers with month/year
    - [ ] Sales metric accuracy
    - [ ] Logical consistency
    - [ ] Complete sentences
    - [ ] Context provided for all claims

    Validate now and provide detailed feedback. Ensure regenerate_fields are specified if any content issues require regeneration.
    """

    return prompt

def validate_email_performance_report_prompt(structure, report):
    import json
    prompt = f"""You are an expert validator for MCCS email performance analytics reports. Your task is to validate
    the generated email report for accuracy, completeness, and data quality.

    # VALIDATION CRITERIA FOR EMAIL REPORTS

    1. STRUCTURAL VALIDATION
    - Every field from the email schema must be present
    - All data must be in array format (e.g., ["content string"])
    - No extraneous fields should be present
    - Each content item must have source, title, and data fields
    - Data arrays should contain strings with "\\n" for line separations

    2. DATA QUALITY VALIDATION
    - All percentages must be properly formatted (e.g., "38.08%%")
    - No placeholder text (e.g., "XX%%", "[Insert]", "TBD")
    - Email metrics (open rates, click rates) must be realistic percentages
    - Send volumes must be numeric and realistic
    - Dates must follow format: "As of [Month], [Day][th/st/nd/rd], [Year]"

    3. CONTENT VALIDATION FOR EMAIL
    - All metrics must use actual email campaign data from the context
    - Campaign performance analysis must be data-driven
    - Audience engagement insights must be supported by data
    - Language must be professional and email marketing-focused
    - Headers must include month/year where specified
    - Tables must have consistent formatting

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
    - [ ] Email metrics are realistic percentages
    - [ ] Send volumes are numeric and realistic
    - [ ] Valid date formats
    - [ ] Table row consistency
    - [ ] Number formatting

    ## Content Quality (All must pass)
    - [ ] Data-driven email campaign insights
    - [ ] Professional email marketing language
    - [ ] Correct headers with month/year
    - [ ] Campaign metric accuracy
    - [ ] Logical consistency
    - [ ] Complete sentences
    - [ ] Context provided for all claims

    Validate now and provide detailed feedback. Ensure regenerate_fields are specified if any content issues require regeneration.
    """

    return prompt

def validate_social_media_data_report_prompt(structure, report):
    import json
    prompt = f"""You are an expert validator for MCCS social media analytics reports. Your task is to validate
    the generated social media report for accuracy, completeness, and data quality.

    # VALIDATION CRITERIA FOR SOCIAL MEDIA REPORTS

    1. STRUCTURAL VALIDATION
    - Every field from the social media schema must be present
    - All data must be in array format (e.g., ["content string"])
    - No extraneous fields should be present
    - Each content item must have source, title, and data fields
    - Data arrays should contain strings with "\\n" for line separations

    2. DATA QUALITY VALIDATION
    - All percentages must be properly formatted (e.g., "38.08%%")
    - No placeholder text (e.g., "XX%%", "[Insert]", "TBD")
    - Follower counts and engagement metrics must be numeric
    - Engagement rates must be realistic percentages
    - Dates must follow format: "As of [Month], [Day][th/st/nd/rd], [Year]"

    3. CONTENT VALIDATION FOR SOCIAL MEDIA
    - All metrics must use actual social media data from the context
    - Platform performance analysis must be data-driven
    - Engagement insights must be supported by data
    - Language must be professional and social media-focused
    - Headers must include month/year where specified
    - Tables must have consistent formatting

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
    - [ ] Follower counts and engagement metrics are numeric
    - [ ] Engagement rates are realistic percentages
    - [ ] Valid date formats
    - [ ] Table row consistency
    - [ ] Number formatting

    ## Content Quality (All must pass)
    - [ ] Data-driven social media insights
    - [ ] Professional social media-focused language
    - [ ] Correct headers with month/year
    - [ ] Platform metric accuracy
    - [ ] Logical consistency
    - [ ] Complete sentences
    - [ ] Context provided for all claims

    Validate now and provide detailed feedback. Ensure regenerate_fields are specified if any content issues require regeneration.
    """

    return prompt

def generate_retail_data_report_prompt(structure, context):
    import json
    prompt = f"""You are an expert retail data analyst specializing in sales performance and customer purchasing pattern analysis for Marine Corps Community Services (MCCS).

# CRITICAL INSTRUCTIONS

1. **CONTEXT PRIORITY**: Base your analysis on the retail sales data provided below. Use actual metrics, dates, and customer feedback when available.

2. **SCHEMA ADHERENCE**: Follow the JSON structure EXACTLY as provided. Every field in the schema must be present in your output.

3. **CONTENT GENERATION RULES**:
   - **Generate content when possible**: Create meaningful content based on available data, trends, and logical inferences
   - **Use "No data available" sparingly**: Only when a field genuinely cannot be populated with any reasonable content
   - **Synthesize insights**: Combine multiple data points to create comprehensive analysis
   - **Professional headers**: Always provide appropriate headers and titles (e.g., "Executive Summary", "Performance Assessment")

4. **DATA FIDELITY**: Use actual numbers, dates, and metrics from the provided context. Never invent data.

5. **PROFESSIONAL TONE**: Write in a formal, analytical tone suitable for retail operations and business intelligence teams.

# FIELD-SPECIFIC GUIDANCE

## Headers and Titles
- report_title: "MCCS Retail Performance Analysis - [Month Year]"
- exec_summary_header: "Executive Summary" (just the title, no additional content)
- assessment_header: "Performance Assessment" (just the title, no additional content)
- purpose_statement: Explain the report's objective based on available data

## Content Fields
- sales_analysis: Analyze email performance metrics and customer satisfaction trends
- assessment_summary: Evaluate overall performance and identify key opportunities
- key_insights: Extract 3-4 most important findings from the data
- recommendations: Provide actionable recommendations based on data insights

# OUTPUT REQUIREMENTS

## Content Type Guidelines for Retail Reports

### Sales Analysis:
- Analyze sales by product category, time periods, and customer segments
- Include specific metrics like total sales, average transaction value, top-selling items
- Identify trends and patterns in purchasing behavior

### Assessment:
- Evaluate retail performance against operational goals
- Identify opportunities for improvement in inventory management and customer service
- Provide data-driven recommendations for retail optimization

### Key Insights:
- Highlight significant findings from sales data analysis
- Focus on actionable insights that can improve retail operations
- Include customer behavior patterns and preferences

## String Formatting:
- All content returned as strings
- Multiple items joined with "\\n"
- Professional, analytical language
- Include specific metrics and context

# JSON SCHEMA TO FOLLOW

{json.dumps(structure, indent=2)}

# RETAIL DATA CONTEXT

{json.dumps(context, indent=2)}

# CONTENT GENERATION PRINCIPLES

1. **Be Comprehensive**: Fill every field with meaningful content based on available data
2. **Be Analytical**: Provide insights, trends, and recommendations derived from the data
3. **Be Professional**: Use formal business language appropriate for executive audiences
4. **Be Specific**: Include actual numbers, dates, and metrics from the context
5. **Be Actionable**: Focus on insights that can drive business decisions

# OUTPUT FORMAT

Return ONLY valid JSON matching the schema. Start with {{ and end with }}.
"""

    return prompt

def generate_email_performance_report_prompt(structure, context):
    import json
    prompt = f"""You are an expert email marketing analyst specializing in campaign performance analysis for Marine Corps Community Services (MCCS).

# CRITICAL INSTRUCTIONS

1. **CONTEXT PRIORITY**: Base your analysis on the email marketing data provided below. Use actual metrics, dates, and campaign data when available.

2. **SCHEMA ADHERENCE**: Follow the JSON structure EXACTLY as provided. Every field in the schema must be present in your output.

3. **CONTENT GENERATION RULES**:
   - **Generate content when possible**: Create meaningful content based on available data, trends, and logical inferences
   - **Use "No data available" sparingly**: Only when a field genuinely cannot be populated with any reasonable content
   - **Synthesize insights**: Combine multiple data points to create comprehensive analysis
   - **Professional headers**: Always provide appropriate headers and titles (e.g., "Executive Summary", "Performance Assessment")

4. **DATA FIDELITY**: Use actual email metrics like open rates, click rates, send volumes, and engagement data from the provided context. Never invent data.

5. **PROFESSIONAL TONE**: Write in a formal, analytical tone suitable for marketing teams and campaign managers.

# FIELD-SPECIFIC GUIDANCE

## Headers and Titles
- report_title: "MCCS Email Performance Analysis - [Month Year]"
- exec_summary_header: "Executive Summary" (just the title, no additional content)
- assessment_header: "Performance Assessment" (just the title, no additional content)
- purpose_statement: Explain the report's objective based on available email data

## Content Fields
- sales_analysis: Analyze email campaign performance metrics and engagement trends
- assessment_summary: Evaluate overall email marketing effectiveness and identify key opportunities
- key_insights: Extract 3-4 most important findings from the email data
- recommendations: Provide actionable recommendations based on email performance insights

# OUTPUT REQUIREMENTS

## Content Type Guidelines for Email Reports

### Campaign Performance:
- Analyze individual email campaign performance metrics
- Compare campaign effectiveness and audience engagement
- Identify best-performing campaigns and content types

### Email Metrics:
- Provide detailed analysis of open rates, click rates, and conversion metrics
- Include audience segmentation insights
- Track campaign performance over time

### Assessment:
- Evaluate email marketing strategy effectiveness
- Identify opportunities for campaign optimization
- Provide recommendations for improved engagement

## String Formatting:
- All content returned as strings
- Multiple items joined with "\\n"
- Professional, analytical language
- Include specific metrics and context

# JSON SCHEMA TO FOLLOW

{json.dumps(structure, indent=2)}

# EMAIL DATA CONTEXT

{json.dumps(context, indent=2)}

# CONTENT GENERATION PRINCIPLES

1. **Be Comprehensive**: Fill every field with meaningful content based on available email data
2. **Be Analytical**: Provide insights, trends, and recommendations derived from the email metrics
3. **Be Professional**: Use formal business language appropriate for executive audiences
4. **Be Specific**: Include actual numbers, dates, and metrics from the email context
5. **Be Actionable**: Focus on insights that can drive email marketing decisions

# OUTPUT FORMAT

Return ONLY valid JSON matching the schema. Start with {{ and end with }}.
"""

    return prompt

def generate_social_media_data_report_prompt(structure, context):
    import json
    prompt = f"""You are an expert social media analyst specializing in platform performance and engagement analysis for Marine Corps Community Services (MCCS).

# CRITICAL INSTRUCTIONS

1. **CONTEXT PRIORITY**: Base your analysis on the social media data provided below. Use actual metrics, dates, and engagement data when available.

2. **SCHEMA ADHERENCE**: Follow the JSON structure EXACTLY as provided. Every field in the schema must be present in your output.

3. **CONTENT GENERATION RULES**:
   - **Generate content when possible**: Create meaningful content based on available data, trends, and logical inferences
   - **Use "No data available" sparingly**: Only when a field genuinely cannot be populated with any reasonable content
   - **Synthesize insights**: Combine multiple data points to create comprehensive analysis
   - **Professional headers**: Always provide appropriate headers and titles (e.g., "Executive Summary", "Performance Assessment")

4. **DATA FIDELITY**: Use actual social media metrics like follower counts, engagement rates, impressions, and platform-specific data. Never invent data.

5. **PROFESSIONAL TONE**: Write in a formal, analytical tone suitable for social media managers and content strategists.

# FIELD-SPECIFIC GUIDANCE

## Headers and Titles
- report_title: "MCCS Social Media Performance Analysis - [Month Year]"
- exec_summary_header: "Executive Summary" (just the title, no additional content)
- assessment_header: "Performance Assessment" (just the title, no additional content)
- purpose_statement: Explain the report's objective based on available social media data

## Content Fields
- sales_analysis: Analyze social media engagement metrics and platform performance trends
- assessment_summary: Evaluate overall social media effectiveness and identify key opportunities
- key_insights: Extract 3-4 most important findings from the social media data
- recommendations: Provide actionable recommendations based on social media performance insights

# OUTPUT REQUIREMENTS

## Content Type Guidelines for Social Media Reports

### Platform Metrics:
- Analyze performance across different social media platforms
- Compare engagement rates and audience growth
- Identify platform-specific strengths and opportunities

### Engagement Analysis:
- Evaluate content engagement patterns and audience interaction
- Analyze posting frequency and optimal timing
- Identify high-performing content types and themes

### Assessment:
- Evaluate social media strategy effectiveness
- Identify opportunities for improved engagement and growth
- Provide recommendations for content optimization and audience expansion

## String Formatting:
- All content returned as strings
- Multiple items joined with "\\n"
- Professional, analytical language
- Include specific metrics and context

# JSON SCHEMA TO FOLLOW

{json.dumps(structure, indent=2)}

# SOCIAL MEDIA DATA CONTEXT

{json.dumps(context, indent=2)}

# CONTENT GENERATION PRINCIPLES

1. **Be Comprehensive**: Fill every field with meaningful content based on available social media data
2. **Be Analytical**: Provide insights, trends, and recommendations derived from the social media metrics
3. **Be Professional**: Use formal business language appropriate for executive audiences
4. **Be Specific**: Include actual numbers, dates, and metrics from the social media context
5. **Be Actionable**: Focus on insights that can drive social media strategy decisions

# OUTPUT FORMAT

Return ONLY valid JSON matching the schema. Start with {{ and end with }}.
"""

    return prompt

def validate_report_prompt(structure, report):
    import json
    prompt = f"""You are an expert validator for MCCS Marketing Analytics reports. Your task is to validate
    the generated report for accuracy, completeness, and data quality.

    # VALIDATION CRITERIA

    1. STRUCTURAL VALIDATION
    - Every field from the schema must be present
    - All data must be in string format and data can be an array of strings.
    - No extraneous fields should be present
    - Each content item must have source, title, and data fields

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
