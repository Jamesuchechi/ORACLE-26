"""
ORACLE-26 — Historical Economic Data Extractor (World Bank)
============================================================
Fetches historical macro stats for WC nations (1960–2022).
Source: World Bank API (via wbgapi)
"""

import pandas as pd
import wbgapi as wb
from pathlib import Path
import os

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import TEAM_TO_FRED_COUNTRY

class WorldBankFetcher:
    def __init__(self):
        # We use the same country codes (ISO3) from our constants
        self.indicators = {
            'gdp_growth': 'NY.GDP.MKTP.KD.ZG',
            'inflation':  'FP.CPI.TOTL.ZG'
        }
        
    def fetch_all(self):
        print("  [econ-data] Fetching historical data from World Bank...")
        
        # Historical WC Years
        wc_years = [1966, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022]
        
        # Get ISO3 codes
        iso3_codes = list(TEAM_TO_FRED_COUNTRY.values())
        
        try:
            # Fetch GDP Growth
            print("    Fetching GDP Growth...")
            gdp_data = wb.data.DataFrame(self.indicators['gdp_growth'], iso3_codes, time=wc_years, labels=True)
            
            # Fetch Inflation
            print("    Fetching Inflation...")
            inf_data = wb.data.DataFrame(self.indicators['inflation'], iso3_codes, time=wc_years, labels=True)
            
            # Flatten the data
            all_data = []
            for team, iso3 in TEAM_TO_FRED_COUNTRY.items():
                try:
                    # wbgapi returns years as 'YR1966' etc.
                    for year in wc_years:
                        yr_col = f"YR{year}"
                        gdp = gdp_data.loc[iso3][yr_col] if iso3 in gdp_data.index else None
                        inf = inf_data.loc[iso3][yr_col] if iso3 in inf_data.index else None
                        
                        if pd.notnull(gdp) or pd.notnull(inf):
                            all_data.append({
                                "team": team,
                                "year": year,
                                "gdp_growth": gdp,
                                "inflation": inf
                            })
                except:
                    continue
                    
            df = pd.DataFrame(all_data)
            base_dir = Path(__file__).resolve().parents[2]
            out_path = base_dir / "data/raw/historical_economic_data.csv"
            df.to_csv(out_path, index=False)
            print(f"  [econ-data] ✓ Saved {len(df)} records to {out_path}")
            return df
            
        except Exception as e:
            print(f"  [econ-data] ✗ Global Fetch Error: {e}")
            return None

if __name__ == "__main__":
    fetcher = WorldBankFetcher()
    fetcher.fetch_all()
