-- Verification queries for date parsing fixes
-- Run these queries after loading data to verify the fixes worked

-- 1. Check for NULL sale_date_time values
SELECT 
    COUNT(*) as null_datetime_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM retail_data), 2) as percentage
FROM retail_data 
WHERE sale_date_time IS NULL;

-- 2. Check for invalid sale_date values (0000-00-00 or NULL)
SELECT 
    COUNT(*) as invalid_date_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM retail_data), 2) as percentage
FROM retail_data 
WHERE sale_date = '0000-00-00' OR sale_date IS NULL;

-- 3. Sample recent data to verify proper parsing
SELECT 
    sale_date_time, 
    sale_date, 
    store_format,
    command_name,
    item_desc,
    file_id
FROM retail_data 
ORDER BY row_id DESC 
LIMIT 20;

-- 4. Check date ranges by file_id
SELECT 
    file_id,
    MIN(sale_date) as earliest_date,
    MAX(sale_date) as latest_date,
    MIN(sale_date_time) as earliest_datetime,
    MAX(sale_date_time) as latest_datetime,
    COUNT(*) as total_rows,
    SUM(CASE WHEN sale_date IS NULL OR sale_date = '0000-00-00' THEN 1 ELSE 0 END) as invalid_dates,
    SUM(CASE WHEN sale_date_time IS NULL THEN 1 ELSE 0 END) as null_datetimes
FROM retail_data
GROUP BY file_id
ORDER BY file_id DESC;

-- 5. Compare old vs new file data quality
SELECT 
    CASE 
        WHEN file_id <= 6 THEN 'Old Files (<=6)'
        ELSE 'New Files (>6)'
    END as file_group,
    COUNT(*) as total_rows,
    SUM(CASE WHEN sale_date IS NULL OR sale_date = '0000-00-00' THEN 1 ELSE 0 END) as invalid_dates,
    SUM(CASE WHEN sale_date_time IS NULL THEN 1 ELSE 0 END) as null_datetimes,
    ROUND(SUM(CASE WHEN sale_date IS NULL OR sale_date = '0000-00-00' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as invalid_date_pct,
    ROUND(SUM(CASE WHEN sale_date_time IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as null_datetime_pct
FROM retail_data
GROUP BY file_group;
