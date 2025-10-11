from config import client
import json

def generate_report(structure: dict, context: dict):
#     """Generate structured report using Gemini"""
#     prompt = f"""
#     Instructions:
#     Forget all previous instructions. You are an expert data analyst.
#         Your only context is the data provided below. Do not reference any other information.
#         Study the data carefully and provide insights based solely on it.
#         Stick strictly to the schema provided.
#         The executive summary should be concise and focus on key insights or highlights from the analysis only.
#         Make sure all points are concise, focused, accurate and relevant. Do not include filler or generic statements.
#         Analyze the following marketing data and generate a report following the provided schema.

#     Follow this JSON structure exactly:
#     {json.dumps(structure, indent=2)}

#     Use the following context to fill in the details:
#     {json.dumps(context, indent=2)}

#     Output the report strictly in valid JSON format following the above structure.
#     """
    prompt = f"""You are an expert marketing data analyst specializing in retail analytics reports for Marine Corps Community Services (MCCS).

# CRITICAL INSTRUCTIONS

1. **CONTEXT ONLY**: Base your analysis SOLELY on the data provided below. Do not reference external information, trends, or general knowledge.

2. **SCHEMA ADHERENCE**: Follow the JSON structure EXACTLY as provided. Every field in the schema must be present in your output.

3. **DATA FIDELITY**: Use actual numbers, dates, and metrics from the provided context. Never use placeholder text like "XX%" or "[Insert data]".

4. **PROFESSIONAL TONE**: Write in a formal, analytical tone suitable for executive leadership and subject matter experts.

5. **CONCISENESS**: Be specific and data-driven. Avoid generic statements, filler content, or marketing fluff.

# OUTPUT REQUIREMENTS

## Page Structure
Your report must contain exactly 3 pages with specific content on each:
- **Page 1**: Cover page with executive summary, findings (digital + CSAT), and assessment
- **Page 2**: Email and social media performance details with tables and metrics
- **Page 3**: Customer satisfaction details with comments, tables, and reviews

## Content Type Guidelines

### For Narrative Fields (strings):
- Write in complete, professional sentences
- Include specific metrics with context
- Compare to previous periods when data is available
- Example: "92% of 382 Main Exchange survey respondents reported overall satisfaction with their experience."

### For List/Bullet Fields (arrays):
- Each bullet should be a complete insight or finding
- Start with the key metric or insight, then provide supporting details
- Use proper formatting with indentation for sub-bullets (use "\\n  - " for sub-points)
- Example:
  ```
  "The Labor Day Promotion assisted in a 6.8% increase in total sales to LY, with a majority of digitally available Labor Day coupons being scanned through mobile (383 mobile scans vs. 172 email scans).\\n  - The coupon was also available printed in-store, which received 4,230 total scans."
  ```

### For Tables (arrays of objects):
- Each row must have consistent keys across all objects
- Use proper percentage formatting: "38.08%" not "38.08" or "0.38"
- Include all columns: location, metrics, comparisons, changes
- Example structure:
  ```json
  [
    {{
      "email_content_name": "Campaign Name",
      "email_subject": "Subject Line",
      "sends": 59680,
      "open_rate": "39.60%",
      "click_rate": "1.24%",
      "click_to_open_rate": "3.14%",
      "unique_unsubscribes": 8,
      "unsubscribe_rate": "0.02%"
    }}
  ]
  ```

### For Comment Fields (arrays of objects):
- Include location, customer type/reason, and actual quoted feedback
- Format quotes properly with opening and closing quotation marks
- Preserve original customer voice and language
- Example:
  ```json
  {{
    "location": "Camp Pendleton",
    "shopper_type": "DOD Civilian | Shopping for a Gift",
    "comment": "\\"I noticed there was 'glam event' when I entered the store...\\""
  }}
  ```

### For Headers:
- Use proper title case
- Include month/year when specified in schema
- Match the exact format from previous reports
- Examples:
  - "September MCX Email Highlight"
  - "Findings – Review of digital performance, advertising campaigns, and sales:"
  - "September 2024 Email Campaigns Performance (as of October 23rd, 2024)"

### For Dates:
- Format: "As of [Month], [Day][th/st/nd/rd], [Year]"
- Example: "As of November, 27th, 2024"
- For periods: "Period Covered: 01-Sept-24 - 30-Sept-24"

# CONCRETE EXAMPLES FROM ACTUAL REPORTS

## Example 1: Executive Summary Bullet (with sub-bullet)
```
"The Labor Day Promotion assisted in a 6.8% increase in total sales to LY, with a majority of digitally available Labor Day coupons being scanned through mobile (383 mobile scans vs. 172 email scans).\\n  - The coupon was also available printed in-store, which received 4,230 total scans."
```

**Why this works:**
- Starts with the key finding (6.8% increase)
- Provides specific attribution (Labor Day Promotion)
- Includes detailed metrics (383 vs 172 scans)
- Uses sub-bullet for additional context
- Compares channels (mobile vs email vs in-store)

## Example 2: Industry Benchmarks (list format)
```json
[
  "The industry standard open rate (OPR) for emails in retail is 15-25% - MCX average for September was 38.08% (32.61% in August, 30.10% in July)",
  "The industry standard click through rate (CTR) is 1-5% - MCX average for September was 0.65% (0.45% in August, 0.53% in July)"
]
```

**Why this works:**
- States industry benchmark first
- Provides current month performance
- Shows historical trend (3 months)
- Demonstrates performance relative to benchmark

## Example 3: Campaign Details (nested structure)
```json
{{
  "title": "Labor Day (3 Emails w/ Coupons) (28-Aug – 02-Sept TY; 23-Aug – 5-Sept LY):",
  "details": [
    "Average OPR: 34.0% | Average CTR: 0.56% | Coupon Scans – Email: 172, Mobile: 383, In-Store Print: 4,230",
    "Total Sales: $12.6M TY; $11.8M LY | Average Daily Sales 2024: $2.52M; Average Daily Sales 2023: $60K",
    "2024 Promotion through email with coupons. 2022 and 2023 promotion through print and coupons"
  ]
}}
```

**Why this works:**
- Title includes campaign name, date range, and year comparison
- Each detail line focuses on specific metric category
- Uses consistent formatting (pipe separators, semicolons)
- Compares This Year (TY) vs Last Year (LY)
- Includes methodology note

## Example 4: Customer Satisfaction Summary
```
"92% of 382 Main Exchange survey respondents reported overall satisfaction with their experience.\\n  - 15.7% said they were shopping sales that were advertised, indicating MCX advertisements are successfully driving footsteps in the door. 45.5% were picking up needed supplies."
```

**Why this works:**
- Opens with overall satisfaction score and sample size
- Provides actionable insight with supporting percentage
- Interprets what the data means for the business
- Includes additional context about customer shopping behavior

## Example 5: Assessment/Recommendation
```
"Marketing will continue to promote exclusive offers which will highlight time-sensitive deals to create urgency and increase CTR, like we saw with the 72 Hour Anniversary Deals and the Labor Day Promotion."
```

**Why this works:**
- States clear action ("Marketing will continue")
- Explains the strategic rationale (urgency, increase CTR)
- References specific successful examples
- Forward-looking and actionable

## Example 6: Customer Comments
```json
{{
  "location": "Camp Lejeune",
  "shopper_type": "Active Duty (Marine Corps) | Shopping Sales that were Advertised",
  "comment": "\\"The sales and scratch-off coupons are such a great bonus to the tax-free shopping! I am looking forward to shopping here again.\\""
}}
```

**Why this works:**
- Clearly identifies location
- Categorizes customer type and shopping reason
- Preserves authentic customer voice
- Shows positive sentiment and intent to return

## Example 7: Satisfaction Table
```json
[
  {{"location": "Camp Pendleton", "sept_satisfied": "90%", "aug_satisfied": "92%", "change": "-2%"}},
  {{"location": "Quantico", "sept_satisfied": "82%", "aug_satisfied": "92%", "change": "-10%"}},
  {{"location": "Twentynine Palms", "sept_satisfied": "96%", "aug_satisfied": "94%", "change": "2%"}}
]
```

**Why this works:**
- Consistent column names across all rows
- Proper percentage formatting with % symbol
- Change column shows direction with +/- sign
- Allows for easy month-over-month comparison

# COMMON MISTAKES TO AVOID

❌ **Generic statements**: "Marketing efforts were successful this month"
✅ **Specific findings**: "September Email Open Rate was 38.08%, up 6% from August's 32.61%"

❌ **Missing context**: "Open rate was 38%"
✅ **With context**: "Open rate was 38.08%, exceeding the retail industry standard of 15-25%"

❌ **Placeholder text**: "Campaign performed well with XX% increase"
✅ **Actual data**: "Labor Day campaign generated a 6.8% increase in total sales to LY"

❌ **Inconsistent formatting**: Some percentages as "0.38" others as "38%"
✅ **Consistent formatting**: All percentages as "38.08%"

❌ **Missing attribution**: "Sales increased"
✅ **Clear attribution**: "The Labor Day Promotion assisted in a 6.8% increase in total sales"

❌ **Vague recommendations**: "We should improve marketing"
✅ **Actionable recommendations**: "Marketing will partner with Business Operations to ensure promotional strategies are executed clearly in-store"

# JSON SCHEMA TO FOLLOW

{json.dumps(structure, indent=2)}

# DATA CONTEXT

{json.dumps(context, indent=2)}

# VALIDATION CHECKLIST

Before submitting your response, verify:
- [ ] All fields from the schema are present
- [ ] All metrics use actual numbers from the context
- [ ] Percentages are formatted consistently (e.g., "38.08%")
- [ ] Lists contain 2-5 meaningful bullets (not just 1)
- [ ] Tables have consistent columns across all rows
- [ ] Customer comments are properly quoted
- [ ] Headers include month/year where applicable
- [ ] Dates follow the specified format
- [ ] No placeholder text (XX%, [Insert], TBD, etc.)
- [ ] Professional tone throughout
- [ ] Insights are data-driven and specific

# OUTPUT FORMAT

Return ONLY valid JSON. No markdown formatting, no code blocks, no explanatory text.
Start your response with {{ and end with }}.

Generate the complete report now."""

    response_text = client.generate("gemini-2.5-pro", prompt)

    try:
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            cleaned_response = response_text[json_start:json_end]
            report_json = json.loads(cleaned_response)
        else:
            raise ValueError("No JSON object found in the response.")
    except Exception as e:
        raise ValueError(f"Gemini output not valid JSON: {e}")

    return report_json

# from config import client
# import json
# from typing import Dict, Any

# def generate_report(structure: dict, context: dict, client) -> dict:
#     """
#     Generate structured report using Gemini with enhanced prompting.
#     Includes concrete examples and detailed expectations.
#     """
    
#     # Build comprehensive prompt with examples and instructions
#     prompt = f"""You are an expert marketing data analyst specializing in retail analytics reports for Marine Corps Community Services (MCCS).

# # CRITICAL INSTRUCTIONS

# 1. **CONTEXT ONLY**: Base your analysis SOLELY on the data provided below. Do not reference external information, trends, or general knowledge.

# 2. **SCHEMA ADHERENCE**: Follow the JSON structure EXACTLY as provided. Every field in the schema must be present in your output.

# 3. **DATA FIDELITY**: Use actual numbers, dates, and metrics from the provided context. Never use placeholder text like "XX%" or "[Insert data]".

# 4. **PROFESSIONAL TONE**: Write in a formal, analytical tone suitable for executive leadership and subject matter experts.

# 5. **CONCISENESS**: Be specific and data-driven. Avoid generic statements, filler content, or marketing fluff.

# # OUTPUT REQUIREMENTS

# ## Page Structure
# Your report must contain exactly 3 pages with specific content on each:
# - **Page 1**: Cover page with executive summary, findings (digital + CSAT), and assessment
# - **Page 2**: Email and social media performance details with tables and metrics
# - **Page 3**: Customer satisfaction details with comments, tables, and reviews

# ## Content Type Guidelines

# ### For Narrative Fields (strings):
# - Write in complete, professional sentences
# - Include specific metrics with context
# - Compare to previous periods when data is available
# - Example: "92% of 382 Main Exchange survey respondents reported overall satisfaction with their experience."

# ### For List/Bullet Fields (arrays):
# - Each bullet should be a complete insight or finding
# - Start with the key metric or insight, then provide supporting details
# - Use proper formatting with indentation for sub-bullets (use "\\n  - " for sub-points)
# - Example:
#   ```
#   "The Labor Day Promotion assisted in a 6.8% increase in total sales to LY, with a majority of digitally available Labor Day coupons being scanned through mobile (383 mobile scans vs. 172 email scans).\\n  - The coupon was also available printed in-store, which received 4,230 total scans."
#   ```

# ### For Tables (arrays of objects):
# - Each row must have consistent keys across all objects
# - Use proper percentage formatting: "38.08%" not "38.08" or "0.38"
# - Include all columns: location, metrics, comparisons, changes
# - Example structure:
#   ```json
#   [
#     {{
#       "email_content_name": "Campaign Name",
#       "email_subject": "Subject Line",
#       "sends": 59680,
#       "open_rate": "39.60%",
#       "click_rate": "1.24%",
#       "click_to_open_rate": "3.14%",
#       "unique_unsubscribes": 8,
#       "unsubscribe_rate": "0.02%"
#     }}
#   ]
#   ```

# ### For Comment Fields (arrays of objects):
# - Include location, customer type/reason, and actual quoted feedback
# - Format quotes properly with opening and closing quotation marks
# - Preserve original customer voice and language
# - Example:
#   ```json
#   {{
#     "location": "Camp Pendleton",
#     "shopper_type": "DOD Civilian | Shopping for a Gift",
#     "comment": "\\"I noticed there was 'glam event' when I entered the store...\\""
#   }}
#   ```

# ### For Headers:
# - Use proper title case
# - Include month/year when specified in schema
# - Match the exact format from previous reports
# - Examples:
#   - "September MCX Email Highlight"
#   - "Findings – Review of digital performance, advertising campaigns, and sales:"
#   - "September 2024 Email Campaigns Performance (as of October 23rd, 2024)"

# ### For Dates:
# - Format: "As of [Month], [Day][th/st/nd/rd], [Year]"
# - Example: "As of November, 27th, 2024"
# - For periods: "Period Covered: 01-Sept-24 - 30-Sept-24"

# # CONCRETE EXAMPLES FROM ACTUAL REPORTS

# ## Example 1: Executive Summary Bullet (with sub-bullet)
# ```
# "The Labor Day Promotion assisted in a 6.8% increase in total sales to LY, with a majority of digitally available Labor Day coupons being scanned through mobile (383 mobile scans vs. 172 email scans).\\n  - The coupon was also available printed in-store, which received 4,230 total scans."
# ```

# **Why this works:**
# - Starts with the key finding (6.8% increase)
# - Provides specific attribution (Labor Day Promotion)
# - Includes detailed metrics (383 vs 172 scans)
# - Uses sub-bullet for additional context
# - Compares channels (mobile vs email vs in-store)

# ## Example 2: Industry Benchmarks (list format)
# ```json
# [
#   "The industry standard open rate (OPR) for emails in retail is 15-25% - MCX average for September was 38.08% (32.61% in August, 30.10% in July)",
#   "The industry standard click through rate (CTR) is 1-5% - MCX average for September was 0.65% (0.45% in August, 0.53% in July)"
# ]
# ```

# **Why this works:**
# - States industry benchmark first
# - Provides current month performance
# - Shows historical trend (3 months)
# - Demonstrates performance relative to benchmark

# ## Example 3: Campaign Details (nested structure)
# ```json
# {{
#   "title": "Labor Day (3 Emails w/ Coupons) (28-Aug – 02-Sept TY; 23-Aug – 5-Sept LY):",
#   "details": [
#     "Average OPR: 34.0% | Average CTR: 0.56% | Coupon Scans – Email: 172, Mobile: 383, In-Store Print: 4,230",
#     "Total Sales: $12.6M TY; $11.8M LY | Average Daily Sales 2024: $2.52M; Average Daily Sales 2023: $60K",
#     "2024 Promotion through email with coupons. 2022 and 2023 promotion through print and coupons"
#   ]
# }}
# ```

# **Why this works:**
# - Title includes campaign name, date range, and year comparison
# - Each detail line focuses on specific metric category
# - Uses consistent formatting (pipe separators, semicolons)
# - Compares This Year (TY) vs Last Year (LY)
# - Includes methodology note

# ## Example 4: Customer Satisfaction Summary
# ```
# "92% of 382 Main Exchange survey respondents reported overall satisfaction with their experience.\\n  - 15.7% said they were shopping sales that were advertised, indicating MCX advertisements are successfully driving footsteps in the door. 45.5% were picking up needed supplies."
# ```

# **Why this works:**
# - Opens with overall satisfaction score and sample size
# - Provides actionable insight with supporting percentage
# - Interprets what the data means for the business
# - Includes additional context about customer shopping behavior

# ## Example 5: Assessment/Recommendation
# ```
# "Marketing will continue to promote exclusive offers which will highlight time-sensitive deals to create urgency and increase CTR, like we saw with the 72 Hour Anniversary Deals and the Labor Day Promotion."
# ```

# **Why this works:**
# - States clear action ("Marketing will continue")
# - Explains the strategic rationale (urgency, increase CTR)
# - References specific successful examples
# - Forward-looking and actionable

# ## Example 6: Customer Comments
# ```json
# {{
#   "location": "Camp Lejeune",
#   "shopper_type": "Active Duty (Marine Corps) | Shopping Sales that were Advertised",
#   "comment": "\\"The sales and scratch-off coupons are such a great bonus to the tax-free shopping! I am looking forward to shopping here again.\\""
# }}
# ```

# **Why this works:**
# - Clearly identifies location
# - Categorizes customer type and shopping reason
# - Preserves authentic customer voice
# - Shows positive sentiment and intent to return

# ## Example 7: Satisfaction Table
# ```json
# [
#   {{"location": "Camp Pendleton", "sept_satisfied": "90%", "aug_satisfied": "92%", "change": "-2%"}},
#   {{"location": "Quantico", "sept_satisfied": "82%", "aug_satisfied": "92%", "change": "-10%"}},
#   {{"location": "Twentynine Palms", "sept_satisfied": "96%", "aug_satisfied": "94%", "change": "2%"}}
# ]
# ```

# **Why this works:**
# - Consistent column names across all rows
# - Proper percentage formatting with % symbol
# - Change column shows direction with +/- sign
# - Allows for easy month-over-month comparison

# # COMMON MISTAKES TO AVOID

# ❌ **Generic statements**: "Marketing efforts were successful this month"
# ✅ **Specific findings**: "September Email Open Rate was 38.08%, up 6% from August's 32.61%"

# ❌ **Missing context**: "Open rate was 38%"
# ✅ **With context**: "Open rate was 38.08%, exceeding the retail industry standard of 15-25%"

# ❌ **Placeholder text**: "Campaign performed well with XX% increase"
# ✅ **Actual data**: "Labor Day campaign generated a 6.8% increase in total sales to LY"

# ❌ **Inconsistent formatting**: Some percentages as "0.38" others as "38%"
# ✅ **Consistent formatting**: All percentages as "38.08%"

# ❌ **Missing attribution**: "Sales increased"
# ✅ **Clear attribution**: "The Labor Day Promotion assisted in a 6.8% increase in total sales"

# ❌ **Vague recommendations**: "We should improve marketing"
# ✅ **Actionable recommendations**: "Marketing will partner with Business Operations to ensure promotional strategies are executed clearly in-store"

# # JSON SCHEMA TO FOLLOW

# {json.dumps(structure, indent=2)}

# # DATA CONTEXT

# {json.dumps(context, indent=2)}

# # VALIDATION CHECKLIST

# Before submitting your response, verify:
# - [ ] All fields from the schema are present
# - [ ] All metrics use actual numbers from the context
# - [ ] Percentages are formatted consistently (e.g., "38.08%")
# - [ ] Lists contain 2-5 meaningful bullets (not just 1)
# - [ ] Tables have consistent columns across all rows
# - [ ] Customer comments are properly quoted
# - [ ] Headers include month/year where applicable
# - [ ] Dates follow the specified format
# - [ ] No placeholder text (XX%, [Insert], TBD, etc.)
# - [ ] Professional tone throughout
# - [ ] Insights are data-driven and specific

# # OUTPUT FORMAT

# Return ONLY valid JSON. No markdown formatting, no code blocks, no explanatory text.
# Start your response with {{ and end with }}.

# Generate the complete report now."""

#     # Generate response from Gemini
#     response_text = client.generate("gemini-2.5-pro",prompt)
    
#     # Extract and parse JSON
#     try:
#         # Remove markdown code blocks if present
#         if "```json" in response_text:
#             response_text = response_text.split("```json")[1].split("```")[0]
#         elif "```" in response_text:
#             response_text = response_text.split("```")[1].split("```")[0]
        
#         # Find JSON boundaries
#         json_start = response_text.find('{')
#         json_end = response_text.rfind('}') + 1
        
#         if json_start == -1 or json_end == 0:
#             raise ValueError("No JSON object found in the response.")
        
#         cleaned_response = response_text[json_start:json_end]
#         report_json = json.loads(cleaned_response)
        
#         # Validate basic structure
#         if "pages" not in report_json:
#             raise ValueError("Generated report missing 'pages' key")
        
#         return report_json
        
#     except json.JSONDecodeError as e:
#         raise ValueError(f"Gemini output not valid JSON: {e}\\nResponse: {response_text[:500]}")
#     except Exception as e:
#         raise ValueError(f"Error processing Gemini response: {e}")