import pandas as pd
import sqlalchemy
from typing import Optional
from datetime import date, timedelta


class SocialMediaDataLoader:
    # Performance tabs (followers, impressions, reach)
    PERFORMANCE_TABS = [
        "Top 5 Channels by Followers",
        "Channels by Post Reach",
        "Channels by Engagement Rate ",
        "Top Changes in Followers"
    ]

    # Engagement tabs (daily and post-level engagement data)
    ENGAGEMENT_TABS = [
        "Brand Post vs Total Engageme",
        "Posts",
        "Engagement Behaviour across ",
        "Post Engagement Scorecard"
    ]

    # Legacy tabs (keeping for compatibility)
    REQUIRED_TABS = PERFORMANCE_TABS + [
        "Channels by Total Engagement",
        "Post Engagement Scorecard ac"
    ]

    def __init__(self, social_file: str, db_engine: Optional[sqlalchemy.engine.Engine] = None):
        self.social_file = social_file
        self.db_engine = db_engine

    def _safe_read(self, sheet: str) -> pd.DataFrame:
        """Read sheet if exists, else return empty DataFrame."""
        try:
            return pd.read_excel(self.social_file, sheet_name=sheet)
        except Exception:
            return pd.DataFrame()

    def extract(self) -> dict:
        """Load performance tabs from workbook."""
        data = {}

        for sheet in self.REQUIRED_TABS:
            df = self._safe_read(sheet)
            if df.empty:
                print(f"⚠️ Sheet missing or empty: {sheet}")
                continue

            # Parse the sheet properly - skip metadata row and use actual headers
            try:
                # Read with header=1 to get the structure
                temp_df = pd.read_excel(self.social_file, sheet_name=sheet, header=1)
                if not temp_df.empty and len(temp_df) > 0:
                    # First row contains actual column names
                    actual_headers = temp_df.iloc[0].values
                    # Data starts from second row
                    df = temp_df.iloc[1:].reset_index(drop=True)
                    df.columns = actual_headers
                data[sheet] = df
            except Exception as e:
                print(f"⚠️ Error parsing sheet {sheet}: {e}")
                data[sheet] = pd.DataFrame()

        return data

    def extract_engagement(self) -> dict:
        """Load engagement tabs from workbook."""
        data = {}

        for sheet in self.ENGAGEMENT_TABS:
            df = self._safe_read(sheet)
            if df.empty:
                print(f"⚠️ Engagement sheet missing or empty: {sheet}")
                continue

            # Parse the sheet properly - skip metadata row and use actual headers
            try:
                # Read with header=1 to get the structure
                temp_df = pd.read_excel(self.social_file, sheet_name=sheet, header=1)
                if not temp_df.empty and len(temp_df) > 0:
                    # First row contains actual column names
                    actual_headers = temp_df.iloc[0].values
                    # Data starts from second row
                    df = temp_df.iloc[1:].reset_index(drop=True)
                    df.columns = actual_headers
                data[sheet] = df
            except Exception as e:
                print(f"⚠️ Error parsing engagement sheet {sheet}: {e}")
                data[sheet] = pd.DataFrame()

        return data

    def transform(self, data: dict) -> pd.DataFrame:
        """Normalize and unify social performance metrics (excluding engagement data)."""
        # Use a dict to merge data by platform and period
        merged_data = {}

        for sheet_name, df in data.items():
            if df.empty:
                continue

            df.columns = [str(c).strip().lower().replace(" ", "_").replace("(", "").replace(")", "").replace("%", "pct") for c in df.columns]

            if sheet_name == "Top 5 Channels by Followers":
                # Follower data by platform
                for _, r in df.iterrows():
                    try:
                        platform_name = r.get("social_network", "Unknown")
                        key = (platform_name, "2024")  # Annual data
                        if key not in merged_data:
                            merged_data[key] = {
                                "platform": platform_name,
                                "period_month": "2024",
                                "followers": 0,
                                "impressions": 0,
                                "engagement_rate": 0.0,
                            }
                        merged_data[key]["followers"] = int(float(r.get("followers_sum", 0))) if r.get("followers_sum") else 0
                    except Exception as e:
                        print(f"Error processing row in {sheet_name}: {e}")

            elif sheet_name == "Channels by Post Reach":
                # Impressions (post reach) by platform
                for _, r in df.iterrows():
                    try:
                        platform_name = r.get("social_network", "Unknown")
                        key = (platform_name, "2024")  # Annual data
                        if key not in merged_data:
                            merged_data[key] = {
                                "platform": platform_name,
                                "period_month": "2024",
                                "followers": 0,
                                "impressions": 0,
                                "engagement_rate": 0.0,
                            }
                        merged_data[key]["impressions"] = int(float(r.get("post_reach_sum", 0))) if r.get("post_reach_sum") else 0
                    except Exception as e:
                        print(f"Error processing row in {sheet_name}: {e}")

            elif sheet_name == "Channels by Engagement Rate ":
                # Engagement rate by platform
                for _, r in df.iterrows():
                    try:
                        platform_name = r.get("social_network", "Unknown")
                        key = (platform_name, "2024")  # Annual data
                        if key not in merged_data:
                            merged_data[key] = {
                                "platform": platform_name,
                                "period_month": "2024",
                                "followers": 0,
                                "impressions": 0,
                                "engagement_rate": 0.0,
                            }
                        eng_rate_str = str(r.get("engagement_rate_in_pct", "0%")).rstrip('%').strip()
                        eng_rate = float(eng_rate_str) / 100 if eng_rate_str else 0.0
                        merged_data[key]["engagement_rate"] = eng_rate
                    except Exception as e:
                        print(f"Error processing row in {sheet_name}: {e}")

            elif sheet_name == "Top Changes in Followers":
                # Quarterly follower data by platform
                for _, r in df.iterrows():
                    try:
                        platform_name = r.get("social_network", "Unknown")
                        quarter_str = r.get("date", "").strip()
                        if "," in quarter_str:
                            quarter, year = quarter_str.split(", ")
                            q_num = quarter.split(" ")[1]
                            period_month = f"{year.strip()}-Q{q_num}"
                            key = (platform_name, period_month)
                            if key not in merged_data:
                                merged_data[key] = {
                                    "platform": platform_name,
                                    "period_month": period_month,
                                    "followers": 0,
                                    "impressions": 0,
                                    "engagement_rate": 0.0,
                                }
                            followers = int(float(r.get("followers_sum", 0))) if r.get("followers_sum") else 0
                            merged_data[key]["followers"] = followers
                    except Exception as e:
                        print(f"Error processing row in {sheet_name}: {e}")

        # Convert merged data to DataFrame
        all_rows = list(merged_data.values())
        transformed_df = pd.DataFrame(all_rows)

        return transformed_df

    def transform_engagement_daily(self, data: dict) -> pd.DataFrame:
        """Transform daily engagement data from multiple sheets."""
        daily_data = []

        for sheet_name, df in data.items():
            if df.empty:
                continue

            df.columns = [str(c).strip().lower().replace(" ", "_").replace("(", "").replace(")", "").replace("%", "pct") for c in df.columns]

            if sheet_name == "Brand Post vs Total Engageme":
                # Daily posts published vs total engagements
                for _, r in df.iterrows():
                    try:
                        daily_data.append({
                            "date": pd.to_datetime(r.get("date")).date() if r.get("date") else None,
                            "posts_published": int(float(r.get("volume_of_published_messages_sum", 0))) if r.get("volume_of_published_messages_sum") else 0,
                            "total_engagements": int(float(r.get("total_engagements_sum", 0))) if r.get("total_engagements_sum") else 0,
                            "likes_reactions": 0,
                            "comments": 0,
                            "shares": 0,
                            "estimated_clicks": 0,
                            "reach": 0
                        })
                    except Exception as e:
                        print(f"Error processing daily engagement row in {sheet_name}: {e}")

            elif sheet_name == "Engagement Behaviour across ":
                # Daily engagement breakdown
                for _, r in df.iterrows():
                    try:
                        date_val = pd.to_datetime(r.get("date")).date() if r.get("date") else None
                        # Find existing entry for this date or create new one
                        existing_entry = None
                        for entry in daily_data:
                            if entry["date"] == date_val:
                                existing_entry = entry
                                break

                        if existing_entry:
                            # Update existing entry
                            existing_entry.update({
                                "total_engagements": int(float(r.get("total_engagements", 0))) if r.get("total_engagements") else 0,
                                "likes_reactions": int(float(r.get("post_likes_and_reactions", 0))) if r.get("post_likes_and_reactions") else 0,
                                "comments": int(float(r.get("post_comments", 0))) if r.get("post_comments") else 0,
                                "shares": int(float(r.get("post_shares", 0))) if r.get("post_shares") else 0,
                                "estimated_clicks": int(float(r.get("estimated_clicks", 0))) if r.get("estimated_clicks") else 0,
                                "reach": int(float(r.get("post_reach", 0))) if r.get("post_reach") else 0
                            })
                        else:
                            # Create new entry
                            daily_data.append({
                                "date": date_val,
                                "posts_published": 0,
                                "total_engagements": int(float(r.get("total_engagements", 0))) if r.get("total_engagements") else 0,
                                "likes_reactions": int(float(r.get("post_likes_and_reactions", 0))) if r.get("post_likes_and_reactions") else 0,
                                "comments": int(float(r.get("post_comments", 0))) if r.get("post_comments") else 0,
                                "shares": int(float(r.get("post_shares", 0))) if r.get("post_shares") else 0,
                                "estimated_clicks": int(float(r.get("estimated_clicks", 0))) if r.get("estimated_clicks") else 0,
                                "reach": int(float(r.get("post_reach", 0))) if r.get("post_reach") else 0
                            })
                    except Exception as e:
                        print(f"Error processing daily engagement row in {sheet_name}: {e}")

        return pd.DataFrame(daily_data)

    def transform_engagement_posts(self, data: dict) -> pd.DataFrame:
        """Transform post-level engagement data."""
        posts_data = []

        for sheet_name, df in data.items():
            if df.empty:
                continue

            df.columns = [str(c).strip().lower().replace(" ", "_").replace("(", "").replace(")", "").replace("%", "pct") for c in df.columns]

            if sheet_name == "Posts":
                # Individual post engagement data
                for _, r in df.iterrows():
                    try:
                        posts_data.append({
                            "date": None,  # Posts sheet doesn't have dates
                            "post_content": str(r.get("outbound_post", "")).strip(),
                            "total_engagements": int(float(r.get("total_engagements_sum", 0))) if r.get("total_engagements_sum") else 0,
                            "likes_reactions": int(float(r.get("post_likes_and_reactions_sum", 0))) if r.get("post_likes_and_reactions_sum") else 0,
                            "comments": int(float(r.get("post_comments_sum", 0))) if r.get("post_comments_sum") else 0,
                            "shares": int(float(r.get("post_shares_sum", 0))) if r.get("post_shares_sum") else 0,
                            "estimated_clicks": int(float(r.get("estimated_clicks_sum", 0))) if r.get("estimated_clicks_sum") else 0,
                            "reach": int(float(r.get("post_reach_sum", 0))) if r.get("post_reach_sum") else 0
                        })
                    except Exception as e:
                        print(f"Error processing post engagement row in {sheet_name}: {e}")

            elif sheet_name == "Post Engagement Scorecard":
                # Dated post engagement data
                for _, r in df.iterrows():
                    try:
                        posts_data.append({
                            "date": pd.to_datetime(r.get("date")).date() if r.get("date") else None,
                            "post_content": str(r.get("outbound_post", "")).strip(),
                            "total_engagements": int(float(r.get("total_engagements_sum", 0))) if r.get("total_engagements_sum") else 0,
                            "likes_reactions": int(float(r.get("post_likes_and_reactions_sum", 0))) if r.get("post_likes_and_reactions_sum") else 0,
                            "comments": int(float(r.get("post_comments_sum", 0))) if r.get("post_comments_sum") else 0,
                            "shares": int(float(r.get("post_shares_sum", 0))) if r.get("post_shares_sum") else 0,
                            "estimated_clicks": int(float(r.get("estimated_clicks_sum", 0))) if r.get("estimated_clicks_sum") else 0,
                            "reach": int(float(r.get("post_reach_sum", 0))) if r.get("post_reach_sum") else 0
                        })
                    except Exception as e:
                        print(f"Error processing post engagement row in {sheet_name}: {e}")

        return pd.DataFrame(posts_data)

    def load(self, df: pd.DataFrame):
        """Load performance data into DB table."""
        if self.db_engine is None:
            raise ValueError("❌ DB engine not initialized")

        # For social media performance data, replace existing data
        df.to_sql("social_media_performance", self.db_engine, if_exists="replace", index=False)
        print(f"✅ Loaded {len(df)} rows into social_media_performance")

    def load_engagement_daily(self, df: pd.DataFrame):
        """Load daily engagement data into DB table."""
        if self.db_engine is None:
            raise ValueError("❌ DB engine not initialized")

        # Load daily engagement data
        df.to_sql("social_media_engagement_daily", self.db_engine, if_exists="replace", index=False)
        print(f"✅ Loaded {len(df)} rows into social_media_engagement_daily")

    def load_engagement_posts(self, df: pd.DataFrame):
        """Load post-level engagement data into DB table."""
        if self.db_engine is None:
            raise ValueError("❌ DB engine not initialized")

        # Load post-level engagement data
        df.to_sql("social_media_engagement_posts", self.db_engine, if_exists="replace", index=False)
        print(f"✅ Loaded {len(df)} rows into social_media_engagement_posts")

    def run(self):
        """Execute full ETL pipeline for all social media data."""
        print("📥 Extracting social media performance data...")
        performance_data = self.extract()

        print("📥 Extracting social media engagement data...")
        engagement_data = self.extract_engagement()

        print("⚙️ Transforming performance data...")
        performance_df = self.transform(performance_data)

        print("⚙️ Transforming daily engagement data...")
        daily_engagement_df = self.transform_engagement_daily(engagement_data)

        print("⚙️ Transforming post-level engagement data...")
        posts_engagement_df = self.transform_engagement_posts(engagement_data)

        if self.db_engine:
            print("🗄️ Loading to DB...")
            self.load(performance_df)
            self.load_engagement_daily(daily_engagement_df)
            self.load_engagement_posts(posts_engagement_df)
        else:
            print("⚠️ DB engine not provided. Returning DataFrames only.")

        return {
            "performance": performance_df,
            "engagement_daily": daily_engagement_df,
            "engagement_posts": posts_engagement_df
        }
