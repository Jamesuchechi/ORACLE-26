"""
◈ CONFLUX — Live Intelligence API
=================================
FastAPI backend for delivering multi-signal predictions across
all four intelligence verticals.
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import numpy as np
from pydantic import BaseModel

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
RAW_DIR = Path("data/raw")
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
    return final_df.replace({np.nan: None}).to_dict(orient="records")

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

    # Call the AI Analyst for a tactical matchup brief
    from src.features.analyst import zerve_analyst
    
    tactical_context = {
        "team1": result["team1_breakdown"],
        "team2": result["team2_breakdown"],
        "venue": result["venue_context"],
        "win_prob": result["win_prob"],
        "loss_prob": result["loss_prob"],
        "signal_delta": result["signal_delta"]
    }
    
    # Generate a concise tactical brief
    tactical_brief = zerve_analyst.generate_insight(
        tactical_context, 
        user_query=f"Provide a 2-sentence tactical scouting report for {team1} vs {team2} at {venue}."
    )
    
    result["intelligence_report"] = tactical_brief
    
    # Calculate specific signal advantages
    result["advantages"] = {
        "sports": team1 if s1["sports"] > s2["sports"] else team2,
        "markets": team1 if s1["markets"] > s2["markets"] else team2,
        "climate_resilience": team1 if s1["climate"] > s2["climate"] else team2
    }
    
    return result

# ─────────────────────────────────────────────────────────────
# TEAM DETAILS & SQUADS
# ─────────────────────────────────────────────────────────────

@app.get("/v1/team/{team_name}/squad")
async def get_team_squad(team_name: str):
    """Get the full squad and valuation for a specific team."""
    import json
    file_path = PROCESSED_DIR / "squad_data.json"
    
    if not file_path.exists():
        # Generate on the fly if missing
        from src.data.squads import SquadEngine
        engine = SquadEngine()
        data = engine.build_all_squads()
    else:
        with open(file_path, "r") as f:
            data = json.load(f)
            
    if team_name not in data:
        # Try to find case-insensitive
        matches = [t for t in data.keys() if t.lower() == team_name.lower()]
        if matches:
            team_name = matches[0]
        else:
            raise HTTPException(status_code=404, detail="Team not found.")
            
    return data[team_name]

# ─────────────────────────────────────────────────────────────
# VERTICAL II: Market Calibration
# ─────────────────────────────────────────────────────────────

@app.get("/v1/markets/dashboard")
async def get_markets_dashboard():
    """Get aggregated prediction market signals and alpha detection."""
    try:
        from src.data.markets import MarketSignalEngine
        engine = MarketSignalEngine()
        
        file_path = RAW_DIR / "market_signals_events.csv"
        if file_path.exists():
            events_df = pd.read_csv(file_path)
        else:
            events_df = engine.fetch_general_markets()
            
        return {
            "events": events_df.replace({np.nan: None}).to_dict(orient="records"),
            "last_refresh": datetime.now().isoformat(),
            "source": "Polymarket & Kalshi (Integrated)"
        }
    except Exception as e:
        print(f"Markets Dashboard Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/predict/market/alpha")
async def get_market_alpha():
    """Get the current market mispricing (alpha) signals."""
    file_path = PROCESSED_DIR / "conflux_market_calib.csv"
    if not file_path.exists():
        # Generate dummy alpha if data missing (fallback)
        wc_data = pd.read_csv(PROCESSED_DIR / "conflux_wc2026.csv")
        wc_data["alpha_gap"] = wc_data["conflux_score"] - wc_data["markets"]
        value_ops = wc_data.sort_values("alpha_gap", ascending=False).head(3)
        hype_ops  = wc_data.sort_values("alpha_gap", ascending=True).head(3)
        return {
            "value": value_ops[["subject", "conflux_score", "markets", "alpha_gap"]].replace({np.nan: None}).to_dict(orient="records"),
            "hype": hype_ops[["subject", "conflux_score", "markets", "alpha_gap"]].replace({np.nan: None}).to_dict(orient="records")
        }
    
    df = pd.read_csv(file_path)
    return df.replace({np.nan: None}).to_dict(orient="records")

# ─────────────────────────────────────────────────────────────
# VERTICAL III: Finance & Economics
# ─────────────────────────────────────────────────────────────

@app.get("/v1/finance/dashboard")
async def get_finance_dashboard():
    """Get macro-economic stability indicators for host nations and top contenders."""
    file_path = RAW_DIR / "economic_signals.csv"
    if not file_path.exists():
        from src.data.economics import EconomicSignalEngine
        engine = EconomicSignalEngine()
        df = engine.build_all_signals()
    else:
        df = pd.read_csv(file_path)
        
    # Pick major host nations + top 3
    targets = ["USA", "Mexico", "Canada", "Argentina", "France", "England", "Brazil", "Germany"]
    highlights = df[df["team"].isin(targets)].replace({np.nan: None}).to_dict(orient="records")
    
    return {
        "highlights": highlights,
        "full_index": df.head(30).to_dict(orient="records"),
        "source": "FRED & World Bank (April 2026 Live)"
    }


# ─────────────────────────────────────────────────────────────
# VERTICAL IV: Climate Risk
# ─────────────────────────────────────────────────────────────

@app.get("/v1/climate/dashboard")
async def get_climate_dashboard():
    """Get regional climate risk intelligence."""
    # Already have get_venue_climate_risk, but let's make it more dashboard-y
    venues = await get_venue_climate_risk()
    
    from src.constants import TRACKED_CLIMATE_REGIONS
    regions = []
    for reg, meta in TRACKED_CLIMATE_REGIONS.items():
        regions.append({
            "region": reg.capitalize(),
            "risk_type": meta["risk_type"],
            "severity": "ELEVATED" if "heat" in meta["risk_type"] else "STABLE"
        })
        
    return {
        "venue_risks": venues,
        "regional_alerts": regions,
        "source": "NOAA & Open-Meteo"
    }

# ─────────────────────────────────────────────────────────────
# VERTICAL V: Social Trends
# ─────────────────────────────────────────────────────────────

@app.get("/v1/social/trends")
async def get_social_trends():
    """Get cultural momentum and sentiment signals."""
    file_path = RAW_DIR / "cultural_moment_signals.csv"
    if not file_path.exists():
        from src.data.social import SocialSignalEngine
        engine = SocialSignalEngine()
        res = engine.run()
        df = res["cultural"]
    else:
        df = pd.read_csv(file_path)
        
    return {
        "topics": df.replace({np.nan: None}).to_dict(orient="records"),
        "source": "Google Trends & Reddit Sentiment (CONFLUX Logic)"
    }



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
        "value": value_ops[["subject", "conflux_score", "markets", "alpha_gap"]].replace({np.nan: None}).to_dict(orient="records"),
        "hype": hype_ops[["subject", "conflux_score", "markets", "alpha_gap"]].replace({np.nan: None}).to_dict(orient="records")
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

@app.get("/v1/predict/climate/venues")
async def get_venue_climate_risk():
    """Get the current climate and altitude risk profile for all 16 venues."""
    file_path = RAW_DIR / "venue_climate_signals.csv"
    if not file_path.exists():
        from src.data.climate import ClimateSignalEngine
        engine = ClimateSignalEngine()
        df = engine.build_venue_signals()
    else:
        df = pd.read_csv(file_path)
        
    results = []
    for _, v in df.iterrows():
        total_risk = 1 - v["climate_signal"]
        results.append({
            "venue": v["venue"],
            "city": v["city"],
            "risk_score": round(total_risk, 2),
            "alt_risk": v["altitude_stress"],
            "heat_risk": v["heat_stress"],
            "status": "CRITICAL" if total_risk > 0.6 else "WARNING" if total_risk > 0.3 else "STABLE"
        })
    
    return sorted(results, key=lambda x: x["risk_score"], reverse=True)


@app.get("/v1/predict/cultural/moments")
async def get_cultural_moments():
    """Get current cultural tipping point probabilities."""
    file_path = PROCESSED_DIR / "conflux_cultural_moment.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Cultural data missing.")
    
    df = pd.read_csv(file_path)
    return df.replace({np.nan: None}).to_dict(orient="records")

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
        
        # Split insight into components
        lines = [l.strip() for l in insight.split("\n") if l.strip()]
        summary = lines[0] if lines else "Analyzing signals..."
        bullets = [l.replace("- ", "").replace("* ", "") for l in lines[1:] if l.startswith("-") or l.startswith("*")][:5]
        
        # Fallback if no bullets found
        if not bullets and len(lines) > 1:
            bullets = lines[1:5]

        briefing = {
            "headline": f"ORACLE-26: AI Intelligence Report",
            "summary": summary,
            "key_bullets": bullets,
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

class ChatRequest(BaseModel):
    message: str

@app.post("/v1/analyst/chat")
async def analyst_chat(request: ChatRequest):
    """Conversational interface with the ORACLE-26 Analyst."""
    user_message = request.message
    
    try:
        # Get current context for the LLM
        file_path = PROCESSED_DIR / "conflux_wc2026.csv"
        top_teams = "Data pending..."
        if file_path.exists():
            wc_df = pd.read_csv(file_path)
            top_teams = wc_df.head(10).to_dict(orient="records")
        
        context = {
            "top_contenders": top_teams,
            "current_timestamp": datetime.now().isoformat(),
            "mission": "Provide World Cup 2026 Intelligence Analysis and tactical scouting across 5 domains (Sports, Markets, Finance, Climate, Social)."
        }
        
        from src.features.analyst import zerve_analyst
        
        system_extension = """
        You are the Zerve Analyst. Keep your responses concise and analytical.
        Highlight interactions between different domains.
        """
        
        response = zerve_analyst.generate_insight(
            context, 
            user_query=f"{system_extension}\n\nUser: {user_message}"
        )
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Chat Error: {e}")
        return {"response": "The neural link is experiencing interference. Please try again."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
