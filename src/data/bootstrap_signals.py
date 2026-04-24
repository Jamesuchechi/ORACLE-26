
"""
◈ CONFLUX | March 2026 Signal Bootstrapper
==========================================
Synchronizes all signal engines to the March 2026 baseline.
Ensures data/raw and data/processed are populated for the demo.
"""

import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Add project root to sys.path
root_path = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_path))

# Import engines
from src.data.sports import SportsSignalEngine
from src.data.economics import EconomicSignalEngine
from src.data.markets import MarketSignalEngine
from src.data.social import SocialSignalEngine
from src.data.squads import SquadEngine
from src.features.fusion import ConfluxFusionEngine, SignalVector

def bootstrap():
    print("\n" + "◈" * 50)
    print("◈ CONFLUX — MARCH 2026 SIGNAL SYNCHRONIZATION")
    print("◈" * 50)

    # 1. Squads & Valuations
    squad_engine = SquadEngine()
    squad_engine.build_all_squads()

    # 2. Sports Signal
    sports_engine = SportsSignalEngine()
    sports_engine.build_all_features()

    # 3. Economics Signal
    from src.data.climate import ClimateSignalEngine
    climate_engine = ClimateSignalEngine()
    climate_engine.run()

    econ_engine = EconomicSignalEngine()
    econ_engine.build_all_signals()

    # 4. Markets Signal
    market_engine = MarketSignalEngine()
    market_engine.run()

    # 5. Social Signal
    social_engine = SocialSignalEngine()
    social_engine.run()


    # 6. Final Conflux Fusion
    print("\n◈ Fusing all signals into conflux_wc2026.csv...")
    fusion_engine = ConfluxFusionEngine()
    
    # Load processed components
    sports_df = pd.read_csv("data/processed/sports_features.csv")
    econ_df   = pd.read_csv("data/raw/economic_signals.csv")
    market_df = pd.read_csv("data/raw/market_signals_wc.csv")
    social_df = pd.read_csv("data/raw/social_signals_wc.csv")
    
    # Climate is currently venue-based, we'll assign a baseline climate resilience score per team
    # (High ELO/Rich nations usually have higher resilience via infrastructure)
    
    rows = []
    for team in sports_df["team"]:
        s_score = sports_df[sports_df["team"] == team]["sports_signal"].iloc[0]
        
        # Safe lookup for Econ
        e_match = econ_df[econ_df["team"] == team]
        e_score = e_match["econ_signal"].iloc[0] if not e_match.empty else 0.5
        
        # Safe lookup for Market
        m_match = market_df[market_df["team"] == team]
        m_score = m_match["market_signal"].iloc[0] if not m_match.empty else 0.2
        
        # Safe lookup for Social
        t_match = social_df[social_df["team"] == team]
        t_score = t_match["social_signal"].iloc[0] if not t_match.empty else 0.3
        
        # Climate resilience score (modelled)
        c_score = 0.5 + (e_score * 0.4) + (random_variation(team) * 0.1)
        
        sv = SignalVector(
            subject=team, vertical="wc2026",
            sports=s_score, markets=m_score, finance=e_score,
            climate=c_score, social=t_score
        )
        
        res = fusion_engine.fuse(sv)
        row = {
            "subject": team,
            "vertical": "wc2026",
            "conflux_score": res.conflux_score,
            "confidence": res.confidence,
            "divergences": res.divergences,
            "interpretation": res.interpretation,
            "sports": s_score,
            "markets": m_score,
            "finance": e_score,
            "climate": c_score,
            "social": t_score
        }
        rows.append(row)

    final_df = pd.DataFrame(rows).sort_values("conflux_score", ascending=False).reset_index(drop=True)
    final_df.to_csv("data/processed/conflux_wc2026.csv", index=False)
    print(f"  [fusion] ✓ Created master conflux ranking for {len(final_df)} teams.")

    # 7. Market Calibration (Alpha Discovery)
    print("\n◈ Discovering Market Alpha...")
    # Alpha = conflux_score - market_signal
    final_df["alpha_gap"] = final_df["conflux_score"] - final_df["markets"]
    final_df.to_csv("data/processed/conflux_market_calib.csv", index=False)
    print(f"  [alpha] ✓ Detected {len(final_df[abs(final_df['alpha_gap']) > 0.1])} significant mispricing events.")

    print("\n" + "◈" * 50)
    print("◈ BOOTSTRAP COMPLETE — March 2026 Intelligence Live")
    print("◈" * 50)

def random_variation(seed_str):
    import random
    random.seed(seed_str)
    return random.random()

if __name__ == "__main__":
    bootstrap()
