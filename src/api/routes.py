"""
ORACLE-26 — API Routes
========================
Endpoint definitions for the FastAPI application.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.api.schemas import MatchPredictionResponse, TeamProfileResponse, SignalBreakdown
from src.models.poisson import PoissonModel
from src.constants import ALL_TEAMS, MONTE_CARLO_SIMS

router = APIRouter()

# Load data at startup
DATA_DIR = Path("data/processed")
FUSED_PATH = DATA_DIR / "oracle_fused_signals.csv"

try:
    fused_df = pd.read_csv(FUSED_PATH)
except:
    fused_df = None

try:
    poisson_model = PoissonModel.load()
except:
    poisson_model = None

@router.get("/")
async def health_check():
    return {"status": "active", "engine": "ORACLE-26", "version": "1.0.0"}

@router.get("/predict", response_model=MatchPredictionResponse)
async def predict_match(
    team1: str = Query(..., description="Name of Team 1"),
    team2: str = Query(..., description="Name of Team 2"),
    venue: str = Query("MetLife Stadium", description="Venue name"),
    date: str = Query("2026-07-01", description="Match date")
):
    if team1 not in ALL_TEAMS or team2 not in ALL_TEAMS:
        raise HTTPException(status_code=404, detail="One or both teams not found in WC2026 roster")

    # 1. Sports Prediction
    pred = poisson_model.predict_match(team1, team2, fused_df)
    
    # 2. Get Signal Breakdown
    t1_fused = fused_df[fused_df["team"] == team1].iloc[0]
    t2_fused = fused_df[fused_df["team"] == team2].iloc[0]
    
    breakdown = SignalBreakdown(
        sports=   (t1_fused["sports_signal"] + t2_fused["sports_signal"]) / 2,
        markets=  (t1_fused["market_signal"] + t2_fused["market_signal"]) / 2,
        economic= (t1_fused["econ_signal"]   + t2_fused["econ_signal"]) / 2,
        climate=  0.7, # Mocked for now, will pull from climate.py
        social=   (t1_fused["social_signal"] + t2_fused["social_signal"]) / 2
    )

    return MatchPredictionResponse(
        team1=team1,
        team2=team2,
        venue=venue,
        date=date,
        win_prob=pred["win_prob"],
        draw_prob=pred["draw_prob"],
        loss_prob=pred["loss_prob"],
        expected_goals={team1: pred["xg1"], team2: pred["xg2"]},
        most_likely_score=pred["most_likely_score"],
        signal_breakdown=breakdown,
        confidence="High" if pred["win_prob"] > 0.5 or pred["loss_prob"] > 0.5 else "Medium",
        model_version="oracle26-v1-poisson"
    )

@router.get("/team/{name}", response_model=TeamProfileResponse)
async def get_team_profile(name: str):
    if fused_df is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    team_data = fused_df[fused_df["team"] == name]
    if team_data.empty:
        raise HTTPException(status_code=404, detail="Team not found")
    
    t = team_data.iloc[0]
    return TeamProfileResponse(
        team=name,
        group=t["group"],
        rank=int(t["oracle_rank"]),
        strength_score=float(t["strength_score"]),
        oracle_score=float(t["oracle_score"]),
        top_signals=["Sports", "Markets"] if t["market_signal"] > 0.05 else ["Sports"],
        tournament_odds={"win": 0.05, "final": 0.12} # Mocked from simulation
    )
