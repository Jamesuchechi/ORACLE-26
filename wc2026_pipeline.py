"""
◈ CONFLUX — Master Pipeline
=============================
Orchestrates all data collection, feature engineering, and signal fusion
across all four intelligence verticals.

Usage:
    python pipeline.py --all
    python pipeline.py --vertical wc2026
    python pipeline.py --vertical market_calib
    python pipeline.py --vertical climate_risk
    python pipeline.py --vertical cultural_moment
"""

import argparse
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from typing import Optional
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from src.constants import (
    ALL_WC_TEAMS, TEAM_TO_GROUP, SIGNAL_WEIGHTS, GROUP_TO_VENUES,
    TRACKED_MARKET_EVENTS, TRACKED_CLIMATE_REGIONS, TRACKED_CULTURAL_TOPICS,

    CURATED_ELO
)
from src.data.sports    import SportsSignalEngine
from src.data.markets   import MarketSignalEngine
from src.data.economics import EconomicSignalEngine
from src.data.climate   import ClimateSignalEngine
from src.data.social    import SocialSignalEngine
from src.features.fusion import ConfluxFusionEngine, SignalVector

PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                    ◈  C O N F L U X                         ║
║           Universal Multi-Signal Intelligence Engine         ║
║                                                              ║
║   5 Signals  ×  4 Verticals  =  Predictive Edge             ║
╚══════════════════════════════════════════════════════════════╝
"""


class ConfluxPipeline:
    """Master orchestrator for all CONFLUX intelligence production."""

    def __init__(self):
        self.sports    = SportsSignalEngine()
        self.markets   = MarketSignalEngine()
        self.economics = EconomicSignalEngine()
        self.climate   = ClimateSignalEngine()
        self.social    = SocialSignalEngine()
        self.fusion    = ConfluxFusionEngine()

        self.sports_features   = None
        self.market_signals    = None
        self.economic_signals  = None
        self.climate_signals   = None
        self.social_signals    = None

    # ──────────────────────────────────────────────────────────────
    # Phase 0: Data Collection
    # ──────────────────────────────────────────────────────────────

    def collect_all_signals(self):
        print("\n[PHASE 0] Signal Collection")
        print("─" * 50)

        print("\n  → Sports")
        self.sports_features = self.sports.build_all_features()

        print("\n  → Markets")
        market_results = self.markets.run()
        self.market_signals = market_results.get("wc")

        print("\n  → Economics")
        self.economic_signals = self.economics.build_all_signals()

        print("\n  → Climate (venues)")
        climate_results = self.climate.run()
        self.climate_signals = climate_results.get("venues")

        print("\n  → Social")
        social_results = self.social.run()
        self.social_signals = social_results.get("teams")

        print("\n  ✓ All signals collected")

    # ──────────────────────────────────────────────────────────────
    # Phase 1: Vertical I — WC2026
    # ──────────────────────────────────────────────────────────────

    def run_wc2026(self) -> pd.DataFrame:
        print("\n[PHASE 1] Vertical I — World Cup 2026")
        print("─" * 50)

        if self.sports_features is None:
            self._lazy_load()

        signal_vectors = []

        for team in ALL_WC_TEAMS:
            s_row = self._get_row(self.sports_features,   "team", team)
            m_row = self._get_row(self.market_signals,    "team", team)
            e_row = self._get_row(self.economic_signals,  "team", team)
            c_row = self._get_row(self.climate_signals,   "venue", None)  # venue-level, handled at match time
            soc_row = self._get_row(self.social_signals,  "team", team)
            
            # Compute team-level climate signal based on assigned group venues
            climate_val = self._get_team_climate_signal(team)


            # Market signal: normalize across all teams
            all_mkt = self.market_signals["market_signal"].tolist() if self.market_signals is not None else []
            m_norm  = self.markets.normalize_market_signal(
                float(m_row.get("market_signal", 0.02)) if m_row else 0.02,
                all_mkt
            )

            sv = SignalVector(
                subject   = team,
                vertical  = "wc2026",
                sports    = float(s_row.get("sports_signal", 0.5) if s_row else 0.5),
                markets   = float(m_norm),
                finance   = float(e_row.get("econ_signal",   0.5) if e_row else 0.5),
                climate   = float(climate_val),

                social    = float(soc_row.get("social_signal", 0.5) if soc_row else 0.5),
            )
            signal_vectors.append(sv)

        fused_df = self.fusion.fuse_batch(signal_vectors)

        # Merge with sports features for full profile
        fused_df["group"] = fused_df["subject"].map(TEAM_TO_GROUP)
        fused_df["elo"]   = fused_df["subject"].map(CURATED_ELO)

        out = PROCESSED_DIR / "conflux_wc2026.csv"
        fused_df.to_csv(out, index=False)
        print(f"  ✓ WC2026 intelligence saved → {out}")

        print("\n  TOP 10 CONFLUX RANKINGS:")
        top10 = fused_df[["subject", "group", "elo", "sports", "markets",
                           "finance", "climate", "social", "conflux_score",
                           "confidence"]].head(10)
        print(top10.to_string(index=False))

        return fused_df

    # ──────────────────────────────────────────────────────────────
    # Phase 2: Vertical II — Market Calibration
    # ──────────────────────────────────────────────────────────────

    def run_market_calibration(self) -> pd.DataFrame:
        print("\n[PHASE 2] Vertical II — Prediction Market Calibration")
        print("─" * 50)

        event_df = self.markets.fetch_general_markets()
        rows = []

        for _, row in event_df.iterrows():
            market_prob = row["implied_prob"]
            event_type  = row["type"]

            # Build model-implied probability from economic + social signals
            # (simplified: economic stability → macro events, social → tech/cultural)
            avg_econ   = self.economic_signals["econ_signal"].mean() if self.economic_signals is not None else 0.5
            avg_social = self.social_signals["social_signal"].mean() if self.social_signals is not None else 0.5
            model_prob = avg_econ * 0.6 + avg_social * 0.4

            alpha = self.markets.compute_market_alpha(market_prob, model_prob, event_type)

            sv = SignalVector(
                subject  = row["event_id"],
                vertical = "market_calib",
                sports   = 0.5,
                markets  = float(market_prob),
                finance  = float(avg_econ),
                climate  = 0.5,
                social   = float(avg_social),
            )
            result = self.fusion.fuse(sv)

            rows.append({
                "event_id":       row["event_id"],
                "description":    row["description"],
                "type":           row["type"],
                "market_prob":    market_prob,
                "model_prob":     round(model_prob, 4),
                "alpha":          alpha["alpha"],
                "signal_strength":alpha["signal_strength"],
                "direction":      alpha["direction"],
                "conflux_score":  result.conflux_score,
                "interpretation": alpha["interpretation"],
            })

        df = pd.DataFrame(rows).sort_values("alpha", key=abs, ascending=False)
        df.to_csv(PROCESSED_DIR / "conflux_market_calib.csv", index=False)
        print(f"  ✓ Market calibration saved → {PROCESSED_DIR}/conflux_market_calib.csv")
        print(df[["event_id", "market_prob", "model_prob", "alpha", "signal_strength"]].to_string(index=False))
        return df

    # ──────────────────────────────────────────────────────────────
    # Phase 3: Vertical III — Climate Risk
    # ──────────────────────────────────────────────────────────────

    def run_climate_risk(self) -> pd.DataFrame:
        print("\n[PHASE 3] Vertical III — Climate Risk Intelligence")
        print("─" * 50)

        regional = self.climate.build_regional_risks()
        rows = []

        for _, row in regional.iterrows():
            region = row["region"]
            econ_row = self.economic_signals[self.economic_signals["team"] == "USA"].iloc[0] \
                if self.economic_signals is not None else None
            soc_row  = self.social_signals[self.social_signals["team"] == "USA"].iloc[0] \
                if self.social_signals is not None else None

            sv = SignalVector(
                subject  = region,
                vertical = "climate_risk",
                sports   = 0.5,
                markets  = 0.5,
                finance  = float(econ_row["econ_signal"]) if econ_row is not None else 0.5,
                climate  = float(row["climate_risk_signal"]),
                social   = float(soc_row["social_signal"]) if soc_row is not None else 0.5,
            )
            result = self.fusion.fuse(sv)

            rows.append({
                "region":         region,
                "risk_type":      row["risk_type"],
                "avg_temp_c":     row["avg_temp_c"],
                "raw_risk":       row["climate_risk_signal"],
                "conflux_risk":   result.conflux_score,
                "confidence":     result.confidence,
                "interpretation": result.interpretation,
            })

        df = pd.DataFrame(rows).sort_values("conflux_risk", ascending=False)
        df.to_csv(PROCESSED_DIR / "conflux_climate_risk.csv", index=False)
        print(f"  ✓ Climate risk saved → {PROCESSED_DIR}/conflux_climate_risk.csv")
        print(df[["region", "risk_type", "conflux_risk", "confidence"]].to_string(index=False))
        return df

    # ──────────────────────────────────────────────────────────────
    # Phase 4: Vertical IV — Cultural Moment
    # ──────────────────────────────────────────────────────────────

    def run_cultural_moment(self) -> pd.DataFrame:
        print("\n[PHASE 4] Vertical IV — Cultural Moment Detection")
        print("─" * 50)

        cultural_df = self.social.build_cultural_moment_signals()
        rows = []

        for _, row in cultural_df.iterrows():
            sv = SignalVector(
                subject  = row["topic"],
                vertical = "cultural_moment",
                sports   = 0.5,
                markets  = 0.5,
                finance  = 0.5,
                climate  = 0.5,
                social   = float(row["social_signal"]),
            )
            result = self.fusion.fuse(sv)

            rows.append({
                "topic":          row["topic"],
                "category":       row["category"],
                "market_proxy":   row.get("market_proxy"),
                "tipping_score":  row["tipping_score"],
                "is_tipping":     row["is_tipping"],
                "conflux_score":  result.conflux_score,
                "interpretation": row["interpretation"],
            })

        df = pd.DataFrame(rows).sort_values("conflux_score", ascending=False)
        df.to_csv(PROCESSED_DIR / "conflux_cultural_moment.csv", index=False)
        print(f"  ✓ Cultural moments saved → {PROCESSED_DIR}/conflux_cultural_moment.csv")
        print(df[["topic", "tipping_score", "is_tipping", "conflux_score"]].to_string(index=False))
        return df

    # ──────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────

    def _lazy_load(self):
        """Load cached signals from disk if not already in memory."""
        cached_sports = PROCESSED_DIR / "sports_features.csv"
        cached_econ   = Path("data/raw/economic_signals.csv")
        cached_social = Path("data/raw/social_signals_wc.csv")
        cached_market = Path("data/raw/market_signals_wc.csv")

        if cached_sports.exists():
            self.sports_features = pd.read_csv(cached_sports)
        if cached_econ.exists():
            self.economic_signals = pd.read_csv(cached_econ)
        if cached_social.exists():
            self.social_signals = pd.read_csv(cached_social)
        if cached_market.exists():
            self.market_signals = pd.read_csv(cached_market)

    def _get_row(self, df: pd.DataFrame, col: str, val) -> Optional[dict]:
        if df is None or val is None:
            return None
        rows = df[df[col] == val]
        return rows.iloc[0].to_dict() if not rows.empty else None

    def _get_team_climate_signal(self, team: str) -> float:
        """Map each team to their group's likely venues and average the climate signals."""
        group = TEAM_TO_GROUP.get(team)
        if not group or group not in GROUP_TO_VENUES or self.climate_signals is None:
            return 0.75
            
        venues = GROUP_TO_VENUES[group]
        signals = []
        
        for v in venues:
            # Look up signal for this venue
            v_match = self.climate_signals[self.climate_signals["venue"] == v]
            if not v_match.empty:
                signals.append(v_match["climate_signal"].iloc[0])
        
        return float(np.mean(signals)) if signals else 0.75


    # ──────────────────────────────────────────────────────────────
    # Run All
    # ──────────────────────────────────────────────────────────────

    def run_all(self):
        print(BANNER)
        print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.collect_all_signals()

        wc_df      = self.run_wc2026()
        market_df  = self.run_market_calibration()
        climate_df = self.run_climate_risk()
        cultural_df= self.run_cultural_moment()

        print("\n" + "=" * 62)
        print("◈ CONFLUX PIPELINE COMPLETE")
        print("=" * 62)
        print(f"\n  Outputs saved to: {PROCESSED_DIR.resolve()}")
        print(f"  WC2026 teams ranked:    {len(wc_df)}")
        print(f"  Market events tracked:  {len(market_df)}")
        print(f"  Climate regions:        {len(climate_df)}")
        print(f"  Cultural topics:        {len(cultural_df)}")
        print(f"\n  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return {
            "wc2026":          wc_df,
            "market_calib":    market_df,
            "climate_risk":    climate_df,
            "cultural_moment": cultural_df,
        }


def Optional(x): return x  # Python typing stub for clarity in _get_row


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="◈ CONFLUX Pipeline")
    parser.add_argument("--all",      action="store_true")
    parser.add_argument("--vertical", choices=["wc2026","market_calib","climate_risk","cultural_moment"])
    args = parser.parse_args()

    pipeline = ConfluxPipeline()

    if args.all or not args.vertical:
        pipeline.run_all()
    else:
        pipeline.collect_all_signals()
        if args.vertical == "wc2026":
            pipeline.run_wc2026()
        elif args.vertical == "market_calib":
            pipeline.run_market_calibration()
        elif args.vertical == "climate_risk":
            pipeline.run_climate_risk()
        elif args.vertical == "cultural_moment":
            pipeline.run_cultural_moment()