"""
◈ CONFLUX — Climate Signal
============================
Fetches and processes climate and energy signals for:
  - Vertical I (WC2026): venue heat/altitude stress per match
  - Vertical III: regional climate risk intelligence
"""

import requests
import pandas as pd
import numpy as np
import time
import concurrent.futures
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import (
    WC2026_VENUES, TRACKED_CLIMATE_REGIONS,
    HEAT_STRESS_THRESHOLDS, ALTITUDE_THRESHOLDS
)

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


class ClimateSignalEngine:
    """
    Fetches climate data and converts it into normalized [0,1] stress signals.
    Signal = 1.0 (ideal conditions) → 0.0 (extreme stress)
    """

    def fetch_venue_climate(self, lat: float, lon: float, venue_name: str) -> dict:
        """
        Fetch June–July climate normals from Open-Meteo climate API.
        Returns avg max temp, avg humidity, and computed stress metrics.
        """
        try:
            url = (
                f"https://climate-api.open-meteo.com/v1/climate"
                f"?latitude={lat}&longitude={lon}"
                f"&start_date=2025-06-15&end_date=2025-07-15"
                f"&models=ERA5"
                f"&daily=temperature_2m_max,relative_humidity_2m_mean"
            )
            resp = requests.get(url, timeout=10)
            data = resp.json()

            if "daily" in data:
                temps  = [t for t in data["daily"]["temperature_2m_max"] if t is not None]
                humids = [h for h in data["daily"]["relative_humidity_2m_mean"] if h is not None]
                return {
                    "avg_temp_c":    round(np.mean(temps), 1) if temps else 25.0,
                    "avg_humidity":  round(np.mean(humids), 1) if humids else 60.0,
                    "source":        "open-meteo-era5",
                }
        except Exception as e:
            print(f"  [climate] Open-Meteo failed for {venue_name}: {e}")

        # Deterministic fallback based on latitude/region
        return self._synthetic_climate(lat, lon)

    def _synthetic_climate(self, lat: float, lon: float) -> dict:
        """Generate plausible June-July climate from latitude."""
        # Rough heuristic: more tropical = hotter and more humid
        base_temp = 30 - abs(lat - 20) * 0.4
        humidity  = 80 - abs(lat - 15) * 0.8
        return {
            "avg_temp_c":   round(float(np.clip(base_temp, 10, 42)), 1),
            "avg_humidity": round(float(np.clip(humidity, 30, 95)), 1),
            "source":       "synthetic-latitude-heuristic",
        }

    def compute_heat_stress_penalty(self, temp_c: float, humidity: float) -> float:
        """
        Map temperature + humidity to a performance penalty coefficient.
        Returns 0.0 (extreme stress) to 1.0 (ideal conditions).
        """
        # Heat index approximation
        hi = temp_c + 0.33 * (humidity / 100 * 6.105 * np.exp(17.27 * temp_c / (237.7 + temp_c))) - 4.0

        for label, thresh in HEAT_STRESS_THRESHOLDS.items():
            if temp_c <= thresh["max_temp"] and humidity <= thresh["max_humidity"]:
                return 1.0 - thresh["penalty"]

        return 1.0 - HEAT_STRESS_THRESHOLDS["extreme"]["penalty"]

    def compute_altitude_penalty(self, altitude_m: float) -> float:
        """Map altitude to a performance penalty coefficient."""
        for label, thresh in ALTITUDE_THRESHOLDS.items():
            if altitude_m <= thresh["max_m"]:
                return 1.0 - thresh["penalty"]
        return 1.0 - ALTITUDE_THRESHOLDS["extreme"]["penalty"]

    def venue_climate_signal(self, venue_name: str) -> dict:
        """
        Compute the full climate signal for a single WC venue.
        Returns normalized signal and breakdown.
        """
        info = WC2026_VENUES.get(venue_name, {})
        if not info:
            return {"venue": venue_name, "climate_signal": 0.7}

        climate = self.fetch_venue_climate(info["lat"], info["lon"], venue_name)

        heat_ok  = self.compute_heat_stress_penalty(climate["avg_temp_c"], climate["avg_humidity"])
        alt_ok   = self.compute_altitude_penalty(info.get("altitude_m", 0))

        # Combined: heat and altitude both reduce performance
        climate_signal = heat_ok * alt_ok

        return {
            "venue":           venue_name,
            "city":            info.get("city", ""),
            "avg_temp_c":      climate["avg_temp_c"],
            "avg_humidity":    climate["avg_humidity"],
            "altitude_m":      info.get("altitude_m", 0),
            "heat_stress":     round(1 - heat_ok, 3),
            "altitude_stress": round(1 - alt_ok, 3),
            "climate_signal":  round(float(climate_signal), 4),
            "source":          climate["source"],
        }

    def build_venue_signals(self) -> pd.DataFrame:
        """Build climate signal table for all WC2026 venues in parallel."""
        print("  [climate] Building venue climate signals in parallel...")
        
        rows = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_venue = {executor.submit(self.venue_climate_signal, v): v for v in WC2026_VENUES.keys()}
            for future in concurrent.futures.as_completed(future_to_venue):
                rows.append(future.result())

        df = pd.DataFrame(rows).sort_values("climate_signal")
        df.to_csv(RAW_DIR / "venue_climate_signals.csv", index=False)
        print(f"  [climate] Saved {len(df)} venue signals")
        return df

    # ──────────────────────────────────────────────
    # Vertical III: Regional Climate Risk
    # ──────────────────────────────────────────────

    def fetch_energy_grid_stress(self, region: str) -> float:
        """
        Estimate energy grid stress based on climate load.
        In production, this would pull from EIA or regional grid operators.
        """
        info = TRACKED_CLIMATE_REGIONS.get(region, {})
        if not info: return 0.5
        
        # Pull current temp for the region
        climate = self.fetch_venue_climate(info["lat"], info["lon"], region)
        temp = climate["avg_temp_c"]
        
        # High heat stress (>32C) or extreme cold triggers grid stress
        stress = 0.2
        if temp > 32: stress += (temp - 32) * 0.1
        if temp < 5:  stress += (5 - temp) * 0.1
        
        return float(np.clip(stress, 0.1, 0.95))

    def compute_regional_risk(self, region: str) -> dict:
        """
        Compute climate risk score for a tracked region.
        Signal 0 = low risk, 1 = extreme risk.
        """
        info = TRACKED_CLIMATE_REGIONS.get(region, {})
        if not info:
            return {"region": region, "climate_risk_signal": 0.5}

        climate = self.fetch_venue_climate(info["lat"], info["lon"], region)
        grid_stress = self.fetch_energy_grid_stress(region)

        # For risk: high temp + high humidity = HIGH risk
        temp_risk = float(np.clip((climate["avg_temp_c"] - 20) / 25, 0, 1))
        hum_risk  = float(np.clip((climate["avg_humidity"] - 50) / 50, 0, 1))

        risk_types = {
            "heat_grid":   temp_risk * 0.5 + hum_risk * 0.2 + grid_stress * 0.3,
            "wildfire":    temp_risk * 0.7 + hum_risk * 0.1 + grid_stress * 0.2,
            "hurricane":   hum_risk  * 0.5 + temp_risk * 0.3 + grid_stress * 0.2,
            "flooding":    hum_risk  * 0.6 + temp_risk * 0.2 + grid_stress * 0.2,
            "heat_stress": temp_risk * 0.6 + hum_risk * 0.4,
            "drought":     temp_risk * 0.4 + (1 - hum_risk) * 0.4 + grid_stress * 0.2,
        }
        raw_risk = risk_types.get(info["risk_type"], 0.5)

        return {
            "region":              region,
            "risk_type":           info["risk_type"],
            "avg_temp_c":          climate["avg_temp_c"],
            "avg_humidity":        climate["avg_humidity"],
            "grid_stress":         round(grid_stress, 4),
            "raw_risk_score":      round(raw_risk, 4),
            "climate_risk_signal": round(raw_risk, 4),  # 0=safe, 1=extreme risk
        }

    def build_regional_risks(self) -> pd.DataFrame:
        """Build climate risk table for all tracked regions in parallel."""
        print("  [climate] Building regional risk signals in parallel...")
        
        rows = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_region = {executor.submit(self.compute_regional_risk, r): r for r in TRACKED_CLIMATE_REGIONS.keys()}
            for future in concurrent.futures.as_completed(future_to_region):
                rows.append(future.result())

        df = pd.DataFrame(rows).sort_values("climate_risk_signal", ascending=False)
        df.to_csv(RAW_DIR / "regional_climate_risks.csv", index=False)
        return df

    def run(self):
        print("\n" + "=" * 50)
        print("◈ CONFLUX | Climate Signal Collection")
        print("=" * 50)
        venues  = self.build_venue_signals()
        regions = self.build_regional_risks()
        return {"venues": venues, "regions": regions}


if __name__ == "__main__":
    engine  = ClimateSignalEngine()
    results = engine.run()
    print("\nVenue climate signals:")
    print(results["venues"][["venue", "avg_temp_c", "altitude_m", "climate_signal"]].to_string(index=False))
    print("\nRegional risk signals:")
    print(results["regions"][["region", "risk_type", "raw_risk_score"]].to_string(index=False))