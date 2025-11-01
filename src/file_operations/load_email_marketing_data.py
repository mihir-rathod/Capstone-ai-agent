import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
import subprocess
import sys
from dotenv import load_dotenv
from ..database.db_connection import DatabaseConnection

load_dotenv()

class SupportingDataLoader:
    def __init__(self, deliveries_file_path=None, engagement_file_path=None, performance_file_path=None, social_media_file_path=None, retail_file_path=None):
        self.db = DatabaseConnection()
        self.deliveries_file = deliveries_file_path
        self.engagement_file = engagement_file_path
        self.performance_file = performance_file_path
        self.social_media_file = social_media_file_path
        self.retail_file = retail_file_path

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
            print(f"Loaded {len(df)} delivery details records")

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
            print(f"Loaded {len(df)} engagement details records")

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
            print(f"Loaded {len(df)} campaign performance records")

        except Exception as e:
            print(f"Error loading campaign performance: {e}")

    def load_all_data(self):
        """Load all email marketing data"""
        print("Starting email marketing data load...")

        self.load_delivery_details()
        self.load_engagement_details()
        self.load_campaign_performance()

        self.db.close_connection()
        print("Email marketing data load completed.")

    def load_social_media_data(self):
        """Load social media performance data"""
        if not self.social_media_file:
            print("No social media file provided")
            return

        try:
            # Use similar logic to the existing social media loader
            # required_tabs = ["Facebook", "Instagram", "YouTube", "TikTok", "Summary"]
            required_tabs = [
                "L1 Performance Metrics",
                "Engagement Summary",
                "Top 5 Channels by Followers",
                "Channels by Total Engagement",
                "Channels by Engagement Rate ",
                "Overall Follower vs Change",
                "Top Changes in Followers",
                "Social Engagement by Month"
            ]
            all_rows = []

            for sheet in required_tabs:
                try:
                    # Read Excel file, skip the first 2 rows (widget metadata), use row 2 as header
                    df = pd.read_excel(self.social_media_file, sheet_name=sheet, engine='openpyxl', header=2)
                    if df.empty:
                        print(f"Sheet missing or empty: {sheet}")
                        continue

                    # Clean column names
                    df.columns = [str(c).strip().lower().replace(" ", "_").replace("(", "").replace(")", "").replace("%", "pct") for c in df.columns]

                    date_col = next((c for c in df.columns if "date" in c or "month" in c), "month")
                    if date_col not in df.columns:
                        df[date_col] = pd.NA

                    followers = next((c for c in df.columns if "follower" in c), None)
                    impressions = next((c for c in df.columns if "impression" in c), None)
                    engagements = next((c for c in df.columns if "engagement" in c and "rate" not in c), None)
                    engagement_rate = next((c for c in df.columns if "engagement_rate" in c or c == "er"), None)
                    video_views = next((c for c in df.columns if "view" in c), None)

                    for _, r in df.iterrows():
                        # Handle NAType values by converting to None
                        def safe_get(col):
                            val = r.get(col)
                            if pd.isna(val):
                                return None
                            return val

                        row = {
                            "platform": sheet,
                            "period_month": safe_get(date_col) if date_col else None,
                            "followers": safe_get(followers) if followers else 0,
                            "impressions": safe_get(impressions) if impressions else 0,
                            "engagements": safe_get(engagements) if engagements else 0,
                            "video_views": safe_get(video_views) if video_views else 0,
                        }

                        if engagement_rate:
                            row["engagement_rate"] = self.clean_numeric(safe_get(engagement_rate))
                        else:
                            try:
                                engagements_val = row["engagements"] if row["engagements"] is not None else 0
                                impressions_val = row["impressions"] if row["impressions"] is not None else 0
                                row["engagement_rate"] = (
                                    (engagements_val / impressions_val) * 100
                                    if impressions_val and impressions_val > 0 else 0
                                )
                            except Exception:
                                row["engagement_rate"] = 0

                        all_rows.append(row)

                except Exception as e:
                    print(f"Error loading sheet {sheet}: {e}")

            if all_rows:
                df = pd.DataFrame(all_rows)
                df["file_source"] = self.social_media_file

                connection = self.db.get_connection()
                cursor = connection.cursor()

                for _, row in df.iterrows():
                    # Ensure period_month is not None
                    period_month = row['period_month'] if row['period_month'] is not None else 'Unknown'

                    cursor.execute("""
                        INSERT INTO social_media_performance
                        (platform, period_month, followers, impressions, engagements, video_views, engagement_rate, file_source)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        followers=VALUES(followers), impressions=VALUES(impressions),
                        engagements=VALUES(engagements), video_views=VALUES(video_views),
                        engagement_rate=VALUES(engagement_rate)
                    """, (
                        row['platform'], period_month, row['followers'],
                        row['impressions'], row['engagements'], row['video_views'],
                        row['engagement_rate'], row['file_source']
                    ))

                connection.commit()
                print(f"Loaded {len(df)} social media performance records")

        except Exception as e:
            print(f"Error loading social media data: {e}")

    def load_retail_data(self):
        """Load retail data using the existing load_retail_data_v1.py script"""
        if not self.retail_file:
            print("No retail file provided")
            return

        try:
            print(f"Loading retail data from {self.retail_file}...")

            # Set PYTHONPATH to include the project root so imports work
            env = os.environ.copy()
            env['PYTHONPATH'] = os.getcwd()

            # The retail script expects .env at ../../.env relative to its location
            # Since we're running from project root, we need to adjust the env file path
            # by temporarily modifying the script or setting the correct working directory

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
            self.load_social_media_data()
        if self.retail_file:
            self.load_retail_data()

        self.db.close_connection()
        print("Supporting data load completed.")

if __name__ == "__main__":
    loader = SupportingDataLoader()
    loader.load_all_data()
