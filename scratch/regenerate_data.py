import pandas as pd
import numpy as np
from pathlib import Path
from src.constants import ALL_WC_TEAMS, CURATED_ELO, TEAM_TO_GROUP
from src.features.fusion import ConfluxFusionEngine

# Paths
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def regenerate_data():
    engine = ConfluxFusionEngine()
    
    # 1. World Cup 2026 Base Data
    wc_data = []
    for team in ALL_WC_TEAMS:
        # Mock signal vector for baseline
        elo = CURATED_ELO.get(team, 1600)
        sports_val = (elo - 1500) / 1000  # Normalize
        
        # Random but deterministic signals for demo
        np.random.seed(len(team))
        markets = np.random.uniform(0.3, 0.8)
        finance = np.random.uniform(0.4, 0.9)
        climate = np.random.uniform(0.1, 0.6)
        social  = np.random.uniform(0.2, 0.7)
        
        # Fuse
        sv = type('SV', (), {
            'sports': sports_val, 'markets': markets, 'finance': finance, 
            'climate': climate, 'social': social, 'vertical': 'wc2026',
            'subject': team
        })()
        
        result = engine.fuse(sv)
        
        wc_data.append({
            "subject": team,
            "group": TEAM_TO_GROUP.get(team, "?"),
            "sports": sports_val,
            "markets": markets,
            "finance": finance,
            "climate": climate,
            "social": social,
            "conflux_score": result.conflux_score,
            "confidence": "HIGH" if sports_val > 0.5 else "MEDIUM",
            "flag": "🏳️" # Placeholder
        })
    
    df = pd.DataFrame(wc_data).sort_values("conflux_score", ascending=False)
    df.to_csv(PROCESSED_DIR / "conflux_wc2026.csv", index=False)
    print(f"Regenerated {len(df)} teams in conflux_wc2026.csv")

if __name__ == "__main__":
    regenerate_data()
