"""
ORACLE-26 — Sports Data Collection
====================================
Pulls and caches:
  1. Full international results (martj42 dataset)
  2. World Cup historical results (filtered)
  3. Live Elo ratings (eloratings.net)
  4. Team-level recent match stats

Usage:
    python src/data/sports.py
    # or import:
    from src.data.sports import SportsDataCollector
    collector = SportsDataCollector()
    collector.run()
"""

import os
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Allow running as script from project root
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import (
    ALL_TEAMS, WC2026_GROUPS, TEAM_TO_RESULTS_NAME,
    CURATED_ELO, LOOKBACK_DAYS, STAGE_WEIGHTS, TEAM_TO_GROUP
)

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────
# Data Sources
# ─────────────────────────────────────────────
RESULTS_SOURCES = [
    # Primary: martj42 international results dataset
    "https://raw.githubusercontent.com/martj42/international_results/master/results.csv",
    # Mirror 1: jsDelivr CDN
    "https://cdn.jsdelivr.net/gh/martj42/international_results@master/results.csv",
]

ELO_SOURCES = [
    "https://eloratings.net/World.tsv",
]


class SportsDataCollector:
    """
    Handles all sports-domain data collection for ORACLE-26.
    Fetches, validates, and caches raw data to data/raw/.
    """

    def __init__(self, force_refresh: bool = False):
        self.force_refresh = force_refresh
        self.results_df: pd.DataFrame | None = None
        self.elo_df: pd.DataFrame | None = None
        self.wc_df: pd.DataFrame | None = None

    # ─────────────────────────────────────────
    # 1. International Results
    # ─────────────────────────────────────────

    def fetch_results(self) -> pd.DataFrame:
        """
        Fetch complete international football results (1872–2026).
        Tries multiple sources, falls back to cached if all fail.
        Returns DataFrame with columns:
            date, home_team, away_team, home_score, away_score,
            tournament, city, country, neutral
        """
        cache_path = RAW_DIR / "international_results.csv"

        if not self.force_refresh and cache_path.exists():
            age_hours = (time.time() - cache_path.stat().st_mtime) / 3600
            if age_hours < 48:
                print(f"  [results] Loading from cache ({age_hours:.0f}h old)")
                df = pd.read_csv(cache_path, parse_dates=["date"])
                self.results_df = df
                return df

        print("  [results] Fetching from remote sources...")
        df = None
        for url in RESULTS_SOURCES:
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                from io import StringIO
                df = pd.read_csv(StringIO(response.text), parse_dates=["date"])
                print(f"  [results] ✓ Fetched {len(df):,} rows from {url[:60]}...")
                break
            except Exception as e:
                print(f"  [results] ✗ Failed: {url[:60]} — {e}")
                continue

        if df is None:
            if cache_path.exists():
                print("  [results] All sources failed — using cached data")
                df = pd.read_csv(cache_path, parse_dates=["date"])
            else:
                raise RuntimeError(
                    "Cannot fetch international results and no cache exists. "
                    "Check internet connection."
                )

        # Clean & validate
        df = self._clean_results(df)
        df.to_csv(cache_path, index=False)
        print(f"  [results] Saved {len(df):,} rows to {cache_path}")
        self.results_df = df
        return df

    def _clean_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean results dataframe."""
        required_cols = ["date", "home_team", "away_team", "home_score", "away_score", "tournament"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Results missing columns: {missing}")

        df = df.dropna(subset=["home_score", "away_score"])
        df["home_score"] = df["home_score"].astype(int)
        df["away_score"] = df["away_score"].astype(int)
        df["date"] = pd.to_datetime(df["date"])
        df = df[df["date"] >= "1990-01-01"].copy()   # Only modern era
        df = df.sort_values("date").reset_index(drop=True)
        return df

    # ─────────────────────────────────────────
    # 2. World Cup Historical Results
    # ─────────────────────────────────────────

    def filter_wc_results(self) -> pd.DataFrame:
        """Filter results to World Cup matches only (1990–2022)."""
        if self.results_df is None:
            self.fetch_results()

        wc_df = self.results_df[
            self.results_df["tournament"] == "FIFA World Cup"
        ].copy()

        cache_path = RAW_DIR / "wc_historical.csv"
        wc_df.to_csv(cache_path, index=False)
        print(f"  [wc] {len(wc_df)} World Cup matches saved to {cache_path}")
        self.wc_df = wc_df
        return wc_df

    # ─────────────────────────────────────────
    # 3. Elo Ratings
    # ─────────────────────────────────────────

    def fetch_elo(self) -> pd.DataFrame:
        """
        Fetch current national team Elo ratings from eloratings.net.
        Falls back to curated values if fetch fails.
        Returns DataFrame: team, elo, rank
        """
        cache_path = RAW_DIR / "elo_ratings.csv"

        if not self.force_refresh and cache_path.exists():
            age_hours = (time.time() - cache_path.stat().st_mtime) / 3600
            if age_hours < 48:
                print(f"  [elo] Loading from cache ({age_hours:.0f}h old)")
                df = pd.read_csv(cache_path)
                self.elo_df = df
                return df

        print("  [elo] Fetching from eloratings.net...")
        df = None
        for url in ELO_SOURCES:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                lines = response.text.strip().split("\n")
                rows = []
                for i, line in enumerate(lines[1:], 1):
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        rows.append({
                            "rank": i,
                            "team": parts[1].strip(),
                            "elo": float(parts[2].strip()),
                        })
                if rows:
                    df = pd.DataFrame(rows)
                    print(f"  [elo] ✓ Fetched {len(df)} teams from eloratings.net")
                    break
            except Exception as e:
                print(f"  [elo] ✗ Failed: {url} — {e}")

        if df is None:
            print("  [elo] Using curated fallback Elo values")
            df = pd.DataFrame([
                {"rank": i + 1, "team": team, "elo": elo}
                for i, (team, elo) in enumerate(
                    sorted(CURATED_ELO.items(), key=lambda x: -x[1])
                )
            ])

        # Ensure all WC2026 teams are present
        existing_teams = set(df["team"].tolist())
        for team, elo in CURATED_ELO.items():
            if team not in existing_teams:
                new_row = pd.DataFrame([{"rank": 999, "team": team, "elo": elo}])
                df = pd.concat([df, new_row], ignore_index=True)

        df.to_csv(cache_path, index=False)
        print(f"  [elo] Saved {len(df)} teams to {cache_path}")
        self.elo_df = df
        return df

    # ─────────────────────────────────────────
    # 4. Head-to-Head Records
    # ─────────────────────────────────────────

    def build_h2h(self, years: int = 10) -> pd.DataFrame:
        """
        Build head-to-head record for every WC2026 team pair.
        Returns DataFrame: team1, team2, h2h_win_rate_team1, h2h_matches
        """
        if self.results_df is None:
            self.fetch_results()

        cutoff = datetime.now() - timedelta(days=years * 365)
        recent = self.results_df[self.results_df["date"] >= cutoff]

        rows = []
        for i, t1 in enumerate(ALL_TEAMS):
            for t2 in ALL_TEAMS[i + 1:]:
                t1_name = TEAM_TO_RESULTS_NAME.get(t1, t1)
                t2_name = TEAM_TO_RESULTS_NAME.get(t2, t2)

                mask = (
                    ((recent["home_team"] == t1_name) & (recent["away_team"] == t2_name)) |
                    ((recent["home_team"] == t2_name) & (recent["away_team"] == t1_name))
                )
                h2h = recent[mask]

                if len(h2h) == 0:
                    rows.append({"team1": t1, "team2": t2, "h2h_matches": 0,
                                 "h2h_win_rate_team1": 0.5, "h2h_draws": 0})
                    continue

                wins_t1 = 0
                draws = 0
                for _, row in h2h.iterrows():
                    if row["home_team"] == t1_name:
                        gf, ga = row["home_score"], row["away_score"]
                    else:
                        gf, ga = row["away_score"], row["home_score"]
                    if gf > ga:
                        wins_t1 += 1
                    elif gf == ga:
                        draws += 1

                n = len(h2h)
                rows.append({
                    "team1": t1,
                    "team2": t2,
                    "h2h_matches": n,
                    "h2h_win_rate_team1": round((wins_t1 + 0.5 * draws) / n, 3),
                    "h2h_draws": draws,
                })

        df = pd.DataFrame(rows)
        cache_path = RAW_DIR / "h2h_records.csv"
        df.to_csv(cache_path, index=False)
        print(f"  [h2h] Built {len(df)} team pair records → {cache_path}")
        return df

    # ─────────────────────────────────────────
    # 5. Run Full Collection
    # ─────────────────────────────────────────

    def run(self):
        """Run all data collection steps."""
        print("\n" + "=" * 55)
        print("ORACLE-26 | Phase 1 — Sports Data Collection")
        print("=" * 55)

        print("\n[1/4] International results...")
        self.fetch_results()

        print("\n[2/4] World Cup historical results...")
        self.filter_wc_results()

        print("\n[3/4] Elo ratings...")
        self.fetch_elo()

        print("\n[4/4] Head-to-head records...")
        self.build_h2h()

        print("\n✅ Sports data collection complete")
        print(f"   Files saved to: {RAW_DIR.resolve()}")


# ─────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ORACLE-26 Sports Data Collector")
    parser.add_argument("--force", action="store_true", help="Force refresh (ignore cache)")
    args = parser.parse_args()
    collector = SportsDataCollector(force_refresh=args.force)
    collector.run()