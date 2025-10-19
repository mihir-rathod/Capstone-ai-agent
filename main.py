from typing import Dict, Any
from fastapi import FastAPI, Body

app = FastAPI(title="Mock Report Generation API")

@app.get("/")
def root():
    return {"message": "✅ Mock Report Generation API is running"}

@app.post("/generate_report")
async def generate_report_endpoint(context_data: Dict[str, Any] = Body(...)):
    mock_response = {
        "items": [
            {
                "id": "as_of_date",
                "title": "As of Date",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "September 30, 2025"
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "As of September, 30th, 2024"
                        ]
                    }
                ]
            },
            {
                "id": "report_title",
                "title": "MCCS Marketing Analytics Assessment",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Marine Corps Community Services (MCCS) Retail Marketing Report – September 2024"
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "MCCS Retail Analytics Report"
                        ]
                    }
                ]
            },
            {
                "id": "purpose_statement",
                "title": "Purpose",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "To evaluate retail marketing performance for MCCS during the reporting period and provide actionable insights for future initiatives."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "This report provides a comprehensive analysis of retail marketing performance and customer satisfaction for Marine Corps Community Services (MCCS) for the period of September 2024."
                        ]
                    }
                ]
            },
            {
                "id": "exec_summary_header",
                "title": "Executive Summary",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "This executive summary presents the high‑level findings from the September 2024 retail marketing analysis."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "Executive Summary: September 2024"
                        ]
                    }
                ]
            },
            {
                "id": "exec_summary_period",
                "title": "Period Covered",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "September 01, 2024 to September 30, 2024"
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "Period Covered: 01-Sept-24 - 30-Sept-24"
                        ]
                    }
                ]
            },
            {
                "id": "exec_summary_highlights",
                "title": "Key Highlights",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "• Total records analyzed: 1,500\n• No specific digital or sales metrics available in the data set\n• Recommendations focus on data collection improvements and baseline strategy development"
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No data was available for the September 2024 reporting period. Consequently, an executive summary of performance highlights cannot be provided. Key performance indicators for digital marketing and customer satisfaction are unavailable for analysis."
                        ]
                    }
                ]
            },
            {
                "id": "digital_findings_header",
                "title": "Findings - Review of digital performance, advertising campaigns, and sales",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "The provided data set does not contain detailed digital performance metrics; therefore, findings are limited to contextual observations."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "Key Findings: Digital Performance"
                        ]
                    }
                ]
            },
            {
                "id": "digital_performance_summary",
                "title": "Digital Performance Overview",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Digital performance data (e.g., website traffic, click‑through rates) was not included in the submitted data."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No digital performance data was available for the reporting period of September 2024. Analysis of email and social media metrics cannot be completed."
                        ]
                    }
                ]
            },
            {
                "id": "campaign_performance",
                "title": "Campaign Performance",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Campaign‑level results are unavailable; no specific advertising spend or conversion data were provided."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No specific campaign data was provided. Therefore, an assessment of individual campaign performance is not possible."
                        ]
                    }
                ]
            },
            {
                "id": "sales_analysis",
                "title": "Sales Analysis",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Sales figures, unit volumes, and revenue data were not part of the data set; analysis is limited to record count."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "Sales data related to digital promotions was not available for analysis."
                        ]
                    }
                ]
            },
            {
                "id": "csat_findings_header",
                "title": "Findings - Review of Main Exchanges, Marine Marts, and MCHS CSAT Surveys and Google Reviews",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Customer satisfaction survey results and Google review details were not supplied."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "Key Findings: Customer Satisfaction (CSAT)"
                        ]
                    }
                ]
            },
            {
                "id": "main_exchange_overview",
                "title": "Main Exchange Performance",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "No performance metrics for Main Exchanges were included in the data."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No customer satisfaction survey data was available for the Main Exchange for September 2024."
                        ]
                    }
                ]
            },
            {
                "id": "marine_mart_overview",
                "title": "Marine Mart Performance",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Marine Mart specific data is absent from the provided information."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No customer satisfaction survey data was available for Marine Marts for September 2024."
                        ]
                    }
                ]
            },
            {
                "id": "mchs_overview",
                "title": "MCHS Overview",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "MCHS service metrics are not present within the supplied dataset."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No Marine Corps Home Store (MCHS) feedback data was available for this period."
                        ]
                    }
                ]
            },
            {
                "id": "reviews_summary",
                "title": "Reviews Summary",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Google review comments and aggregate ratings were not provided."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No Google Reviews or other external review data was provided for analysis in September 2024."
                        ]
                    }
                ]
            },
            {
                "id": "assessment_header",
                "title": "Assessment",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Overall assessment highlights the need for comprehensive data collection to enable robust analysis."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "Overall Assessment"
                        ]
                    }
                ]
            },
            {
                "id": "assessment_summary",
                "title": "Summary",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Given the limited data, the assessment focuses on structural recommendations rather than quantitative performance."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "A comprehensive assessment of retail performance for September 2024 cannot be provided due to the absence of performance and customer satisfaction data. Key metrics across digital marketing and customer feedback channels were unavailable for this reporting period."
                        ]
                    }
                ]
            },
            {
                "id": "key_insights",
                "title": "Key Insights",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "• Record count indicates a sizable transaction volume (1,500 records) for the period.\n• Absence of metric data prevents performance benchmarking.\n• Establishing a standardized reporting framework is critical."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No key insights can be derived as no underlying data was provided."
                        ]
                    }
                ]
            },
            {
                "id": "recommendations",
                "title": "Recommendations",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "1. Implement a data capture plan that records digital traffic, campaign spend, and sales outcomes.\n2. Integrate CSAT and Google review collection into the reporting pipeline.\n3. Define key performance indicators (KPIs) such as conversion rate, average order value, and net promoter score (NPS).\n4. Schedule monthly data reviews to track trends and adjust tactics promptly."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "It is recommended to ensure data sources for digital marketing, sales, and customer satisfaction are correctly populated for future reporting periods to enable performance analysis and strategic planning."
                        ]
                    }
                ]
            },
            {
                "id": "email_highlight_header",
                "title": "Email Campaign Highlight",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Email campaign data not available; placeholder information provided."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "September MCX Email Highlight"
                        ]
                    }
                ]
            },
            {
                "id": "email_highlight_campaign",
                "title": "Email Campaign",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "N/A"
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No data available."
                        ]
                    }
                ]
            },
            {
                "id": "email_highlight_image",
                "title": "Email Campaign Image",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Image placeholder – no image supplied."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            ""
                        ]
                    }
                ]
            },
            {
                "id": "email_highlight_details",
                "title": "Campaign Details",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Details are not provided in the source data."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No campaign was highlighted as no email performance data was available for September 2024."
                        ]
                    }
                ]
            },
            {
                "id": "email_highlight_metrics",
                "title": "Campaign Metrics",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Open rate: N/A%%\nClick‑through rate: N/A%%\nConversion rate: N/A%%"
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "Metrics for a highlighted campaign are not available."
                        ]
                    }
                ]
            },
            {
                "id": "email_performance_header",
                "title": "Email Campaigns Performance",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Performance metrics could not be calculated due to missing data."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "September 2024 Email Performance"
                        ]
                    }
                ]
            },
            {
                "id": "email_metrics_table",
                "title": "Performance Metrics Table",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Metric\tValue\nSent\t0\nDelivered\t0\nOpened\t0\nClicked\t0"
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No email campaign data available to generate the performance table."
                        ]
                    }
                ]
            },
            {
                "id": "email_metrics_summary",
                "title": "Metrics Summary",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "All email metrics are unavailable for September 2024."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "An overall summary of email performance cannot be generated due to the lack of campaign data for September 2024. Metrics such as open rates, click-through rates, and conversions are unavailable."
                        ]
                    }
                ]
            },
            {
                "id": "social_media_header",
                "title": "Social Media Highlights",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Social media data was not included in the submission."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "September 2024 Social Media Performance"
                        ]
                    }
                ]
            },
            {
                "id": "social_media_metrics",
                "title": "Platform Metrics",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Followers: N/A\nPosts: N/A\nEngagements: N/A"
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No social media metrics (e.g., impressions, reach, engagement rate) were provided for this reporting period."
                        ]
                    }
                ]
            },
            {
                "id": "social_media_engagement",
                "title": "Engagement Analysis",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Engagement rates cannot be computed without raw interaction data."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "An analysis of social media engagement is not possible as no platform-specific data was available for September 2024."
                        ]
                    }
                ]
            },
            {
                "id": "enclosure_number",
                "title": "Enclosure Number",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Enclosure 1"
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "(2)"
                        ]
                    }
                ]
            },
            {
                "id": "satisfaction_header",
                "title": "Customer Satisfaction Highlights",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Customer satisfaction metrics were not part of the provided dataset."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "Customer Satisfaction Analysis: September 2024"
                        ]
                    }
                ]
            },
            {
                "id": "satisfaction_overview",
                "title": "Overall Satisfaction Metrics",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Overall CSAT score: N/A%%"
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "This section details customer feedback from available sources. For September 2024, no customer satisfaction data was provided, preventing a detailed analysis of customer sentiment and experience."
                        ]
                    }
                ]
            },
            {
                "id": "mchs_comments_header",
                "title": "Marine Corps Hospitality Services (MCHS) Comments",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "No MCHS comment data supplied."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "Marine Corps Home Store (MCHS) Feedback"
                        ]
                    }
                ]
            },
            {
                "id": "mchs_feedback",
                "title": "Customer Feedback",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Feedback content unavailable."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No MCHS customer comments were recorded or provided for this reporting period."
                        ]
                    }
                ]
            },
            {
                "id": "mchs_analysis",
                "title": "Analysis",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Cannot perform analysis without feedback data."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "Analysis of MCHS feedback is not possible due to the absence of customer comments."
                        ]
                    }
                ]
            },
            {
                "id": "google_reviews_header",
                "title": "Google Reviews Comments",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Google review comments were not provided."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "Google Reviews"
                        ]
                    }
                ]
            },
            {
                "id": "reviews_details",
                "title": "Review Details",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "No review details available."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "No Google Reviews were provided for analysis in September 2024."
                        ]
                    }
                ]
            },
            {
                "id": "reviews_analysis",
                "title": "Analysis",
                "content": [
                    {
                        "source": "Ollama",
                        "data": "Analysis cannot be conducted without review data."
                    },
                    {
                        "source": "Gemini",
                        "data": [
                            "An analysis of Google Reviews cannot be conducted as no review data was available for this period."
                        ]
                    }
                ]
            }
        ],
        "metadata": {
            "reportType": "retail",
            "period": "2024-09",
            "dateRange": {
                "startDate": "2024-09-01",
                "endDate": "2024-09-30"
            },
            "recordCount": 1500
        }
    }
    
    return mock_response