from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
from datetime import datetime

router = APIRouter()

# Request model for POST endpoint
class ReportRequest(BaseModel):
    user_input: str
    report_type: Optional[str] = "marketing_analytics"
    month: Optional[str] = None
    year: Optional[str] = None

@router.post("/generate-report")
async def generate_mock_report(request: ReportRequest):
    """
    Mock endpoint that simulates MCCS Marketing Analytics Report generation.
    This matches the structure of the actual LLM-generated reports.
    
    Example request body:
    {
        "user_input": "Generate marketing analytics report for September 2024",
        "report_type": "marketing_analytics",
        "month": "September",
        "year": "2024"
    }
    """
    
    # Determine report period from request
    month = request.month or "September"
    year = request.year or "2024"
    
    return {
        "report_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "report_metadata": {
            "title": f"{month} {year} MCCS Marketing Analytics Assessment",
            "generated_date": datetime.now().strftime("As of %B %d, %Y"),
            "data_collection_date": f"Data collected on {datetime.now().strftime('%B %d, %Y')}",
            "report_type": request.report_type,
            "is_mock": True
        },
        "summary": f"Hello! This is a mock {month} {year} Marketing Analytics Report. "
                   f"The actual report will contain real email campaign performance data, "
                   f"customer satisfaction metrics, and actionable insights from the LLM.",
        
        # Email Campaigns Performance Section
        "email_campaigns": {
            "section_title": f"{month} {year} Email Campaigns Performance",
            "total_sends": 895773,
            "average_open_rate": "38.08%",
            "average_click_rate": "0.65%",
            "average_click_to_open_rate": "1.70%",
            "total_unsubscribes": 192,
            "average_unsubscribe_rate": "0.02%",
            "campaigns": [
                {
                    "email_content_name": "Your onboarding isn't complete - join the MCX Social Community!",
                    "email_subject": "Your onboarding isn't complete - join the MCX Social Community!",
                    "sends": 1432,
                    "open_rate": "45.95%",
                    "click_rate": "4.72%",
                    "click_to_open_rate": "10.27%",
                    "unique_unsubscribes": 3,
                    "unsubscribe_rate": "0.24%"
                },
                {
                    "email_content_name": "Welcome Aboard! Explore your Earned Benefits!",
                    "email_subject": "Welcome Aboard! Explore your Earned Benefits!",
                    "sends": 1246,
                    "open_rate": "45.37%",
                    "click_rate": "5.83%",
                    "click_to_open_rate": "12.84%",
                    "unique_unsubscribes": 1,
                    "unsubscribe_rate": "0.09%"
                },
                {
                    "email_content_name": "09-12-24 Deals of the Day",
                    "email_subject": "Sneak peek for TOMORROW! 9/13 Deals of the Day! 🎉",
                    "sends": 59685,
                    "open_rate": "39.83%",
                    "click_rate": "0.57%",
                    "click_to_open_rate": "1.43%",
                    "unique_unsubscribes": 5,
                    "unsubscribe_rate": "0.01%"
                }
            ]
        },
        
        # Customer Satisfaction Section
        "customer_satisfaction": {
            "section_title": f"{month} {year} Customer Satisfaction",
            "location_data": [
                {
                    "location": "Camp Pendleton",
                    "current_month_satisfaction": "90%",
                    "previous_month_satisfaction": "92%",
                    "change": "-2%"
                },
                {
                    "location": "Camp Lejeune",
                    "current_month_satisfaction": "94%",
                    "previous_month_satisfaction": "96%",
                    "change": "-2%"
                },
                {
                    "location": "Cherry Point",
                    "current_month_satisfaction": "96%",
                    "previous_month_satisfaction": "96%",
                    "change": "0%"
                },
                {
                    "location": "Quantico",
                    "current_month_satisfaction": "82%",
                    "previous_month_satisfaction": "92%",
                    "change": "-10%"
                },
                {
                    "location": "Twentynine Palms",
                    "current_month_satisfaction": "96%",
                    "previous_month_satisfaction": "94%",
                    "change": "2%"
                }
            ]
        },
        
        # Customer Feedback/Comments Section
        "customer_feedback": {
            "section_title": "Customer Feedback & Comments",
            "feedback_items": [
                {
                    "category": "Promotions & Signage",
                    "comment": "I noticed there was 'glam event' when I entered the store. There were price signs and final sale signs around the beauty department but no signs indicating that if you spent $50 you would receive a promotion item...",
                    "sentiment": "neutral"
                },
                {
                    "category": "Positive Experience",
                    "comment": "The sales and scratch-off coupons are such a great bonus to the tax-free shopping! I am looking forward to shopping here again.",
                    "sentiment": "positive"
                },
                {
                    "category": "Facility Issues",
                    "comment": "The freezers at this location have been out for some time now we haven't had any frozen foods available for quite some time.",
                    "sentiment": "negative"
                },
                {
                    "category": "Product Availability",
                    "comment": "We need medicine in the store... they said the manager won't authorize medicine, but we can't leave during the cycle and we get aches and pains.",
                    "sentiment": "negative"
                }
            ]
        },
        
        # Key Insights & Opportunities Section
        "key_insights": [
            {
                "title": "Email Campaign Performance",
                "insight": "Onboarding and welcome emails show significantly higher engagement rates (45%+ open rates) compared to promotional emails (37-40% open rates).",
                "priority": "high"
            },
            {
                "title": "Customer Satisfaction Trends",
                "insight": "Notable decreases in satisfaction at Quantico (-10%), South Carolina (-12%), and Yuma (-10%) require immediate attention.",
                "priority": "critical"
            },
            {
                "title": "Promotional Signage",
                "insight": "Opportunity to increase satisfaction score by ensuring advertisements and information at locations is up to date and readily available.",
                "priority": "medium"
            }
        ],
        
        # Recommendations Section
        "recommendations": [
            "Investigate satisfaction drops at Quantico, South Carolina, and Yuma locations - conduct follow-up surveys",
            "Improve promotional signage clarity, especially for spend-threshold promotions",
            "Address facility maintenance issues (freezers, equipment) that impact customer experience",
            "Leverage high-performing email templates (onboarding/welcome) for future campaigns",
            "Update location information channels (TV displays, digital signage) to ensure accuracy",
            "Consider expanding product availability (medicine, niche items) based on customer feedback"
        ],
        
        # Metadata about the report generation
        "generation_metadata": {
            "model": "mock-gemini-1.5",
            "tokens_used": 0,
            "processing_time_ms": 150,
            "confidence_score": 0.95,
            "data_sources": ["email_campaigns", "customer_surveys", "location_metrics"]
        }
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Mock LLM API",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/report-example")
async def get_report_example():
    """
    Returns an example request/response for frontend developers
    """
    return {
        "endpoint": "/api/v1/generate-report",
        "method": "POST",
        "description": "Generates MCCS Marketing Analytics Assessment Report",
        "example_request": {
            "user_input": "Generate marketing analytics report for September 2024",
            "report_type": "marketing_analytics",
            "month": "September",
            "year": "2024"
        },
        "response_structure": {
            "report_id": "UUID string",
            "timestamp": "ISO datetime",
            "status": "success/error",
            "report_metadata": "Report header information",
            "summary": "Executive summary text",
            "email_campaigns": "Email performance data array",
            "customer_satisfaction": "Location satisfaction metrics",
            "customer_feedback": "Customer comments and sentiment",
            "key_insights": "Analytical insights array",
            "recommendations": "Action items array",
            "generation_metadata": "LLM generation details"
        }
    }