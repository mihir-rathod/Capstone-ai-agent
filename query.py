"""
Marketing Analytics Queries for MCCS Data Analysis

This file contains SQL queries for comprehensive analysis of:
1. Retail data trends and correlations
2. Email marketing performance
3. Social media engagement and performance

All queries are parameterized and include trend analysis capabilities.
"""

# =============================================================================
# RETAIL DATA ANALYSIS QUERIES
# =============================================================================

# 1. Monthly Sales Trends
RETAIL_MONTHLY_SALES = """
SELECT
    DATE_FORMAT(sale_date, '%Y-%m') as month,
    COUNT(DISTINCT sale_date) as days_with_sales,
    COUNT(*) as total_transactions,
    SUM(extension_amount) as total_sales,
    AVG(extension_amount) as avg_transaction_value,
    SUM(qty) as total_quantity_sold,
    COUNT(DISTINCT item_id) as unique_items_sold
FROM retail_data
WHERE sale_date BETWEEN %s AND %s
GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
ORDER BY month;
"""

# 2. Period-over-Period Sales Comparison (45 days, etc.)
RETAIL_PERIOD_COMPARISON = """
WITH current_period AS (
    SELECT
        SUM(extension_amount) as current_sales,
        COUNT(*) as current_transactions,
        AVG(extension_amount) as current_avg_transaction,
        SUM(qty) as current_quantity
    FROM retail_data
    WHERE sale_date BETWEEN %s AND %s
),
previous_period AS (
    SELECT
        SUM(extension_amount) as previous_sales,
        COUNT(*) as previous_transactions,
        AVG(extension_amount) as previous_avg_transaction,
        SUM(qty) as previous_quantity
    FROM retail_data
    WHERE sale_date BETWEEN DATE_SUB(%s, INTERVAL (DATEDIFF(%s, %s) + 1) DAY) AND DATE_SUB(%s, INTERVAL 1 DAY)
)
SELECT
    cp.current_sales,
    pp.previous_sales,
    ROUND(((cp.current_sales - pp.previous_sales) / pp.previous_sales) * 100, 2) as sales_growth_pct,
    cp.current_transactions,
    pp.previous_transactions,
    ROUND(((cp.current_transactions - pp.previous_transactions) / pp.previous_transactions) * 100, 2) as transaction_growth_pct,
    cp.current_avg_transaction,
    pp.previous_avg_transaction,
    ROUND(((cp.current_avg_transaction - pp.previous_avg_transaction) / pp.previous_avg_transaction) * 100, 2) as avg_transaction_growth_pct
FROM current_period cp, previous_period pp;
"""

# 3. Top 3 Sales Trends by Category
RETAIL_TOP_TRENDS = """
WITH monthly_sales AS (
    SELECT
        DATE_FORMAT(sale_date, '%Y-%m') as month,
        store_format,
        command_name,
        SUM(extension_amount) as monthly_sales,
        SUM(qty) as monthly_quantity,
        COUNT(*) as monthly_transactions
    FROM retail_data
    WHERE sale_date BETWEEN %s AND %s
    GROUP BY DATE_FORMAT(sale_date, '%Y-%m'), store_format, command_name
),
sales_trends AS (
    SELECT
        store_format,
        command_name,
        AVG(monthly_sales) as avg_monthly_sales,
        STDDEV(monthly_sales) as sales_volatility,
        COUNT(*) as months_active,
        (MAX(monthly_sales) - MIN(monthly_sales)) / AVG(monthly_sales) as sales_variation
    FROM monthly_sales
    GROUP BY store_format, command_name
    HAVING COUNT(*) >= 2
)
SELECT
    store_format,
    command_name,
    avg_monthly_sales,
    sales_volatility,
    sales_variation,
    CASE
        WHEN sales_variation > 0.5 THEN 'High Variation'
        WHEN sales_variation > 0.2 THEN 'Moderate Variation'
        ELSE 'Stable'
    END as trend_stability
FROM sales_trends
ORDER BY avg_monthly_sales DESC
LIMIT 3;
"""

# 4. Retail Sales Correlation with Email/Social Media
RETAIL_CORRELATION_ANALYSIS = """
WITH daily_metrics AS (
    SELECT
        rd.sale_date,
        SUM(rd.extension_amount) as daily_sales,
        SUM(rd.qty) as daily_quantity,
        COUNT(*) as daily_transactions,

        -- Email metrics (simplified - would need proper date matching)
        COALESCE(AVG(eed.open_rate), 0) as avg_email_open_rate,
        COALESCE(SUM(eed.unique_opens), 0) as total_email_opens,

        -- Social media metrics
        COALESCE(SUM(smed.total_engagements), 0) as daily_social_engagements,
        COALESCE(SUM(smed.posts_published), 0) as daily_social_posts

    FROM retail_data rd
    LEFT JOIN email_engagement_details eed ON DATE(eed.send_date) = rd.sale_date
    LEFT JOIN social_media_engagement_daily smed ON smed.date = rd.sale_date
    WHERE rd.sale_date BETWEEN %s AND %s
    GROUP BY rd.sale_date
)
SELECT
    CORR(daily_sales, avg_email_open_rate) as sales_email_open_correlation,
    CORR(daily_sales, total_email_opens) as sales_email_opens_correlation,
    CORR(daily_sales, daily_social_engagements) as sales_social_engagement_correlation,
    CORR(daily_sales, daily_social_posts) as sales_social_posts_correlation,
    AVG(daily_sales) as avg_daily_sales,
    AVG(avg_email_open_rate) as avg_email_open_rate,
    AVG(daily_social_engagements) as avg_social_engagements
FROM daily_metrics
WHERE daily_sales > 0;
"""

# 5. Store Performance Analysis
RETAIL_STORE_PERFORMANCE = """
SELECT
    site_name,
    store_format,
    command_name,
    COUNT(DISTINCT sale_date) as active_days,
    SUM(extension_amount) as total_sales,
    AVG(extension_amount) as avg_daily_sales,
    SUM(qty) as total_quantity,
    COUNT(*) as total_transactions,
    COUNT(DISTINCT item_id) as unique_items_sold,
    MAX(sale_date) as last_sale_date
FROM retail_data
WHERE sale_date BETWEEN %s AND %s
GROUP BY site_name, store_format, command_name
ORDER BY total_sales DESC;
"""

# =============================================================================
# EMAIL MARKETING ANALYSIS QUERIES
# =============================================================================

# 1. Email Campaign Performance Overview
EMAIL_CAMPAIGN_OVERVIEW = """
SELECT
    ecp.email_content_name,
    ecp.email_subject,
    ecp.sends,
    ecp.open_rate,
    ecp.click_to_open_rate,
    eed.unique_opens,
    eed.unique_clicks,
    eed.click_rate,
    eed.unsubscribe_rate,
    eed.send_date
FROM email_campaign_performance ecp
LEFT JOIN email_engagement_details eed ON ecp.email_content_name = eed.message_name
WHERE eed.send_date BETWEEN %s AND %s
ORDER BY ecp.sends DESC, ecp.open_rate DESC;
"""

# 2. Email Performance Trends Over Time
EMAIL_PERFORMANCE_TRENDS = """
SELECT
    DATE_FORMAT(send_date, '%Y-%m') as month,
    COUNT(*) as campaigns_sent,
    SUM(sends) as total_sends,
    AVG(open_rate) as avg_open_rate,
    AVG(click_rate) as avg_click_rate,
    AVG(click_to_open_rate) as avg_click_to_open_rate,
    SUM(unique_opens) as total_unique_opens,
    SUM(unique_clicks) as total_unique_clicks,
    AVG(unsubscribe_rate) as avg_unsubscribe_rate
FROM email_engagement_details
WHERE send_date BETWEEN %s AND %s
GROUP BY DATE_FORMAT(send_date, '%Y-%m')
ORDER BY month;
"""

# 3. Email Delivery Performance
EMAIL_DELIVERY_ANALYSIS = """
SELECT
    edd.email_content_name,
    edd.send_date,
    edd.sends,
    edd.deliveries,
    edd.bounces,
    edd.bounce_rate,
    ROUND((edd.deliveries / edd.sends) * 100, 2) as delivery_rate,
    eed.open_rate,
    eed.click_rate
FROM email_delivery_details edd
LEFT JOIN email_engagement_details eed ON edd.email_content_name = eed.message_name
    AND edd.send_date = eed.send_date
WHERE edd.send_date BETWEEN %s AND %s
ORDER BY edd.send_date DESC, edd.sends DESC;
"""

# 4. Top Performing Email Campaigns
EMAIL_TOP_PERFORMERS = """
WITH campaign_metrics AS (
    SELECT
        message_name,
        campaign,
        AVG(open_rate) as avg_open_rate,
        AVG(click_rate) as avg_click_rate,
        AVG(click_to_open_rate) as avg_click_to_open_rate,
        SUM(unique_opens) as total_opens,
        SUM(unique_clicks) as total_clicks,
        SUM(sends) as total_sends,
        COUNT(*) as campaign_instances
    FROM email_engagement_details
    WHERE send_date BETWEEN %s AND %s
    GROUP BY message_name, campaign
)
SELECT
    message_name,
    campaign,
    avg_open_rate,
    avg_click_rate,
    avg_click_to_open_rate,
    total_opens,
    total_clicks,
    total_sends,
    ROUND((total_opens / total_sends) * 100, 2) as actual_open_rate,
    ROUND((total_clicks / total_opens) * 100, 2) as actual_click_to_open_rate
FROM campaign_metrics
ORDER BY avg_open_rate DESC
LIMIT 10;
"""

# 5. Email Engagement Rate Trends
EMAIL_ENGAGEMENT_TRENDS = """
WITH monthly_engagement AS (
    SELECT
        DATE_FORMAT(send_date, '%Y-%m') as month,
        AVG(open_rate) as avg_open_rate,
        AVG(click_rate) as avg_click_rate,
        AVG(click_to_open_rate) as avg_click_to_open_rate,
        AVG(unsubscribe_rate) as avg_unsubscribe_rate
    FROM email_engagement_details
    WHERE send_date BETWEEN %s AND %s
    GROUP BY DATE_FORMAT(send_date, '%Y-%m')
),
engagement_changes AS (
    SELECT
        month,
        avg_open_rate,
        LAG(avg_open_rate) OVER (ORDER BY month) as prev_open_rate,
        avg_click_rate,
        LAG(avg_click_rate) OVER (ORDER BY month) as prev_click_rate,
        avg_click_to_open_rate,
        LAG(avg_click_to_open_rate) OVER (ORDER BY month) as prev_click_to_open_rate
    FROM monthly_engagement
)
SELECT
    month,
    avg_open_rate,
    ROUND(((avg_open_rate - prev_open_rate) / prev_open_rate) * 100, 2) as open_rate_change_pct,
    avg_click_rate,
    ROUND(((avg_click_rate - prev_click_rate) / prev_click_rate) * 100, 2) as click_rate_change_pct,
    avg_click_to_open_rate,
    ROUND(((avg_click_to_open_rate - prev_click_to_open_rate) / prev_click_to_open_rate) * 100, 2) as click_to_open_change_pct
FROM engagement_changes
ORDER BY month;
"""

# =============================================================================
# SOCIAL MEDIA ANALYSIS QUERIES
# =============================================================================

# 1. Social Media Performance Overview
SOCIAL_MEDIA_OVERVIEW = """
SELECT
    platform,
    period_month,
    followers,
    impressions,
    engagement_rate,
    ROUND((impressions / followers), 2) as reach_ratio
FROM social_media_performance
WHERE period_month LIKE %s
ORDER BY followers DESC;
"""

# 2. Daily Social Media Engagement Trends
SOCIAL_MEDIA_DAILY_TRENDS = """
SELECT
    date,
    posts_published,
    total_engagements,
    likes_reactions,
    comments,
    shares,
    estimated_clicks,
    reach,
    ROUND((total_engagements / reach) * 100, 2) as engagement_rate_pct,
    ROUND((likes_reactions / total_engagements) * 100, 2) as likes_pct,
    ROUND((comments / total_engagements) * 100, 2) as comments_pct,
    ROUND((shares / total_engagements) * 100, 2) as shares_pct
FROM social_media_engagement_daily
WHERE date BETWEEN %s AND %s
ORDER BY date;
"""

# 3. Social Media Platform Comparison
SOCIAL_MEDIA_PLATFORM_COMPARISON = """
WITH platform_metrics AS (
    SELECT
        smp.platform,
        smp.followers,
        smp.impressions,
        smp.engagement_rate,
        AVG(smed.total_engagements) as avg_daily_engagements,
        AVG(smed.posts_published) as avg_daily_posts,
        SUM(smed.total_engagements) as total_engagements,
        SUM(smed.reach) as total_reach
    FROM social_media_performance smp
    LEFT JOIN social_media_engagement_daily smed ON smed.date >= %s AND smed.date <= %s
    GROUP BY smp.platform, smp.followers, smp.impressions, smp.engagement_rate
)
SELECT
    platform,
    followers,
    impressions,
    engagement_rate,
    avg_daily_engagements,
    avg_daily_posts,
    total_engagements,
    total_reach,
    ROUND((total_engagements / total_reach) * 100, 2) as actual_engagement_rate
FROM platform_metrics
ORDER BY followers DESC;
"""

# 4. Top Performing Social Media Posts
SOCIAL_MEDIA_TOP_POSTS = """
SELECT
    date,
    LEFT(post_content, 100) as post_preview,
    total_engagements,
    likes_reactions,
    comments,
    shares,
    estimated_clicks,
    reach,
    ROUND((total_engagements / reach) * 100, 2) as engagement_rate,
    ROUND((likes_reactions / total_engagements) * 100, 2) as likes_ratio
FROM social_media_engagement_posts
WHERE date BETWEEN %s AND %s
ORDER BY total_engagements DESC
LIMIT 20;
"""

# 5. Social Media Engagement Trends Over Time
SOCIAL_MEDIA_ENGAGEMENT_TRENDS = """
WITH weekly_engagement AS (
    SELECT
        DATE_FORMAT(date, '%Y-%u') as week,
        SUM(posts_published) as weekly_posts,
        SUM(total_engagements) as weekly_engagements,
        SUM(likes_reactions) as weekly_likes,
        SUM(comments) as weekly_comments,
        SUM(shares) as weekly_shares,
        SUM(reach) as weekly_reach,
        AVG(total_engagements) as avg_daily_engagements
    FROM social_media_engagement_daily
    WHERE date BETWEEN %s AND %s
    GROUP BY DATE_FORMAT(date, '%Y-%u')
),
engagement_changes AS (
    SELECT
        week,
        weekly_posts,
        weekly_engagements,
        LAG(weekly_engagements) OVER (ORDER BY week) as prev_week_engagements,
        weekly_likes,
        weekly_comments,
        weekly_shares,
        weekly_reach,
        ROUND((weekly_engagements / weekly_reach) * 100, 2) as engagement_rate
    FROM weekly_engagement
)
SELECT
    week,
    weekly_posts,
    weekly_engagements,
    ROUND(((weekly_engagements - prev_week_engagements) / prev_week_engagements) * 100, 2) as engagement_change_pct,
    weekly_likes,
    weekly_comments,
    weekly_shares,
    weekly_reach,
    engagement_rate
FROM engagement_changes
ORDER BY week;
"""

# 6. Social Media Content Performance Analysis
SOCIAL_MEDIA_CONTENT_ANALYSIS = """
WITH content_performance AS (
    SELECT
        CASE
            WHEN LOWER(post_content) LIKE '%video%' THEN 'Video'
            WHEN LOWER(post_content) LIKE '%photo%' OR LOWER(post_content) LIKE '%image%' THEN 'Photo'
            WHEN LOWER(post_content) LIKE '%link%' THEN 'Link'
            ELSE 'Text'
        END as content_type,
        COUNT(*) as post_count,
        AVG(total_engagements) as avg_engagements,
        AVG(reach) as avg_reach,
        AVG(total_engagements / reach) as avg_engagement_rate,
        SUM(total_engagements) as total_engagements,
        SUM(reach) as total_reach
    FROM social_media_engagement_posts
    WHERE date BETWEEN %s AND %s
    GROUP BY
        CASE
            WHEN LOWER(post_content) LIKE '%video%' THEN 'Video'
            WHEN LOWER(post_content) LIKE '%photo%' OR LOWER(post_content) LIKE '%image%' THEN 'Photo'
            WHEN LOWER(post_content) LIKE '%link%' THEN 'Link'
            ELSE 'Text'
        END
)
SELECT
    content_type,
    post_count,
    ROUND(avg_engagements, 2) as avg_engagements,
    ROUND(avg_reach, 2) as avg_reach,
    ROUND(avg_engagement_rate * 100, 2) as avg_engagement_rate_pct,
    total_engagements,
    total_reach
FROM content_performance
ORDER BY avg_engagement_rate DESC;
"""

# =============================================================================
# CORRELATION ANALYSIS QUERIES
# =============================================================================

# 1. Multi-Channel Correlation Analysis
MULTI_CHANNEL_CORRELATION = """
WITH daily_channel_metrics AS (
    SELECT
        rd.sale_date as date,
        SUM(rd.extension_amount) as retail_sales,
        AVG(eed.open_rate) as email_open_rate,
        SUM(eed.unique_clicks) as email_clicks,
        SUM(smed.total_engagements) as social_engagements,
        SUM(smed.reach) as social_reach,
        AVG(smp.engagement_rate) as social_engagement_rate
    FROM retail_data rd
    LEFT JOIN email_engagement_details eed ON DATE(eed.send_date) = rd.sale_date
    LEFT JOIN social_media_engagement_daily smed ON smed.date = rd.sale_date
    LEFT JOIN social_media_performance smp ON smp.period_month = '2024'
    WHERE rd.sale_date BETWEEN %s AND %s
    GROUP BY rd.sale_date
)
SELECT
    CORR(retail_sales, email_open_rate) as sales_email_open_corr,
    CORR(retail_sales, email_clicks) as sales_email_clicks_corr,
    CORR(retail_sales, social_engagements) as sales_social_engagement_corr,
    CORR(retail_sales, social_reach) as sales_social_reach_corr,
    CORR(email_open_rate, social_engagements) as email_social_engagement_corr,
    AVG(retail_sales) as avg_daily_sales,
    AVG(email_open_rate) as avg_email_open_rate,
    AVG(social_engagements) as avg_social_engagements
FROM daily_channel_metrics
WHERE retail_sales > 0;
"""

# 2. Trend Analysis with Top 3 Changes
TREND_ANALYSIS_TOP_CHANGES = """
WITH monthly_kpis AS (
    SELECT
        DATE_FORMAT(date, '%Y-%m') as month,
        'Retail Sales' as metric,
        SUM(extension_amount) as value
    FROM retail_data
    WHERE sale_date BETWEEN %s AND %s
    GROUP BY DATE_FORMAT(sale_date, '%Y-%m')

    UNION ALL

    SELECT
        DATE_FORMAT(send_date, '%Y-%m') as month,
        'Email Open Rate' as metric,
        AVG(open_rate) as value
    FROM email_engagement_details
    WHERE send_date BETWEEN %s AND %s
    GROUP BY DATE_FORMAT(send_date, '%Y-%m')

    UNION ALL

    SELECT
        DATE_FORMAT(date, '%Y-%m') as month,
        'Social Engagements' as metric,
        SUM(total_engagements) as value
    FROM social_media_engagement_daily
    WHERE date BETWEEN %s AND %s
    GROUP BY DATE_FORMAT(date, '%Y-%m')
),
kpi_changes AS (
    SELECT
        metric,
        month,
        value,
        LAG(value) OVER (PARTITION BY metric ORDER BY month) as prev_value,
        ROUND(((value - LAG(value) OVER (PARTITION BY metric ORDER BY month)) /
               LAG(value) OVER (PARTITION BY metric ORDER BY month)) * 100, 2) as change_pct
    FROM monthly_kpis
)
SELECT
    metric,
    month,
    value,
    prev_value,
    change_pct
FROM kpi_changes
WHERE change_pct IS NOT NULL
ORDER BY ABS(change_pct) DESC
LIMIT 9;
"""

# =============================================================================
# UTILITY QUERIES
# =============================================================================

# Data Quality Check
DATA_QUALITY_CHECK = """
SELECT
    'retail_data' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT sale_date) as unique_dates,
    MIN(sale_date) as min_date,
    MAX(sale_date) as max_date,
    SUM(extension_amount) as total_sales
FROM retail_data

UNION ALL

SELECT
    'email_engagement_details' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT send_date) as unique_dates,
    MIN(send_date) as min_date,
    MAX(send_date) as max_date,
    AVG(open_rate) as avg_metric
FROM email_engagement_details

UNION ALL

SELECT
    'social_media_engagement_daily' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT date) as unique_dates,
    MIN(date) as min_date,
    MAX(date) as max_date,
    SUM(total_engagements) as total_metric
FROM social_media_engagement_daily

UNION ALL

SELECT
    'social_media_engagement_posts' as table_name,
    COUNT(*) as total_rows,
    COUNT(DISTINCT date) as unique_dates,
    MIN(date) as min_date,
    MAX(date) as max_date,
    SUM(total_engagements) as total_metric
FROM social_media_engagement_posts;
"""

# Date Range Validation
DATE_RANGE_VALIDATION = """
SELECT
    'Retail Data' as data_source,
    MIN(sale_date) as earliest_date,
    MAX(sale_date) as latest_date,
    COUNT(DISTINCT sale_date) as days_with_data
FROM retail_data

UNION ALL

SELECT
    'Email Data' as data_source,
    MIN(send_date) as earliest_date,
    MAX(send_date) as latest_date,
    COUNT(DISTINCT send_date) as days_with_data
FROM email_engagement_details

UNION ALL

SELECT
    'Social Media Daily' as data_source,
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    COUNT(DISTINCT date) as days_with_data
FROM social_media_engagement_daily

UNION ALL

SELECT
    'Social Media Posts' as data_source,
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    COUNT(DISTINCT date) as days_with_data
FROM social_media_engagement_posts;
"""

# =============================================================================
# QUERY EXECUTION HELPERS
# =============================================================================

def get_period_comparison_dates(start_date, end_date):
    """
    Calculate previous period dates for comparison
    """
    from datetime import datetime, timedelta

    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    period_days = (end - start).days + 1

    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days - 1)

    return prev_start.strftime('%Y-%m-%d'), prev_end.strftime('%Y-%m-%d')

def format_query_results(results, query_name):
    """
    Helper to format query results for reporting
    """
    print(f"\n=== {query_name} ===")
    if results:
        for row in results:
            print(row)
    else:
        print("No results found")

# Example usage:
"""
# Monthly retail sales for Q4 2024
cursor.execute(RETAIL_MONTHLY_SALES, ('2024-10-01', '2024-12-31'))

# Period comparison (45 days ending 2024-12-31 vs previous 45 days)
cursor.execute(RETAIL_PERIOD_COMPARISON, ('2024-11-17', '2024-12-31', '2024-11-17', '2024-12-31', '2024-11-17'))

# Email performance trends
cursor.execute(EMAIL_PERFORMANCE_TRENDS, ('2024-01-01', '2024-12-31'))

# Social media daily trends
cursor.execute(SOCIAL_MEDIA_DAILY_TRENDS, ('2024-01-01', '2024-12-31'))
"""
