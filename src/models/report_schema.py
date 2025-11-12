from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

class ContentItem(BaseModel):
    source: str
    data: Union[str, List[str]]  # Can be either a single string or a list of strings

class Tag(BaseModel):
    id: str
    title: str
    content: List[ContentItem] = []

class Page(BaseModel):
    page_number: int
    tags: List[Tag]

class DocumentSchema(BaseModel):
    pages: List[Page]

def get_current_date():
    return datetime.now().strftime("%B %d, %Y")

from ..services import retrievers as r

# Full marketing report schema (used for all_categories)
marketing_report_schema = DocumentSchema(
    pages=[
        # Page 1: Main Report Content
        Page(
            page_number=1,
            tags=[
                # Header Information
                Tag(id="as_of_date", title="As of Date", content=[]),
                Tag(id="report_title", title="MCCS Marketing Analytics Assessment", content=[]),
                Tag(id="purpose_statement", title="Purpose", content=[
                    ContentItem(
                        source="system",
                        data=[
                            "To support leaders' and subject matter experts' in their decision-making process",
                            "To generate smart revenue and increase brand affinity",
                            "To reduce stress on Marines and their families"
                        ]
                    )
                ]),

                # Executive Summary Section
                Tag(id="exec_summary_header", title="Executive Summary", content=[]),
                Tag(id="exec_summary_period", title="Period Covered", content=[]),
                Tag(id="exec_summary_highlights", title="Key Highlights", content=[]),

                # Digital Performance Section
                Tag(id="digital_findings_header", title="Findings - Review of digital performance, advertising campaigns, and sales", content=[]),
                Tag(id="digital_performance_summary", title="Digital Performance Overview", content=[]),
                Tag(id="campaign_performance", title="Campaign Performance", content=[]),
                Tag(id="sales_analysis", title="Sales Analysis", content=[]),

                # Customer Satisfaction Section
                Tag(id="csat_findings_header", title="Findings - Review of Main Exchanges, Marine Marts, and MCHS CSAT Surveys and Google Reviews", content=[]),
                Tag(id="main_exchange_overview", title="Main Exchange Performance", content=[]),
                Tag(id="marine_mart_overview", title="Marine Mart Performance", content=[]),
                Tag(id="mchs_overview", title="MCHS Overview", content=[]),
                Tag(id="reviews_summary", title="Reviews Summary", content=[]),

                # Assessment Section
                Tag(id="assessment_header", title="Assessment", content=[]),
                Tag(id="assessment_summary", title="Summary", content=[]),
                Tag(id="key_insights", title="Key Insights", content=[]),
                Tag(id="recommendations", title="Recommendations", content=[]),
            ],
        ),

        # Page 2: Email and Social Media Details
        Page(
            page_number=2,
            tags=[
                # Email Campaign Section
                Tag(id="email_highlight_header", title="Email Campaign Highlight", content=[]),
                Tag(id="email_highlight_campaign", title="Email Campaign", content=[]),
                Tag(id="email_highlight_image", title="Email Campaign Image", content=[]),
                Tag(id="email_highlight_details", title="Campaign Details", content=[]),
                Tag(id="email_highlight_metrics", title="Campaign Metrics", content=[]),

                # Email Performance Section
                Tag(id="email_performance_header", title="Email Campaigns Performance", content=[]),
                Tag(id="email_metrics_table", title="Performance Metrics Table", content=[]),
                Tag(id="email_metrics_summary", title="Metrics Summary", content=[]),

                # Social Media Section
                Tag(id="social_media_header", title="Social Media Highlights", content=[]),
                Tag(id="social_media_metrics", title="Platform Metrics", content=[]),
                Tag(id="social_media_engagement", title="Engagement Analysis", content=[]),

                Tag(id="enclosure_number", title="Enclosure Number", content=[]),
            ],
        ),

        # Page 3: Customer Satisfaction Details
        Page(
            page_number=3,
            tags=[
                # Customer Satisfaction Section
                Tag(id="satisfaction_header", title="Customer Satisfaction Highlights", content=[]),
                Tag(id="satisfaction_overview", title="Overall Satisfaction Metrics", content=[]),

                # MCHS Comments Section
                Tag(id="mchs_comments_header", title="Marine Corps Hospitality Services (MCHS) Comments", content=[]),
                Tag(id="mchs_feedback", title="Customer Feedback", content=[]),
                Tag(id="mchs_analysis", title="Analysis", content=[]),

                # Google Reviews Section
                Tag(id="google_reviews_header", title="Google Reviews Comments", content=[]),
                Tag(id="reviews_details", title="Review Details", content=[]),
                Tag(id="reviews_analysis", title="Analysis", content=[]),

                Tag(id="enclosure_number", title="Enclosure Number", content=[]),
            ],
        ),
    ],
)

# Retail data specific schema
def get_retail_data_schema():
    return DocumentSchema(
        pages=[
            Page(
                page_number=1,
                tags=[
                    Tag(id="as_of_date", title="As of Date", content=[]),
                    Tag(id="report_title", title="MCCS Retail Data Analytics Assessment", content=[]),
                    Tag(id="purpose_statement", title="Purpose", content=[
                        ContentItem(
                            source="system",
                            data=[
                                "To analyze retail sales performance and customer purchasing patterns",
                                "To support data-driven retail decisions",
                                "To optimize inventory and sales strategies"
                            ]
                        )
                    ]),
                    Tag(id="exec_summary_header", title="Executive Summary", content=[]),
                    Tag(id="exec_summary_period", title="Period Covered", content=[]),
                    Tag(id="exec_summary_highlights", title="Key Highlights", content=[]),
                    Tag(id="sales_analysis", title="Sales Analysis", content=[]),
                    Tag(id="assessment_header", title="Assessment", content=[]),
                    Tag(id="assessment_summary", title="Summary", content=[]),
                    Tag(id="key_insights", title="Key Insights", content=[]),
                    Tag(id="recommendations", title="Recommendations", content=[]),
                ],
            ),
        ],
    )

# Email performance specific schema
def get_email_performance_schema():
    return DocumentSchema(
        pages=[
            Page(
                page_number=1,
                tags=[
                    Tag(id="as_of_date", title="As of Date", content=[]),
                    Tag(id="report_title", title="MCCS Email Performance Analytics Assessment", content=[]),
                    Tag(id="purpose_statement", title="Purpose", content=[
                        ContentItem(
                            source="system",
                            data=[
                                "To analyze email marketing campaign performance",
                                "To optimize email engagement and conversion rates",
                                "To improve email marketing ROI"
                            ]
                        )
                    ]),
                    Tag(id="exec_summary_header", title="Executive Summary", content=[]),
                    Tag(id="exec_summary_period", title="Period Covered", content=[]),
                    Tag(id="exec_summary_highlights", title="Key Highlights", content=[]),
                    Tag(id="digital_findings_header", title="Email Campaign Findings", content=[]),
                    Tag(id="digital_performance_summary", title="Email Performance Overview", content=[]),
                    Tag(id="campaign_performance", title="Campaign Performance", content=[]),
                ],
            ),
            Page(
                page_number=2,
                tags=[
                    Tag(id="email_highlight_header", title="Email Campaign Highlight", content=[]),
                    Tag(id="email_highlight_campaign", title="Email Campaign", content=[]),
                    Tag(id="email_highlight_image", title="Email Campaign Image", content=[]),
                    Tag(id="email_highlight_details", title="Campaign Details", content=[]),
                    Tag(id="email_highlight_metrics", title="Campaign Metrics", content=[]),
                    Tag(id="email_performance_header", title="Email Campaigns Performance", content=[]),
                    Tag(id="email_metrics_table", title="Performance Metrics Table", content=[]),
                    Tag(id="email_metrics_summary", title="Metrics Summary", content=[]),
                    Tag(id="assessment_header", title="Assessment", content=[]),
                    Tag(id="assessment_summary", title="Summary", content=[]),
                    Tag(id="key_insights", title="Key Insights", content=[]),
                    Tag(id="recommendations", title="Recommendations", content=[]),
                ],
            ),
        ],
    )

# Social media data specific schema
def get_social_media_data_schema():
    return DocumentSchema(
        pages=[
            Page(
                page_number=1,
                tags=[
                    Tag(id="as_of_date", title="As of Date", content=[]),
                    Tag(id="report_title", title="MCCS Social Media Analytics Assessment", content=[]),
                    Tag(id="purpose_statement", title="Purpose", content=[
                        ContentItem(
                            source="system",
                            data=[
                                "To analyze social media engagement and performance",
                                "To optimize social media marketing strategies",
                                "To increase brand awareness and engagement"
                            ]
                        )
                    ]),
                    Tag(id="exec_summary_header", title="Executive Summary", content=[]),
                    Tag(id="exec_summary_period", title="Period Covered", content=[]),
                    Tag(id="exec_summary_highlights", title="Key Highlights", content=[]),
                    Tag(id="digital_findings_header", title="Social Media Findings", content=[]),
                    Tag(id="digital_performance_summary", title="Social Media Performance Overview", content=[]),
                ],
            ),
            Page(
                page_number=2,
                tags=[
                    Tag(id="social_media_header", title="Social Media Highlights", content=[]),
                    Tag(id="social_media_metrics", title="Platform Metrics", content=[]),
                    Tag(id="social_media_engagement", title="Engagement Analysis", content=[]),
                    Tag(id="assessment_header", title="Assessment", content=[]),
                    Tag(id="assessment_summary", title="Summary", content=[]),
                    Tag(id="key_insights", title="Key Insights", content=[]),
                    Tag(id="recommendations", title="Recommendations", content=[]),
                ],
            ),
        ],
    )

# Function to get the appropriate schema based on report type
def get_report_schema(report_type: str):
    if report_type == "retail-data":
        return get_retail_data_schema()
    elif report_type == "email-performance-data":
        return get_email_performance_schema()
    elif report_type == "social-media-data":
        return get_social_media_data_schema()
    elif report_type == "all-categories":
        return marketing_report_schema
    else:
        # Default to full schema for unknown types
        return marketing_report_schema

marketing_report_retrievers = {
    # Page 1 - Cover and Executive Summary
    "as_of_date": {
        "retriever": (lambda self: self.as_of_date),
        "multiple_values": False
    },
    "report_title": {
        "retriever": (lambda self: f"{self.get_month_name()} {self.year} MCCS Marketing Analytics Assessment"),
        "multiple_values": False
    },
    "exec_summary_period": {
        "retriever": (lambda self: f"Period Covered: 01-{self.get_month_abbrev()}-{str(self.year)[2:]} - {self.get_last_day()}-{self.get_month_abbrev()}-{str(self.year)[2:]}"),
        "multiple_values": False
    },
    "exec_summary_bullets": {
        "retriever": (
            r._get_executive_summary_bullets,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": True
    },
    
    # Findings - Digital Performance
    "findings_digital_header": {
        "retriever": (lambda self: "Findings – Review of digital performance, advertising campaigns, and sales:"),
        "multiple_values": False
    },
    "industry_benchmarks": {
        "retriever": (
            r._get_industry_benchmarks,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "email_blast_highlights": {
        "retriever": (
            r._get_email_blast_highlights,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": True
    },
    "campaigns_details": {
        "retriever": (
            r._get_all_campaigns_details,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": True
    },
    "other_initiatives": {
        "retriever": (
            r._get_other_initiatives,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    
    # Findings - CSAT and Reviews
    "findings_csat_header": {
        "retriever": (lambda self: "Findings – Review of Main Exchanges, Marine Marts, and MCHS CSAT Surveys and Google Reviews:"),
        "multiple_values": False
    },
    "main_exchange_satisfaction": {
        "retriever": (
            r._get_main_exchange_satisfaction_summary,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "marine_mart_satisfaction": {
        "retriever": (
            r._get_marine_mart_satisfaction_summary,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "mchs_satisfaction": {
        "retriever": (
            r._get_mchs_satisfaction_summary,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "google_reviews_summary": {
        "retriever": (
            r._get_google_reviews_summary,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "assessment_bullets": {
        "retriever": (
            r._get_assessment_bullets,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": True
    },
    
    # Page 2 - Email Details and Social Media
    "assessment_continued": {
        "retriever": (
            r._get_assessment_continued,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": True
    },
    "email_highlight_header": {
        "retriever": (lambda self: f"{self.get_month_name()} MCX Email Highlight"),
        "multiple_values": False
    },
    "email_highlight_campaign": {
        "retriever": (
            r._get_email_highlight_campaign,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "email_highlight_image": {
        "retriever": (
            r._get_email_highlight_image,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "email_highlight_details": {
        "retriever": (
            r._get_email_highlight_details,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": True
    },
    "email_highlight_metrics": {
        "retriever": (
            r._get_email_highlight_metrics,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "email_campaigns_table_header": {
        "retriever": (lambda self: f"{self.get_month_name()} {self.year} Email Campaigns Performance (as of {self.data_collection_date})"),
        "multiple_values": False
    },
    "email_campaigns_table": {
        "retriever": (
            r._get_email_campaigns_table,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "email_total_sends": {
        "retriever": (
            r._get_email_total_sends,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "email_avg_open_rate": {
        "retriever": (
            r._get_email_avg_open_rate,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "email_avg_click_rate": {
        "retriever": (
            r._get_email_avg_click_rate,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "email_avg_click_to_open": {
        "retriever": (
            r._get_email_avg_click_to_open,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "email_total_unsubscribes": {
        "retriever": (
            r._get_email_total_unsubscribes,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "email_avg_unsubscribe_rate": {
        "retriever": (
            r._get_email_avg_unsubscribe_rate,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "social_media_header": {
        "retriever": (lambda self: f"{self.get_month_name()} MCX Social Media Highlights"),
        "multiple_values": False
    },
    "social_media_table": {
        "retriever": (
            r._get_social_media_table,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "social_media_highlights": {
        "retriever": (
            r._get_social_media_highlights,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": True
    },
    
    # Page 3 - Customer Satisfaction Details
    "social_media_continued": {
        "retriever": (
            r._get_social_media_continued,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": True
    },
    "customer_satisfaction_header": {
        "retriever": (lambda self: f"{self.get_month_name()} MCX Customer Satisfaction Highlights"),
        "multiple_values": False
    },
    "main_exchange_comments_header": {
        "retriever": (lambda self: "Main Exchange Comments"),
        "multiple_values": False
    },
    "main_exchange_comments": {
        "retriever": (
            r._get_main_exchange_comments,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": True
    },
    "marine_mart_comments_header": {
        "retriever": (lambda self: 'Marine Mart Responses to "What item(s) was MCX not carrying that you were interested in?":'),
        "multiple_values": False
    },
    "marine_mart_comments": {
        "retriever": (
            r._get_marine_mart_comments,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": True
    },
    "main_store_satisfaction_table": {
        "retriever": (
            r._get_main_store_satisfaction_table,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "marine_mart_satisfaction_table": {
        "retriever": (
            r._get_marine_mart_satisfaction_table,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "data_collection_date": {
        "retriever": (lambda self: f"Data collected on {self.data_collection_date}"),
        "multiple_values": False
    },
    "store_type": {
        "retriever": (lambda self: "Main Store"),
        "multiple_values": False
    },
    "mchs_comments_header": {
        "retriever": (lambda self: f"{self.get_month_name()} {self.year} Marine Corps Hospitality Services (MCHS) Comments:"),
        "multiple_values": False
    },
    "mchs_comments": {
        "retriever": (
            r._get_mchs_comments,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": True
    },
    "google_reviews_header": {
        "retriever": (lambda self: f"{self.get_month_name()} {self.year} Google Reviews Comments:"),
        "multiple_values": False
    },
    "google_reviews_details": {
        "retriever": (
            r._get_google_reviews_details,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": True
    },
    "satisfaction_opportunity_note": {
        "retriever": (
            r._get_satisfaction_opportunity_note,
            (lambda self: self.month, lambda self: self.year, lambda self: self.company),
        ),
        "multiple_values": False
    },
    "enclosure_number": {
        "retriever": (lambda self, page: str(page - 1) if page > 1 else ""),
        "multiple_values": False
    },
    
    # Helper attributes
    "month": {
        "retriever": (lambda self: self.month),
        "multiple_values": False
    },
    "year": {
        "retriever": (lambda self: self.year),
        "multiple_values": False
    },
}
