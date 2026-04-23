"""
ORACLE-26 — Sports Feature Engineering
=========================================
Transforms raw sports data into ML-ready features for all 48 WC2026 teams.

Features produced per team:
  - elo                  : Current Elo rating
  - elo_change_1yr       : Elo trend over past 12 months
  - win_rate_3yr         : Win rate across all competitions (last 3 years)
  - win_rate_wc_qual     : Win rate in WC qualifiers specifically
  - goals_scored_avg     : Average goals scored per game (last 3 years)
  - goals_conceded_avg   : Average goals conceded per game
  - clean_sheet_rate     : Proportion of games with 0 goals conceded
  - form_5_games         : Form score from last 5 games (0.0–1.0)
  - form_10_games        : Form score from last 10 games (0.0–1.0)
  - weighted_form        : Recency-weighted form (recent games count more)
  - xg_proxy_scored      : Estimated xG scored (goals * competition weight)
  - xg_proxy_conceded    : Estimated xG conceded
  - h2h_win_rate         : Head-to-head win rate vs specific opponent (match-time feature)
  - wc_experience_score  : Composite WC historical performance
  - avg_wc_round         : Average round reached across WC tournaments
  - squad_strength_proxy : Composite team strength (0–100)
  - strength_score       : Final normalized team strength (0–100)
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import (
    ALL_TEAMS, WC2026_GROUPS, TEAM_TO_GROUP, TEAM_TO_RESULTS_NAME,
    CURATED_ELO, LOOKBACK_DAYS, STAGE_WEIGHTS
)

RAW_DIR       = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# WC round → numeric score (for avg_wc_round)
WC_ROUND_SCORES = {
    "Group Stage":    1,
    "Round of 16":    2,
    "Quarter-finals": 3,
    "Semi-finals":    4,
    "Third place":    4,
    "Final":          5,
    "Champion":       6,
}

# Historical WC performance (1990–2022) — used when live data unavailable
HISTORICAL_WC_PERF = {
    "Argentina":   {"appearances": 9,  "avg_round": 3.8, "titles": 3},
    "France":      {"appearances": 8,  "avg_round": 3.5, "titles": 2},
    "Brazil":      {"appearances": 9,  "avg_round": 3.9, "titles": 5},
    "Germany":     {"appearances": 9,  "avg_round": 4.1, "titles": 4},
    "Italy":       {"appearances": 9,  "avg_round": 3.6, "titles": 4},
    "Spain":       {"appearances": 9,  "avg_round": 3.2, "titles": 1},
    "England":     {"appearances": 8,  "avg_round": 2.8, "titles": 1},
    "Netherlands": {"appearances": 8,  "avg_round": 3.3, "titles": 0},
    "Portugal":    {"appearances": 8,  "avg_round": 3.0, "titles": 0},
    "Croatia":     {"appearances": 6,  "avg_round": 3.2, "titles": 0},
    "Uruguay":     {"appearances": 9,  "avg_round": 2.9, "titles": 2},
    "Belgium":     {"appearances": 8,  "avg_round": 2.7, "titles": 0},
    "Mexico":      {"appearances": 9,  "avg_round": 2.2, "titles": 0},
    "USA":         {"appearances": 8,  "avg_round": 2.1, "titles": 0},
    "Colombia":    {"appearances": 6,  "avg_round": 2.3, "titles": 0},
    "Morocco":     {"appearances": 6,  "avg_round": 2.2, "titles": 0},
    "Japan":       {"appearances": 7,  "avg_round": 2.1, "titles": 0},
    "Senegal":     {"appearances": 3,  "avg_round": 2.3, "titles": 0},
    "South Korea": {"appearances": 9,  "avg_round": 2.0, "titles": 0},
    "Switzerland": {"appearances": 7,  "avg_round": 2.0, "titles": 0},
    "Australia":   {"appearances": 5,  "avg_round": 1.8, "titles": 0},
    "Nigeria":     {"appearances": 6,  "avg_round": 2.0, "titles": 0},
    "Ecuador":     {"appearances": 4,  "avg_round": 1.5, "titles": 0},
    "Cameroon":    {"appearances": 7,  "avg_round": 1.6, "titles": 0},
    "Iran":        {"appearances": 5,  "avg_round": 1.2, "titles": 0},
    "Norway":      {"appearances": 4,  "avg_round": 2.0, "titles": 0},
    "Serbia":      {"appearances": 4,  "avg_round": 1.5, "titles": 0},
    "Scotland":    {"appearances": 8,  "avg_round": 1.0, "titles": 0},
    "Austria":     {"appearances": 2,  "avg_round": 1.5, "titles": 0},
    "Canada":      {"appearances": 1,  "avg_round": 1.0, "titles": 0},
    "Chile":       {"appearances": 9,  "avg_round": 2.1, "titles": 0},
    "Turkey":      {"appearances": 2,  "avg_round": 2.5, "titles": 0},
    "Algeria":     {"appearances": 4,  "avg_round": 1.5, "titles": 0},
    "Tunisia":     {"appearances": 5,  "avg_round": 1.2, "titles": 0},
    "Egypt":       {"appearances": 3,  "avg_round": 1.0, "titles": 0},
    "DR Congo":    {"appearances": 2,  "avg_round": 1.0, "titles": 0},
    "Saudi Arabia":{"appearances": 6,  "avg_round": 1.2, "titles": 0},
    "Paraguay":    {"appearances": 8,  "avg_round": 2.0, "titles": 0},
    "South Africa":{"appearances": 3,  "avg_round": 1.3, "titles": 0},
    "Jordan":      {"appearances": 0,  "avg_round": 0.0, "titles": 0},
    "Iraq":        {"appearances": 1,  "avg_round": 1.0, "titles": 0},
    "Qatar":       {"appearances": 1,  "avg_round": 1.0, "titles": 0},
    "Bosnia":      {"appearances": 1,  "avg_round": 1.0, "titles": 0},
    "Uzbekistan":  {"appearances": 0,  "avg_round": 0.0, "titles": 0},
    "Suriname":    {"appearances": 0,  "avg_round": 0.0, "titles": 0},
    "Haiti":       {"appearances": 1,  "avg_round": 1.0, "titles": 0},
    "Curacao":     {"appearances": 0,  "avg_round": 0.0, "titles": 0},
    "New Caledonia":{"appearances":0,  "avg_round": 0.0, "titles": 0},
}


class SportsFeatureEngineer:
    """
    Builds the sports signal feature matrix for all 48 WC2026 teams.
    """

    def __init__(self):
        self.results_df:  Optional[pd.DataFrame] = None
        self.elo_df:      Optional[pd.DataFrame] = None
        self.features_df: Optional[pd.DataFrame] = None

    # ─────────────────────────────────────────
    # Data Loading
    # ─────────────────────────────────────────

    def load_data(self):
        """Load cached raw data from data/raw/."""
        results_path = RAW_DIR / "international_results.csv"
        elo_path     = RAW_DIR / "elo_ratings.csv"

        if results_path.exists():
            self.results_df = pd.read_csv(results_path, parse_dates=["date"])
            print(f"  [features] Loaded {len(self.results_df):,} results")
        else:
            print("  [features] No cached results — using synthetic features (run sports.py first)")

        if elo_path.exists():
            self.elo_df = pd.read_csv(elo_path)
            print(f"  [features] Loaded Elo for {len(self.elo_df)} teams")
        else:
            print("  [features] No cached Elo — using curated values")
            self.elo_df = pd.DataFrame(
                [{"team": t, "elo": e} for t, e in CURATED_ELO.items()]
            )

    # ─────────────────────────────────────────
    # Individual Feature Computations
    # ─────────────────────────────────────────

    def _get_elo(self, team: str) -> float:
        """Get Elo rating for a team."""
        if self.elo_df is not None:
            row = self.elo_df[self.elo_df["team"] == team]
            if not row.empty:
                return float(row.iloc[0]["elo"])
        return float(CURATED_ELO.get(team, 1700))

    def _get_team_matches(
        self,
        team: str,
        days: int = LOOKBACK_DAYS,
        tournaments: Optional[list] = None,
    ) -> pd.DataFrame:
        """Get all matches involving a team within the lookback window."""
        if self.results_df is None:
            return pd.DataFrame()

        name = TEAM_TO_RESULTS_NAME.get(team, team)
        cutoff = datetime.now() - timedelta(days=days)
        mask = (
            ((self.results_df["home_team"] == name) |
             (self.results_df["away_team"] == name)) &
            (self.results_df["date"] >= cutoff)
        )
        df = self.results_df[mask].copy()

        if tournaments:
            df = df[df["tournament"].isin(tournaments)]

        return df

    def _compute_match_outcomes(
        self, team: str, matches: pd.DataFrame
    ) -> dict:
        """Compute win/draw/loss and goals from a matches DataFrame."""
        name = TEAM_TO_RESULTS_NAME.get(team, team)
        wins = draws = losses = clean_sheets = 0
        goals_for, goals_against = [], []
        comp_weighted_gf = 0.0
        comp_weighted_ga = 0.0
        total_weight = 0.0

        for _, row in matches.iterrows():
            is_home = row["home_team"] == name
            gf = row["home_score"] if is_home else row["away_score"]
            ga = row["away_score"] if is_home else row["home_score"]
            goals_for.append(gf)
            goals_against.append(ga)

            w = STAGE_WEIGHTS.get(row.get("tournament", ""), 0.3)
            comp_weighted_gf += gf * w
            comp_weighted_ga += ga * w
            total_weight += w

            if gf > ga:
                wins += 1
            elif gf == ga:
                draws += 1
            else:
                losses += 1
            if ga == 0:
                clean_sheets += 1

        n = len(matches)
        if n == 0:
            return {"wins": 0, "draws": 0, "losses": 0, "n": 0,
                    "goals_for": [], "goals_against": [],
                    "clean_sheets": 0, "total_weight": 0,
                    "xg_proxy_scored": 1.2, "xg_proxy_conceded": 1.5}

        xg_scored   = comp_weighted_gf / total_weight if total_weight > 0 else np.mean(goals_for)
        xg_conceded = comp_weighted_ga / total_weight if total_weight > 0 else np.mean(goals_against)

        return {
            "wins": wins, "draws": draws, "losses": losses, "n": n,
            "goals_for": goals_for, "goals_against": goals_against,
            "clean_sheets": clean_sheets, "total_weight": total_weight,
            "xg_proxy_scored": round(xg_scored, 3),
            "xg_proxy_conceded": round(xg_conceded, 3),
        }

    def _form_score(self, team: str, last_n: int = 5) -> float:
        """
        Compute form score from last N games.
        3 points for win, 1 for draw, 0 for loss — normalized to 0.0–1.0.
        """
        matches = self._get_team_matches(team, days=365)
        if matches.empty or len(matches) < 1:
            return 0.45

        matches = matches.tail(last_n)
        name = TEAM_TO_RESULTS_NAME.get(team, team)
        pts = 0
        for _, row in matches.iterrows():
            is_home = row["home_team"] == name
            gf = row["home_score"] if is_home else row["away_score"]
            ga = row["away_score"] if is_home else row["home_score"]
            if gf > ga:
                pts += 3
            elif gf == ga:
                pts += 1
        return round(pts / (last_n * 3), 4)

    def _weighted_form(self, team: str, last_n: int = 10) -> float:
        """Recency-weighted form — most recent game counts most."""
        matches = self._get_team_matches(team, days=365 * 2)
        if matches.empty:
            return 0.45

        matches = matches.tail(last_n).reset_index(drop=True)
        name = TEAM_TO_RESULTS_NAME.get(team, team)
        total_pts = 0.0
        total_weight = 0.0

        for i, (_, row) in enumerate(matches.iterrows()):
            weight = (i + 1) / len(matches)   # more recent = higher weight
            is_home = row["home_team"] == name
            gf = row["home_score"] if is_home else row["away_score"]
            ga = row["away_score"] if is_home else row["home_score"]
            pts = 3 if gf > ga else (1 if gf == ga else 0)
            total_pts   += pts * weight
            total_weight += 3 * weight

        return round(total_pts / total_weight, 4) if total_weight > 0 else 0.45

    def _elo_change(self, team: str, months: int = 12) -> float:
        """
        Estimate Elo trend over past N months.
        Positive = improving, negative = declining.
        Uses results data as proxy if Elo history unavailable.
        """
        matches = self._get_team_matches(team, days=months * 30)
        if matches.empty or len(matches) < 5:
            return 0.0

        name = TEAM_TO_RESULTS_NAME.get(team, team)
        # Simple proxy: points in first half vs second half of period
        mid = len(matches) // 2
        first_half  = matches.iloc[:mid]
        second_half = matches.iloc[mid:]

        def points(df):
            p = 0
            for _, row in df.iterrows():
                is_home = row["home_team"] == name
                gf = row["home_score"] if is_home else row["away_score"]
                ga = row["away_score"] if is_home else row["home_score"]
                p += 3 if gf > ga else (1 if gf == ga else 0)
            return p / max(len(df), 1)

        trend = points(second_half) - points(first_half)
        return round(trend, 4)

    def _wc_experience(self, team: str) -> dict:
        """Get historical World Cup performance metrics."""
        perf = HISTORICAL_WC_PERF.get(team, {"appearances": 0, "avg_round": 0.0, "titles": 0})
        score = (
            perf["appearances"] * 0.5 +
            perf["avg_round"]   * 1.0 +
            perf["titles"]      * 3.0
        )
        return {
            "wc_appearances":    perf["appearances"],
            "avg_wc_round":      perf["avg_round"],
            "wc_titles":         perf["titles"],
            "wc_experience_score": round(score, 2),
        }

    # ─────────────────────────────────────────
    # Main Feature Builder
    # ─────────────────────────────────────────

    def build_team_features(self, team: str) -> dict:
        """Build complete sports feature vector for one team."""
        elo   = self._get_elo(team)
        all_m = self._get_team_matches(team, days=LOOKBACK_DAYS)
        wc_qual_m = self._get_team_matches(
            team, days=LOOKBACK_DAYS,
            tournaments=["FIFA World Cup qualification"]
        )

        all_stats    = self._compute_match_outcomes(team, all_m)
        wc_qual_stats = self._compute_match_outcomes(team, wc_qual_m)
        wc_exp       = self._wc_experience(team)

        n = all_stats["n"]
        q = wc_qual_stats["n"]

        # Fallback values if no data
        elo_norm = (elo - 1500) / 600   # roughly -0.33 to 1.0

        if n == 0:
            # Synthesize from Elo
            win_rate     = round(min(0.90, max(0.10, 0.45 + elo_norm * 0.5)), 3)
            goals_scored = round(max(0.5, 1.0  + elo_norm * 1.5), 2)
            goals_conc   = round(max(0.3, 2.0  - elo_norm * 1.2), 2)
            cs_rate      = round(max(0.05, 0.15 + elo_norm * 0.25), 3)
            form5        = round(min(1.0, max(0.0, 0.4 + elo_norm * 0.5)), 4)
            form10       = form5
            w_form       = form5
            xg_scored    = goals_scored
            xg_conceded  = goals_conc
            wr_qual      = win_rate
        else:
            win_rate     = round(all_stats["wins"] / n, 3)
            goals_scored = round(np.mean(all_stats["goals_for"]),     2)
            goals_conc   = round(np.mean(all_stats["goals_against"]), 2)
            cs_rate      = round(all_stats["clean_sheets"] / n,       3)
            form5        = self._form_score(team, last_n=5)
            form10       = self._form_score(team, last_n=10)
            w_form       = self._weighted_form(team, last_n=10)
            xg_scored    = all_stats["xg_proxy_scored"]
            xg_conceded  = all_stats["xg_proxy_conceded"]
            wr_qual      = round(wc_qual_stats["wins"] / q, 3) if q > 0 else win_rate

        return {
            "team":               team,
            "group":              TEAM_TO_GROUP.get(team, "?"),
            "elo":                round(elo, 1),
            "elo_change_1yr":     self._elo_change(team),
            "matches_played":     n,
            "win_rate_3yr":       win_rate,
            "win_rate_wc_qual":   wr_qual,
            "goals_scored_avg":   goals_scored,
            "goals_conceded_avg": goals_conc,
            "clean_sheet_rate":   cs_rate,
            "form_5_games":       form5,
            "form_10_games":      form10,
            "weighted_form":      w_form,
            "xg_proxy_scored":    xg_scored,
            "xg_proxy_conceded":  xg_conceded,
            **wc_exp,
        }

    def build_all_features(self) -> pd.DataFrame:
        """Build features for all 48 WC2026 teams and save."""
        if self.results_df is None:
            self.load_data()

        print("\n  [features] Building features for all 48 teams...")
        rows = []
        for team in ALL_TEAMS:
            feat = self.build_team_features(team)
            rows.append(feat)
            print(f"  ✓ {team}")

        df = pd.DataFrame(rows)

        # Composite strength score (0–100)
        elo_min, elo_max = df["elo"].min(), df["elo"].max()
        df["strength_score"] = (
            (df["elo"] - elo_min) / (elo_max - elo_min) * 45 +
            df["win_rate_3yr"]              * 15 +
            df["weighted_form"]             * 15 +
            df["xg_proxy_scored"].clip(0,4) / 4 * 10 +
            (1 - df["xg_proxy_conceded"].clip(0,4) / 4) * 10 +
            df["wc_experience_score"].clip(0,20) / 20 * 5
        ).round(2)

        df = df.sort_values("strength_score", ascending=False).reset_index(drop=True)
        df["sports_rank"] = df.index + 1

        # Save
        out_path = PROCESSED_DIR / "sports_features.csv"
        df.to_csv(out_path, index=False)
        print(f"\n  [features] Saved {len(df)} teams → {out_path}")
        self.features_df = df
        return df

    def get_match_features(
        self, team1: str, team2: str,
        h2h_df: Optional[pd.DataFrame] = None,
    ) -> dict:
        """
        Build per-match feature vector for a specific matchup.
        Used at prediction time.
        """
        if self.features_df is None:
            self.build_all_features()

        r1 = self.features_df[self.features_df["team"] == team1]
        r2 = self.features_df[self.features_df["team"] == team2]

        if r1.empty or r2.empty:
            raise ValueError(f"Unknown team(s): {team1}, {team2}")

        r1, r2 = r1.iloc[0], r2.iloc[0]

        h2h_win = 0.5
        if h2h_df is not None:
            row = h2h_df[
                ((h2h_df["team1"] == team1) & (h2h_df["team2"] == team2))
            ]
            if not row.empty:
                h2h_win = float(row.iloc[0]["h2h_win_rate_team1"])
            else:
                row = h2h_df[
                    ((h2h_df["team1"] == team2) & (h2h_df["team2"] == team1))
                ]
                if not row.empty:
                    h2h_win = 1 - float(row.iloc[0]["h2h_win_rate_team1"])

        return {
            "elo_diff":            round(r1["elo"] - r2["elo"], 1),
            "elo_ratio":           round(r1["elo"] / max(r2["elo"], 1), 4),
            "win_rate_diff":       round(r1["win_rate_3yr"] - r2["win_rate_3yr"], 4),
            "form_diff":           round(r1["weighted_form"] - r2["weighted_form"], 4),
            "goals_diff":          round(r1["goals_scored_avg"] - r2["goals_scored_avg"], 3),
            "defense_diff":        round(r2["goals_conceded_avg"] - r1["goals_conceded_avg"], 3),
            "xg_diff":             round(r1["xg_proxy_scored"] - r2["xg_proxy_scored"], 3),
            "wc_exp_diff":         round(r1["wc_experience_score"] - r2["wc_experience_score"], 2),
            "elo_change_diff":     round(r1["elo_change_1yr"] - r2["elo_change_1yr"], 4),
            "h2h_win_rate_team1":  round(h2h_win, 3),
            "strength_diff":       round(r1["strength_score"] - r2["strength_score"], 2),
        }


# ─────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    engineer = SportsFeatureEngineer()
    engineer.load_data()
    df = engineer.build_all_features()
    print("\nTop 10 teams by strength score:")
    print(df[["team", "group", "elo", "strength_score", "form_5_games"]].head(10).to_string(index=False))