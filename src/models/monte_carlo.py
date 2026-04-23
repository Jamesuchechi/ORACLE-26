"""
ORACLE-26 — Monte Carlo Tournament Simulator
===============================================
Runs thousands of full tournament simulations to calculate
qualification and victory probabilities for all 48 teams.
"""

import numpy as np
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from typing import Optional, List, Dict

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.constants import WC2026_GROUPS, MONTE_CARLO_SIMS
from src.models.poisson import PoissonModel

class TournamentSimulator:
    def __init__(self, model: Optional[PoissonModel] = None):
        self.model = model or PoissonModel.load()
        self.features_df = pd.read_csv("data/processed/sports_features.csv")

    def simulate_group(self, group_name: str, teams: List[str]) -> Dict[str, Dict]:
        """Simulate a single group stage."""
        points = {t: 0 for t in teams}
        gd = {t: 0 for t in teams}
        gs = {t: 0 for t in teams}

        # Round robin
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                t1, t2 = teams[i], teams[j]
                pred = self.model.predict_match(t1, t2, self.features_df)
                
                # Sample outcome
                r = np.random.random()
                if r < pred["win_prob"]:
                    points[t1] += 3
                    g1 = np.random.poisson(pred["xg1"])
                    g2 = max(0, g1 - np.random.randint(1, 3))
                elif r < pred["win_prob"] + pred["draw_prob"]:
                    points[t1] += 1; points[t2] += 1
                    g1 = g2 = np.random.poisson((pred["xg1"] + pred["xg2"]) / 2)
                else:
                    points[t2] += 3
                    g2 = np.random.poisson(pred["xg2"])
                    g1 = max(0, g2 - np.random.randint(1, 3))
                
                gd[t1] += (g1 - g2); gd[t2] += (g2 - g1)
                gs[t1] += g1; gs[t2] += g2

        # Sort standings
        standings = sorted(teams, key=lambda t: (points[t], gd[t], gs[t]), reverse=True)
        return {
            "first": standings[0],
            "second": standings[1],
            "third": standings[2] # In WC2026, some 3rd place teams qualify
        }

    def run_full_simulation(self, iterations: int = 1000):
        """Run N full tournament simulations."""
        print(f"  [sim] Running {iterations} full tournament simulations...")
        
        results = {t: {"win": 0, "final": 0, "semi": 0, "quarter": 0, "r16": 0, "r32": 0} 
                   for teams in WC2026_GROUPS.values() for t in teams}

        for _ in tqdm(range(iterations)):
            # 1. Group Stage
            qualified = []
            for group, teams in WC2026_GROUPS.items():
                res = self.simulate_group(group, teams)
                qualified.extend([res["first"], res["second"]])
                # Note: Simplified WC2026 logic (top 2 from 12 groups + 8 best 3rd)
                # For this version, we'll take top 2 + 8 random 3rd to fill 32
            
            # 2. Knockouts (Simplified Bracket)
            bracket = qualified[:32] # 32 teams
            
            # Round of 32
            bracket = self._run_knockout_round(bracket, results, "r32")
            # Round of 16
            bracket = self._run_knockout_round(bracket, results, "r16")
            # Quarter-finals
            bracket = self._run_knockout_round(bracket, results, "quarter")
            # Semi-finals
            bracket = self._run_knockout_round(bracket, results, "semi")
            # Final
            winner = self._run_knockout_round(bracket, results, "final")
            
            if winner:
                results[winner[0]]["win"] += 1

        # Normalize probabilities
        prob_df = pd.DataFrame.from_dict(results, orient='index')
        prob_df = (prob_df / iterations).round(4)
        prob_df.to_csv("data/processed/tournament_simulation.csv")
        print(f"  [sim] Results saved to data/processed/tournament_simulation.csv")
        return prob_df

    def _run_knockout_round(self, bracket: List[str], stats: Dict, round_key: str) -> List[str]:
        winners = []
        for i in range(0, len(bracket), 2):
            t1, t2 = bracket[i], bracket[i+1]
            stats[t1][round_key] += 1
            stats[t2][round_key] += 1
            
            pred = self.model.predict_match(t1, t2, self.features_df, knockout=True)
            if np.random.random() < pred["win_prob"]:
                winners.append(t1)
            else:
                winners.append(t2)
        return winners

if __name__ == "__main__":
    sim = TournamentSimulator()
    sim.run_full_simulation(iterations=1000)
