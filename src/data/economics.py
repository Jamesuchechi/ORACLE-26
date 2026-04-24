"""
◈ CONFLUX — Economic Signal
============================
Fetches macro indicators from FRED and World Bank.
Normalizes into [0,1] economic stability scores for all 48 team nations
and for general event analysis.
"""

import os
import numpy as np
import pandas as pd
import requests
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import ALL_WC_TEAMS, TEAM_TO_FRED_COUNTRY

load_dotenv()
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


class EconomicSignalEngine:
    """
    Builds economic stability scores for nations.
    Higher score = more stable, more resources, better performing macro.
    """

    WORLD_BANK_GDP_URL    = "https://api.worldbank.org/v2/country/{iso3}/indicator/NY.GDP.MKTP.KD.ZG?format=json&mrv=3"
    WORLD_BANK_INF_URL    = "https://api.worldbank.org/v2/country/{iso3}/indicator/FP.CPI.TOTL.ZG?format=json&mrv=3"

    def __init__(self):
        self.fred_key   = os.getenv("FRED_API_KEY")
        self.alpha_key  = os.getenv("ALPHA_VANTAGE_KEY")

    def fetch_fred_indicator(self, series_id: str) -> Optional[float]:
        """Fetch most recent value from FRED API."""
        if not self.fred_key: return None
        try:
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={self.fred_key}&file_type=json&sort_order=desc&limit=1"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if "observations" in data and data["observations"]:
                return float(data["observations"][0]["value"])
        except: return None
        return None

    def fetch_alpha_vantage_equity(self, symbol: str) -> Optional[float]:
        """Fetch daily return signal for a symbol from Alpha Vantage."""
        if not self.alpha_key: return None
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.alpha_key}"
            resp = requests.get(url, timeout=5)
            data = resp.json().get("Global Quote", {})
            if not data: return None
            # Return percentage change normalized
            change = float(data.get("10. change percent", "0%").strip("%"))
            return change
        except: return None
        return None


    def fetch_world_bank(self, iso3: str, indicator_url: str) -> Optional[float]:
        """Fetch most recent indicator value from World Bank API (free, no key)."""
        try:
            resp = requests.get(indicator_url.format(iso3=iso3), timeout=8)
            data = resp.json()
            if len(data) >= 2 and data[1]:
                vals = [d["value"] for d in data[1] if d.get("value") is not None]
                return float(vals[0]) if vals else None
        except:
            pass
        return None

    def score_nation(self, team: str) -> dict:
        """Compute economic signal score for a team's nation."""
        iso3 = TEAM_TO_FRED_COUNTRY.get(team)

        gdp_growth = None
        inflation  = None

        if iso3:
            gdp_growth = self.fetch_world_bank(iso3, self.WORLD_BANK_GDP_URL)
            inflation  = self.fetch_world_bank(iso3, self.WORLD_BANK_INF_URL)

        # Fallback: tier-based estimates from known economic status
        if gdp_growth is None:
            gdp_growth = self._tier_gdp(team)
        if inflation is None:
            inflation = self._tier_inflation(team)

        # Stability score:
        # High GDP growth (2-4%) = good, Negative = bad
        # Low inflation (1-3%) = good, High inflation = bad
        gdp_score = float(np.clip((gdp_growth + 2) / 8, 0, 1))
        inf_score = float(np.clip(1 - (inflation - 1) / 20, 0, 1))
        econ_signal = gdp_score * 0.55 + inf_score * 0.45

        return {
            "team":        team,
            "iso3":        iso3 or "UNK",
            "gdp_growth":  round(gdp_growth, 2),
            "inflation":   round(inflation, 2),
            "econ_signal": round(float(np.clip(econ_signal, 0, 1)), 4),
        }

    def _tier_gdp(self, team: str) -> float:
        high_income = {"USA","Germany","France","England","Spain","Portugal",
                       "Netherlands","Belgium","Norway","Austria","Switzerland","Australia","Japan","South Korea","Canada"}
        emerging    = {"Brazil","Mexico","Argentina","Colombia","Turkey","Serbia","Chile","Uruguay","Saudi Arabia","Qatar","Iran"}
        if team in high_income:
            return 2.2
        elif team in emerging:
            return 3.1
        else:
            return 4.0   # Lower income nations often show higher nominal GDP growth

    def _tier_inflation(self, team: str) -> float:
        stable = {"USA","Germany","France","England","Spain","Netherlands","Belgium",
                  "Norway","Austria","Switzerland","Canada","Australia","Japan","South Korea"}
        moderate = {"Brazil","Mexico","Colombia","Turkey","Serbia","Chile","Uruguay","Saudi Arabia"}
        if team in stable:
            return 2.8
        elif team in moderate:
            return 6.5
        else:
            return 8.0

    def build_all_signals(self) -> pd.DataFrame:
        """Build economic signal table for all 48 WC teams."""
        print("  [economics] Scoring all 48 team nations...")
        
        # Pull global macro baseline
        us_unemployment = self.fetch_fred_indicator("UNRATE") or 3.8
        sp500_momentum  = self.fetch_alpha_vantage_equity("SPY") or 0.12
        
        rows = []
        for team in ALL_WC_TEAMS:
            score_data = self.score_nation(team)
            # Adjust score based on global macro baseline
            if sp500_momentum > 0:
                score_data["econ_signal"] = float(np.clip(score_data["econ_signal"] + 0.02, 0, 1))
            
            rows.append(score_data)
            
        df = pd.DataFrame(rows).sort_values("econ_signal", ascending=False).reset_index(drop=True)
        df.to_csv(RAW_DIR / "economic_signals.csv", index=False)
        print(f"  [economics] Saved {len(df)} economic signals (Global Unemployment: {us_unemployment}%)")
        return df


    def run(self):
        print("\n" + "=" * 50)
        print("◈ CONFLUX | Economic Signal Collection")
        print("=" * 50)
        return self.build_all_signals()


if __name__ == "__main__":
    engine = EconomicSignalEngine()
    df = engine.run()
    print(df[["team","gdp_growth","inflation","econ_signal"]].head(15).to_string(index=False))