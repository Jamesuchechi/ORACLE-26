"""
ORACLE-26 — Climate Data Collection
=====================================
Fetches historical climate normals for WC2026 venues.
Source: Open-Meteo Climate API
"""

import pandas as pd
import requests
import time
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import WC2026_VENUES

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

class ClimateDataCollector:
    """
    Collects climate signals (temp, humidity) for all WC venues.
    """

    def fetch_venue_climate(self):
        """Fetch historical normals for June/July at each venue."""
        print("  [climate] Fetching historical climate data from Open-Meteo...")
        climate_rows = []
        
        for name, info in WC2026_VENUES.items():
            lat, lon = info["lat"], info["lon"]
            
            try:
                # We query for June 15 - July 15 (peak tournament)
                # Using the climate-api endpoint for historical normals
                url = f"https://climate-api.open-meteo.com/v1/climate?latitude={lat}&longitude={lon}&start_date=2025-06-15&end_date=2025-07-15&models=ERA5&daily=temperature_2m_max,relative_humidity_2m_mean"
                
                resp = requests.get(url, timeout=10)
                data = resp.json()
                
                if "daily" in data:
                    avg_max_temp = sum(data["daily"]["temperature_2m_max"]) / len(data["daily"]["temperature_2m_max"])
                    avg_humidity = sum(data["daily"]["relative_humidity_2m_mean"]) / len(data["daily"]["relative_humidity_2m_mean"])
                    
                    climate_rows.append({
                        "venue": name,
                        "city": info["city"],
                        "avg_temp_june_july": round(avg_max_temp, 2),
                        "avg_humidity": round(avg_humidity, 2),
                        "altitude_m": info.get("altitude_m", 0)
                    })
                    print(f"    ✓ {name} ({avg_max_temp:.1f}°C)")
                
                time.sleep(0.5) # Rate limiting respect
                
            except Exception as e:
                print(f"    ✗ Failed for {name}: {e}")

        df = pd.DataFrame(climate_rows)
        out_path = RAW_DIR / "venue_climate_signals.csv"
        df.to_csv(out_path, index=False)
        print(f"  [climate] Saved climate signals to {out_path}")
        return df

    def run(self):
        print("\n" + "="*50)
        print("🌍 ORACLE-26 | Phase 2.3 — Climate Signals")
        print("="*50)
        self.fetch_venue_climate()

if __name__ == "__main__":
    collector = ClimateDataCollector()
    collector.run()
