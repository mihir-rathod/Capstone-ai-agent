import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
import subprocess
import sys
import tempfile
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
from ..database.db_connection import DatabaseConnection
from .load_social_media_data import SocialMediaDataLoader
from sqlalchemy import create_engine

load_dotenv()

class SupportingDataLoader:
    def __init__(self, deliveries_file_path=None, engagement_file_path=None, performance_file_path=None, social_media_file_path=None, retail_file_path=None, s3_bucket=None):
        self.db = DatabaseConnection()
        self.s3_bucket = s3_bucket
        self.temp_files = []  # Track temporary files for cleanup

        # Download files from S3 if bucket is provided and paths look like S3 keys
        self.deliveries_file = self._resolve_file_path(deliveries_file_path)
        self.engagement_file = self._resolve_file_path(engagement_file_path)
        self.performance_file = self._resolve_file_path(performance_file_path)
        self.social_media_file = self._resolve_file_path(social_media_file_path)
        self.retail_file = self._resolve_file_path(retail_file_path)

    def _resolve_file_path(self, file_path):
        """Resolve file path - download from S3 if needed, otherwise return as-is"""
        if not file_path or not self.s3_bucket:
            return file_path

        # Download from S3 if bucket is provided and file_path is a non-empty string
        if isinstance(file_path, str) and file_path.strip():
            try:
                return self._download_from_s3(file_path)
            except Exception as e:
                print(f"Failed to download {file_path} from S3: {e}")
                return None
        return file_path

    def _download_from_s3(self, s3_key):
        """Download file from S3 and return local path"""
        try:
            s3_client = boto3.client('s3')

            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(s3_key)[1])
            temp_file.close()

            # Download the file
            s3_client.download_file(self.s3_bucket, s3_key, temp_file.name)

            # Track for cleanup
            self.temp_files.append(temp_file.name)

            print(f"Downloaded {s3_key} from S3 bucket {self.s3_bucket} to {temp_file.name}")
            return temp_file.name

        except NoCredentialsError:
            raise Exception("AWS credentials not found")
        except ClientError as e:
            raise Exception(f"S3 download failed: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error downloading from S3: {e}")

    def cleanup_temp_files(self):
        """Clean up temporary files downloaded from S3"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    print(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                print(f"Failed to cleanup {temp_file}: {e}")
        self.temp_files = []

    def clean_numeric(self, value):
        """Convert string percentages/rates to decimal"""
        if isinstance(value, str):
            if '%' in value:
                return float(value.replace('%', '')) / 100
            try:
                return float(value)
            except ValueError:
                return None
        return value

    def clean_date(self, date_str):
        """Convert date string to YYYY-MM-DD format"""
        if isinstance(date_str, str):
            try:
                # Handle various date formats
                if '-' in date_str:
                    parts = date_str.split('-')
                    if len(parts) == 3:
                        # Assume MM-DD-YYYY or DD-MM-YYYY, but from data it's YYYY-MM-DD
                        return date_str
                return date_str
            except:
                return None
        return date_str

    def load_delivery_timeline(self):
        """Load daily delivery metrics"""
        try:
            df = pd.read_excel(self.deliveries_file, sheet_name='Email Deliveries Delivery Timeline', engine='openpyxl')
            # Skip header rows, data starts after the widget info
            # From the content, data starts at row with "Daily"
            start_row = None
            for idx, row in df.iterrows():
                if str(row.iloc[0]).strip().lower() == 'daily':
                    start_row = idx + 1
                    break

            if start_row is None:
                print("Could not find data start for delivery timeline")
                return

            df = df.iloc[start_row:].reset_index(drop=True)
            df.columns = ['date', 'sends', 'deliveries', 'delivery_rate', 'bounces', 'bounce_rate']

            # Clean data
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
            df['sends'] = pd.to_numeric(df['sends'], errors='coerce').astype('Int64')
            df['deliveries'] = pd.to_numeric(df['deliveries'], errors='coerce').astype('Int64')
            df['bounces'] = pd.to_numeric(df['bounces'], errors='coerce').astype('Int64')
            df['delivery_rate'] = df['delivery_rate'].apply(self.clean_numeric)
            df['bounce_rate'] = df['bounce_rate'].apply(self.clean_numeric)

            # Remove rows with all NaN
            df = df.dropna(how='all')

            connection = self.db.get_connection()
            cursor = connection.cursor()

            for _, row in df.iterrows():
                if pd.notna(row['date']):
                    cursor.execute("""
                        INSERT INTO email_delivery_daily
                        (date, sends, deliveries, delivery_rate, bounces, bounce_rate)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        sends=VALUES(sends), deliveries=VALUES(deliveries),
                        delivery_rate=VALUES(delivery_rate), bounces=VALUES(bounces),
                        bounce_rate=VALUES(bounce_rate)
                    """, (
                        row['date'], row['sends'], row['deliveries'],
                        row['delivery_rate'], row['bounces'], row['bounce_rate']
                    ))

            connection.commit()
            print(f"Loaded {len(df)} delivery timeline records")

        except Exception as e:
            print(f"Error loading delivery timeline: {e}")

    def load_delivery_audience(self):
        """Load audience delivery data"""
        try:
            df = pd.read_excel(self.deliveries_file, sheet_name='By Audience', engine='openpyxl')
            # Skip header rows
            start_row = None
            for idx, row in df.iterrows():
                if str(row.iloc[0]).strip().lower() == 'audience name':
                    start_row = idx + 1
                    break

            if start_row is None:
                print("Could not find data start for delivery audience")
                return

            df = df.iloc[start_row:].reset_index(drop=True)
            df.columns = ['audience_name', 'audience_type', 'sends', 'deliveries', 'bounces', 'bounce_rate']

            # Clean data
            df['sends'] = pd.to_numeric(df['sends'], errors='coerce').astype('Int64')
            df['deliveries'] = pd.to_numeric(df['deliveries'], errors='coerce').astype('Int64')
            df['bounces'] = pd.to_numeric(df['bounces'], errors='coerce').astype('Int64')
            df['bounce_rate'] = df['bounce_rate'].apply(self.clean_numeric)

            # Remove empty rows
            df = df.dropna(subset=['audience_name'])

            connection = self.db.get_connection()
            cursor = connection.cursor()

            for _, row in df.iterrows():
                if pd.notna(row['audience_name']):
                    cursor.execute("""
                        INSERT INTO email_delivery_audience
                        (audience_name, audience_type, sends, deliveries, bounces, bounce_rate)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        sends=VALUES(sends), deliveries=VALUES(deliveries),
                        bounces=VALUES(bounces), bounce_rate=VALUES(bounce_rate)
                    """, (
                        row['audience_name'], row['audience_type'], row['sends'],
                        row['deliveries'], row['bounces'], row['bounce_rate']
                    ))

            connection.commit()
            print(f"Loaded {len(df)} delivery audience records")

        except Exception as e:
            print(f"Error loading delivery audience: {e}")

    def log_file_upload(self, file_name, file_type, row_count, user_id="System"):
        """Log file upload to file_upload_logs table following retail data pattern"""
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()

            # Insert initial log entry
            cursor.execute("""
                INSERT INTO file_upload_logs (file_name, file_type, no_rows, user_id, load_status, date_time)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (file_name, file_type, row_count, user_id, 1))  # load_status = 1 (completed)

            connection.commit()
            print(f"Logged {file_type} file: {file_name} with {row_count} rows")

        except Exception as e:
            print(f"Error logging file upload: {e}")

    def load_delivery_details(self):
        """Load per-email delivery details"""
        try:
            df = pd.read_excel(self.deliveries_file, sheet_name='Email Deliveries Details', engine='openpyxl')
            # Skip header rows
            start_row = None
            for idx, row in df.iterrows():
                if str(row.iloc[0]).strip().lower() == 'email content name':
                    start_row = idx + 1
                    break

            if start_row is None:
                print("Could not find data start for delivery details")
                return

            df = df.iloc[start_row:].reset_index(drop=True)
            df.columns = ['email_content_name', 'send_date', 'sends', 'deliveries', 'bounces', 'bounce_rate']

            # Clean data
            df['send_date'] = pd.to_datetime(df['send_date'], errors='coerce').dt.date
            df['sends'] = pd.to_numeric(df['sends'], errors='coerce').astype('Int64')
            df['deliveries'] = pd.to_numeric(df['deliveries'], errors='coerce').astype('Int64')
            df['bounces'] = pd.to_numeric(df['bounces'], errors='coerce').astype('Int64')
            df['bounce_rate'] = df['bounce_rate'].apply(self.clean_numeric)

            # Remove empty rows
            df = df.dropna(subset=['email_content_name'])

            connection = self.db.get_connection()
            cursor = connection.cursor()

            for _, row in df.iterrows():
                if pd.notna(row['email_content_name']):
                    cursor.execute("""
                        INSERT INTO email_delivery_details
                        (email_content_name, send_date, sends, deliveries, bounces, bounce_rate)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        sends=VALUES(sends), deliveries=VALUES(deliveries),
                        bounces=VALUES(bounces), bounce_rate=VALUES(bounce_rate)
                    """, (
                        row['email_content_name'], row['send_date'], row['sends'],
                        row['deliveries'], row['bounces'], row['bounce_rate']
                    ))

            connection.commit()
            row_count = len(df)
            print(f"Loaded {row_count} delivery details records")

            # Log file upload
            file_name = os.path.basename(self.deliveries_file) if self.deliveries_file else "email_deliveries.xlsx"
            self.log_file_upload(file_name, "email_delivery", row_count)

        except Exception as e:
            print(f"Error loading delivery details: {e}")

    def load_engagement_timeline(self):
        """Load daily engagement metrics"""
        try:
            df = pd.read_excel(self.engagement_file, sheet_name='Email Engagement Engagement Timeline', engine='openpyxl')
            # Skip header rows
            start_row = None
            for idx, row in df.iterrows():
                if str(row.iloc[0]).strip().lower() == 'daily':
                    start_row = idx + 1
                    break

            if start_row is None:
                print("Could not find data start for engagement timeline")
                return

            df = df.iloc[start_row:].reset_index(drop=True)
            df.columns = ['date', 'deliveries', 'unique_opens', 'open_rate', 'unique_clicks',
                         'click_rate', 'click_to_open_rate', 'unique_unsubscribes', 'unsubscribe_rate']

            # Clean data
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
            df['deliveries'] = pd.to_numeric(df['deliveries'], errors='coerce').astype('Int64')
            df['unique_opens'] = pd.to_numeric(df['unique_opens'], errors='coerce').astype('Int64')
            df['unique_clicks'] = pd.to_numeric(df['unique_clicks'], errors='coerce').astype('Int64')
            df['unique_unsubscribes'] = pd.to_numeric(df['unique_unsubscribes'], errors='coerce').astype('Int64')
            df['open_rate'] = df['open_rate'].apply(self.clean_numeric)
            df['click_rate'] = df['click_rate'].apply(self.clean_numeric)
            df['click_to_open_rate'] = df['click_to_open_rate'].apply(self.clean_numeric)
            df['unsubscribe_rate'] = df['unsubscribe_rate'].apply(self.clean_numeric)

            # Remove rows with all NaN
            df = df.dropna(how='all')

            connection = self.db.get_connection()
            cursor = connection.cursor()

            for _, row in df.iterrows():
                if pd.notna(row['date']):
                    cursor.execute("""
                        INSERT INTO email_engagement_daily
                        (date, deliveries, unique_opens, open_rate, unique_clicks, click_rate,
                         click_to_open_rate, unique_unsubscribes, unsubscribe_rate)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        deliveries=VALUES(deliveries), unique_opens=VALUES(unique_opens),
                        open_rate=VALUES(open_rate), unique_clicks=VALUES(unique_clicks),
                        click_rate=VALUES(click_rate), click_to_open_rate=VALUES(click_to_open_rate),
                        unique_unsubscribes=VALUES(unique_unsubscribes), unsubscribe_rate=VALUES(unsubscribe_rate)
                    """, (
                        row['date'], row['deliveries'], row['unique_opens'], row['open_rate'],
                        row['unique_clicks'], row['click_rate'], row['click_to_open_rate'],
                        row['unique_unsubscribes'], row['unsubscribe_rate']
                    ))

            connection.commit()
            print(f"Loaded {len(df)} engagement timeline records")

        except Exception as e:
            print(f"Error loading engagement timeline: {e}")

    def load_engagement_audience(self):
        """Load audience engagement data"""
        try:
            df = pd.read_excel(self.engagement_file, sheet_name='By Audience', engine='openpyxl')
            # Skip header rows
            start_row = None
            for idx, row in df.iterrows():
                if str(row.iloc[0]).strip().lower() == 'audience name':
                    start_row = idx + 1
                    break

            if start_row is None:
                print("Could not find data start for engagement audience")
                return

            df = df.iloc[start_row:].reset_index(drop=True)
            df.columns = ['audience_name', 'audience_type', 'unique_opens', 'open_rate',
                         'unique_clicks', 'click_rate', 'click_to_open_rate', 'unique_unsubscribes', 'unsubscribe_rate']

            # Clean data
            df['unique_opens'] = pd.to_numeric(df['unique_opens'], errors='coerce').astype('Int64')
            df['unique_clicks'] = pd.to_numeric(df['unique_clicks'], errors='coerce').astype('Int64')
            df['unique_unsubscribes'] = pd.to_numeric(df['unique_unsubscribes'], errors='coerce').astype('Int64')
            df['open_rate'] = df['open_rate'].apply(self.clean_numeric)
            df['click_rate'] = df['click_rate'].apply(self.clean_numeric)
            df['click_to_open_rate'] = df['click_to_open_rate'].apply(self.clean_numeric)
            df['unsubscribe_rate'] = df['unsubscribe_rate'].apply(self.clean_numeric)

            # Remove empty rows
            df = df.dropna(subset=['audience_name'])

            connection = self.db.get_connection()
            cursor = connection.cursor()

            for _, row in df.iterrows():
                if pd.notna(row['audience_name']):
                    cursor.execute("""
                        INSERT INTO email_engagement_audience
                        (audience_name, audience_type, unique_opens, open_rate, unique_clicks,
                         click_rate, click_to_open_rate, unique_unsubscribes, unsubscribe_rate)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        unique_opens=VALUES(unique_opens), open_rate=VALUES(open_rate),
                        unique_clicks=VALUES(unique_clicks), click_rate=VALUES(click_rate),
                        click_to_open_rate=VALUES(click_to_open_rate),
                        unique_unsubscribes=VALUES(unique_unsubscribes), unsubscribe_rate=VALUES(unsubscribe_rate)
                    """, (
                        row['audience_name'], row['audience_type'], row['unique_opens'],
                        row['open_rate'], row['unique_clicks'], row['click_rate'],
                        row['click_to_open_rate'], row['unique_unsubscribes'], row['unsubscribe_rate']
                    ))

            connection.commit()
            print(f"Loaded {len(df)} engagement audience records")

        except Exception as e:
            print(f"Error loading engagement audience: {e}")

    def load_engagement_details(self):
        """Load per-email engagement details"""
        try:
            # Read Excel file, skip the first 4 rows (widget metadata), use row 4 as header
            df = pd.read_excel(self.engagement_file, sheet_name='Email Engagement Details', engine='openpyxl', header=4)

            # Clean column names
            df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]

            # Rename columns to match expected names
            column_mapping = {
                'message_name': 'message_name',
                'campaign': 'campaign',
                'send_date': 'send_date',
                'open_rate': 'open_rate',
                'click_rate': 'click_rate',
                'click_to_open_rate': 'click_to_open_rate',
                'unsubscribe_rate': 'unsubscribe_rate',
                'unique_opens': 'unique_opens',
                'unique_clicks': 'unique_clicks',
                'unique_unsubscribes': 'unique_unsubscribes'
            }

            # Keep only expected columns that exist in the dataframe
            available_cols = [col for col in column_mapping.keys() if col in df.columns]
            df = df[available_cols]
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in available_cols})

            # Clean data
            df['send_date'] = pd.to_datetime(df['send_date'], errors='coerce').dt.date
            df['unique_opens'] = pd.to_numeric(df['unique_opens'], errors='coerce').astype('Int64')
            df['unique_clicks'] = pd.to_numeric(df['unique_clicks'], errors='coerce').astype('Int64')
            df['unique_unsubscribes'] = pd.to_numeric(df['unique_unsubscribes'], errors='coerce').astype('Int64')
            df['open_rate'] = df['open_rate'].apply(self.clean_numeric)
            df['click_rate'] = df['click_rate'].apply(self.clean_numeric)
            df['click_to_open_rate'] = df['click_to_open_rate'].apply(self.clean_numeric)
            df['unsubscribe_rate'] = df['unsubscribe_rate'].apply(self.clean_numeric)

            # Remove empty rows and rows with NaN in key columns
            df = df.dropna(subset=['message_name'])
            df = df[df['message_name'].notna()]

            # Filter out rows where message_name is 'nan' (string), empty, or contains widget metadata
            df = df[
                (df['message_name'].astype(str).str.lower() != 'nan') &
                (df['message_name'].astype(str).str.strip() != '') &
                (~df['message_name'].astype(str).str.contains('widget', case=False, na=False)) &
                (~df['message_name'].astype(str).str.contains('unnamed', case=False, na=False))
            ]

            connection = self.db.get_connection()
            cursor = connection.cursor()

            for _, row in df.iterrows():
                if pd.notna(row['message_name']) and str(row['message_name']).lower() != 'nan':
                    # Convert NaN values to None for SQL
                    def clean_value(val):
                        if pd.isna(val):
                            return None
                        return val

                    cursor.execute("""
                        INSERT INTO email_engagement_details
                        (message_name, campaign, send_date, open_rate, click_rate,
                         click_to_open_rate, unsubscribe_rate, unique_opens, unique_clicks, unique_unsubscribes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        open_rate=VALUES(open_rate), click_rate=VALUES(click_rate),
                        click_to_open_rate=VALUES(click_to_open_rate), unsubscribe_rate=VALUES(unsubscribe_rate),
                        unique_opens=VALUES(unique_opens), unique_clicks=VALUES(unique_clicks),
                        unique_unsubscribes=VALUES(unique_unsubscribes)
                    """, (
                        clean_value(row['message_name']), clean_value(row['campaign']), clean_value(row['send_date']),
                        clean_value(row['open_rate']), clean_value(row['click_rate']), clean_value(row['click_to_open_rate']),
                        clean_value(row['unsubscribe_rate']), clean_value(row['unique_opens']), clean_value(row['unique_clicks']),
                        clean_value(row['unique_unsubscribes'])
                    ))

            connection.commit()
            row_count = len(df)
            print(f"Loaded {row_count} engagement details records")

            # Log file upload
            file_name = os.path.basename(self.engagement_file) if self.engagement_file else "email_engagement.xlsx"
            self.log_file_upload(file_name, "email_engagement", row_count)

        except Exception as e:
            print(f"Error loading engagement details: {e}")

    def load_campaign_performance(self):
        """Load campaign performance summary data"""
        try:
            # Read Excel file, skip the first 4 rows (widget metadata), use row 4 as header
            df = pd.read_excel(self.performance_file, sheet_name='Email Performance Email Sends T', engine='openpyxl', header=4)

            # Clean column names
            df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]

            # Rename columns to match expected names
            column_mapping = {
                'email_content_name': 'email_content_name',
                'email_subject': 'email_subject',
                'sends': 'sends',
                'open_rate': 'open_rate',
                'click_to_open_rate': 'click_to_open_rate'
            }

            # Keep only expected columns that exist in the dataframe
            available_cols = [col for col in column_mapping.keys() if col in df.columns]
            df = df[available_cols]
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in available_cols})

            # Clean data
            df['sends'] = pd.to_numeric(df['sends'], errors='coerce').astype('Int64')
            df['open_rate'] = df['open_rate'].apply(self.clean_numeric)
            df['click_to_open_rate'] = df['click_to_open_rate'].apply(self.clean_numeric)

            # Remove empty rows and rows with NaN in key columns
            df = df.dropna(subset=['email_content_name'])
            df = df[df['email_content_name'].notna()]

            # Filter out rows where email_content_name is 'nan' (string), empty, or contains widget metadata
            df = df[
                (df['email_content_name'].astype(str).str.lower() != 'nan') &
                (df['email_content_name'].astype(str).str.strip() != '') &
                (~df['email_content_name'].astype(str).str.contains('widget', case=False, na=False)) &
                (~df['email_content_name'].astype(str).str.contains('unnamed', case=False, na=False))
            ]

            connection = self.db.get_connection()
            cursor = connection.cursor()

            for _, row in df.iterrows():
                if pd.notna(row['email_content_name']) and str(row['email_content_name']).lower() != 'nan':
                    # Convert NaN values to None for SQL
                    def clean_value(val):
                        if pd.isna(val):
                            return None
                        return val

                    cursor.execute("""
                        INSERT INTO email_campaign_performance
                        (email_content_name, email_subject, sends, open_rate, click_to_open_rate)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        sends=VALUES(sends), open_rate=VALUES(open_rate),
                        click_to_open_rate=VALUES(click_to_open_rate)
                    """, (
                        clean_value(row['email_content_name']), clean_value(row['email_subject']),
                        clean_value(row['sends']), clean_value(row['open_rate']), clean_value(row['click_to_open_rate'])
                    ))

            connection.commit()
            row_count = len(df)
            print(f"Loaded {row_count} campaign performance records")

            # Log file upload
            file_name = os.path.basename(self.performance_file) if self.performance_file else "email_performance.xlsx"
            self.log_file_upload(file_name, "email_performance", row_count)

        except Exception as e:
            print(f"Error loading campaign performance: {e}")

    def load_all_data(self):
        """Load all email marketing data"""
        print("Starting email marketing data load...")

        self.load_delivery_details()
        # self.load_delivery_timeline()  # Commented out - table is empty
        # self.load_delivery_audience()  # Commented out - table is empty
        self.load_engagement_details()
        # self.load_engagement_timeline()  # Commented out - table is empty
        # self.load_engagement_audience()  # Commented out - table is empty
        self.load_campaign_performance()

        self.db.close_connection()
        print("Email marketing data load completed.")



    def load_retail_data(self):
        """Load retail data using the existing load_retail_data_v1.py script"""
        if not self.retail_file:
            print("No retail file provided")
            return

        try:
            print(f"Loading retail data from {self.retail_file}...")

            # Close our database connection to avoid conflicts with the retail script
            self.db.close_connection()

            # Set PYTHONPATH to include the project root so imports work
            env = os.environ.copy()
            env['PYTHONPATH'] = os.getcwd()

            # Change to the script's directory so the relative path works
            script_dir = os.path.join(os.getcwd(), "src", "file_operations")

            # Call the existing load_retail_data_v1.py script
            result = subprocess.run(
                [sys.executable, "load_retail_data_v1.py", self.retail_file],
                capture_output=True,
                text=True,
                cwd=script_dir,
                env=env
            )

            if result.returncode != 0:
                print("Retail data loading failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                raise Exception(f"Retail data loading failed with return code {result.returncode}")

            print("Retail data loaded successfully")
            print("Output:", result.stdout)

        except Exception as e:
            print(f"Error loading retail data: {e}")
            raise  # Re-raise to propagate the error

    def load_all_data(self):
        """Load all supporting data"""
        print("Starting supporting data load...")

        # Load email data if files provided
        if self.deliveries_file:
            self.load_delivery_details()
        if self.engagement_file:
            self.load_engagement_details()
        if self.performance_file:
            self.load_campaign_performance()
        if self.social_media_file:
            # Create SQLAlchemy engine for SocialMediaDataLoader
            # URL encode the password to handle special characters like '@'
            from urllib.parse import quote_plus
            password = quote_plus(os.getenv('MYSQL_PASSWORD', 'password'))
            db_url = f"mysql+mysqlconnector://{os.getenv('MYSQL_USER', 'user')}:{password}@{os.getenv('MYSQL_HOST', 'db')}/{os.getenv('MYSQL_DATABASE', 'capstone_db')}"
            engine = create_engine(db_url)
            # Use the external SocialMediaDataLoader
            social_loader = SocialMediaDataLoader(self.social_media_file, engine)
            social_loader.run()

            # Log social media file upload (approximate total rows loaded)
            # Since SocialMediaDataLoader doesn't return row counts, we'll use a placeholder
            file_name = os.path.basename(self.social_media_file) if self.social_media_file else "social_media_performance.xlsx"
            self.log_file_upload(file_name, "social_media", 0)  # 0 as placeholder since we don't have exact count
        if self.retail_file:
            self.load_retail_data()

        self.db.close_connection()
        print("Supporting data load completed.")

if __name__ == "__main__":
    loader = SupportingDataLoader()
    loader.load_all_data()
