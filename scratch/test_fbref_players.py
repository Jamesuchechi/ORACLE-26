
import soccerdata as sd
import pandas as pd
from pathlib import Path

# Try to get player stats for World Cup
try:
    fbref = sd.FBref(leagues="INT-World Cup", seasons=["2022"])
    player_stats = fbref.read_player_stats(stat_type="standard")
    print("Columns:", player_stats.columns.tolist())
    # Filter for Argentina
    # Level names: ['league', 'season', 'team', 'player']
    arg_players = player_stats.xs(('INT-World Cup', '2022', 'Argentina'), level=(0, 1, 2))
    print("\nArgentina Players (WC 2022):")
    print(arg_players.head())
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
