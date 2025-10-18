from pydantic import BaseModel, Field
from typing import List, Optional

class ContentItem(BaseModel):
    source: str
    title: str
    data: str

class Tag(BaseModel):
    id: str
    content: List[ContentItem] = []

class Page(BaseModel):
    page_number: int
    tags: List[Tag]

class DocumentSchema(BaseModel):
    pages: List[Page]

# Helper function to create a content item
def create_content(data: str, title: str = "", source: str = "system") -> List[ContentItem]:
    if not data:
        return []
    return [ContentItem(source=source, title=title, data=data)]

from ..services import retrievers as r

marketing_report_schema = DocumentSchema(
    pages=[
        # PAGE 1: Cover Page with Executive Summary and Findings
        Page(
            page_number=1,
            tags=[
                Tag(id="as_of_date", content=[]),
                Tag(id="report_title", content=[]),
                Tag(id="purpose_statement", content=create_content(
                    "To support leaders' and subject matter experts' in their decision-making process while aiming to generate smart revenue, increase brand affinity, and reduce stress on Marines and their families.",
                    "Purpose Statement"
                )),
                
                # Executive Summary Section
                Tag(id="exec_summary_period", content=[]),
                Tag(id="exec_summary_bullets", content=[]),
                
                # Findings - Digital Performance Section
                Tag(id="findings_digital_header", content=[]),
                Tag(id="industry_benchmarks", content=[]),
                Tag(id="email_blast_highlights", content=[]),
                Tag(id="campaigns_details", content=[]),
                Tag(id="other_initiatives", content=[]),
                
                # Findings - CSAT and Reviews Section
                Tag(id="findings_csat_header", content=[]),
                Tag(id="main_exchange_satisfaction", content=[]),
                Tag(id="marine_mart_satisfaction", content=[]),
                Tag(id="mchs_satisfaction", content=[]),
                Tag(id="google_reviews_summary", content=[]),
                
                # Assessment Section (continued on page 2)
                Tag(id="assessment_bullets", content=[]),
            ],
        ),
        
        # PAGE 2 (Enclosure 1): Email and Social Media Details
        Page(
            page_number=2,
            tags=[
                Tag(id="assessment_continued", content=[]),
                
                # Email Highlight Section
                Tag(id="email_highlight_header", content=[]),
                Tag(id="email_highlight_campaign", content=[]),
                Tag(id="email_highlight_image", content=[]),
                Tag(id="email_highlight_details", content=[]),
                Tag(id="email_highlight_metrics", content=[]),
                
                # Email Campaigns Performance Table
                Tag(id="email_campaigns_table_header", content=[]),
                Tag(id="email_campaigns_table", content=[]),
                Tag(id="email_total_sends", content=[]),
                Tag(id="email_avg_open_rate", content=[]),
                Tag(id="email_avg_click_rate", content=[]),
                Tag(id="email_avg_click_to_open", content=[]),
                Tag(id="email_total_unsubscribes", content=[]),
                Tag(id="email_avg_unsubscribe_rate", content=[]),
                
                # Social Media Highlights Section
                Tag(id="social_media_header", content=[]),
                Tag(id="social_media_table", content=[]),
                Tag(id="social_media_highlights", content=[]),
                
                Tag(id="enclosure_number", content=[]),
            ],
        ),
        
        # PAGE 3 (Enclosure 2): Customer Satisfaction Details
        Page(
            page_number=3,
            tags=[
                Tag(id="as_of_date", title="As Of Date", content=[]),
                Tag(id="social_media_continued", title="Social Media Content Continued", content=[]),
                
                # Customer Satisfaction Highlights Section
                Tag(id="customer_satisfaction_header", title="Customer Satisfaction Header", content=[]),
                
                # Main Exchange Comments
                Tag(id="main_exchange_comments_header", title="Main Exchange Comments Header", content=[]),
                Tag(id="main_exchange_comments", title="Main Exchange Comments", content=[]),
                
                # Marine Mart Comments
                Tag(id="marine_mart_comments_header", title="Marine Mart Comments Header", content=[]),
                Tag(id="marine_mart_comments", title="Marine Mart Comments", content=[]),
                
                # Satisfaction Tables
                Tag(id="main_store_satisfaction_table", title="Main Store Satisfaction Table", content=[]),
                Tag(id="marine_mart_satisfaction_table", title="Marine Mart Satisfaction Table", content=[]),
                Tag(id="data_collection_date", title="Data Collection Date", content=[]),
                Tag(id="store_type", title="Store Type", content=[]),
                
                # MCHS Comments
                Tag(id="mchs_comments_header", title="MCHS Comments Header", content=[]),
                Tag(id="mchs_comments", title="MCHS Comments", content=[]),
                
                # Google Reviews
                Tag(id="google_reviews_header", title="Google Reviews Header", content=[]),
                Tag(id="google_reviews_details", title="Google Reviews Details", content=[]),
                
                Tag(id="satisfaction_opportunity_note", title="Satisfaction Opportunity Note", content=[]),
                Tag(id="enclosure_number", title="Enclosure Number", content=[]),
            ],
        ),
    ],
)

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
