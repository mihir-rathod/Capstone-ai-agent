import pandas as pd
import sqlalchemy
from typing import Optional


class SocialMediaDataLoader:
    REQUIRED_TABS = ["Facebook", "Instagram", "YouTube", "TikTok", "Summary"]

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
        """Load only required tabs from workbook."""
        data = {}

        for sheet in self.REQUIRED_TABS:
            df = self._safe_read(sheet)
            if df.empty:
                print(f"⚠️ Sheet missing or empty: {sheet}")
            data[sheet] = df

        return data

    def transform(self, data: dict) -> pd.DataFrame:
        """Normalize and unify social performance metrics."""
        all_rows = []

        for platform, df in data.items():
            if df.empty:
                continue

            df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

            date_col = next((c for c in df.columns if "date" in c or "month" in c), None)
            if not date_col:
                date_col = "month"
                df[date_col] = pd.NA

            followers = next((c for c in df.columns if "follower" in c), None)
            impressions = next((c for c in df.columns if "impression" in c), None)
            engagements = next((c for c in df.columns if "engagement" in c and "rate" not in c), None)
            engagement_rate = next((c for c in df.columns if "engagement_rate" in c or c == "er"), None)
            video_views = next((c for c in df.columns if "view" in c), None)

            for _, r in df.iterrows():
                row = {
                    "platform": platform,
                    "period_month": r.get(date_col),
                    "followers": r.get(followers, 0) if followers else 0,
                    "impressions": r.get(impressions, 0) if impressions else 0,
                    "engagements": r.get(engagements, 0) if engagements else 0,
                    "video_views": r.get(video_views, 0) if video_views else 0,
                }

                if engagement_rate:
                    row["engagement_rate"] = r.get(engagement_rate)
                else:
                    try:
                        row["engagement_rate"] = (
                            (row["engagements"] / row["impressions"]) * 100
                            if row["impressions"] else 0
                        )
                    except Exception:
                        row["engagement_rate"] = 0

                all_rows.append(row)

        transformed_df = pd.DataFrame(all_rows)
        transformed_df["file_source"] = self.social_file

        return transformed_df

    def load(self, df: pd.DataFrame):
        """Load into DB table."""
        if self.db_engine is None:
            raise ValueError("❌ DB engine not initialized")

        df.to_sql("social_media_performance", self.db_engine, if_exists="append", index=False)
        print(f"✅ Loaded {len(df)} rows into social_media_performance")

    def run(self):
        """Execute full ETL pipeline."""
        print("📥 Extracting social media data...")
        data = self.extract()

        print("⚙️ Transforming data...")
        df = self.transform(data)

        if self.db_engine:
            print("🗄️ Loading to DB...")
            self.load(df)
        else:
            print("⚠️ DB engine not provided. Returning DataFrame only.")

        return df
