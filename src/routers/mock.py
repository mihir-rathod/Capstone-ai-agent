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
    Mock endpoint that returns MCCS Marketing Analytics Report matching the exact schema structure.
    Returns data organized by pages matching the DocumentSchema.
    
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
        
        # Metadata
        "report_metadata": {
            "report_type": "marketing_analytics",
            "month": month,
            "year": year,
            "total_pages": 3
        },
        
        # PAGE 1 - Cover Page with Executive Summary and Findings
        "page_1": {
            "page_number": 1,
            "as_of_date": "As of November, 27th, 2024",
            "report_title": f"{month} {year} MCCS Marketing Analytics Assessment",
            "purpose_statement": "To support leaders' and subject matter experts' in their decision-making process while aiming to generate smart revenue, increase brand affinity, and reduce stress on Marines and their families.",
            
            # Executive Summary
            "exec_summary_period": "Period Covered: 01-Sept-24 - 31-Sept-24",
            "exec_summary_bullets": [
                "The Labor Day Promotion assisted in a 6.8% increase in total sales to LY, with a majority of digitally available Labor Day coupons being scanned through mobile (383 mobile scans vs. 172 email scans).\n  - The coupon was also available printed in-store, which received 4,230 total scans.",
                "September Email Open Rate (OPR) was 38.08%, up nearly 6% to last month. Click through Rate (CTR) was 0.65%, up only 0.20% to last month.",
                "Promotions with time-sensitivity, such as the 72 Hour Anniversary Deals and the Labor Day Promotions, boosted digital engagement and drove footsteps into the door.",
                "Opportunity to ensure promotional strategies are executed clearly in-store and store associates are informed of promotions within their department. (see Enclosure 2 for CSAT comments)"
            ],
            
            # Findings - Digital Performance
            "findings_digital_header": "Findings – Review of digital performance, advertising campaigns, and sales:",
            "industry_benchmarks": [
                "The industry standard open rate (OPR) for emails in retail is 15-25% - MCX average for September was 38.08% (32.61% in August, 30.10% in July)",
                "The industry standard click through rate (CTR) is 1-5% - MCX average for September was 0.65% (0.45% in August, 0.53% in July)"
            ],
            "email_blast_highlights": [
                {
                    "title": "09-13 - \"For a limited time only – our 72 Hour Anniversary deals start today!\"",
                    "opr": "39.60%",
                    "ctr": "1.24%"
                },
                {
                    "title": "Quantico Firearms – \"Attention NOVA MCX Customers!\"",
                    "opr": "44.60%",
                    "ctr": "0.52%"
                }
            ],
            "campaigns_details": [
                {
                    "title": "Labor Day (3 Emails w/ Coupons) (28-Aug – 02-Sept TY; 23-Aug – 5-Sept LY):",
                    "details": [
                        "Average OPR: 34.0% | Average CTR: 0.56% | Coupon Scans – Email: 172, Mobile: 383, In-Store Print: 4,230",
                        "Total Sales: $12.6M TY; $11.8M LY | Average Daily Sales 2024: $2.52M; Average Daily Sales 2023: $60K",
                        "2024 Promotion through email with coupons. 2022 and 2023 promotion through print and coupons"
                    ]
                },
                {
                    "title": "Anniversary (4-Sept – 17-Sept TY; 6-Sept – 19-Sept LY):",
                    "details": [
                        "Advertised Sales: $3.30M TY (22.28% of Participating MS); $3.27M LY (24.40% of Participating MS)",
                        "EMAG page views: 79.4K TY | Main Exchange Total Sales: $15.7M TY / 15.4M LY; Trans: 273K TY / 272K LY"
                    ]
                },
                {
                    "title": "Glamorama (4-Sept – 17-Sept TY; 6-Sept– 19-Sept LY):",
                    "details": [
                        "Advertised Sales: $405K TY (3.20% of Participating MS TY), $422K (3.19% of Participating MS LY)",
                        "EMAG page views: 43.2K TY | Main Exchange Total Sales: $15.7M TY / 15.4M LY; Trans: 273K TY / 272K LY"
                    ]
                },
                {
                    "title": "Fall Sight & Sound (18-Sept – 1-Oct TY; 20-Sept– 3-Oct LY):",
                    "details": [
                        "Advertised Sales: $466K TY (4.22% of Participating MS TY), $591K (5.08% of Participating MS LY)",
                        "EMAG page views: 19.3K TY | Main Exchange Total Sales: $13.7M TY / 13.9M LY; Trans: 246K TY / 262K LY"
                    ]
                },
                {
                    "title": "Sept Designer/Fall Trend (18-Sept – 1-Oct TY; 20-Sept– 3-Oct LY):",
                    "details": [
                        "Advertised Sales: $405K TY (4.22% of Participating MS TY), $961K (5.08% of Participating MS LY)",
                        "EMAG page views: 16.4K TY | Main Exchange Total Sales: $13.3M TY / 13.9M LY; Trans: 246K TY / 262K LY"
                    ]
                }
            ],
            "other_initiatives": "Other Initiatives: Baby & Me: 19 coupons used | Hallmark: 14 coupons used | Case Wine 10%: 35 coupons used",
            
            # Findings - CSAT and Reviews
            "findings_csat_header": "Findings – Review of Main Exchanges, Marine Marts, and MCHS CSAT Surveys and Google Reviews:",
            "main_exchange_satisfaction": "92% of 382 Main Exchange survey respondents reported overall satisfaction with their experience.\n  - 15.7% said they were shopping sales that were advertised, indicating MCX advertisements are successfully driving footsteps in the door. 45.5% were picking up needed supplies.",
            "marine_mart_satisfaction": "96% of 520 Marine Mart survey respondents reported overall satisfaction with their experience.\n  - 42 customers were unable to purchase everything they intended. 50% of these customers said it was because MCX did not carry the item they were looking for. (See Enclosure 2 for sought after items comments)",
            "mchs_satisfaction": "There were 392 MCHS survey respondents, with an average CSAT score of 91.8.\n  - In September 2023, there were 603 survey respondents with an average CSAT score of 88.1\n  - 40.8% of respondents were TAD/TDY. 32.1% of respondents were traveling for leisure.\n  - Respondents traveling for leisure averaged a CSAT score of 90.1. Respondents TAD/TDY averaged 87.6.",
            "google_reviews_summary": "All time Google Reviews have an average rating of 4.4 out of 5 and there has been a total of 10,637 reviews.",
            
            # Assessment
            "assessment_bullets": [
                "To boost overall CTR, Marketing will continue to improve clarity, attractiveness, and relatability of the call-to-action's on emails and social media.",
                "The Labor Day Promotion generated a 6.8% increase in total sales compared to the previous year, with a majority of digitally available coupons being scanned through mobile (383 mobile scans vs. 172 email scans)."
            ]
        },
        
        # PAGE 2 (Enclosure 1) - Email and Social Media Details
        "page_2": {
            "page_number": 2,
            "enclosure_number": "Enclosure (1)",
            "as_of_date": "As of November, 27th, 2024",
            
            # Assessment Continued
            "assessment_continued": [
                "Marketing will continue to promote exclusive offers which will highlight time-sensitive deals to create urgency and increase CTR, like we saw with the 72 Hour Anniversary Deals and the Labor Day Promotion.",
                "Marketing will consider a mobile-first strategy in which mobile-friendly promotions will be prioritized and integrated into email campaigns, social media, and in-store experiences to further drive conversion.",
                "Opportunity to ensure promotional strategies are executed clearly in-store and store associates are informed of promotions within department. Marketing will partner with Business Operations to identify ways to support."
            ],
            
            # Email Highlight
            "email_highlight_header": "September MCX Email Highlight",
            "email_highlight_campaign": "09-13 – \"For a limited time only – our 72 Hour Anniversary deals start today!\" 39.60% OPR 1.24% CTR",
            "email_highlight_image": "[Email preview image showing Anniversary Sale with scratch & save coupons, Glam & Pamper beauty products, and MCX branding with 'IT MATTERS WHERE YOU SHOP' tagline]",
            "email_highlight_details": [
                "This email blast was sent to 59,680 subscribers and had one of the highest CTRs for September emails.",
                "The portion of the email including the click through to the MCX Offers page, via a clickable button titled \"Click to View Ads\" received the most clicks accounting for 72.1% (473) of the total clicks.",
                "Advertisements in the email body included: 25% off Luggage, 25% off American Eagle, RVCA, Volcom, Old Navy, and O'Neill, 25% off all Gourmet Candies, 20% off Keurig products, and 2/$6 Dude Wipes.\n  - Monthly Hardline sales were -4.3% to LY | Monthly Softlines sales were -0.6% to LY.",
                "Supporting 72 Hour Specials Mobile Message sent to 15,823 subscribers with 725 link clicks (4.58% CTR)"
            ],
            "email_highlight_metrics": {
                "subscribers": 59680,
                "ctr": "1.24%",
                "top_click_percentage": "72.1%",
                "total_clicks": 473
            },
            
            # Email Campaigns Table
            "email_campaigns_table_header": "September 2024 Email Campaigns Performance (as of October 23rd, 2024)",
            "email_campaigns_table": [
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
                    "email_content_name": "Quantico Firearms",
                    "email_subject": "Attention NOVA MCX Customers!",
                    "sends": 11459,
                    "open_rate": "44.60%",
                    "click_rate": "0.52%",
                    "click_to_open_rate": "1.16%",
                    "unique_unsubscribes": 1,
                    "unsubscribe_rate": "0.01%"
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
                },
                {
                    "email_content_name": "09-13-24 Anniversary Sale 72 Hour Specials",
                    "email_subject": "For a limited time only - our 72 Hour Anniversary deals start today!",
                    "sends": 59680,
                    "open_rate": "39.60%",
                    "click_rate": "1.24%",
                    "click_to_open_rate": "3.14%",
                    "unique_unsubscribes": 8,
                    "unsubscribe_rate": "0.02%"
                }
            ],
            "email_total_sends": 895773,
            "email_avg_open_rate": "38.08%",
            "email_avg_click_rate": "0.65%",
            "email_avg_click_to_open": "1.70%",
            "email_total_unsubscribes": 192,
            "email_avg_unsubscribe_rate": "0.02%",
            
            # Social Media
            "social_media_header": "September MCX Social Media Highlights",
            "social_media_table": [
                {
                    "published_date": "Sep 12, 2024, 11:08 AM",
                    "post_content": "MCXRG - Get ready for a 72hr party like with Deals of the Bae. Run don't walk.",
                    "total_engagements": 123,
                    "post_likes_reactions": 101,
                    "post_comments": 2,
                    "post_shares": 20,
                    "post_reach": 1226
                },
                {
                    "published_date": "Sep 04, 2024, 10:00 AM",
                    "post_content": "Marine Corps Exchange - We've got everything needed for your 🏝️ dive or lobster 🦞 ooh-rah!",
                    "total_engagements": 92,
                    "post_likes_reactions": 31,
                    "post_comments": 20,
                    "post_shares": 1,
                    "post_reach": 1486
                },
                {
                    "published_date": "Sep 03, 2024, 04:00 PM",
                    "post_content": "Marine Corps Exchange - Bath and sunscreens--we've got an exciting contest for you! 🎊 Watch the vid!",
                    "total_engagements": 41,
                    "post_likes_reactions": 17,
                    "post_comments": 23,
                    "post_shares": 1,
                    "post_reach": 866
                }
            ],
            "social_media_highlights": [
                "The September 12th post on Instagram was video content created by Buyers, Business Operations Directorate, Business & Support Services Division (MR), to drive customers into the store for Deals of the Day. The video featured various products and their prices from a shopper's point of view, similar to another post created from March 11th, 2024, that also had higher than average engagement.\n(continued on second page)"
            ]
        },
        
        # PAGE 3 (Enclosure 2) - Customer Satisfaction Details
        "page_3": {
            "page_number": 3,
            "enclosure_number": "Enclosure (2)",
            "as_of_date": "As of November, 27th, 2024",
            
            # Social Media Continued
            "social_media_continued": [
                "Content creation that involves the customer point of view, often showing a customer with a shopping cart that they load with the advertised deals, is tried and true content used by competitors as well – such as Target.",
                "September 4th and 5th posts both were related to contests for eligible patrons who follow our social media. Historically, contest promotion through social media generates higher than average engagement, and these posts are no exception.",
                "So What: Marketing to continue creation of content that resonates with followers, including video content featuring advertised deals and sharing events that happen at specific installations, to drive social media engagement, which drives brand affinity and encourages footsteps in the door. At present, available resources do not support creation of quality video content required."
            ],
            
            # Customer Satisfaction
            "customer_satisfaction_header": "September MCX Customer Satisfaction Highlights",
            
            # Main Exchange Comments
            "main_exchange_comments_header": "Main Exchange Comments",
            "main_exchange_comments": [
                {
                    "location": "Camp Pendleton",
                    "shopper_type": "DOD Civilian | Shopping for a Gift",
                    "comment": "\"I noticed there was \"glam event\" when I entered the store. There were price signs and final sale signs around the beauty depart(ment) but no signs indicating that if you spent $50 you would receive a promotion item… there was a sign that showed a free gift bag but there was no signage indicating what needed to be spent in order to receive it. Today when I went back I saw it and asked the woman standing there and she was very accommodating and gave me the free gift… The only reason I found out about the promotion was because I came back today…\""
                },
                {
                    "location": "Camp Lejeune",
                    "shopper_type": "Active Duty (Marine Corps) | Shopping Sales that were Advertised",
                    "comment": "\"The sales and scratch-off coupons are such a great bonus to the tax-free shopping! I am looking forward to shopping here again.\""
                }
            ],
            
            # Marine Mart Comments
            "marine_mart_comments_header": "Marine Mart Responses to \"What item(s) was MCX not carrying that you were interested in?\":",
            "marine_mart_comments": [
                {
                    "location": "Barstow - 12300",
                    "shopper_type": "Contractor | Shopping Frequency: 5-6 times a week",
                    "comment": "\"The freezers at this location have been out for some time now we haven't had any frozen foods available for quite some time. The staff here is very friendly, but they still have no information as to when. The higher-ups above them are going to get these freezers fixed for us\"."
                },
                {
                    "location": "Quantico - 2205",
                    "shopper_type": "Active Duty (Marine Corps) | Shopping Frequency: every day",
                    "comment": "\"We need medicine in the store… they said the manager won't authorize medicine, but we can't leave during the cycle and we get aches and pains.\""
                }
            ],
            
            # Satisfaction Tables
            "main_store_satisfaction_table": [
                {"location": "Camp Pendleton", "sept_satisfied": "90%", "aug_satisfied": "92%", "change": "-2%"},
                {"location": "Camp Lejeune", "sept_satisfied": "94%", "aug_satisfied": "96%", "change": "-2%"},
                {"location": "Cherry Point", "sept_satisfied": "96%", "aug_satisfied": "96%", "change": "0%"},
                {"location": "Henderson Hall", "sept_satisfied": "90%", "aug_satisfied": "96%", "change": "-6%"},
                {"location": "Iwakuni", "sept_satisfied": "84%", "aug_satisfied": "84%", "change": "0%"},
                {"location": "Kbay", "sept_satisfied": "94%", "aug_satisfied": "94%", "change": "0%"},
                {"location": "Miramar", "sept_satisfied": "94%", "aug_satisfied": "96%", "change": "-2%"},
                {"location": "Quantico", "sept_satisfied": "82%", "aug_satisfied": "92%", "change": "-10%"},
                {"location": "San Diego", "sept_satisfied": "96%", "aug_satisfied": "98%", "change": "-2%"},
                {"location": "South Carolina", "sept_satisfied": "88%", "aug_satisfied": "100%", "change": "-12%"},
                {"location": "Twentynine Palms", "sept_satisfied": "96%", "aug_satisfied": "94%", "change": "2%"},
                {"location": "Yuma", "sept_satisfied": "86%", "aug_satisfied": "96%", "change": "-10%"}
            ],
            "marine_mart_satisfaction_table": [
                {"location": "Camp Elmore", "sept_satisfied": "86%", "aug_satisfied": "100%", "change": "-14%"},
                {"location": "Camp Hansen", "sept_satisfied": "96%", "aug_satisfied": "98%", "change": "-2%"},
                {"location": "Camp Lejeune", "sept_satisfied": "92%", "aug_satisfied": "90%", "change": "2%"},
                {"location": "Camp Pendleton", "sept_satisfied": "92%", "aug_satisfied": "94%", "change": "-2%"},
                {"location": "Henderson Hall", "sept_satisfied": "96%", "aug_satisfied": "100%", "change": "-4%"},
                {"location": "Iwakuni", "sept_satisfied": "100%", "aug_satisfied": "-", "change": "0%"},
                {"location": "Kbay", "sept_satisfied": "98%", "aug_satisfied": "98%", "change": "0%"},
                {"location": "Miramar", "sept_satisfied": "98%", "aug_satisfied": "98%", "change": "0%"},
                {"location": "Quantico", "sept_satisfied": "94%", "aug_satisfied": "96%", "change": "-2%"},
                {"location": "San Diego", "sept_satisfied": "98%", "aug_satisfied": "98%", "change": "0%"},
                {"location": "South Carolina", "sept_satisfied": "100%", "aug_satisfied": "100%", "change": "0%"},
                {"location": "Twentynine Palms", "sept_satisfied": "96%", "aug_satisfied": "100%", "change": "-4%"},
                {"location": "Yuma", "sept_satisfied": "100%", "aug_satisfied": "100%", "change": "0%"}
            ],
            "data_collection_date": "Data collected on October 23rd, 2024",
            "store_type": "Main Store",
            
            # MCHS Comments
            "mchs_comments_header": "September 2024 Marine Corps Hospitality Services (MCHS) Comments:",
            "mchs_comments": [
                {
                    "location": "Miramar",
                    "reason": "Reason for Stay - Other:",
                    "comment": "\"You need to update information TV channel, info [is] wrong. Restaurants on base [is] incorrect.\""
                },
                {
                    "location": "Beaufort",
                    "reason": "Reason for Stay - TAD/TDY:",
                    "comment": "\"Everyone was extremely friendly and courteous, no issues with the booking or getting the required documentation for my stay.\""
                }
            ],
            
            # Google Reviews
            "google_reviews_header": "September 2024 Google Reviews Comments:",
            "google_reviews_details": [
                {
                    "intro": "Main Exchange Google Reviews highlight various wins and opportunities to enhance in-store experience that are not always captured by the CSAT surveys. This may be due to the fact that a customer is required to make a purchase to complete the CSAT survey, whereas any customer who wishes to leave a Google Review may do so."
                },
                {
                    "location": "Quantico Main Exchange",
                    "rating": "overall 4.5 out of 5 (1,222 total reviews)",
                    "comment": "\"Store in disarray right now for renovations.\""
                },
                {
                    "location": "Twentynine Palms Main Exchange",
                    "rating": "overall 4.4 out of 5 (1,242 total reviews)",
                    "comment": "\"...The inclusion of Starbucks, Popeyes, and a local BBQ joint make it exceptional. I wish they had more niche items or tools, as it is very limited.\""
                },
                {
                    "location": "KBay Main Exchange",
                    "rating": "overall 4.4 out of 5 (633 total reviews)",
                    "comment": "\"Great prices and good selection on clothes, housewares, toys..\""
                }
            ],
            
            "satisfaction_opportunity_note": "* Opportunity to increase satisfaction score by ensuring advertisements and information at locations is up to date and readily available *"
        }
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MCCS Marketing Analytics Mock API",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/report-structure")
async def get_report_structure():
    """
    Returns the structure documentation matching the DocumentSchema
    """
    return {
        "report_type": "MCCS Marketing Analytics Assessment",
        "total_pages": 3,
        "schema_structure": {
            "page_1": {
                "page_number": 1,
                "tags": [
                    "as_of_date", "report_title", "purpose_statement",
                    "exec_summary_period", "exec_summary_bullets",
                    "findings_digital_header", "industry_benchmarks", "email_blast_highlights",
                    "campaigns_details", "other_initiatives",
                    "findings_csat_header", "main_exchange_satisfaction", "marine_mart_satisfaction",
                    "mchs_satisfaction", "google_reviews_summary", "assessment_bullets"
                ]
            },
            "page_2": {
                "page_number": 2,
                "tags": [
                    "as_of_date", "assessment_continued",
                    "email_highlight_header", "email_highlight_campaign", "email_highlight_image",
                    "email_highlight_details", "email_highlight_metrics",
                    "email_campaigns_table_header", "email_campaigns_table",
                    "email_total_sends", "email_avg_open_rate", "email_avg_click_rate",
                    "email_avg_click_to_open", "email_total_unsubscribes", "email_avg_unsubscribe_rate",
                    "social_media_header", "social_media_table", "social_media_highlights",
                    "enclosure_number"
                ]
            },
            "page_3": {
                "page_number": 3,
                "tags": [
                    "as_of_date", "social_media_continued",
                    "customer_satisfaction_header",
                    "main_exchange_comments_header", "main_exchange_comments",
                    "marine_mart_comments_header", "marine_mart_comments",
                    "main_store_satisfaction_table", "marine_mart_satisfaction_table",
                    "data_collection_date", "store_type",
                    "mchs_comments_header", "mchs_comments",
                    "google_reviews_header", "google_reviews_details",
                    "satisfaction_opportunity_note", "enclosure_number"
                ]
            }
        },
        "note": "All tag IDs match the marketing_report_schema exactly"
    }