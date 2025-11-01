#!/usr/bin/env python3
"""
Python equivalent of load_retail_data_v1.sh
Loads retail data from parquet files into MySQL database.
"""

import sys
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from src.database.db_connection import DatabaseConnection


def check_files(file_path: str, file_type: str) -> None:
    """Check if required files exist."""
    if not os.path.isfile(file_path):
        print(f"{file_type} not found at {file_path}")
        sys.exit(1)


def convert_parquet_to_csv(data_file: str) -> str:
    """Convert parquet file to CSV using the existing Python script."""
    print(f"Converting {data_file} to CSV...")

    try:
        # Run the conversion script and capture output
        result = subprocess.run(
            [sys.executable, "convert_parquet_to_csv_1.py", data_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )

        if result.returncode != 0:
            print("CSV conversion failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            sys.exit(1)

        # The last line of output should be the CSV file path
        output_lines = result.stdout.strip().split('\n')
        csv_file = output_lines[-1]

        if not os.path.isfile(csv_file):
            print("CSV conversion failed!")
            print(f"Expected CSV file: {csv_file}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            sys.exit(1)

        print(f"Conversion complete: {csv_file}")
        return csv_file

    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)


def run_sql_query(db_connection, query: str, silent: bool = False) -> None:
    """Execute SQL query."""
    try:
        cursor = db_connection.cursor()
        if silent:
            # Execute silently - no output
            cursor.execute(query)
        else:
            cursor.execute(query)
            # Print results if any
            results = cursor.fetchall()
            if results:
                for row in results:
                    print(row)
        db_connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error executing query: {e}")
        db_connection.rollback()
        sys.exit(1)


def run_sql_query_return(db_connection, query: str) -> str:
    """Execute SQL query and return single result."""
    try:
        cursor = db_connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error executing query: {e}")
        sys.exit(1)


def main():
    # Check arguments
    if len(sys.argv) != 2:
        print("Usage: python load_retail_data_v1.py <parquet_file_path>")
        sys.exit(1)

    data_file = sys.argv[1]
    env_file = "../../.env"

    # Check required files
    check_files(env_file, ".env")
    check_files(data_file, "Data File")

    # Load environment variables
    load_dotenv(env_file)

    # Convert parquet to CSV
    csv_file = convert_parquet_to_csv(data_file)

    file_name = os.path.basename(csv_file)
    user_id = "Test User"

    # Initialize database connection
    db = DatabaseConnection()
    connection = db.get_connection()

    if not connection:
        print("Failed to connect to database")
        sys.exit(1)

    try:
        # 1. Insert a new record into file_upload_logs
        insert_query = f"""
        INSERT INTO file_upload_logs (file_name, file_type, no_rows, user_id, load_status, date_time)
        VALUES ('{file_name}', 'csv', 0, '{user_id}', 0, NOW());
        SELECT LAST_INSERT_ID();
        """

        file_id = run_sql_query_return(connection, insert_query)
        print(f"New file_id created: {file_id}")

        # 2. Load CSV data into retail_data
        print("Loading data into retail_data...")

        load_query = f"""
        LOAD DATA LOCAL INFILE '{csv_file}'
        INTO TABLE retail_data
        FIELDS TERMINATED BY ','
        OPTIONALLY ENCLOSED BY '"'
        LINES TERMINATED BY '\\n'
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
            file_id = {file_id},
            load_status = 1;
        """

        run_sql_query(connection, load_query)

        # 3. Update file_upload_logs with counts
        print("Updating load log...")

        update_query = f"""
        UPDATE file_upload_logs
        SET no_rows = (SELECT COUNT(*) FROM retail_data WHERE file_id = {file_id}),
            load_status = 1,
            date_time = NOW()
        WHERE file_id = {file_id};
        """

        run_sql_query(connection, update_query)

        # Get row count
        row_count = run_sql_query_return(connection, f"SELECT no_rows FROM file_upload_logs WHERE file_id = {file_id};")

        print("")
        print("File load complete!")
        print(f"File ID:     {file_id}")
        print(f"Rows Loaded: {row_count}")
        print(f"Source:      {csv_file}")
        print(f"Database:    {os.getenv('MYSQL_DATABASE')}")
        print("Table:       retail_data")

    except Exception as e:
        print(f"Error during data loading: {e}")
        sys.exit(1)
    finally:
        # Close database connection
        db.close_connection()


if __name__ == "__main__":
    main()
