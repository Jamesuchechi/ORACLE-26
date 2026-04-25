
import pandas as pd
from pathlib import Path
import json

def generate_legacy_index():
    df = pd.read_csv("data/raw/wc_historical.csv")
    df['year'] = pd.to_datetime(df['date']).dt.year
    
    teams = pd.concat([df['home_team'], df['away_team']]).unique()
    legacy = {}
    
    for team in teams:
        team_matches = df[(df['home_team'] == team) | (df['away_team'] == team)]
        appearances = team_matches['year'].nunique()
        total_games = len(team_matches)
        
        # Heuristic for best round:
        # 7 games in one WC = Finalist/Winner
        # 6 games = SF/3rd place
        # 5 games = QF
        # 4 games = R16
        max_games_in_year = team_matches.groupby('year').size().max()
        
        best_round = "Group Stage"
        if max_games_in_year >= 7: best_round = "Final"
        elif max_games_in_year >= 6: best_round = "Semi-Final"
        elif max_games_in_year >= 5: best_round = "Quarter-Final"
        elif max_games_in_year >= 4: best_round = "Round of 16"
        
        legacy[team] = {
            "best_finish": best_round,
            "wc_appearances": int(appearances),
            "total_wc_games": int(total_games)
        }
    
    with open("data/processed/legacy_index.json", "w") as f:
        json.dump(legacy, f, indent=2)
    print("◈ Legacy Index Generated.")

if __name__ == "__main__":
    generate_legacy_index()
