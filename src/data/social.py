"""
ORACLE-26 — Social & Cultural Trends
======================================
Tracks public attention and sentiment for all 48 teams.
Sources: 
  1. Google Trends (pytrends)
  2. Reddit (PRAW)
"""

import os
import pandas as pd
from pathlib import Path
from pytrends.request import TrendReq
from dotenv import load_dotenv

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import ALL_TEAMS

load_dotenv()

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

class SocialDataCollector:
    """
    Collects attention and sentiment signals from the web.
    """

    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)

    def fetch_google_trends(self):
        """Fetch search momentum for teams."""
        print("  [social] Fetching Google Trends momentum...")
        trend_rows = []
        
        # We'll batch teams to avoid rate limits
        for i in range(0, len(ALL_TEAMS), 5):
            batch = ALL_TEAMS[i:i+5]
            try:
                self.pytrends.build_payload(batch, timeframe='today 3-m')
                interest = self.pytrends.interest_over_time()
                
                for team in batch:
                    if team in interest.columns:
                        momentum = interest[team].mean()
                        trend_rows.append({"team": team, "search_momentum": round(momentum, 2)})
            except Exception as e:
                print(f"    ✗ Trends failed for batch {batch}: {e}")
                
        df = pd.DataFrame(trend_rows)
        return df

    def fetch_reddit_sentiment(self):
        """Fetch sentiment from Reddit (Simplified)."""
        print("  [social] Skipping Reddit API fetch (Auth required). Using baseline sentiment.")
        return pd.DataFrame([{"team": t, "sentiment_score": 0.5} for t in ALL_TEAMS])

    def run(self):
        print("\n" + "="*50)
        print("📣 ORACLE-26 | Phase 2.4 — Social Signals")
        print("="*50)
        trends_df = self.fetch_google_trends()
        reddit_df = self.fetch_reddit_sentiment()
        
        # Merge
        combined = pd.merge(trends_df, reddit_df, on="team", how="outer").fillna(0.5)
        out_path = RAW_DIR / "social_signals.csv"
        combined.to_csv(out_path, index=False)
        print(f"  [social] Saved social signals to {out_path}")

if __name__ == "__main__":
    collector = SocialDataCollector()
    collector.run()
