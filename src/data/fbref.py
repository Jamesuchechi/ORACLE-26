"""
ORACLE-26 — FBref Data Scraper
================================
Uses the soccerdata library to pull advanced team stats from FBref.
Focuses on: xG, xGA, Possession, and Shooting stats (2022–2026).
"""

import os
import time
import pandas as pd
import soccerdata as sd
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import ALL_TEAMS

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

class FBrefScraper:
    """
    Scraper for advanced football metrics from FBref.
    Uses soccerdata under the hood.
    """

    def __init__(self, seasons: Optional[list] = None):
        self.seasons = seasons or ["2022", "2023", "2024"]
        # Note: soccerdata caches its own results in ~/.soccerdata
        self.fbref = sd.FBref(leagues="Intl: World Cup", seasons=self.seasons)

    def scrape_team_stats(self):
        """Fetch team-level advanced stats."""
        print(f"  [fbref] Scraping advanced stats for seasons: {self.seasons}...")
        
        try:
            # Get squad-level stats
            stats = self.fbref.read_team_stats(stat_type="standard")
            
            # Clean and filter
            stats = stats.reset_index()
            
            # Save to raw data
            out_path = DATA_DIR / "fbref_team_stats.csv"
            stats.to_csv(out_path, index=False)
            print(f"  [fbref] ✓ Saved stats to {out_path}")
            return stats
            
        except Exception as e:
            print(f"  [fbref] ✗ Scraping failed: {e}")
            print("  [fbref] Falling back to proxy metrics in feature engineer.")
            return None

if __name__ == "__main__":
    scraper = FBrefScraper()
    scraper.scrape_team_stats()
