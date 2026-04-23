"""
ORACLE-26 — Dixon-Coles Poisson Model
========================================
Predicts match outcomes using a Bivariate Poisson distribution
with the Dixon-Coles low-scoring correction.

How it works:
  1. Estimate attack (λ_atk) and defense (λ_def) parameters per team
  2. Expected goals: μ1 = atk1 * def2 * home_adv * elo_adj
                     μ2 = atk2 * def1 * elo_adj_inv
  3. Simulate 50,000 Poisson draws → win/draw/loss probabilities
  4. Apply Dixon-Coles ρ correction for 0-0, 1-0, 0-1, 1-1 scorelines

Reference:
  Dixon, M. & Coles, S. (1997). Modelling Association Football Scores
  and Inefficiencies in the Football Betting Market.
"""

import numpy as np
import pandas as pd
from scipy.stats import poisson
from scipy.optimize import minimize
from typing import Optional
from pathlib import Path
import joblib

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import BASE_GOALS_PER_GAME, ALL_TEAMS, TEAM_TO_RESULTS_NAME

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
# Dixon-Coles correction factor τ
# ─────────────────────────────────────────────

def dc_tau(goals1: int, goals2: int, mu1: float, mu2: float, rho: float) -> float:
    """
    Dixon-Coles correction for low-scoring cells.
    Adjusts probability of 0-0, 1-0, 0-1, 1-1 scorelines.
    """
    if goals1 == 0 and goals2 == 0:
        return 1 - mu1 * mu2 * rho
    elif goals1 == 1 and goals2 == 0:
        return 1 + mu2 * rho
    elif goals1 == 0 and goals2 == 1:
        return 1 + mu1 * rho
    elif goals1 == 1 and goals2 == 1:
        return 1 - rho
    else:
        return 1.0


def dc_probability(goals1: int, goals2: int, mu1: float, mu2: float, rho: float) -> float:
    """Probability of a specific scoreline (goals1-goals2) under Dixon-Coles."""
    p = poisson.pmf(goals1, mu1) * poisson.pmf(goals2, mu2) * dc_tau(goals1, goals2, mu1, mu2, rho)
    return max(0.0, p)


# ─────────────────────────────────────────────
# Core Prediction Class
# ─────────────────────────────────────────────

class PoissonModel:
    """
    Bivariate Poisson match prediction model for ORACLE-26.

    Can operate in two modes:
      - Fitted mode: MLE-fitted attack/defense parameters from historical data
      - Feature mode: Uses precomputed team features (xG proxy, Elo) directly
    """

    def __init__(self, rho: float = -0.13):
        """
        Args:
            rho: Dixon-Coles correction parameter (typically small negative).
                 -0.13 is a commonly fitted value for international football.
        """
        self.rho         = rho
        self.attack_: dict  = {}    # team → attack parameter
        self.defense_: dict = {}    # team → defense parameter
        self.is_fitted   = False
        self.N_SIM       = 50_000

    # ─────────────────────────────────────────
    # Parameter Fitting (MLE)
    # ─────────────────────────────────────────

    def fit(self, results_df: pd.DataFrame, teams: list[str]) -> "PoissonModel":
        """
        Fit attack/defense parameters using MLE on historical results.

        Args:
            results_df: DataFrame with home_team, away_team, home_score, away_score
            teams: List of team names to include
        """
        print("  [poisson] Fitting attack/defense parameters...")

        team_to_idx = {t: i for i, t in enumerate(teams)}
        n_teams     = len(teams)

        # Normalize team names in results
        results_df = results_df.copy()
        inv_map = {v: k for k, v in TEAM_TO_RESULTS_NAME.items()}
        results_df["home_team"] = results_df["home_team"].map(lambda x: inv_map.get(x, x))
        results_df["away_team"] = results_df["away_team"].map(lambda x: inv_map.get(x, x))

        # Filter to teams in our set and recent era (post-2014)
        mask = (
            results_df["home_team"].isin(teams) &
            results_df["away_team"].isin(teams) &
            (results_df["date"] >= "2014-01-01")
        )
        df = results_df[mask].copy()

        if len(df) < 10:
            print(f"  [poisson] Insufficient data ({len(df)} matches) — using feature-based mode")
            return self

        # Prepare matrices for vectorized calculation
        h_indices = df["home_team"].map(team_to_idx).values
        a_indices = df["away_team"].map(team_to_idx).values
        h_goals = df["home_score"].values.astype(float)
        a_goals = df["away_score"].values.astype(float)

        def neg_log_likelihood(params):
            """Vectorized negative log-likelihood."""
            home_adv   = params[0]
            atk_params = params[1: n_teams + 1]
            def_params = params[n_teams + 1:]

            # Log-linear expectations
            mu1 = np.exp(atk_params[h_indices] - def_params[a_indices] + home_adv)
            mu2 = np.exp(atk_params[a_indices] - def_params[h_indices])

            # Poisson log-likelihood: y*log(mu) - mu
            ll = np.sum(h_goals * np.log(mu1) - mu1 + a_goals * np.log(mu2) - mu2)
            
            # Simplified Tau adjustment (only for low scores)
            # In vectorized mode, we skip the DC tau if it's too slow, 
            # or apply it selectively.
            return -ll

        # Smart Initialization: use log of average goals
        avg_goals = results_df["home_score"].mean()
        x0 = [0.1] + [np.log(avg_goals)] * n_teams + [np.log(avg_goals)] * n_teams

        result = minimize(
            neg_log_likelihood,
            x0,
            method="L-BFGS-B",
            options={"maxiter": 200, "ftol": 1e-6}
        )

        if result.success:
            params     = result.x
            atk_params = params[1: n_teams + 1]
            def_params = params[n_teams + 1:]
            self.home_advantage_ = params[0]

            for team in teams:
                i = team_to_idx[team]
                self.attack_[team]  = float(atk_params[i])
                self.defense_[team] = float(def_params[i])

            self.is_fitted = True
            print(f"  [poisson] Fitted on {len(df)} matches — home_adv={params[0]:.3f}")
        else:
            print(f"  [poisson] Optimization did not converge: {result.message}")

        return self

    # ─────────────────────────────────────────
    # Expected Goals Calculation
    # ─────────────────────────────────────────

    def _xg_from_features(
        self,
        team1: str, team2: str,
        features_df: pd.DataFrame,
        neutral: bool = True,
    ) -> tuple[float, float]:
        """
        Compute expected goals from team feature vectors.
        Used when model isn't fitted or team not in training data.
        """
        r1 = features_df[features_df["team"] == team1]
        r2 = features_df[features_df["team"] == team2]

        if r1.empty or r2.empty:
            return BASE_GOALS_PER_GAME, BASE_GOALS_PER_GAME

        r1, r2 = r1.iloc[0], r2.iloc[0]

        # Attack strength relative to average
        atk1 = r1["xg_proxy_scored"]   / BASE_GOALS_PER_GAME
        def1 = r1["xg_proxy_conceded"] / BASE_GOALS_PER_GAME
        atk2 = r2["xg_proxy_scored"]   / BASE_GOALS_PER_GAME
        def2 = r2["xg_proxy_conceded"] / BASE_GOALS_PER_GAME

        # Elo-based scaling factor
        elo_diff  = r1["elo"] - r2["elo"]
        elo_scale = 1 + (elo_diff / 2200)

        home_adv = 1.0 if neutral else 1.12

        xg1 = BASE_GOALS_PER_GAME * atk1 * def2 * elo_scale  * home_adv
        xg2 = BASE_GOALS_PER_GAME * atk2 * def1 / elo_scale

        return (
            float(np.clip(xg1, 0.25, 4.5)),
            float(np.clip(xg2, 0.25, 4.5)),
        )

    def _xg_from_fitted(
        self,
        team1: str, team2: str,
        neutral: bool = True,
    ) -> tuple[float, float]:
        """Compute expected goals from MLE-fitted parameters."""
        if team1 not in self.attack_ or team2 not in self.attack_:
            return BASE_GOALS_PER_GAME, BASE_GOALS_PER_GAME

        home_adv = self.home_advantage_ if not neutral else 0.0

        xg1 = np.exp(self.attack_[team1] - self.defense_[team2] + home_adv)
        xg2 = np.exp(self.attack_[team2] - self.defense_[team1])

        return (
            float(np.clip(xg1, 0.25, 4.5)),
            float(np.clip(xg2, 0.25, 4.5)),
        )

    # ─────────────────────────────────────────
    # Monte Carlo Match Simulation
    # ─────────────────────────────────────────

    def predict_match(
        self,
        team1: str,
        team2: str,
        features_df: Optional[pd.DataFrame] = None,
        neutral: bool = True,
        knockout: bool = False,
    ) -> dict:
        """
        Predict match outcome probabilities.

        Args:
            team1: Name of first team
            team2: Name of second team
            features_df: Sports feature DataFrame (used if model not fitted)
            neutral: True if played at neutral venue
            knockout: True if knockout round (no draws — goes to pens)

        Returns:
            dict with keys:
              team1, team2, xg1, xg2,
              win_prob, draw_prob, loss_prob,
              most_likely_score, score_probs (top 10 scorelines)
        """
        # Get expected goals
        if self.is_fitted and team1 in self.attack_ and team2 in self.attack_:
            xg1, xg2 = self._xg_from_fitted(team1, team2, neutral)
        elif features_df is not None:
            xg1, xg2 = self._xg_from_features(team1, team2, features_df, neutral)
        else:
            xg1 = xg2 = BASE_GOALS_PER_GAME

        # Monte Carlo simulation
        rng = np.random.default_rng(seed=42)
        g1  = rng.poisson(xg1, self.N_SIM)
        g2  = rng.poisson(xg2, self.N_SIM)

        # Apply Dixon-Coles correction via resampling weights
        weights = np.array([
            dc_tau(int(a), int(b), xg1, xg2, self.rho)
            for a, b in zip(g1, g2)
        ], dtype=float)
        weights = np.clip(weights, 0, None)
        weights /= weights.sum()

        # Weighted outcome probabilities
        indices  = rng.choice(self.N_SIM, size=self.N_SIM, replace=True, p=weights)
        g1_w = g1[indices]
        g2_w = g2[indices]

        win_prob  = float(np.mean(g1_w > g2_w))
        draw_prob = float(np.mean(g1_w == g2_w))
        loss_prob = float(np.mean(g1_w < g2_w))

        # In knockout, draws lead to extra time / pens
        if knockout:
            pen_home = 0.5  # assume roughly 50/50 in pens
            win_prob  = win_prob  + draw_prob * pen_home
            loss_prob = loss_prob + draw_prob * (1 - pen_home)
            draw_prob = 0.0

        # Top scorelines
        from collections import Counter
        score_counter = Counter(zip(g1_w.tolist(), g2_w.tolist()))
        top_scores = sorted(score_counter.items(), key=lambda x: -x[1])[:10]
        score_probs = [
            {"score": f"{s[0]}-{s[1]}", "prob": round(c / self.N_SIM, 4)}
            for s, c in top_scores
        ]
        most_likely = score_probs[0]["score"] if score_probs else "1-1"

        return {
            "team1":             team1,
            "team2":             team2,
            "xg1":               round(xg1, 2),
            "xg2":               round(xg2, 2),
            "win_prob":          round(win_prob,  3),
            "draw_prob":         round(draw_prob, 3),
            "loss_prob":         round(loss_prob, 3),
            "most_likely_score": most_likely,
            "score_probs":       score_probs,
            "neutral":           neutral,
            "knockout":          knockout,
        }

    # ─────────────────────────────────────────
    # Persistence
    # ─────────────────────────────────────────

    def save(self, path: str = "models/poisson_model.pkl"):
        joblib.dump(self, path)
        print(f"  [poisson] Model saved → {path}")

    @classmethod
    def load(cls, path: str = "models/poisson_model.pkl") -> "PoissonModel":
        model = joblib.load(path)
        print(f"  [poisson] Model loaded from {path}")
        return model


# ─────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from src.features.sports_features import SportsFeatureEngineer

    print("Loading features...")
    eng = SportsFeatureEngineer()
    eng.load_data()
    features_df = eng.build_all_features()

    model = PoissonModel(rho=-0.13)

    # Try to fit if results available
    results_path = Path("data/raw/international_results.csv")
    if results_path.exists():
        results_df = pd.read_csv(results_path, parse_dates=["date"])
        model.fit(results_df, ALL_TEAMS)

    # Test predictions
    print("\nTest predictions:")
    tests = [
        ("Argentina", "France",  True,  False),
        ("Brazil",    "Germany", True,  False),
        ("England",   "Spain",   True,  True),
        ("Morocco",   "USA",     True,  False),
    ]
    for t1, t2, neutral, ko in tests:
        r = model.predict_match(t1, t2, features_df, neutral=neutral, knockout=ko)
        print(f"  {t1:15s} vs {t2:15s}  "
              f"xG {r['xg1']:.2f}-{r['xg2']:.2f}  "
              f"Win {r['win_prob']:.1%} Draw {r['draw_prob']:.1%} Loss {r['loss_prob']:.1%}  "
              f"Most likely: {r['most_likely_score']}")

    model.save()