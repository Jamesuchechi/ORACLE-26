"""
◈ CONFLUX — Live Intelligence API
=================================
FastAPI backend for delivering multi-signal predictions across
all four intelligence verticals.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from src.features.fusion import ConfluxFusionEngine, SignalVector
from src.constants import ALL_WC_TEAMS, WC2026_VENUES, SIGNAL_WEIGHTS

app = FastAPI(
    title="◈ CONFLUX API",
    description="Universal Multi-Signal Intelligence Engine",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROCESSED_DIR = Path("data/processed")
fusion_engine = ConfluxFusionEngine()

# ─────────────────────────────────────────────────────────────
# VERTICAL I: WC2026
# ─────────────────────────────────────────────────────────────

@app.get("/v1/predict/wc2026/rankings")
async def get_wc_rankings(
    w_sports: float = 0.40,
    w_markets: float = 0.25,
    w_finance: float = 0.15,
    w_climate: float = 0.10,
    w_social: float = 0.10
):
    """Get the current Conflux rankings with optional custom weighting."""
    file_path = PROCESSED_DIR / "conflux_wc2026.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="WC2026 data not yet generated.")
    
    df = pd.read_csv(file_path)
    
    # Re-calculate conflux_score with custom weights
    weights = {
        "sports": w_sports, "markets": w_markets, "finance": w_finance,
        "climate": w_climate, "social": w_social
    }
    
    # We need to re-fuse each row
    rows = []
    for _, row in df.iterrows():
        sv = SignalVector(
            subject=row["subject"], vertical="wc2026",
            sports=row["sports"], markets=row["markets"],
            finance=row["finance"], climate=row["climate"], social=row["social"]
        )
        res = fusion_engine.fuse(sv, custom_weights=weights)
        rows.append(res.to_dict())
    
    # Sort by new score
    final_df = pd.DataFrame(rows).sort_values("conflux_score", ascending=False).reset_index(drop=True)
    return final_df.to_dict(orient="records")

@app.get("/v1/predict/wc2026/match")
async def predict_match(
    team1: str = Query(..., description="Home/Team 1 name"),
    team2: str = Query(..., description="Away/Team 2 name"),
    venue: str = Query("MetLife Stadium", description="Venue name"),
    w_sports: float = 0.40,
    w_markets: float = 0.25,
    w_finance: float = 0.15,
    w_climate: float = 0.10,
    w_social: float = 0.10
):
    """Run an on-demand match prediction with custom weighting."""
    if team1 not in ALL_WC_TEAMS or team2 not in ALL_WC_TEAMS:
        raise HTTPException(status_code=400, detail="Teams not in WC2026 field.")

    try:
        wc_data = pd.read_csv(PROCESSED_DIR / "conflux_wc2026.csv")
        s1 = wc_data[wc_data["subject"] == team1].iloc[0]
        s2 = wc_data[wc_data["subject"] == team2].iloc[0]
    except:
        raise HTTPException(status_code=404, detail="Signal data missing.")

    weights = {
        "sports": w_sports, "markets": w_markets, "finance": w_finance,
        "climate": w_climate, "social": w_social
    }

    sv1 = SignalVector(
        subject=team1, vertical="wc2026",
        sports=s1["sports"], markets=s1["markets"],
        finance=s1["finance"], climate=s1["climate"], social=s1["social"]
    )
    sv2 = SignalVector(
        subject=team2, vertical="wc2026",
        sports=s2["sports"], markets=s2["markets"],
        finance=s2["finance"], climate=s2["climate"], social=s2["social"]
    )

    # Base sports prob
    diff = s1["sports"] - s2["sports"]
    win_p = 0.38 + (diff * 0.5)
    draw_p = 0.24
    
    # We call fuse_match with custom weights
    result = fusion_engine.fuse_match(sv1, sv2, win_p, draw_p, custom_weights=weights)
    
    # Add venue context
    v_meta = WC2026_VENUES.get(venue, WC2026_VENUES["MetLife Stadium"])
    result["venue_context"] = {
        "name": venue,
        "city": v_meta["city"],
        "altitude": v_meta["altitude_m"]
    }
    
    return result

# ─────────────────────────────────────────────────────────────
# VERTICAL II: Market Calibration
# ─────────────────────────────────────────────────────────────

@app.get("/v1/predict/market/alpha")
async def get_market_alpha():
    """Get the current market mispricing (alpha) signals."""
    file_path = PROCESSED_DIR / "conflux_market_calib.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Market data not yet generated.")
    
    df = pd.read_csv(file_path)
    return df.to_dict(orient="records")

@app.get("/v1/alpha/opportunities")
async def get_alpha_opportunities():
    """Surface the top 3 'Alpha' opportunities in the WC2026 vertical."""
    file_path = PROCESSED_DIR / "conflux_wc2026.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Data missing.")
    
    df = pd.read_csv(file_path)
    
    # Opportunities are where Conflux Score >> Markets Signal (Value)
    # or Conflux Score << Markets Signal (Hype)
    df["alpha_gap"] = df["conflux_score"] - df["markets"]
    
    # Get top 3 Value and top 3 Hype
    value_ops = df.sort_values("alpha_gap", ascending=False).head(3)
    hype_ops  = df.sort_values("alpha_gap", ascending=True).head(3)
    
    return {
        "value": value_ops[["subject", "conflux_score", "markets", "alpha_gap"]].to_dict(orient="records"),
        "hype": hype_ops[["subject", "conflux_score", "markets", "alpha_gap"]].to_dict(orient="records")
    }

# ─────────────────────────────────────────────────────────────
# VERTICAL III: Climate Risk
# ─────────────────────────────────────────────────────────────

@app.get("/v1/predict/climate/risk")
async def get_climate_risk(region: Optional[str] = None):
    """Get regional climate risk intelligence."""
    file_path = PROCESSED_DIR / "conflux_climate_risk.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Climate data missing.")
    
    df = pd.read_csv(file_path)
    if region:
        df = df[df["region"].str.lower() == region.lower()]
    
    return df.to_dict(orient="records")

# ─────────────────────────────────────────────────────────────
# VERTICAL IV: Cultural Moment
# ─────────────────────────────────────────────────────────────

@app.get("/v1/predict/cultural/moments")
async def get_cultural_moments():
    """Get current cultural tipping point probabilities."""
    file_path = PROCESSED_DIR / "conflux_cultural_moment.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Cultural data missing.")
    
    df = pd.read_csv(file_path)
    return df.to_dict(orient="records")

@app.get("/v1/analyst/briefing")
async def get_analyst_briefing():
    """Generate a multi-signal executive briefing using Groq (Llama 3)."""
    try:
        wc_df = pd.read_csv(PROCESSED_DIR / "conflux_wc2026.csv")
        # Get top 5 teams for context
        top_5 = wc_df.head(5).to_dict(orient="records")
        
        # Get market alpha
        alpha_df = pd.read_csv(PROCESSED_DIR / "conflux_market_calib.csv")
        alpha_top = alpha_df.head(3).to_dict(orient="records")
        
        context = {
            "top_contenders": top_5,
            "market_alpha": alpha_top,
            "system_status": "Online"
        }
        
        # Call the Groq Analyst
        from src.features.analyst import zerve_analyst
        insight = zerve_analyst.generate_insight(context)
        
        # Split insight into bullets for the UI
        bullets = [b.strip().replace("- ", "") for b in insight.split("\n") if b.strip().startswith("-") or len(b.strip()) > 20][:4]
        
        briefing = {
            "headline": f"ORACLE-26: AI Intelligence Report",
            "summary": insight.split("\n")[0][:200], # First line as summary
            "key_bullets": bullets if bullets else ["Analyzing signal confluence...", "Scanning for market alpha..."],
            "raw_insight": insight,
            "timestamp": datetime.now().isoformat()
        }
        return briefing
    except Exception as e:
        print(f"Briefing Error: {e}")
        return {
            "headline": "Analyst Offline",
            "summary": "Internal signal processing error.",
            "key_bullets": ["Check API credentials", "Verify data integrity"],
            "timestamp": datetime.now().isoformat()
        }

# ─────────────────────────────────────────────────────────────
# SYSTEM
# ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "system": "◈ CONFLUX"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
