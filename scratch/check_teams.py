import csv
from pathlib import Path

WC2026_GROUPS = {
    "A": ["Mexico",    "South Africa", "South Korea", "Czechia"],
    "B": ["Canada",    "Bosnia",       "Ukraine",     "Switzerland"],
    "C": ["Brazil",    "Morocco",      "Chile",       "Scotland"],
    "D": ["USA",       "Paraguay",     "Australia",   "Turkey"],
    "E": ["Germany",   "Sweden",       "Ivory Coast", "Ecuador"],
    "F": ["Netherlands","Japan",       "Peru",        "Tunisia"],
    "G": ["Belgium",   "Egypt",        "Iran",        "New Zealand"],
    "H": ["Spain",     "Venezuela",    "Saudi Arabia","Uruguay"],
    "I": ["France",    "Senegal",      "Iraq",        "Norway"],
    "J": ["Argentina", "Algeria",      "Austria",     "Colombia"],
    "K": ["Portugal",  "DR Congo",     "Uzbekistan",  "Denmark"],
    "L": ["England",   "Croatia",      "Ghana",       "Panama"],
}

ALL_WC_TEAMS = [t for teams in WC2026_GROUPS.values() for t in teams]

results_path = Path("data/raw/international_results.csv")
all_results_teams = set()
with open(results_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        all_results_teams.add(row["home_team"])
        all_results_teams.add(row["away_team"])

missing = [t for t in ALL_WC_TEAMS if t not in all_results_teams]
print(f"Missing teams: {missing}")

# Check for partial matches
for m in missing:
    matches = [t for t in all_results_teams if m in t]
    print(f"Partial matches for {m}: {matches}")
    if not matches:
        # Try reverse partial match
        matches = [t for t in all_results_teams if any(word in t for word in m.split())]
        print(f"Word matches for {m}: {matches[:10]}...")
