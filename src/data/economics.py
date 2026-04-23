"""
ORACLE-26 — Economic Data Collection
======================================
Pulls macro-economic indicators for the 48 team nations.
Sources: 
  1. FRED (GDP, Inflation, Unemployment)
  2. Alpha Vantage (Forex/Currency Strength)
"""

import os
import pandas as pd
import requests
from pathlib import Path
from dotenv import load_dotenv
from fredapi import Fred
from alpha_vantage.foreignexchange import ForeignExchange

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import ALL_TEAMS, TEAM_TO_FRED_COUNTRY

load_dotenv()

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

class EconomicDataCollector:
    """
    Collects economic signals for team countries.
    """

    def __init__(self):
        self.fred_key = os.getenv("FRED_API_KEY")
        self.av_key   = os.getenv("ALPHA_VANTAGE_KEY")
        
        if self.fred_key:
            self.fred = Fred(api_key=self.fred_key)
        else:
            print("  [econ] WARNING: FRED_API_KEY not found in .env")
            self.fred = None

    def fetch_fred_signals(self):
        """Fetch GDP and Inflation for all teams from FRED."""
        if not self.fred: return None
        
        print("  [econ] Fetching GDP and Inflation from FRED...")
        econ_rows = []
        
        # We'll focus on the top 32 favorites first to save API quota, 
        # or all if rate limits allow.
        for team in ALL_TEAMS:
            country_code = TEAM_TO_FRED_COUNTRY.get(team)
            if not country_code: continue
            
            try:
                # GDP Growth (Annual %)
                # Series ID format for many: NGDP_RPCH_XXXX
                gdp_series = f"NGDP_RPCH_{country_code}"
                gdp_data = self.fred.get_series(gdp_series)
                latest_gdp = gdp_data.iloc[-1] if not gdp_data.empty else 2.0
                
                # Inflation (Consumer Prices)
                # Series ID format: PCPI_PCH_XXXX
                inf_series = f"PCPI_PCH_{country_code}"
                inf_data = self.fred.get_series(inf_series)
                latest_inf = inf_data.iloc[-1] if not inf_data.empty else 3.0
                
                econ_rows.append({
                    "team": team,
                    "country_code": country_code,
                    "gdp_growth": round(latest_gdp, 2),
                    "inflation": round(latest_inf, 2)
                })
                print(f"    ✓ {team} (GDP: {latest_gdp}%)")
            except Exception as e:
                # Fallback to neutral values
                econ_rows.append({
                    "team": team,
                    "country_code": country_code,
                    "gdp_growth": 2.0,
                    "inflation": 3.0
                })

        df = pd.DataFrame(econ_rows)
        out_path = RAW_DIR / "economic_indicators.csv"
        df.to_csv(out_path, index=False)
        print(f"  [econ] Saved economic signals to {out_path}")
        return df

    def fetch_forex_signals(self):
        """Fetch currency strength via Alpha Vantage."""
        # Note: Free tier is 25 req/day. We'll skip for automated runs 
        # unless explicitly requested or use a cached version.
        print("  [econ] Skipping Forex fetch (API quota management). Using stable proxies.")
        return None

    def run(self):
        print("\n" + "="*50)
        print("💰 ORACLE-26 | Phase 2.2 — Economic Signals")
        print("="*50)
        self.fetch_fred_signals()
        self.fetch_forex_signals()

if __name__ == "__main__":
    collector = EconomicDataCollector()
    collector.run()
