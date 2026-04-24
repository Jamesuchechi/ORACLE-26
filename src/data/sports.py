"""
◈ CONFLUX — Sports Signal
==========================
Collects and engineers sports features for WC2026 vertical.
Produces normalized [0,1] sports signal scores for all 48 teams.
"""

import numpy as np
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from scipy.stats import poisson
from scipy.optimize import minimize

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import (
    ALL_WC_TEAMS, CURATED_ELO, TEAM_TO_GROUP,
    BASE_GOALS_PER_GAME, LOOKBACK_DAYS, STAGE_WEIGHTS, MONTE_CARLO_SIMS
)
from src.features.fusion import SignalVector

RAW_DIR       = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"


class SportsSignalEngine:
    """
    Builds sports signal vectors for all 48 WC2026 teams.
    Core model: Dixon-Coles Bivariate Poisson with MLE-fitted parameters.
    """

    def __init__(self):
        self.results_df:  Optional[pd.DataFrame] = None
        self.elo_df:      Optional[pd.DataFrame] = None
        self.features_df: Optional[pd.DataFrame] = None
        self.attack_:     dict = {}
        self.defense_:    dict = {}
        self.home_adv_:   float = 0.1
        self.rho_:        float = -0.13
        self.is_fitted:   bool = False

    # ──────────────────────────────────────────────
    # Data Collection
    # ──────────────────────────────────────────────

    def load_results(self) -> pd.DataFrame:
        cache = RAW_DIR / "international_results.csv"
        if cache.exists() and (time.time() - cache.stat().st_mtime) < 48 * 3600:
            self.results_df = pd.read_csv(cache, parse_dates=["date"])
            print(f"  [sports] Loaded {len(self.results_df):,} results from cache")
            return self.results_df

        print("  [sports] Fetching international results...")
        try:
            df = pd.read_csv(RESULTS_URL, parse_dates=["date"])
            df = df[df["date"] >= "1990-01-01"].copy()
            df.to_csv(cache, index=False)
            print(f"  [sports] Fetched {len(df):,} results")
            self.results_df = df
        except Exception as e:
            print(f"  [sports] Fetch failed ({e}), generating synthetic features")
            self.results_df = None
        return self.results_df

    def load_elo(self) -> pd.DataFrame:
        cache = RAW_DIR / "elo_ratings.csv"
        if cache.exists() and (time.time() - cache.stat().st_mtime) < 48 * 3600:
            self.elo_df = pd.read_csv(cache)
            return self.elo_df

        print("  [sports] Fetching Elo ratings...")
        try:
            resp = requests.get("https://eloratings.net/World.tsv", timeout=10)
            lines = resp.text.strip().split("\n")
            rows = [{"team": p[1].strip(), "elo": float(p[2].strip())}
                    for p in (l.split("\t") for l in lines[1:]) if len(p) >= 3]
            self.elo_df = pd.DataFrame(rows)
            self.elo_df.to_csv(cache, index=False)
        except:
            self.elo_df = pd.DataFrame(
                [{"team": t, "elo": e} for t, e in CURATED_ELO.items()]
            )
        return self.elo_df

    # ──────────────────────────────────────────────
    # Dixon-Coles Model Fitting
    # ──────────────────────────────────────────────

    def fit_poisson(self, teams: list) -> "SportsSignalEngine":
        if self.results_df is None:
            print("  [sports] No results data — using Elo-proxy mode")
            return self

        team_idx = {t: i for i, t in enumerate(teams)}
        n = len(teams)

        mask = (
            self.results_df["home_team"].isin(teams) &
            self.results_df["away_team"].isin(teams) &
            (self.results_df["date"] >= "2014-01-01")
        )
        df = self.results_df[mask].copy()

        if len(df) < 20:
            print(f"  [sports] Only {len(df)} usable matches — using Elo-proxy mode")
            return self

        h_idx = df["home_team"].map(team_idx).values
        a_idx = df["away_team"].map(team_idx).values
        hg    = df["home_score"].values.astype(float)
        ag    = df["away_score"].values.astype(float)

        def nll(params):
            ha  = params[0]
            atk = params[1: n + 1]
            dfc = params[n + 1:]
            mu1 = np.exp(atk[h_idx] - dfc[a_idx] + ha)
            mu2 = np.exp(atk[a_idx] - dfc[h_idx])
            ll  = np.sum(hg * np.log(mu1 + 1e-9) - mu1 + ag * np.log(mu2 + 1e-9) - mu2)
            return -ll

        avg = np.log(max(df["home_score"].mean(), 0.5))
        x0  = [0.1] + [avg] * n + [avg] * n

        res = minimize(nll, x0, method="L-BFGS-B", options={"maxiter": 300})
        if res.success:
            params = res.x
            for t in teams:
                i = team_idx[t]
                self.attack_[t]  = float(params[1 + i])
                self.defense_[t] = float(params[n + 1 + i])
            self.home_adv_  = float(params[0])
            self.is_fitted  = True
            print(f"  [sports] Poisson model fitted on {len(df)} matches")

        return self

    # ──────────────────────────────────────────────
    # Match Prediction
    # ──────────────────────────────────────────────

    def _tau(self, g1, g2, mu1, mu2):
        if g1 == 0 and g2 == 0: return 1 - mu1 * mu2 * self.rho_
        if g1 == 1 and g2 == 0: return 1 + mu2 * self.rho_
        if g1 == 0 and g2 == 1: return 1 + mu1 * self.rho_
        if g1 == 1 and g2 == 1: return 1 - self.rho_
        return 1.0

    def predict_match(
        self, team1: str, team2: str, neutral: bool = True, knockout: bool = False
    ) -> dict:
        """Dixon-Coles Poisson match prediction."""
        if self.is_fitted and team1 in self.attack_:
            ha   = 0.0 if neutral else self.home_adv_
            xg1  = np.exp(self.attack_[team1] - self.defense_[team2] + ha)
            xg2  = np.exp(self.attack_[team2] - self.defense_[team1])
        else:
            # Elo-proxy fallback
            e1 = CURATED_ELO.get(team1, 1700)
            e2 = CURATED_ELO.get(team2, 1700)
            scale = 1 + (e1 - e2) / 2200
            xg1 = BASE_GOALS_PER_GAME * scale
            xg2 = BASE_GOALS_PER_GAME / scale

        xg1 = float(np.clip(xg1, 0.25, 4.5))
        xg2 = float(np.clip(xg2, 0.25, 4.5))

        rng   = np.random.default_rng(42)
        g1    = rng.poisson(xg1, MONTE_CARLO_SIMS)
        g2    = rng.poisson(xg2, MONTE_CARLO_SIMS)
        tau_w = np.array([self._tau(a, b, xg1, xg2) for a, b in zip(g1, g2)], dtype=float)
        tau_w = np.clip(tau_w, 0, None)
        tau_w /= tau_w.sum()

        idx = rng.choice(MONTE_CARLO_SIMS, size=MONTE_CARLO_SIMS, replace=True, p=tau_w)
        g1w, g2w = g1[idx], g2[idx]

        win  = float(np.mean(g1w > g2w))
        draw = float(np.mean(g1w == g2w))
        loss = float(np.mean(g1w < g2w))

        if knockout:
            win += draw * 0.5; loss += draw * 0.5; draw = 0.0

        from collections import Counter
        top = sorted(Counter(zip(g1w.tolist(), g2w.tolist())).items(), key=lambda x: -x[1])[:5]

        return {
            "xg1": round(xg1, 2), "xg2": round(xg2, 2),
            "win_prob": round(win, 3), "draw_prob": round(draw, 3), "loss_prob": round(loss, 3),
            "most_likely_score": f"{top[0][0][0]}-{top[0][0][1]}" if top else "1-1",
        }

    # ──────────────────────────────────────────────
    # Team Features → Signal Vector
    # ──────────────────────────────────────────────

    def _get_elo(self, team: str) -> float:
        if self.elo_df is not None:
            row = self.elo_df[self.elo_df["team"] == team]
            if not row.empty:
                return float(row.iloc[0]["elo"])
        return float(CURATED_ELO.get(team, 1700))

    def _form_score(self, team: str, n: int = 5) -> float:
        if self.results_df is None:
            return 0.45
        cutoff = datetime.now() - timedelta(days=365)
        mask = (
            ((self.results_df["home_team"] == team) | (self.results_df["away_team"] == team)) &
            (self.results_df["date"] >= cutoff)
        )
        matches = self.results_df[mask].tail(n)
        if matches.empty:
            return 0.45
        pts = 0
        for _, row in matches.iterrows():
            gf = row["home_score"] if row["home_team"] == team else row["away_score"]
            ga = row["away_score"] if row["home_team"] == team else row["home_score"]
            pts += 3 if gf > ga else (1 if gf == ga else 0)
        return round(pts / (n * 3), 4)

    def team_to_signal_vector(self, team: str, vertical: str = "wc2026") -> SignalVector:
        """Convert a team's features into a normalized SignalVector."""
        elo = self._get_elo(team)
        elo_min, elo_max = 1500.0, 2100.0
        elo_norm = (elo - elo_min) / (elo_max - elo_min)
        form = self._form_score(team)
        sports_score = elo_norm * 0.7 + form * 0.3

        return SignalVector(
            subject=team,
            vertical=vertical,
            sports=float(np.clip(sports_score, 0, 1)),
            metadata={"elo": elo, "form_5": form},
        )

    # ──────────────────────────────────────────────
    # Build All Team Features
    # ──────────────────────────────────────────────

    def build_all_features(self) -> pd.DataFrame:
        self.load_results()
        self.load_elo()
        self.fit_poisson(ALL_WC_TEAMS)

        rows = []
        elos = [self._get_elo(t) for t in ALL_WC_TEAMS]
        elo_min, elo_max = min(elos), max(elos)

        for team in ALL_WC_TEAMS:
            elo  = self._get_elo(team)
            form = self._form_score(team)
            elo_norm = (elo - elo_min) / (elo_max - elo_min)
            sports_signal = elo_norm * 0.7 + form * 0.3
            rows.append({
                "team":           team,
                "group":          TEAM_TO_GROUP.get(team, "?"),
                "elo":            round(elo, 1),
                "form_5":         round(form, 4),
                "sports_signal":  round(float(np.clip(sports_signal, 0, 1)), 4),
            })

        df = pd.DataFrame(rows).sort_values("sports_signal", ascending=False).reset_index(drop=True)
        df["sports_rank"] = df.index + 1
        out = PROCESSED_DIR / "sports_features.csv"
        df.to_csv(out, index=False)
        print(f"  [sports] Saved features for {len(df)} teams → {out}")
        self.features_df = df
        return df


if __name__ == "__main__":
    engine = SportsSignalEngine()
    df = engine.build_all_features()
    print("\nTop 10 by sports signal:")
    print(df[["team", "group", "elo", "form_5", "sports_signal"]].head(10).to_string(index=False))

    print("\nTest: Brazil vs Germany")
    pred = engine.predict_match("Brazil", "Germany")
    print(f"  xG {pred['xg1']}-{pred['xg2']} | Win {pred['win_prob']:.1%} Draw {pred['draw_prob']:.1%} Loss {pred['loss_prob']:.1%}")