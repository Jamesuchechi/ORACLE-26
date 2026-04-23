"""
ORACLE-26 — API Schemas
=========================
Pydantic models for request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class SignalBreakdown(BaseModel):
    sports:   float = Field(..., description="Normalized sports signal (0-1)")
    markets:  float = Field(..., description="Normalized market signal (0-1)")
    economic: float = Field(..., description="Normalized economic signal (0-1)")
    climate:  float = Field(..., description="Normalized climate signal (0-1)")
    social:   float = Field(..., description="Normalized social signal (0-1)")

class MatchPredictionResponse(BaseModel):
    team1: str
    team2: str
    venue: str
    date: str
    win_prob: float
    draw_prob: float
    loss_prob: float
    expected_goals: Dict[str, float]
    most_likely_score: str
    signal_breakdown: SignalBreakdown
    confidence: str = Field(..., description="Low, Medium, or High")
    model_version: str

class TeamProfileResponse(BaseModel):
    team: str
    group: str
    rank: int
    strength_score: float
    oracle_score: float
    top_signals: List[str]
    tournament_odds: Dict[str, float]

class GroupSimulationResponse(BaseModel):
    group: str
    standings: List[Dict[str, float]]
    qualified: List[str]

class BracketSimulationResponse(BaseModel):
    simulation_id: str
    last_updated: str
    top_favorites: List[Dict[str, float]]
    full_bracket_url: Optional[str]
