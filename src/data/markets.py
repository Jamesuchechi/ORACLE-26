"""
◈ CONFLUX — Markets Signal
============================
Fetches real-money prediction market odds and detects systematic
mispricing vs macro and social signals.

Covers all four verticals:
  - WC2026 match odds
  - Election / policy event probabilities  
  - Commodity / finance event odds
  - Cultural milestone betting
"""

import os
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
from dataclasses import dataclass

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import (
    ALL_WC_TEAMS, TRACKED_MARKET_EVENTS,
    MARKET_DIVERGENCE_THRESHOLD, MARKET_ALPHA_STRONG
)

load_dotenv()
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class MarketSignal:
    event_id:     str
    source:       str            # polymarket | kalshi | metaculus
    implied_prob: float          # [0, 1]
    volume_usd:   Optional[float] = None
    last_updated: Optional[str]  = None
    raw_odds:     Optional[float] = None


class MarketSignalEngine:
    """
    Pulls and normalizes prediction market signals across all verticals.
    """

    def __init__(self):
        self.kalshi_email = os.getenv("KALSHI_EMAIL")
        self.kalshi_pass  = os.getenv("KALSHI_PASSWORD")
        self._kalshi_token: Optional[str] = None

    # ──────────────────────────────────────────────
    # Polymarket
    # ──────────────────────────────────────────────

    def fetch_polymarket_event(self, slug: str) -> Optional[MarketSignal]:
        """Fetch a single Polymarket event by slug."""
        try:
            url = f"https://gamma-api.polymarket.com/markets?slug={slug}"
            resp = requests.get(url, timeout=8)
            data = resp.json()
            if not data:
                return None
            m = data[0]
            price = float(m.get("outcomePrices", [0.5])[0])
            return MarketSignal(
                event_id=slug, source="polymarket",
                implied_prob=price,
                volume_usd=float(m.get("volume", 0)),
            )
        except Exception as e:
            print(f"  [markets] Polymarket failed for {slug}: {e}")
            return None

    def scan_wc_markets(self) -> pd.DataFrame:
        """Scan Polymarket for WC2026 team winner odds."""
        print("  [markets] Scanning WC2026 Polymarket odds...")
        rows = []
        for team in ALL_WC_TEAMS:
            slug = f"fifa-world-cup-2026-winner-{team.lower().replace(' ', '-')}"
            sig  = self.fetch_polymarket_event(slug)
            prob = sig.implied_prob if sig else self._fallback_market_prob(team)
            rows.append({
                "team":            team,
                "market_prob":     round(prob, 4),
                "market_signal":   round(prob, 4),   # normalized [0,1] by nature
                "source":          sig.source if sig else "fallback",
                "volume_usd":      sig.volume_usd if sig else None,
            })
        df = pd.DataFrame(rows)
        df.to_csv(RAW_DIR / "market_signals_wc.csv", index=False)
        return df

    # ──────────────────────────────────────────────
    # General Event Markets (Vertical II)
    # ──────────────────────────────────────────────

    def fetch_general_markets(self) -> pd.DataFrame:
        """Fetch all tracked market events (Fed, BTC, elections, etc.)"""
        print("  [markets] Fetching general market events...")
        rows = []
        for event_id, meta in TRACKED_MARKET_EVENTS.items():
            sig = self.fetch_polymarket_event(event_id)
            if sig:
                rows.append({
                    "event_id":    event_id,
                    "description": meta["description"],
                    "type":        meta["type"],
                    "implied_prob":sig.implied_prob,
                    "source":      sig.source,
                    "volume_usd":  sig.volume_usd,
                })
            else:
                rows.append({
                    "event_id":    event_id,
                    "description": meta["description"],
                    "type":        meta["type"],
                    "implied_prob": 0.50,  # neutral fallback
                    "source":      "fallback",
                    "volume_usd":  None,
                })

        df = pd.DataFrame(rows)
        df.to_csv(RAW_DIR / "market_signals_events.csv", index=False)
        return df

    # ──────────────────────────────────────────────
    # Market Alpha: Divergence Detection (Vertical II core)
    # ──────────────────────────────────────────────

    def compute_market_alpha(
        self,
        market_prob: float,
        model_prob: float,
        event_type: str = "general",
    ) -> dict:
        """
        Compute the CONFLUX market alpha signal.
        
        Alpha = model_prob - market_prob
        Positive: market under-prices what the data says
        Negative: market over-prices (hype signal)
        """
        alpha = model_prob - market_prob
        abs_alpha = abs(alpha)

        if abs_alpha >= MARKET_ALPHA_STRONG:
            signal_strength = "strong"
        elif abs_alpha >= MARKET_DIVERGENCE_THRESHOLD:
            signal_strength = "moderate"
        else:
            signal_strength = "noise"

        direction = "value" if alpha > 0 else "hype"

        return {
            "alpha":            round(alpha, 4),
            "abs_alpha":        round(abs_alpha, 4),
            "signal_strength":  signal_strength,
            "direction":        direction,
            "market_prob":      round(market_prob, 4),
            "model_prob":       round(model_prob, 4),
            "interpretation": (
                f"Market {'undervalues' if alpha > 0 else 'overvalues'} this outcome "
                f"by {abs_alpha:.1%} vs model. "
                f"{'Potential value opportunity.' if direction == 'value' else 'Potential hype trap.'}"
            ) if signal_strength != "noise" else "Signal within noise threshold — no actionable divergence.",
        }

    # ──────────────────────────────────────────────
    # Normalize to [0, 1] for fusion
    # ──────────────────────────────────────────────

    def normalize_market_signal(
        self, market_prob: float, all_probs: list
    ) -> float:
        """
        Normalize a market probability relative to the distribution
        of all market probabilities in the same event class.
        Converts raw probability to a [0,1] relative strength signal.
        """
        if not all_probs or max(all_probs) == min(all_probs):
            return market_prob
        return float(
            (market_prob - min(all_probs)) / (max(all_probs) - min(all_probs))
        )

    # ──────────────────────────────────────────────
    # Fallback: Elo-derived market proxy
    # ──────────────────────────────────────────────

    def _fallback_market_prob(self, team: str) -> float:
        """Generate a plausible market proxy from Elo when API unavailable."""
        from src.constants import CURATED_ELO
        elo     = CURATED_ELO.get(team, 1700)
        elo_min = min(CURATED_ELO.values())
        elo_max = max(CURATED_ELO.values())
        # Softmax-like: exponential to create realistic winner market shape
        relative = (elo - elo_min) / (elo_max - elo_min)
        # Apply tournament compression (no team > 30%, most < 5%)
        return float(np.clip(relative ** 2.5 * 0.30, 0.002, 0.30))

    # ──────────────────────────────────────────────
    # Run Full Collection
    # ──────────────────────────────────────────────

    def run(self) -> dict:
        print("\n" + "=" * 50)
        print("◈ CONFLUX | Markets Signal Collection")
        print("=" * 50)
        wc_df    = self.scan_wc_markets()
        event_df = self.fetch_general_markets()
        return {"wc": wc_df, "events": event_df}


if __name__ == "__main__":
    engine = MarketSignalEngine()
    results = engine.run()

    print("\nWC2026 Market Odds (top 10):")
    print(results["wc"].head(10)[["team","market_prob","source"]].to_string(index=False))

    print("\nGeneral Events:")
    print(results["events"][["event_id","implied_prob","source"]].to_string(index=False))