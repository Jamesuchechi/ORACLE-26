"""
◈ CONFLUX — Signal Fusion Core
================================
The engine that normalizes, weights, and combines five independent
signal domains into a single intelligence layer per vertical.

This is the intellectual heart of CONFLUX. All verticals route through here.
"""

import numpy as np
import pandas as pd
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import (
    SIGNAL_WEIGHTS, DIVERGENCE_MILD, DIVERGENCE_MODERATE, DIVERGENCE_STRONG,
    MARKET_DIVERGENCE_THRESHOLD
)


@dataclass
class SignalVector:
    """
    Normalized representation of all five signal scores for a subject.
    All values are in [0, 1].
    """
    subject:  str
    vertical: str                     # wc2026 | market_calib | climate_risk | cultural_moment

    sports:   float = 0.5
    markets:  float = 0.5
    finance:  float = 0.5
    climate:  float = 0.5
    social:   float = 0.5

    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "subject":  self.subject,
            "vertical": self.vertical,
            "sports":   round(self.sports,  4),
            "markets":  round(self.markets, 4),
            "finance":  round(self.finance, 4),
            "climate":  round(self.climate, 4),
            "social":   round(self.social,  4),
        }


@dataclass
class FusionResult:
    """
    The output of the fusion engine for a single prediction request.
    """
    subject:       str
    vertical:      str
    conflux_score: float          # Weighted composite [0, 1]
    confidence:    str            # low | medium | high
    divergences:   list           # Cross-domain surprises detected
    signal_vector: SignalVector
    interpretation: str           # Human-readable summary
    metadata:       dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "subject":        self.subject,
            "vertical":       self.vertical,
            "conflux_score":  round(self.conflux_score, 4),
            "confidence":     self.confidence,
            "divergences":    self.divergences,
            "signal_breakdown": self.signal_vector.to_dict(),
            "interpretation": self.interpretation,
        }


class ConfluxFusionEngine:
    """
    The core fusion engine. Normalizes and aggregates signal vectors
    using vertical-specific weights, then detects cross-domain divergences.

    Usage:
        engine = ConfluxFusionEngine()
        result = engine.fuse(signal_vector)
    """

    def __init__(self):
        self.weights = SIGNAL_WEIGHTS

    # ─────────────────────────────────────────
    # Main Fusion Method
    # ─────────────────────────────────────────

    def fuse(self, sv: SignalVector, custom_weights: Optional[dict] = None) -> FusionResult:
        """
        Fuse a SignalVector into a CONFLUX prediction.
        Supports optional custom weights for 'What-If' analysis.
        """
        # 1. Use custom weights if provided, else fall back to vertical defaults
        base_weights = self.weights.get(sv.vertical, self.weights["wc2026"])
        w = custom_weights if custom_weights else base_weights

        # 2. Apply Cross-Domain Interaction Effects (The CONFLUX Thesis)
        sv = self._apply_interaction_effects(sv)

        # 3. Weighted composite
        score = (
            sv.sports   * w.get("sports", 0)  +
            sv.markets  * w.get("markets", 0) +
            sv.finance  * w.get("finance", 0) +
            sv.climate  * w.get("climate", 0) +
            sv.social   * w.get("social", 0)
        )

        # 4. Normalize score by weights sum if they don't add to 1.0
        weight_sum = sum(w.values())
        if weight_sum > 0:
            score = score / weight_sum

        # 5. Cross-domain divergence detection
        divergences = self._detect_divergences(sv, w)

        # 6. Confidence: based on spread of signals
        signal_values = [sv.sports, sv.markets, sv.finance, sv.climate, sv.social]
        signal_std    = float(np.std(signal_values))
        confidence    = self._score_to_confidence(score, signal_std)

        # 7. Key Drivers (For explainability in React)
        key_drivers = self._get_key_drivers(sv, w)

        # 8. Interpretation
        interpretation = self._interpret(sv, score, divergences, w)

        return FusionResult(
            subject        = sv.subject,
            vertical       = sv.vertical,
            conflux_score  = float(score),
            confidence     = confidence,
            divergences    = divergences,
            signal_vector  = sv,
            interpretation = interpretation,
            metadata       = {"key_drivers": key_drivers}
        )

    def _get_key_drivers(self, sv: SignalVector, w: dict) -> list:
        """Identify the top positive and negative contributors to the score."""
        drivers = [
            {"name": "Sports",  "val": sv.sports,  "weight": w.get("sports", 0)},
            {"name": "Markets", "val": sv.markets, "weight": w.get("markets", 0)},
            {"name": "Finance", "val": sv.finance, "weight": w.get("finance", 0)},
            {"name": "Climate", "val": sv.climate, "weight": w.get("climate", 0)},
            {"name": "Social",  "val": sv.social,  "weight": w.get("social", 0)},
        ]
        
        for d in drivers:
            d["impact"] = round((d["val"] - 0.5) * d["weight"], 4)
            
        # Sort by absolute impact
        return sorted(drivers, key=lambda x: abs(x["impact"]), reverse=True)

    # ─────────────────────────────────────────
    # Interaction Logic (The Thesis)
    # ─────────────────────────────────────────

    def _apply_interaction_effects(self, sv: SignalVector) -> SignalVector:
        """
        Implement the CONFLUX thesis: signals don't just add up, they interact.
        Returns a modified SignalVector with interaction adjustments.
        """
        # Rule 1: Economic Stress → Performance Penalty
        if sv.vertical == "wc2026" and sv.finance < 0.3:
            penalty = (0.3 - sv.finance) * 0.5
            sv.sports = max(0.01, sv.sports - penalty)
            sv.metadata["interactions"] = sv.metadata.get("interactions", []) + ["Econ penalty applied to Sports"]

        # Rule 2: Social Momentum → Market Alpha
        if sv.vertical in ["market_calib", "cultural_moment"]:
            if sv.social > 0.8 and sv.markets < 0.4:
                sv.markets += (sv.social - sv.markets) * 0.2
                sv.metadata["interactions"] = sv.metadata.get("interactions", []) + ["Social-Market alpha adjustment"]

        # Rule 3: Climate Stress → Infrastructure Risk
        if sv.vertical == "climate_risk" and sv.climate > 0.8 and sv.finance < 0.4:
            sv.climate = min(1.0, sv.climate + 0.15)
            sv.metadata["interactions"] = sv.metadata.get("interactions", []) + ["Climate-Finance risk escalation"]

        return sv

    # ─────────────────────────────────────────
    # Match Fusion (two-team comparison)
    # ─────────────────────────────────────────

    def fuse_match(
        self,
        sv1: SignalVector,   # Team 1
        sv2: SignalVector,   # Team 2
        sports_win_prob: float,
        sports_draw_prob: float,
        custom_weights: Optional[dict] = None
    ) -> dict:
        """
        Fuse two team signal vectors into a match prediction.
        Adjusts the base sports probability with multi-signal deltas.
        """
        r1 = self.fuse(sv1, custom_weights=custom_weights)
        r2 = self.fuse(sv2, custom_weights=custom_weights)

        # Signal delta (positive favours team1)
        delta = r1.conflux_score - r2.conflux_score

        # Map delta to probability adjustment (sigmoid-like)
        # delta in [-1, 1], adjustment in [-0.15, +0.15]
        adjustment = np.tanh(delta * 3) * 0.15

        # Adjust win probability
        raw_win  = sports_win_prob  + adjustment
        raw_loss = sports_draw_prob - adjustment   # symmetrical
        raw_draw = 1 - raw_win - max(0, raw_loss)

        # Normalize to sum = 1
        total  = raw_win + raw_draw + max(0, raw_loss)
        win_p  = max(0.02, raw_win  / total)
        draw_p = max(0.05, raw_draw / total)
        loss_p = max(0.02, max(0, raw_loss) / total)

        # Re-normalize after floors
        s     = win_p + draw_p + loss_p
        win_p /= s; draw_p /= s; loss_p /= s

        # Divergence signals (cross-vertical surprises)
        divergences = self._detect_match_divergences(sv1, sv2)

        return {
            "team1":               sv1.subject,
            "team2":               sv2.subject,
            "win_prob":            round(float(win_p),  3),
            "draw_prob":           round(float(draw_p), 3),
            "loss_prob":           round(float(loss_p), 3),
            "signal_delta":        round(float(delta),  4),
            "confidence":          r1.confidence if abs(delta) > 0.1 else "medium",
            "divergences":         divergences,
            "team1_conflux":       round(r1.conflux_score, 4),
            "team2_conflux":       round(r2.conflux_score, 4),
            "team1_breakdown":     sv1.to_dict(),
            "team2_breakdown":     sv2.to_dict(),
        }

    # ─────────────────────────────────────────
    # Divergence Detection
    # ─────────────────────────────────────────

    def _detect_divergences(
        self, sv: SignalVector, weights: dict
    ) -> list:
        """
        Find cases where a high-weight signal strongly disagrees
        with the composite. These are the 'surprises' CONFLUX surfaces.
        """
        signals = {
            "sports":  sv.sports,
            "markets": sv.markets,
            "finance": sv.finance,
            "climate": sv.climate,
            "social":  sv.social,
        }
        mean_signal = np.mean(list(signals.values()))
        divergences = []

        for domain, value in signals.items():
            gap = abs(value - mean_signal)
            w   = weights.get(domain, 0.1)

            if gap >= DIVERGENCE_STRONG and w >= 0.10:
                divergences.append({
                    "domain":    domain,
                    "direction": "above" if value > mean_signal else "below",
                    "magnitude": round(gap, 3),
                    "severity":  "strong",
                    "message":   f"{domain.title()} signal strongly {'exceeds' if value > mean_signal else 'lags'} composite by {gap:.0%}",
                })
            elif gap >= DIVERGENCE_MODERATE and w >= 0.15:
                divergences.append({
                    "domain":    domain,
                    "direction": "above" if value > mean_signal else "below",
                    "magnitude": round(gap, 3),
                    "severity":  "moderate",
                    "message":   f"{domain.title()} signal diverges from consensus ({gap:.0%} gap)",
                })

        return divergences

    def _detect_match_divergences(
        self, sv1: SignalVector, sv2: SignalVector
    ) -> list:
        """Detect where signals tell different stories for each team."""
        domains = ["sports", "markets", "finance", "climate", "social"]
        divergences = []

        for domain in domains:
            v1 = getattr(sv1, domain)
            v2 = getattr(sv2, domain)
            gap = abs(v1 - v2)
            if gap >= DIVERGENCE_MODERATE:
                favour = sv1.subject if v1 > v2 else sv2.subject
                divergences.append({
                    "domain":    domain,
                    "favour":    favour,
                    "magnitude": round(gap, 3),
                    "severity":  "strong" if gap >= DIVERGENCE_STRONG else "moderate",
                    "message":   f"{domain.title()} strongly favours {favour} ({gap:.0%} gap vs opponent)",
                })

        return divergences

    # ─────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────

    def _score_to_confidence(self, score: float, signal_std: float) -> str:
        """Map score extremity and signal agreement to confidence level."""
        extremity = abs(score - 0.5) * 2   # 0 = perfectly uncertain, 1 = extreme
        agreement = 1 - min(signal_std * 4, 1)  # 1 = all signals agree

        combined = extremity * 0.5 + agreement * 0.5

        if combined >= 0.65:
            return "high"
        elif combined >= 0.40:
            return "medium"
        else:
            return "low"

    def _interpret(
        self,
        sv: SignalVector,
        score: float,
        divergences: list,
        weights: dict,
    ) -> str:
        """Generate a plain-English interpretation of the fusion result."""
        # Find dominant signal (highest weight × value)
        domains = {
            "sports": sv.sports, "markets": sv.markets,
            "finance": sv.finance, "climate": sv.climate, "social": sv.social,
        }
        dominant = max(domains, key=lambda d: domains[d] * weights.get(d, 0.1))
        dominant_val = domains[dominant]

        direction = "strong" if score > 0.65 else ("moderate" if score > 0.55 else ("neutral" if score > 0.45 else "adverse"))

        base = f"CONFLUX score {score:.2f} — {direction} outlook driven primarily by {dominant} signal ({dominant_val:.2f})."

        if divergences:
            surprise = divergences[0]
            base += f" Notable divergence: {surprise['message']}."

        return base

    # ─────────────────────────────────────────
    # Batch Fusion (for full tournament / market scan)
    # ─────────────────────────────────────────

    def fuse_batch(self, signal_vectors: list[SignalVector]) -> pd.DataFrame:
        """Fuse a list of SignalVectors and return a ranked DataFrame."""
        results = [self.fuse(sv) for sv in signal_vectors]
        rows = []
        for r in results:
            row = r.signal_vector.to_dict()
            row.update({
                "conflux_score": r.conflux_score,
                "confidence":    r.confidence,
                "n_divergences": len(r.divergences),
                "interpretation": r.interpretation,
            })
            rows.append(row)

        df = pd.DataFrame(rows).sort_values("conflux_score", ascending=False).reset_index(drop=True)
        df["conflux_rank"] = df.index + 1
        return df