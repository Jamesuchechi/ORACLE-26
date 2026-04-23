"""
ORACLE-26 — Constants
=====================
Single source of truth for all static data:
teams, groups, venues, weights, and config.
"""

# ─────────────────────────────────────────────
# WC 2026 — All 48 Teams by Group
# ─────────────────────────────────────────────
WC2026_GROUPS = {
    "A": ["Mexico", "South Korea", "Czechia", "South Africa"],
    "B": ["USA", "Australia", "Paraguay", "Turkey"],
    "C": ["Canada", "Switzerland", "Qatar", "Bosnia"],
    "D": ["France", "Morocco", "Japan", "Haiti"],
    "E": ["Spain", "Nigeria", "Serbia", "New Caledonia"],
    "F": ["England", "Senegal", "DR Congo", "Uzbekistan"],
    "G": ["Brazil", "Colombia", "Belgium", "Saudi Arabia"],
    "H": ["Argentina", "Ecuador", "Croatia", "Algeria"],
    "I": ["Portugal", "Egypt", "Iran", "Suriname"],
    "J": ["Germany", "Cameroon", "Uruguay", "Curacao"],
    "K": ["Netherlands", "Tunisia", "Chile", "Iraq"],
    "L": ["Norway", "Scotland", "Austria", "Jordan"],
}

ALL_TEAMS = [team for teams in WC2026_GROUPS.values() for team in teams]

TEAM_TO_GROUP = {
    team: group
    for group, teams in WC2026_GROUPS.items()
    for team in teams
}

# ─────────────────────────────────────────────
# Name Normalization Maps
# ─────────────────────────────────────────────

# ORACLE name → how it appears in historical results datasets
TEAM_TO_RESULTS_NAME = {
    "Turkey":     "Turkey",
    "Bosnia":     "Bosnia-Herzegovina",
    "DR Congo":   "DR Congo",
    "USA":        "United States",
    "Curacao":    "Curaçao",
    "Czechia":    "Czech Republic",
}

# ORACLE name → ISO alpha-2 country code (for flag/API lookups)
TEAM_TO_ISO2 = {
    "Argentina":     "AR", "France":       "FR", "Spain":        "ES",
    "England":       "GB-ENG", "Brazil":   "BR", "Portugal":     "PT",
    "Germany":       "DE", "Netherlands":  "NL", "Belgium":      "BE",
    "Croatia":       "HR", "Uruguay":      "UY", "Colombia":     "CO",
    "Morocco":       "MA", "USA":          "US", "Mexico":       "MX",
    "Switzerland":   "CH", "Japan":        "JP", "Serbia":       "RS",
    "Norway":        "NO", "Senegal":      "SN", "Ecuador":      "EC",
    "South Korea":   "KR", "Austria":      "AT", "Turkey":       "TR",
    "Iran":          "IR", "Australia":    "AU", "Nigeria":      "NG",
    "Egypt":         "EG", "Algeria":      "DZ", "Scotland":     "GB-SCT",
    "Tunisia":       "TN", "Czechia":      "CZ", "Paraguay":     "PY",
    "Chile":         "CL", "Cameroon":     "CM", "Saudi Arabia":  "SA",
    "Canada":        "CA", "Iraq":         "IQ", "DR Congo":     "CD",
    "South Africa":  "ZA", "Qatar":        "QA", "Jordan":       "JO",
    "Uzbekistan":    "UZ", "Haiti":        "HT", "Bosnia":       "BA",
    "Suriname":      "SR", "New Caledonia": "NC", "Curacao":     "CW",
}

# ORACLE name → FRED country code (for economic data)
TEAM_TO_FRED_COUNTRY = {
    "USA":          "USA", "Germany":      "DEU", "France":       "FRA",
    "England":      "GBR", "Spain":        "ESP", "Italy":        "ITA",
    "Brazil":       "BRA", "Argentina":    "ARG", "Mexico":       "MEX",
    "Japan":        "JPN", "South Korea":  "KOR", "Australia":    "AUS",
    "Canada":       "CAN", "Netherlands":  "NLD", "Belgium":      "BEL",
    "Portugal":     "PRT", "Switzerland":  "CHE", "Norway":       "NOR",
    "Austria":      "AUT", "Czechia":      "CZE", "Poland":       "POL",
    "Croatia":      "HRV", "Serbia":       "SRB", "Turkey":       "TUR",
    "Morocco":      "MAR", "Senegal":      "SEN", "Nigeria":      "NGA",
    "Egypt":        "EGY", "Algeria":      "DZA", "Tunisia":      "TUN",
    "Cameroon":     "CMR", "South Africa": "ZAF", "DR Congo":     "COD",
    "Saudi Arabia": "SAU", "Iran":         "IRN", "Iraq":         "IRQ",
    "Qatar":        "QAT", "Uruguay":      "URY", "Colombia":     "COL",
    "Ecuador":      "ECU", "Paraguay":     "PRY", "Chile":        "CHL",
    "Canada":       "CAN", "Haiti":        "HTI", "Jordan":       "JOR",
    "Uzbekistan":   "UZB", "Bosnia":       "BIH", "Scotland":     "GBR",
    "Suriname":     "SUR", "Curacao":      "CUW", "New Caledonia": "NCL",
}

# ─────────────────────────────────────────────
# WC 2026 Venues
# ─────────────────────────────────────────────
WC2026_VENUES = {
    # United States
    "MetLife Stadium":        {"city": "East Rutherford, NJ", "lat": 40.8135,  "lon": -74.0745,  "capacity": 82500, "country": "USA"},
    "AT&T Stadium":           {"city": "Arlington, TX",        "lat": 32.7480,  "lon": -97.0930,  "capacity": 80000, "country": "USA"},
    "SoFi Stadium":           {"city": "Inglewood, CA",        "lat": 33.9535,  "lon": -118.3392, "capacity": 70240, "country": "USA"},
    "Levi's Stadium":         {"city": "Santa Clara, CA",      "lat": 37.4033,  "lon": -121.9694, "capacity": 68500, "country": "USA"},
    "Arrowhead Stadium":      {"city": "Kansas City, MO",      "lat": 39.0489,  "lon": -94.4839,  "capacity": 76416, "country": "USA"},
    "Gillette Stadium":       {"city": "Foxborough, MA",       "lat": 42.0909,  "lon": -71.2643,  "capacity": 65878, "country": "USA"},
    "Lincoln Financial Field":{"city": "Philadelphia, PA",     "lat": 39.9008,  "lon": -75.1675,  "capacity": 69176, "country": "USA"},
    "Hard Rock Stadium":      {"city": "Miami Gardens, FL",    "lat": 25.9579,  "lon": -80.2388,  "capacity": 65326, "country": "USA"},
    "Empower Field":          {"city": "Denver, CO",           "lat": 39.7439,  "lon": -105.0201, "capacity": 76125, "country": "USA", "altitude_m": 1609},
    "NRG Stadium":            {"city": "Houston, TX",          "lat": 29.6847,  "lon": -95.4107,  "capacity": 72220, "country": "USA"},
    "Seattle Stadium":        {"city": "Seattle, WA",          "lat": 47.5952,  "lon": -122.3316, "capacity": 69000, "country": "USA"},
    # Canada
    "BC Place":               {"city": "Vancouver, BC",        "lat": 49.2767,  "lon": -123.1122, "capacity": 54500, "country": "Canada"},
    "BMO Field":              {"city": "Toronto, ON",          "lat": 43.6333,  "lon": -79.4179,  "capacity": 45736, "country": "Canada"},
    "Stade Olympique":        {"city": "Montreal, QC",         "lat": 45.5597,  "lon": -73.5515,  "capacity": 66308, "country": "Canada"},
    # Mexico
    "Estadio Azteca":         {"city": "Mexico City",          "lat": 19.3029,  "lon": -99.1505,  "capacity": 87523, "country": "Mexico", "altitude_m": 2240},
    "Estadio BBVA":           {"city": "Monterrey",            "lat": 25.6694,  "lon": -100.3102, "capacity": 53500, "country": "Mexico"},
    "Estadio Akron":          {"city": "Guadalajara",          "lat": 20.7139,  "lon": -103.4058, "capacity": 49850, "country": "Mexico"},
}

# ─────────────────────────────────────────────
# Curated Elo Ratings (April 2026)
# ─────────────────────────────────────────────
CURATED_ELO = {
    "Argentina":     2090, "France":        2050, "Spain":         2040,
    "England":       2020, "Brazil":        2010, "Portugal":      2000,
    "Germany":       1990, "Netherlands":   1980, "Belgium":       1960,
    "Croatia":       1950, "Uruguay":       1940, "Colombia":      1930,
    "Morocco":       1910, "USA":           1900, "Mexico":        1890,
    "Switzerland":   1880, "Serbia":        1870, "Norway":        1860,
    "Japan":         1855, "Senegal":       1850, "Ecuador":       1840,
    "South Korea":   1830, "Austria":       1820, "Turkey":        1810,
    "Iran":          1800, "Australia":     1790, "Nigeria":       1780,
    "Egypt":         1770, "Algeria":       1760, "Scotland":      1750,
    "Tunisia":       1740, "Czechia":       1730, "Paraguay":      1720,
    "Chile":         1710, "Cameroon":      1700, "Saudi Arabia":  1690,
    "Canada":        1685, "Iraq":          1680, "DR Congo":      1670,
    "South Africa":  1660, "Qatar":         1650, "Jordan":        1640,
    "Uzbekistan":    1630, "Haiti":         1600, "Bosnia":        1620,
    "Suriname":      1580, "New Caledonia": 1500, "Curacao":       1520,
}

# ─────────────────────────────────────────────
# Signal Fusion Weights
# ─────────────────────────────────────────────
SIGNAL_WEIGHTS = {
    "sports":    0.45,
    "markets":   0.25,
    "economic":  0.10,
    "climate":   0.10,
    "social":    0.10,
}

# ─────────────────────────────────────────────
# Model Config
# ─────────────────────────────────────────────
MONTE_CARLO_SIMS    = 10_000
BASE_GOALS_PER_GAME = 1.35      # Historical average goals per team in international football
ELO_K_FACTOR        = 40        # Elo K-factor for international matches
FORM_WINDOW_GAMES   = 5         # Number of recent games for form calculation
LOOKBACK_DAYS       = 365 * 3   # 3 years of historical data for feature engineering

# Tournament stage multipliers (knockout format)
STAGE_WEIGHTS = {
    "FIFA World Cup":          1.0,
    "UEFA Euro":               0.85,
    "Copa America":            0.85,
    "Africa Cup of Nations":   0.75,
    "FIFA World Cup qualifier": 0.60,
    "UEFA Nations League":     0.55,
    "Friendly":                0.20,
}