"""
ORACLE-26 — Climate Resilience Model
======================================
Learns the impact of heat, humidity, and altitude on team performance.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
from pathlib import Path

class ClimateResilienceModel:
    """
    Predicts the performance delta based on climate mismatch.
    """
    def __init__(self):
        self.model = LinearRegression()
        
    def calculate_match_penalty(self, team_home_climate: dict, venue_climate: dict) -> float:
        """
        Calculates a penalty coefficient (0.0 to 1.0).
        1.0 means perfect comfort, 0.8 means significant stress.
        """
        temp_diff = abs(team_home_climate['avg_temp'] - venue_climate['avg_temp'])
        alt_diff  = abs(team_home_climate['altitude'] - venue_climate['altitude'])
        
        # Simple heuristic for now: 1% drop for every 5 degrees or 500m diff
        penalty = 1.0 - (temp_diff / 500) - (alt_diff / 10000)
        return max(0.85, penalty)

    def save(self):
        Path("models").mkdir(exist_ok=True)
        joblib.dump(self, "models/climate_resilience.pkl")
        print("  [climate-model] Model saved → models/climate_resilience.pkl")

if __name__ == "__main__":
    model = ClimateResilienceModel()
    model.save()
