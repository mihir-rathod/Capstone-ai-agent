#!/bin/ksh
set -e

# Function to check required files
check_files() {
    file_path="$1"
    file_type="$2"
    
    if [ ! -f "$file_path" ]; then
        echo "${file_type} not found at ${file_path}"
        exit 1
    fi
}

# Convert .parquet files to csv using python
convert_parquet_to_csv() {
    data_file="$1"
    
    echo "Converting $data_file to CSV..." >&2
    # Capture all output for debugging and the CSV file path
    CSV_FILE=$(python3 convert_parquet_to_csv_1.py "$data_file" 2>&1 | tee /dev/tty | tail -n 1)

    if [ ! -f "$CSV_FILE" ]; then
        echo "CSV conversion failed!" >&2
        echo "Expected CSV file: $CSV_FILE" >&2
        echo "Files in current directory:" >&2
        ls -la >&2
        exit 1
    fi
    echo "Conversion complete: $CSV_FILE" >&2
    echo "$CSV_FILE"
}

# Function to run SQL query
run_sql_query() {
    query="$1"
    silent="${2:-false}"
    
    if [ "$silent" = "true" ]; then
        /opt/homebrew/opt/mysql@8.0/bin/mysql --local-infile=1 -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" -D "$MYSQL_DATABASE" \
              -N \
              -e "$query" 2>/dev/null
    else
        /opt/homebrew/opt/mysql@8.0/bin/mysql --local-infile=1 -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" -D "$MYSQL_DATABASE" -e "$query"
    fi
}

# Function to run SQL query and return result
run_sql_query_return() {
    query="$1"
    
    /opt/homebrew/opt/mysql@8.0/bin/mysql --local-infile=1 -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" -D "$MYSQL_DATABASE" \
          -N \
          -s \
          -e "$query"
}

# === Check arguments ===
if [ $# -ne 1 ]; then
    echo "Usage: ./load_retail_data.sh <parquet_file_path>"
    exit 1
fi

data_file="$1"
env_file="../../.env"

check_files "$env_file" ".env"
check_files "$data_file" "Data File"

# === Export env variables ===
export $(grep -v '^#' "$env_file" | xargs)

# Capture only the CSV file path
CSV_FILE=$(convert_parquet_to_csv "$data_file")

FILE_NAME=$(basename "$CSV_FILE")
USER_ID="Test User"

# === 1. Insert a new record into file_upload_logs ===
INSERT_QUERY="INSERT INTO file_upload_logs (file_name, file_type, no_rows, user_id, load_status, date_time)
VALUES ('$FILE_NAME', 'csv', 0, '$USER_ID', 0, NOW());
SELECT LAST_INSERT_ID();"

FILE_ID=$(run_sql_query_return "$INSERT_QUERY")

echo "New file_id created: $FILE_ID"

# === 2. Load CSV data into retail_data ===
echo "Loading data into retail_data..."

LOAD_QUERY="
LOAD DATA LOCAL INFILE '$CSV_FILE'
INTO TABLE retail_data
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '\"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@sale_date_time,
 @sale_date,
 store_format,
 command_name,
 site_id,
 site_name,
 slip_no,
 line,
 item_id,
 item_desc,
 extension_amount,
 qty,
 return_ind,
 price_status
)
SET 
    sale_date_time = STR_TO_DATE(@sale_date_time, '%m/%d/%Y %H:%i'),
    sale_date = STR_TO_DATE(@sale_date, '%m/%d/%Y'),
    file_id = $FILE_ID,
    load_status = 1;
"

run_sql_query "$LOAD_QUERY"

# === 3. Update file_upload_logs with counts ===
echo "Updating load log..."

UPDATE_QUERY="
UPDATE file_upload_logs
SET no_rows = (SELECT COUNT(*) FROM retail_data WHERE file_id = $FILE_ID),
    load_status = 1,
    date_time = NOW()
WHERE file_id = $FILE_ID;
"

run_sql_query "$UPDATE_QUERY"

# Get row count
ROW_COUNT=$(run_sql_query_return "SELECT no_rows FROM file_upload_logs WHERE file_id = $FILE_ID;")

echo ""
echo "File load complete!"
echo "File ID:     $FILE_ID"
echo "Rows Loaded: $ROW_COUNT"
echo "Source:      $CSV_FILE"
echo "Database:    $MYSQL_DATABASE"
echo "Table:       retail_data"

exit 0
