import pandas as pd
from pathlib import Path
import json
from datetime import datetime

PROCESSED_DIR = Path("data/processed")

def get_tournament_simulation():
    """Run a Monte Carlo simulation of the entire WC2026 tournament."""
    try:
        df = pd.read_csv(PROCESSED_DIR / "conflux_wc2026.csv")
        print(f"Read {len(df)} rows. Columns: {df.columns.tolist()}")
        
        # 1. Group Stage Simulation
        groups = df['group'].unique()
        print(f"Groups: {groups}")
        group_results = {}
        
        for g_name in groups:
            print(f"Simulating group {g_name}")
            g_teams = df[df['group'] == g_name].copy()
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
            print(f"Processing advancement for {t['subject']} in group {t['group']}")
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
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_tournament_simulation()
