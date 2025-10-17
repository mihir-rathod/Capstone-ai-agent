def _get_purpose_statement():
    return ""

def _get_executive_summary_bullets(month, year, company):
    return []

def _get_industry_benchmarks(month, year, company):
    return ""

def _get_email_blast_highlights(month, year, company):
    return []

def _get_all_campaigns_details(month, year, company):
    return []

def _get_other_initiatives(month, year, company):
    return ""

def _get_main_exchange_satisfaction_summary(month, year, company):
    return ""

def _get_marine_mart_satisfaction_summary(month, year, company):
    return ""

def _get_mchs_satisfaction_summary(month, year, company):
    return ""

def _get_google_reviews_summary(month, year, company):
    return ""

def _get_assessment_bullets(month, year, company):
    return []

def _get_assessment_continued(month, year, company):
    return []

def _get_email_highlight_campaign(month, year, company):
    return ""

def _get_email_highlight_image(month, year, company):
    return ""

def _get_email_highlight_details(month, year, company):
    return []

def _get_email_highlight_metrics(month, year, company):
    return ""

def _get_email_campaigns_table(month, year, company):
    return ""

def _get_email_total_sends(month, year, company):
    return ""

def _get_email_avg_open_rate(month, year, company):
    return ""

def _get_email_avg_click_rate(month, year, company):
    return ""

def _get_email_avg_click_to_open(month, year, company):
    return ""

def _get_email_total_unsubscribes(month, year, company):
    return ""

def _get_email_avg_unsubscribe_rate(month, year, company):
    return ""

def _get_social_media_table(month, year, company):
    return ""

def _get_social_media_highlights(month, year, company):
    return []

def _get_social_media_continued(month, year, company):
    return []

def _get_main_exchange_comments(month, year, company):
    return []

def _get_marine_mart_comments(month, year, company):
    return []

def _get_main_store_satisfaction_table(month, year, company):
    return ""

def _get_marine_mart_satisfaction_table(month, year, company):
    return ""

def _get_mchs_comments(month, year, company):
    return []

def _get_google_reviews_details(month, year, company):
    return []

def _get_satisfaction_opportunity_note(month, year, company):
    return ""

def get_mock_data():
    """
    Simulates fetching structured numerical and contextual data
    for September 2024 MCCS Marketing Analytics Report.
    """

    # 🏪 Store Information
    store_information = {
        "total_stores": 12,
        "reporting_stores": 12,
        "survey_responses": 382
    }
    
    # 💬 Customer Comments
    customer_comments = {
        "main_exchange": [
            {
                "location": "Camp Pendleton",
                "shopper_type": "Active Duty (Marine Corps) | Shopping for Essentials",
                "comment": "Great selection of items and friendly staff!"
            },
            {
                "location": "Quantico",
                "shopper_type": "Military Dependent | Shopping Sales",
                "comment": "The Anniversary sale had amazing deals."
            }
        ],
        "marine_mart": [
            {
                "location": "Camp Lejeune",
                "request": "More healthy snack options",
                "frequency": 3
            },
            {
                "location": "Twentynine Palms",
                "request": "Energy drinks variety",
                "frequency": 2
            }
        ]
    }
    
    # 📨 Email Campaign Performance Summary
    email_performance_summary = {
        "month": "September 2024",
        "total_sends": 895_773,
        "avg_open_rate": 38.08,
        "avg_click_rate": 0.65,
        "avg_click_to_open_rate": 1.70,
        "total_unsubscribes": 192,
        "avg_unsubscribe_rate": 0.02,
        "campaign_examples": [
            {
                "campaign_name": "09-13-24 Anniversary Sale",
                "sends": 59_680,
                "open_rate": 39.60,
                "click_rate": 1.24,
                "click_to_open": 3.14,
                "unsubscribes": 8,
                "unsubscribe_rate": 0.02
            },
            {
                "campaign_name": "Quantico Firearms",
                "sends": 11_459,
                "open_rate": 44.60,
                "click_rate": 0.52,
                "click_to_open": 1.16,
                "unsubscribes": 1,
                "unsubscribe_rate": 0.01
            },
            {
                "campaign_name": "09-04-24 Anniversary Sale + Fall Glam",
                "sends": 59_625,
                "open_rate": 38.38,
                "click_rate": 1.42,
                "click_to_open": 3.69,
                "unsubscribes": 9,
                "unsubscribe_rate": 0.02
            }
        ]
    }

    # 🏬 Customer Satisfaction by Location
    satisfaction_data = {
        "month": "September 2024",
        "locations": [
            {"name": "Camp Pendleton", "sept_satisfied": 90, "aug_satisfied": 92, "change": -2},
            {"name": "Camp Lejeune", "sept_satisfied": 94, "aug_satisfied": 96, "change": -2},
            {"name": "Cherry Point", "sept_satisfied": 96, "aug_satisfied": 96, "change": 0},
            {"name": "Henderson Hall", "sept_satisfied": 90, "aug_satisfied": 96, "change": -6},
            {"name": "Iwakuni", "sept_satisfied": 84, "aug_satisfied": 84, "change": 0},
            {"name": "Kbay", "sept_satisfied": 94, "aug_satisfied": 94, "change": 0},
            {"name": "Miramar", "sept_satisfied": 94, "aug_satisfied": 96, "change": -2},
            {"name": "Quantico", "sept_satisfied": 82, "aug_satisfied": 92, "change": -10},
            {"name": "San Diego", "sept_satisfied": 96, "aug_satisfied": 98, "change": -2},
            {"name": "South Carolina", "sept_satisfied": 88, "aug_satisfied": 100, "change": -12},
            {"name": "Twentynine Palms", "sept_satisfied": 96, "aug_satisfied": 94, "change": 2},
            {"name": "Yuma", "sept_satisfied": 86, "aug_satisfied": 96, "change": -10}
        ]
    }

    # 🎯 Combine all into single context
    mock_context = {
        "report_title": "MCCS Marketing Analytics and Customer Satisfaction Report",
        "report_month": "September 2024",
        "email_performance": email_performance_summary,
        "customer_satisfaction": satisfaction_data,
        "notes": (
            "The data combines marketing analytics (email campaign KPIs) "
            "and customer satisfaction feedback from various locations. "
            "The goal is to generate insights, trends, and improvement recommendations."
        )
    }

    return mock_context
