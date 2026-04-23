"""
ORACLE-26 — Signal Fusion Engine
=================================
Combines 5 independent signals into a unified intelligence layer.
Fuses: Sports, Markets, Economic, Climate, and Social signals.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import SIGNAL_WEIGHTS, ALL_TEAMS

PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR = Path("data/raw")

class SignalFusionEngine:
    """
    Normalizes and aggregates multi-signal data.
    """

    def __init__(self):
        self.sports_df:   Optional[pd.DataFrame] = None
        self.market_df:   Optional[pd.DataFrame] = None
        self.economic_df: Optional[pd.DataFrame] = None
        self.climate_df:  Optional[pd.DataFrame] = None
        self.social_df:   Optional[pd.DataFrame] = None

    def load_signals(self):
        """Load all raw signals."""
        try:
            self.sports_df   = pd.read_csv(PROCESSED_DIR / "sports_features.csv")
            self.market_df   = pd.read_csv(RAW_DIR / "market_signals.csv")
            self.economic_df = pd.read_csv(RAW_DIR / "economic_indicators.csv")
            self.social_df   = pd.read_csv(RAW_DIR / "social_signals.csv")
            # Venue climate is match-specific, handled at prediction time
            print("  [fusion] All signals loaded successfully.")
        except Exception as e:
            print(f"  [fusion] ✗ Error loading signals: {e}")

    def fuse_team_signals(self):
        """Aggregate team-level signals (excluding match-specific climate)."""
        if self.sports_df is None: self.load_signals()
        
        # Start with sports features
        fused = self.sports_df.copy()
        
        # Merge Market (Implied Prob)
        if self.market_df is not None:
            m_pivot = self.market_df.groupby("team")["prob"].mean().reset_index()
            fused = pd.merge(fused, m_pivot, on="team", how="left").rename(columns={"prob": "market_signal"})
            fused["market_signal"] = fused["market_signal"].fillna(0.02)
        
        # Merge Economic (Stability Score)
        if self.economic_df is not None:
            # Normalize GDP/Inflation to 0-1
            econ = self.economic_df.copy()
            econ["econ_score"] = (econ["gdp_growth"] - econ["inflation"]).clip(-5, 5)
            econ["econ_signal"] = (econ["econ_score"] + 5) / 10
            fused = pd.merge(fused, econ[["team", "econ_signal"]], on="team", how="left")
            fused["econ_signal"] = fused["econ_signal"].fillna(0.5)

        # Merge Social (Momentum)
        if self.social_df is not None:
            soc = self.social_df.copy()
            # Normalize search momentum
            mx = soc["search_momentum"].max() if soc["search_momentum"].max() > 0 else 1
            soc["social_signal"] = (soc["search_momentum"] / mx * 0.7 + soc["sentiment_score"] * 0.3)
            fused = pd.merge(fused, soc[["team", "social_signal"]], on="team", how="left")
            fused["social_signal"] = fused["social_signal"].fillna(0.5)

        # Final Weighted Score (Composite Intelligence)
        w = SIGNAL_WEIGHTS
        # Sports signal is normalized strength_score
        fused["sports_signal"] = fused["strength_score"] / 100
        
        fused["oracle_score"] = (
            fused["sports_signal"] * w["sports"] +
            fused["market_signal"] * w["markets"] +
            fused["econ_signal"]   * w["economic"] +
            fused["social_signal"] * w["social"]
        ) * 100 # Back to 0-100 scale

        fused = fused.sort_values("oracle_score", ascending=False).reset_index(drop=True)
        fused["oracle_rank"] = fused.index + 1
        
        out_path = PROCESSED_DIR / "oracle_fused_signals.csv"
        fused.to_csv(out_path, index=False)
        print(f"  [fusion] Saved unified intelligence layer to {out_path}")
        return fused

if __name__ == "__main__":
    engine = SignalFusionEngine()
    engine.fuse_team_signals()
