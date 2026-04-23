"""
ORACLE-26 — Market Calibration Model
======================================
Detects irrationalities and biases in prediction markets (Polymarket/Kalshi).
Identifies when the 'Wisdom of the Crowd' diverges from 'Statistical Reality'.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import joblib

class MarketCalibrationModel:
    """
    Learns to weigh market sentiment vs statistical models.
    """
    def __init__(self):
        self.model = LogisticRegression()
        
    def calculate_divergence_signal(self, model_prob: float, market_prob: float) -> float:
        """
        Calculates the Alpha signal.
        Positive: Market is under-valuing the team compared to stats.
        Negative: Market is over-hyping the team (Bubble).
        """
        divergence = model_prob - market_prob
        
        # If divergence is > 10%, we consider it a 'Value' or 'Hype' signal
        return round(divergence, 3)

    def save(self):
        joblib.dump(self, "models/market_calibration.pkl")
        print("  [market-model] Model saved → models/market_calibration.pkl")

if __name__ == "__main__":
    model = MarketCalibrationModel()
    model.save()
