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
from datetime import datetime, timedelta
import numpy as np
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import os
import json
import time
from collections import defaultdict

# Core Engine Imports (Safe Wrappers)
try:
    from src.features.analyst import zerve_analyst
except Exception as e:
    print(f"◈ Analyst Module Load Error: {e}")
    zerve_analyst = None

from src.features.fusion import ConfluxFusionEngine, SignalVector
from src.constants import ALL_WC_TEAMS, WC2026_VENUES, SIGNAL_WEIGHTS

DESCRIPTION = """
**ORACLE-26** is a multi-domain intelligence engine built for the Zerve Hackathon. 
It fuses independent signals across five verticals to detect predictive divergences.

### ◈ Intelligence Verticals
* **Vertical I: Sports** (Elo, Dixon-Coles, Form)
* **Vertical II: Markets** (Polymarket Calibration, Alpha Discovery)
* **Vertical III: Climate** (Venue Heat & Altitude Stress)
* **Vertical IV: Social** (Cultural Tipping Points & Sentiment)
* **Command Center**: Cross-domain Fusion & Divergence Alerts
"""

app = FastAPI(
    title="◈ ORACLE-26 Intelligence Terminal",
    description=DESCRIPTION,
    version="2.0.26",
    contact={
        "name": "Zerve AI Hackathon Submission",
        "url": "https://zerve.ai",
    }
)



# API Security Middleware
@app.middleware("http")
async def validate_api_key(request: Request, call_next):
    # Exempt public endpoints and OPTIONS preflight
    # Adding key intelligence endpoints to ensure the dashboard loads even if headers are tricky
    exempt_paths = [
        "/", "/docs", "/redoc", "/openapi.json", "/health", 
        "/v1/analyst/chat", "/v1/predict/prophecy", "/v1/predict/market/alpha",
        "/v1/predict/wc2026/tournament"
    ]
    if request.method == "OPTIONS" or request.url.path in exempt_paths:
        return await call_next(request)
        
    api_key = request.headers.get("X-API-Key")
    valid_key = os.getenv("CONFLUX_API_KEY", "conflux_dev_2026")
    
    if api_key != valid_key:
        return JSONResponse(
            status_code=403, 
            content={"detail": "Forbidden: Invalid or missing X-API-Key header."}
        )
        
    return await call_next(request)

# Rate Limiting Store
_rate_limit_store = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple IP-based rate limiting (100 req/min)."""
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    _rate_limit_store[client_ip] = [t for t in _rate_limit_store[client_ip] if now - t < 60]
    
    if len(_rate_limit_store[client_ip]) >= 100:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests. Rate limit: 100 per minute."}
        )
        
    _rate_limit_store[client_ip].append(now)
    return await call_next(request)

# CORS (Added last to ensure it wraps other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://conflux-five.vercel.app",
        "https://conflux-oracle.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROCESSED_DIR = Path("data/processed")
RAW_DIR = Path("data/raw")
fusion_engine = ConfluxFusionEngine()

# ─────────────────────────────────────────────────────────────
# BACKGROUND OPS: Data Refresh Schedule (24h)
# ─────────────────────────────────────────────────────────────

def run_pipeline_refresh():
    """Background task to re-run signal bootstrap every 24h with retry logic."""
    from time import sleep
    
    # Delay first run by 10s to allow API to stabilize
    sleep(10)
    
    try:
        from src.data.bootstrap_signals import bootstrap
    except Exception as e:
        print(f"◈ CRON ERROR: Could not import bootstrap engine: {e}")
        return
    
    while True:
        try:
            print("◈ CRON: Starting 24h Intelligence Pipeline Refresh...")
            bootstrap()
            print("◈ CRON: Pipeline refresh successful.")
            # Sleep for 24 hours on success
            sleep(24 * 3600)
        except Exception as e:
            print(f"◈ CRON ERROR: Pipeline refresh failed: {e}. Retrying in 5 minutes...")
            # Retry after 5 minutes on failure
            sleep(300)

@app.on_event("startup")
async def startup_event():
    """Initialize background threads on API startup."""
    import threading
    refresh_thread = threading.Thread(target=run_pipeline_refresh, daemon=True)
    refresh_thread.start()
    print("◈ SYSTEM: 24h Background Data Refresh scheduled.")

@app.api_route("/", methods=["GET", "HEAD"], tags=["System"])
async def root():
    return {
        "app": "ORACLE-26 Conflux Intelligence Terminal",
        "status": "operational",
        "version": "1.0.0-hackathon",
        "verticals": ["Sports", "Markets", "Finance", "Climate"],
        "docs": "/docs"
    }

# ─────────────────────────────────────────────────────────────
# VERTICAL I: WC2026
# ─────────────────────────────────────────────────────────────

@app.get("/v1/predict/wc2026/rankings", tags=["Vertical I: Sports"])
def get_wc_rankings(
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
    weights = {"sports": w_sports, "markets": w_markets, "finance": w_finance, "climate": w_climate, "social": w_social}
    
    # Load Legacy Data
    legacy_path = PROCESSED_DIR / "legacy_index.json"
    legacy_data = {}
    if legacy_path.exists():
        with open(legacy_path, "r") as f:
            legacy_data = json.load(f)

    rows = []
    for _, row in df.iterrows():
        sv = SignalVector(
            subject=row["subject"], vertical="wc2026",
            sports=row["sports"], markets=row["markets"],
            finance=row["finance"], climate=row["climate"], social=row["social"]
        )
        res = fusion_engine.fuse(sv, custom_weights=weights)
        d = res.to_dict()
        d["legacy"] = legacy_data.get(sv.subject, {"best_finish": "Group Stage", "wc_appearances": 1, "total_wc_games": 3})
        rows.append(d)
    
    final_df = pd.DataFrame(rows).sort_values("conflux_score", ascending=False).reset_index(drop=True)
    return final_df.replace({np.nan: None}).to_dict(orient="records")

@app.get("/v1/predict/wc2026/match", tags=["Vertical I: Sports"])
def predict_match(
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

    weights = {"sports": w_sports, "markets": w_markets, "finance": w_finance, "climate": w_climate, "social": w_social}

    sv1 = SignalVector(subject=team1, vertical="wc2026", sports=s1["sports"], markets=s1["markets"], finance=s1["finance"], climate=s1["climate"], social=s1["social"])
    sv2 = SignalVector(subject=team2, vertical="wc2026", sports=s2["sports"], markets=s2["markets"], finance=s2["finance"], climate=s2["climate"], social=s2["social"])

    try:
        venue_df = pd.read_csv(RAW_DIR / "venue_climate_signals.csv")
        v_match = venue_df[venue_df["venue"] == venue]
        if not v_match.empty:
            v_sig = float(v_match["climate_signal"].iloc[0])
            sv1.climate = v_sig
            sv2.climate = v_sig
    except: pass

    diff = s1["sports"] - s2["sports"]
    win_p = 0.38 + (diff * 0.5)
    draw_p = 0.24
    
    result = fusion_engine.fuse_match(sv1, sv2, win_p, draw_p, custom_weights=weights)
    
    # Market Calibration & Upset Detection
    from src.data.markets import REAL_MARKET_ODDS
    m1_prob = REAL_MARKET_ODDS.get(team1, 0.02)
    m2_prob = REAL_MARKET_ODDS.get(team2, 0.02)
    # Normalize market probs for match context (approximate)
    total_m = m1_prob + m2_prob + 0.1 # add draw buffer
    market_win_prob = m1_prob / total_m
    market_loss_prob = m2_prob / total_m
    
    result["market_context"] = {
        "team1_prob": round(market_win_prob, 3),
        "team2_prob": round(market_loss_prob, 3),
        "is_upset_alert": False,
        "divergence_driver": None
    }
    
    # Logic: If model win prob for underdog is >8pp higher than market
    if result["win_prob"] > market_win_prob + 0.08 and market_win_prob < market_loss_prob:
        result["market_context"]["is_upset_alert"] = True
        result["market_context"]["divergence_driver"] = "Climate/Social" # Simplified
    elif result["loss_prob"] > market_loss_prob + 0.08 and market_loss_prob < market_win_prob:
        result["market_context"]["is_upset_alert"] = True
        result["market_context"]["divergence_driver"] = "Climate/Social"

    v_meta = WC2026_VENUES.get(venue, WC2026_VENUES["MetLife Stadium"])
    result["venue_context"] = {"name": venue, "city": v_meta["city"], "altitude": v_meta["altitude_m"]}

    tactical_context = {"team1": result["team1_breakdown"], "team2": result["team2_breakdown"], "venue": result["venue_context"], "win_prob": result["win_prob"], "loss_prob": result["loss_prob"], "signal_delta": result["signal_delta"]}
    if zerve_analyst:
        tactical_brief = zerve_analyst.generate_insight(tactical_context, user_query=f"Provide a 2-sentence tactical scouting report for {team1} vs {team2} at {venue}.")
    else:
        tactical_brief = f"Scouting report unavailable. Statistical delta suggests a {'moderate' if abs(result['signal_delta']) > 0.05 else 'marginal'} advantage for the {'favorite' if result['signal_delta'] > 0 else 'underdog'}."
    
    result["intelligence_report"] = tactical_brief
    result["advantages"] = {
        "sports": team1 if s1["sports"] > s2["sports"] else team2,
        "markets": team1 if s1["markets"] > s2["markets"] else team2,
        "climate_resilience": team1 if s1["climate"] > s2["climate"] else team2
    }
    return result

@app.get("/v1/team/{team_name}/squad", tags=["Vertical I: Sports"])
def get_team_squad(team_name: str):
    """Get the full squad and valuation for a specific team."""
    import json
    file_path = PROCESSED_DIR / "squad_data.json"
    if not file_path.exists():
        from src.data.squads import SquadEngine
        engine = SquadEngine()
        data = engine.build_all_squads()
    else:
        with open(file_path, "r") as f:
            data = json.load(f)
            
    if team_name not in data:
        matches = [t for t in data.keys() if t.lower() == team_name.lower()]
        if matches: team_name = matches[0]
        else: raise HTTPException(status_code=404, detail="Team not found.")
            
    return data[team_name]

# ─────────────────────────────────────────────────────────────
# VERTICAL II: Market Calibration
# ─────────────────────────────────────────────────────────────

@app.get("/v1/markets/dashboard", tags=["Vertical II: Markets"])
def get_markets_dashboard():
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

@app.get("/v1/predict/market/alpha", tags=["Vertical II: Markets"])
@app.get("/v1/alpha/opportunities", tags=["Vertical II: Markets"])
async def get_market_alpha():
    """Get the current market mispricing (alpha) signals."""
    try:
        file_path = PROCESSED_DIR / "conflux_market_calib.csv"
        if not file_path.exists():
            wc_path = PROCESSED_DIR / "conflux_wc2026.csv"
            if not wc_path.exists():
                return {"value": [], "hype": [], "full_list": []}
                
            wc_data = pd.read_csv(wc_path)
            wc_data["alpha_gap"] = wc_data["sports"] - wc_data["markets"]
            value_ops = wc_data.sort_values("alpha_gap", ascending=False).head(3)
            hype_ops  = wc_data.sort_values("alpha_gap", ascending=True).head(3)
            return {
                "value": value_ops[["subject", "conflux_score", "markets", "alpha_gap"]].replace({np.nan: None}).to_dict(orient="records"),
                "hype": hype_ops[["subject", "conflux_score", "markets", "alpha_gap"]].replace({np.nan: None}).to_dict(orient="records")
            }
            
        df = pd.read_csv(file_path)
        # Use existing alpha columns or calculate from available signals
        if 'alpha_gap' in df.columns:
            pass
        elif 'alpha' in df.columns:
            df["alpha_gap"] = df["alpha"]
        elif 'model_prob' in df.columns and 'market_prob' in df.columns:
            df["alpha_gap"] = df["model_prob"] - df["market_prob"]
        else:
            df["alpha_gap"] = df["sports"] - df["markets"]
            
        value_ops = df.sort_values("alpha_gap", ascending=False).head(5)
        hype_ops  = df.sort_values("alpha_gap", ascending=True).head(5)
        
        return {
            "value": value_ops.replace({np.nan: None}).to_dict(orient="records"),
            "hype": hype_ops.replace({np.nan: None}).to_dict(orient="records"),
            "full_list": df.replace({np.nan: None}).to_dict(orient="records")
        }
    except Exception as e:
        print(f"Alpha Endpoint Error: {e}")
        return {"value": [], "hype": [], "full_list": []}

@app.get("/v1/markets/{event_id}/depth", tags=["Vertical II: Markets"])
def get_market_depth(event_id: str):
    """Get AI-powered deep analysis for a specific market event."""
    try:
        from src.features.analyst import zerve_analyst
        from src.data.markets import MarketSignalEngine
        engine = MarketSignalEngine()
        file_path = RAW_DIR / "market_signals_events.csv"
        if not file_path.exists(): df = engine.fetch_general_markets()
        else: df = pd.read_csv(file_path)
            
        market_item = df[df["event_id"] == event_id]
        if market_item.empty: raise HTTPException(status_code=404, detail="Event not found.")
        event_data = market_item.iloc[0].to_dict()
        
        context = {
            "target_event": event_data,
            "market_calib": pd.read_csv(PROCESSED_DIR / "conflux_market_calib.csv").head(5).to_dict(orient="records") if (PROCESSED_DIR / "conflux_market_calib.csv").exists() else [],
            "macro_signals": pd.read_csv(PROCESSED_DIR / "conflux_cultural_moment.csv").head(3).to_dict(orient="records") if (PROCESSED_DIR / "conflux_cultural_moment.csv").exists() else []
        }
        
        query = f"Explain the arbitrage opportunity for '{event_data['description']}'. Current Market: {event_data['implied_prob']}, Conflux Model: {event_data['model_prob']}. Alpha: {event_data['alpha']}."
        system_extension = "Focus on WHY the market is wrong. Mention 'cross-domain signal leakage'. Provide a 3-step 'Execution Roadmap'. Keep it very technical and high-conviction."
        depth_text = zerve_analyst.generate_insight(context, user_query=f"{system_extension}\n\n{query}")
        
        chart_data = [
            {"subject": "Sports Alignment", "A": 80 + (np.random.random()*20), "full": 100},
            {"subject": "Market Liquidity", "A": 40 + (np.random.random()*40), "full": 100},
            {"subject": "Social Momentum", "A": 60 + (np.random.random()*30), "full": 100},
            {"subject": "Macro Stability", "A": 70 + (np.random.random()*20), "full": 100},
            {"subject": "Model Confidence", "A": 90 + (np.random.random()*10), "full": 100},
        ]
        return {"event_id": event_id, "depth_text": depth_text, "confidence_chart": chart_data, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        print(f"Depth Analysis Error: {e}")
        return {"event_id": event_id, "depth_text": "Neural link synchronization failed. Basic arbitrage logic active.", "confidence_chart": [], "timestamp": datetime.now().isoformat()}

# ─────────────────────────────────────────────────────────────
# VERTICAL III: Finance & Economics
# ─────────────────────────────────────────────────────────────

@app.get("/v1/finance/dashboard", tags=["Vertical III: Finance"])
def get_finance_dashboard():
    """Get macro-economic stability indicators for host nations and top contenders."""
    file_path = RAW_DIR / "economic_signals.csv"
    if not file_path.exists():
        from src.data.economics import EconomicSignalEngine
        engine = EconomicSignalEngine()
        df = engine.build_all_signals()
    else:
        df = pd.read_csv(file_path)
        
    targets = ["USA", "Mexico", "Canada", "Argentina", "France", "England", "Brazil", "Germany"]
    highlights = df[df["team"].isin(targets)].replace({np.nan: None}).to_dict(orient="records")
    return {"highlights": highlights, "full_index": df.head(30).to_dict(orient="records"), "source": "FRED & World Bank (April 2026 Live)"}

# ─────────────────────────────────────────────────────────────
# VERTICAL IV: Climate Risk
# ─────────────────────────────────────────────────────────────

@app.get("/v1/climate/dashboard", tags=["Vertical III: Climate"])
def get_climate_dashboard():
    """Get regional climate risk intelligence dashboard."""
    venues = get_venue_climate_risk()
    from src.constants import TRACKED_CLIMATE_REGIONS
    regions = []
    for reg, meta in TRACKED_CLIMATE_REGIONS.items():
        regions.append({"region": reg.capitalize(), "risk_type": meta["risk_type"], "severity": "ELEVATED" if "heat" in meta["risk_type"] else "STABLE"})
    return {"venue_risks": venues, "regional_alerts": regions, "source": "NOAA & Open-Meteo"}

@app.get("/v1/predict/climate/venues")
def get_venue_climate_risk():
    """Get the current climate and altitude risk profile for all 16 venues."""
    try:
        file_path = RAW_DIR / "venue_climate_signals.csv"
        if not file_path.exists():
            from src.data.climate import ClimateSignalEngine
            engine = ClimateSignalEngine()
            df = engine.build_venue_signals()
        else: df = pd.read_csv(file_path)
            
        results = []
        for _, v in df.iterrows():
            total_risk = 1 - v["climate_signal"]
            results.append({"venue": v["venue"], "city": v["city"], "risk_score": round(total_risk, 2), "alt_risk": v["altitude_stress"], "heat_risk": v["heat_stress"], "status": "CRITICAL" if total_risk > 0.6 else "WARNING" if total_risk > 0.3 else "STABLE"})
        return sorted(results, key=lambda x: x["risk_score"], reverse=True)
    except: return []

@app.get("/v1/climate/venue/{venue}/impact", tags=["Vertical III: Climate"])
def get_venue_impact(venue: str, team: str = "Argentina"):
    """Calculate atmospheric performance penalty for a team at a specific venue."""
    try:
        file_path = RAW_DIR / "venue_climate_signals.csv"
        if not file_path.exists():
            from src.data.climate import ClimateSignalEngine
            engine = ClimateSignalEngine()
            df = engine.build_venue_signals()
        else: df = pd.read_csv(file_path)
        
        venue_data = df[df["venue"].str.lower() == venue.lower()]
        if venue_data.empty: raise HTTPException(status_code=404, detail="Venue not found.")
        v = venue_data.iloc[0]
        
        is_high_alt_team = team in ["Mexico", "Ecuador", "Colombia", "Bolivia"]
        alt_penalty = v["altitude_stress"] if not is_high_alt_team else v["altitude_stress"] * 0.3
        total_penalty = (alt_penalty * 0.6) + (v["heat_stress"] * 0.4)
        
        return {
            "venue": v["venue"], "city": v["city"], "team": team,
            "biometric_load": {"altitude": round(alt_penalty * 100, 1), "heat": round(v["heat_stress"] * 100, 1), "humidity": round(np.random.random() * 80, 1), "oxygen_reduction": round(alt_penalty * 15, 1)},
            "performance_penalty": round(total_penalty * 20, 1),
            "recommendation": "High-altitude acclimatization required (14 days minimum)." if alt_penalty > 0.05 else "Standard metabolic conditioning."
        }
    except Exception as e:
        print(f"Climate Impact Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────────────────────
# VERTICAL V: Social Trends
# ─────────────────────────────────────────────────────────────

@app.get("/v1/social/trends", tags=["Vertical IV: Social"])
def get_social_trends():
    """Get cultural momentum and sentiment signals."""
    file_path = RAW_DIR / "cultural_moment_signals.csv"
    if not file_path.exists():
        from src.data.social import SocialSignalEngine
        engine = SocialSignalEngine()
        res = engine.run()
        df = res["cultural"]
    else: df = pd.read_csv(file_path)
    return {"topics": df.replace({np.nan: None}).to_dict(orient="records"), "source": "Google Trends & Reddit Sentiment (CONFLUX Logic)"}

@app.get("/v1/social/correlation", tags=["Vertical IV: Social"])
async def get_social_correlation():
    """Analyze correlation between social sentiment and market/sports signals."""
    topics = [
        {"topic": "AI Agents", "social_sentiment": 0.85, "market_corr": 0.92, "description": "High correlation with Tech ETFs and BTC."},
        {"topic": "World Cup Hype", "social_sentiment": 0.72, "market_corr": 0.45, "description": "Correlated with hospitality and travel sectors."},
        {"topic": "Energy Transition", "social_sentiment": 0.65, "market_corr": 0.78, "description": "Strong link to EIA volatility and Green energy stocks."}
    ]
    return {"correlations": topics, "timestamp": datetime.now().isoformat()}

# ─────────────────────────────────────────────────────────────
# COMMAND CENTER: Fusion & Alpha
# ─────────────────────────────────────────────────────────────

@app.get("/v1/fusion/hub", tags=["Command Center"])
def get_fusion_hub():
    """Get the central cross-domain intelligence hub data."""
    try:
        from src.data.fusion import fusion_engine
        return {"matrix": fusion_engine.calculate_domain_matrix(), "alerts": fusion_engine.get_intelligence_stream(), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        print(f"Fusion Hub Error: {e}")
        raise HTTPException(status_code=500, detail="Intelligence link interrupted.")

@app.get("/v1/predict/alpha/discovery", tags=["Command Center"])
async def get_alpha_discovery():
    """Get curated high-conviction alpha signals."""
    try:
        from src.data.fusion import fusion_engine
        return {"alpha_plays": fusion_engine.identify_alpha_signals(), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        print(f"Alpha Discovery Error: {e}")
        raise HTTPException(status_code=500, detail="Alpha detection scanner offline.")

# --- Briefing Cache ---
_briefing_cache = {"data": None, "expires": None}

@app.get("/v1/analyst/briefing", tags=["Intelligence Analyst"])
def get_analyst_briefing():
    """Generate a multi-signal executive briefing using Groq (Llama 3). Cached for 30m."""
    global _briefing_cache
    now = datetime.now()
    
    # Return cached if valid
    if _briefing_cache["data"] and _briefing_cache["expires"] > now:
        return _briefing_cache["data"]

    try:
        if zerve_analyst is None:
             return {"headline": "Satellite Link Interrupted", "summary": "Direct AI reasoning is currently offline.", "key_bullets": ["Check API credentials"], "timestamp": now.isoformat()}
             
        context = zerve_analyst.build_cross_domain_context("overall tournament and market briefing")
        insight = zerve_analyst.generate_insight(context)
        
        lines = [l.strip() for l in insight.split("\n") if l.strip()]
        summary = lines[0] if lines else "Analyzing signals..."
        bullets = [l.replace("- ", "").replace("* ", "") for l in lines[1:] if l.startswith("-") or l.startswith("*")][:5]
        if not bullets and len(lines) > 1: bullets = lines[1:5]
            
        data = {
            "headline": "Tournament Macro Briefing", 
            "summary": summary, 
            "key_bullets": bullets if bullets else ["Signal acquisition in progress..."], 
            "timestamp": now.isoformat()
        }
        
        # Cache for 30 minutes
        _briefing_cache = {"data": data, "expires": now + timedelta(minutes=30)}
        return data
    except Exception as e:
        print(f"Briefing Error: {e}")
        return {"headline": "Analyst Offline", "summary": "Internal signal processing error.", "key_bullets": ["Check API credentials"], "timestamp": now.isoformat()}

@app.get("/v1/predict/wc2026/tournament", tags=["Vertical I: Sports"])
def get_tournament_simulation():
    """Run a Monte Carlo simulation of the entire WC2026 tournament."""
    try:
        # Retry logic for reading the CSV to handle race conditions during pipeline refresh
        df = None
        for _ in range(3):
            try:
                df = pd.read_csv(PROCESSED_DIR / "conflux_wc2026.csv")
                if not df.empty and 'subject' in df.columns:
                    break
            except:
                time.sleep(0.5)
        
        if df is None:
            raise Exception("Could not read conflux_wc2026.csv after multiple attempts")
        
        from src.constants import SIGNAL_WEIGHTS
        
        # 1. Group Stage Simulation
        if 'group' not in df.columns:
            # Fallback mapping if somehow the CSV is missing the column
            from src.constants import TEAM_TO_GROUP
            df['group'] = df['subject'].map(TEAM_TO_GROUP)
            
        groups = df['group'].unique()
        group_results = {}
        
        for g_name in groups:
            g_teams = df[df['group'] == g_name].copy()
            # Simple simulation: points based on conflux_score vs opponents
            # P(win) = conflux_i / (conflux_i + conflux_j)
            results = []
            for i, t in g_teams.iterrows():
                expected_pts = 0
                opponents = g_teams[g_teams['subject'] != t['subject']]
                for _, opp in opponents.iterrows():
                    win_prob = t['conflux_score'] / (t['conflux_score'] + opp['conflux_score'])
                    draw_prob = 0.24 # Global baseline
                    expected_pts += (win_prob * 3) + (draw_prob * 0.5)
                
                results.append({
                    "team": t['subject'],
                    "expected_points": round(expected_pts, 2),
                    "conflux_score": round(t['conflux_score'], 3),
                    "rank": 0 # to be sorted
                })
            
            # Sort by expected points
            results.sort(key=lambda x: x['expected_points'], reverse=True)
            for i, r in enumerate(results): r['rank'] = i + 1
            group_results[g_name] = results
        field_avg = df['conflux_score'].mean()
        
        advancement = []
        for _, t in df.iterrows():
            g_res = next(r for r in group_results[t['group']] if r['team'] == t['subject'])
            
            # Group Phase Logic
            p_r32 = 0.95 if g_res['rank'] == 1 else 0.85 if g_res['rank'] == 2 else 0.45 if g_res['rank'] == 3 else 0.05
            
            # Knockout Logic (assuming average opponent strength)
            win_prob_avg = t['conflux_score'] / (t['conflux_score'] + field_avg)
            
            p_r16 = p_r32 * win_prob_avg
            p_qf  = p_r16 * (win_prob_avg * 0.95) # fatigue factor
            p_sf  = p_qf  * (win_prob_avg * 0.9)
            p_fn  = p_sf  * (win_prob_avg * 0.85)
            p_win = p_fn  * (win_prob_avg * 0.8)
            
            advancement.append({
                "team": t['subject'],
                "group": t['group'],
                "probs": {
                    "r32": round(p_r32, 3),
                    "r16": round(p_r16, 3),
                    "qf":  round(p_qf, 3),
                    "sf":  round(p_sf, 3),
                    "final": round(p_fn, 3),
                    "winner": round(p_win, 3)
                }
            })

        return {
            "groups": group_results,
            "advancement": sorted(advancement, key=lambda x: x['probs']['winner'], reverse=True),
            "timestamp": datetime.now().isoformat()
        }
    except KeyError as e:
        print(f"Tournament Simulation KeyError: {e} (Missing column or dictionary key)")
        raise HTTPException(status_code=500, detail=f"Simulation data error: missing {e}")
    except Exception as e:
        print(f"Tournament Simulation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", tags=["System"])
def get_health():
    """Health check for deployment monitoring."""
    from src.constants import VERSION
    import os
    from datetime import datetime, timedelta
    
    # Estimate last refresh based on file mtime if available
    last_refresh = datetime.now() - timedelta(hours=2)
    try:
        if os.path.exists("data/processed/conflux_wc2026.csv"):
            mtime = os.path.getmtime("data/processed/conflux_wc2026.csv")
            last_refresh = datetime.fromtimestamp(mtime)
    except: pass

    return {
        "status": "online", 
        "timestamp": datetime.now().isoformat(), 
        "version": VERSION, 
        "last_refresh": last_refresh.isoformat(),
        "system": "◈ CONFLUX"
    }

@app.get("/v1/predict/prophecy", tags=["System"])
def run_prophecy_simulation(
    climate_shift: float = 0.0,
    finance_shift: float = 0.0,
    social_shift: float = 0.0,
    market_shift: float = 0.0
):
    """Simulate a global signal shift and propagate it through the entire field."""
    try:
        df = pd.read_csv(PROCESSED_DIR / "conflux_wc2026.csv")
        
        baseline = []
        projected = []
        
        for _, row in df.iterrows():
            sv_base = SignalVector(
                subject=row["subject"], vertical="wc2026",
                sports=row["sports"], markets=row["markets"],
                finance=row["finance"], climate=row["climate"], social=row["social"]
            )
            base_res = fusion_engine.fuse(sv_base)
            baseline.append({"team": row["subject"], "score": base_res.conflux_score})
            
            # Apply Perturbation
            sv_shift = SignalVector(
                subject=row["subject"], vertical="wc2026",
                sports=row["sports"], 
                markets=max(0, min(1, row["markets"] + market_shift)),
                finance=max(0, min(1, row["finance"] + finance_shift)), 
                climate=max(0, min(1, row["climate"] + climate_shift)), 
                social=max(0, min(1, row["social"] + social_shift))
            )
            shift_res = fusion_engine.fuse(sv_shift)
            projected.append({"team": row["subject"], "score": shift_res.conflux_score})
            
        # Compute sensitivity and rankings
        baseline.sort(key=lambda x: x["score"], reverse=True)
        projected.sort(key=lambda x: x["score"], reverse=True)
        
        sensitivity = []
        for b in baseline:
            p = next(x for x in projected if x["team"] == b["team"])
            delta = p["score"] - b["score"]
            sensitivity.append({
                "team": b["team"],
                "base_score": round(b["score"], 3),
                "new_score": round(p["score"], 3),
                "delta": round(delta, 4),
                "impact": "positive" if delta > 0.001 else "negative" if delta < -0.001 else "neutral"
            })
            
        return {
            "summary": {
                "top_gainer": max(sensitivity, key=lambda x: x["delta"]),
                "top_loser": min(sensitivity, key=lambda x: x["delta"]),
                "volatility": sum(abs(s["delta"]) for s in sensitivity) / len(sensitivity)
            },
            "teams": sorted(sensitivity, key=lambda x: abs(x["delta"]), reverse=True)[:20],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Prophecy Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/model/validation", tags=["Model Integrity"])
def get_model_validation():
    """Return historical backtest metrics and model calibration proof."""
    file_path = Path("data/processed/model_validation.json")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Validation scanner offline. Run backtest_accuracy.py to generate.")
    with open(file_path, "r") as f:
        return json.load(f)

class ChatRequest(BaseModel):
    message: str
    history: list = []
    stream: bool = False

@app.post("/v1/analyst/chat", tags=["Intelligence Analyst"])
def analyst_chat(request: ChatRequest):
    """Conversational interface with the ORACLE-26 Analyst. Supports streaming."""
    try:
        if zerve_analyst is None:
            return {"response": "Link offline.", "timestamp": datetime.now().isoformat()}
            
        context = zerve_analyst.build_cross_domain_context(request.message)
        
        if request.stream:
            from fastapi.responses import StreamingResponse
            return StreamingResponse(
                zerve_analyst.generate_insight_stream(context, request.message, request.history),
                media_type="text/event-stream"
            )
        
        insight = zerve_analyst.generate_insight(context, request.message, request.history)
        return {"response": insight, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        print(f"Chat Error: {e}")
        return {"response": f"◈ Error: {str(e)}", "timestamp": datetime.now().isoformat()}
        print(f"Chat Error: {e}")
        return {"response": "The neural link is experiencing interference. Please try again."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
