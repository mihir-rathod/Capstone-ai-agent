from typing import Dict, Any
from fastapi import FastAPI, Body

app = FastAPI(title="Mock Report Generation API")

@app.get("/")
def root():
    return {"message": "✅ Mock Report Generation API is running"}

@app.post("/generate_report")
async def generate_report_endpoint(context_data: Dict[str, Any] = Body(...)):
    mock_response = {
        'items': [
            {'id': 'as_of_date', 'title': 'As of Date', 'content': [{'source': 'Ollama', 'data': ['September 30, 2024']}, {'source': 'Gemini', 'data': ['As of September, 30th, 2024']}]},
            {'id': 'report_title', 'title': 'MCCS Marketing Analytics Assessment', 'content': [{'source': 'Ollama', 'data': ['MCCS Marketing Analytics Assessment']}, {'source': 'Gemini', 'data': ['MCCS Retail Analytics Report - September 2024']}]},
            {'id': 'purpose_statement', 'title': 'Purpose', 'content': [{'source': 'Ollama', 'data': ['Purpose: Analyze retail marketing performance for September 2024 using the provided dataset of 1,500 records.']}, {'source': 'Gemini', 'data': ['This report provides a comprehensive analysis of MCCS retail marketing performance for September 2024, focusing on digital marketing outreach and customer satisfaction feedback.']}]},
            {'id': 'exec_summary_header', 'title': 'Executive Summary', 'content': [{'source': 'Ollama', 'data': ['Executive Summary']}, {'source': 'Gemini', 'data': ['Executive Summary']}]},
            {'id': 'exec_summary_period', 'title': 'Period Covered', 'content': [{'source': 'Ollama', 'data': ['Period Covered: September 01, 2024 to September 30, 2024']}, {'source': 'Gemini', 'data': ['Period Covered: 01-Sept-24 - 30-Sept-24']}]},
            {'id': 'exec_summary_highlights', 'title': 'Key Highlights', 'content': [{'source': 'Ollama', 'data': ['Highlights: The dataset includes 1,500 records for the retail segment in September 2024. No detailed metric data was provided.']}, {'source': 'Gemini', 'data': ['No performance data was available for the September 2024 reporting period. Therefore, a summary of key highlights cannot be provided.']}]},
            {'id': 'digital_findings_header', 'title': 'Findings - Review of digital performance, advertising campaigns, and sales', 'content': [{'source': 'Ollama', 'data': ['Findings - Review of digital performance, advertising campaigns, and sales']}, {'source': 'Gemini', 'data': ['Key Findings: Digital Performance']}]},
            {'id': 'digital_performance_summary', 'title': 'Digital Performance Overview', 'content': [{'source': 'Ollama', 'data': ['Digital performance data not available in the provided context.']}, {'source': 'Gemini', 'data': ['No digital performance data, including email and social media metrics, was available for the September 2024 period.']}]},
            {'id': 'campaign_performance', 'title': 'Campaign Performance', 'content': [{'source': 'Ollama', 'data': ['Campaign performance details are not included in the provided data.']}, {'source': 'Gemini', 'data': ['No data was available for campaign performance analysis.']}]},
            {'id': 'sales_analysis', 'title': 'Sales Analysis', 'content': [{'source': 'Ollama', 'data': ['Sales analysis cannot be performed due to lack of sales figures.']}, {'source': 'Gemini', 'data': ['No sales data was provided for this reporting period, preventing any analysis of sales trends or campaign impact on revenue.']}]},
            {'id': 'csat_findings_header', 'title': 'Findings - Review of Main Exchanges, Marine Marts, and MCHS CSAT Surveys and Google Reviews', 'content': [{'source': 'Ollama', 'data': ['Findings - Review of Main Exchanges, Marine Marts, and MCHS CSAT Surveys and Google Reviews']}, {'source': 'Gemini', 'data': ['Key Findings: Customer Satisfaction (CSAT)']}]},
            {'id': 'main_exchange_overview', 'title': 'Main Exchange Performance', 'content': [{'source': 'Ollama', 'data': ['Main Exchange performance metrics are not provided.']}, {'source': 'Gemini', 'data': ['No customer satisfaction data available for the Main Exchange.']}]},
            {'id': 'marine_mart_overview', 'title': 'Marine Mart Performance', 'content': [{'source': 'Ollama', 'data': ['Marine Mart performance metrics are not provided.']}, {'source': 'Gemini', 'data': ['No customer satisfaction data available for Marine Marts.']}]},
            {'id': 'mchs_overview', 'title': 'MCHS Overview', 'content': [{'source': 'Ollama', 'data': ['MCHS overview data is not available.']}, {'source': 'Gemini', 'data': ['No customer satisfaction data available for MCHS.']}]},
            {'id': 'reviews_summary', 'title': 'Reviews Summary', 'content': [{'source': 'Ollama', 'data': ['Google and CSAT review data are not included.']}, {'source': 'Gemini', 'data': ['No Google Reviews data was available for analysis.']}]},
            {'id': 'assessment_header', 'title': 'Assessment', 'content': [{'source': 'Ollama', 'data': ['Assessment']}, {'source': 'Gemini', 'data': ['Overall Assessment']}]},
            {'id': 'assessment_summary', 'title': 'Summary', 'content': [{'source': 'Ollama', 'data': ['Based on the limited data, a comprehensive assessment cannot be completed.']}, {'source': 'Gemini', 'data': ['A comprehensive assessment of retail performance is not possible due to the absence of marketing, sales, and customer satisfaction data for the September 2024 period.']}]},
            {'id': 'key_insights', 'title': 'Key Insights', 'content': [{'source': 'Ollama', 'data': ['Key insights are limited to the presence of 1,500 records for September 2024.']}, {'source': 'Gemini', 'data': ['No key insights can be derived as no data was provided for this reporting period.']}]},
            {'id': 'recommendations', 'title': 'Recommendations', 'content': [{'source': 'Ollama', 'data': ['Recommendations: Collect detailed digital, campaign, sales, and satisfaction data for future analyses.']}, {'source': 'Gemini', 'data': ['No recommendations can be formulated without performance data. It is recommended to investigate the data pipeline to ensure metrics are available for future reporting cycles.']}]},
            {'id': 'email_highlight_header', 'title': 'Email Campaign Highlight', 'content': [{'source': 'Ollama', 'data': ['Email Campaign Highlight']}, {'source': 'Gemini', 'data': ['September MCX Email Highlight']}]},
            {'id': 'email_highlight_campaign', 'title': 'Email Campaign', 'content': [{'source': 'Ollama', 'data': ['No specific email campaign data provided.']}, {'source': 'Gemini', 'data': ['No Data Available']}]},
            {'id': 'email_highlight_image', 'title': 'Email Campaign Image', 'content': [{'source': 'Ollama', 'data': ['Image not available.']}, {'source': 'Gemini', 'data': ['']}]},
            {'id': 'email_highlight_details', 'title': 'Campaign Details', 'content': [{'source': 'Ollama', 'data': ['Details are unavailable.']}, {'source': 'Gemini', 'data': ['No data is available to highlight a top-performing email campaign for September 2024.']}]},
            {'id': 'email_highlight_metrics', 'title': 'Campaign Metrics', 'content': [{'source': 'Ollama', 'data': ['Metrics not provided.']}, {'source': 'Gemini', 'data': ['No metrics available.']}]},
            {'id': 'email_performance_header', 'title': 'Email Campaigns Performance', 'content': [{'source': 'Ollama', 'data': ['Email Campaigns Performance']}, {'source': 'Gemini', 'data': ['Overall Email Performance: September 2024']}]},
            {'id': 'email_metrics_table', 'title': 'Performance Metrics Table', 'content': [{'source': 'Ollama', 'data': ['Performance metrics table cannot be generated due to lack of data.']}, {'source': 'Gemini', 'data': ['No data available.']}]},
            {'id': 'email_metrics_summary', 'title': 'Metrics Summary', 'content': [{'source': 'Ollama', 'data': ['Summary unavailable.']}, {'source': 'Gemini', 'data': ['An overall summary of email performance cannot be generated as no campaign data was provided for September 2024.']}]},
            {'id': 'social_media_header', 'title': 'Social Media Highlights', 'content': [{'source': 'Ollama', 'data': ['Social Media Highlights']}, {'source': 'Gemini', 'data': ['Social Media Performance']}]},
            {'id': 'social_media_metrics', 'title': 'Platform Metrics', 'content': [{'source': 'Ollama', 'data': ['Social media platform metrics are not included.']}, {'source': 'Gemini', 'data': ['No social media metrics are available for this reporting period.']}]},
            {'id': 'social_media_engagement', 'title': 'Engagement Analysis', 'content': [{'source': 'Ollama', 'data': ['Engagement analysis cannot be performed.']}, {'source': 'Gemini', 'data': ['No social media engagement data is available for this reporting period.']}]},
            {'id': 'enclosure_number', 'title': 'Enclosure Number', 'content': [{'source': 'Ollama', 'data': ['Enclosure 2']}, {'source': 'Gemini', 'data': ['Enclosure (1)']}]},
            {'id': 'satisfaction_header', 'title': 'Customer Satisfaction Highlights', 'content': [{'source': 'Ollama', 'data': ['Customer Satisfaction Highlights']}, {'source': 'Gemini', 'data': ['Customer Satisfaction and Feedback']}]},
            {'id': 'satisfaction_overview', 'title': 'Overall Satisfaction Metrics', 'content': [{'source': 'Ollama', 'data': ['Overall satisfaction metrics are not provided.']}, {'source': 'Gemini', 'data': ['This section details customer feedback from MCHS surveys and Google Reviews. No data was available for the September 2024 period.']}]},
            {'id': 'mchs_comments_header', 'title': 'Marine Corps Hospitality Services (MCHS) Comments', 'content': [{'source': 'Ollama', 'data': ['Marine Corps Hospitality Services (MCHS) Comments']}, {'source': 'Gemini', 'data': ['MCHS Customer Feedback']}]},
            {'id': 'mchs_feedback', 'title': 'Customer Feedback', 'content': [{'source': 'Ollama', 'data': ['Feedback comments are unavailable.']}, {'source': 'Gemini', 'data': ['No customer feedback comments were recorded for this period.']}]},
            {'id': 'mchs_analysis', 'title': 'Analysis', 'content': [{'source': 'Ollama', 'data': ['Analysis cannot be performed.']}, {'source': 'Gemini', 'data': ['Analysis of customer feedback is not possible due to the lack of available data.']}]},
            {'id': 'google_reviews_header', 'title': 'Google Reviews Comments', 'content': [{'source': 'Ollama', 'data': ['Google Reviews Comments']}, {'source': 'Gemini', 'data': ['Google Reviews']}]},
            {'id': 'reviews_details', 'title': 'Review Details', 'content': [{'source': 'Ollama', 'data': ['Review details are not provided.']}, {'source': 'Gemini', 'data': ['No Google Reviews data was provided for this period.']}]},
            {'id': 'reviews_analysis', 'title': 'Analysis', 'content': [{'source': 'Ollama', 'data': ['Analysis unavailable.']}, {'source': 'Gemini', 'data': ['Analysis of Google Reviews is not possible due to the lack of available data.']}]}
        ],
        'metadata': {
            'reportType': 'retail',
            'period': '2024-09',
            'dateRange': {'startDate': '2024-09-01', 'endDate': '2024-09-30'},
            'recordCount': 1500
        }
    }
    
    return mock_response