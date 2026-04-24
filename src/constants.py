"""
◈ CONFLUX — Constants & Configuration
=======================================
Single source of truth for all static data, mappings, and config.
Covers all four intelligence verticals.
"""

# ─────────────────────────────────────────────────────────────
# SYSTEM
# ─────────────────────────────────────────────────────────────
VERSION         = "1.0.0"
SYSTEM_NAME     = "CONFLUX"
SYSTEM_SUBTITLE = "Universal Multi-Signal Intelligence Engine"

# ─────────────────────────────────────────────────────────────
# VERTICAL I — FIFA World Cup 2026
# ─────────────────────────────────────────────────────────────
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

ALL_WC_TEAMS   = [t for teams in WC2026_GROUPS.values() for t in teams]
TEAM_TO_GROUP  = {t: g for g, teams in WC2026_GROUPS.items() for t in teams}

WC2026_VENUES = {
    "MetLife Stadium":         {"city": "East Rutherford, NJ", "lat": 40.8135,  "lon": -74.0745,  "country": "USA",    "altitude_m": 0},
    "AT&T Stadium":            {"city": "Arlington, TX",        "lat": 32.7480,  "lon": -97.0930,  "country": "USA",    "altitude_m": 185},
    "SoFi Stadium":            {"city": "Inglewood, CA",        "lat": 33.9535,  "lon": -118.3392, "country": "USA",    "altitude_m": 30},
    "Levi's Stadium":          {"city": "Santa Clara, CA",      "lat": 37.4033,  "lon": -121.9694, "country": "USA",    "altitude_m": 15},
    "Arrowhead Stadium":       {"city": "Kansas City, MO",      "lat": 39.0489,  "lon": -94.4839,  "country": "USA",    "altitude_m": 290},
    "Gillette Stadium":        {"city": "Foxborough, MA",       "lat": 42.0909,  "lon": -71.2643,  "country": "USA",    "altitude_m": 30},
    "Lincoln Financial Field": {"city": "Philadelphia, PA",     "lat": 39.9008,  "lon": -75.1675,  "country": "USA",    "altitude_m": 8},
    "Hard Rock Stadium":       {"city": "Miami Gardens, FL",    "lat": 25.9579,  "lon": -80.2388,  "country": "USA",    "altitude_m": 2},
    "Empower Field":           {"city": "Denver, CO",           "lat": 39.7439,  "lon": -105.0201, "country": "USA",    "altitude_m": 1609},
    "NRG Stadium":             {"city": "Houston, TX",          "lat": 29.6847,  "lon": -95.4107,  "country": "USA",    "altitude_m": 15},
    "BC Place":                {"city": "Vancouver, BC",        "lat": 49.2767,  "lon": -123.1122, "country": "Canada", "altitude_m": 5},
    "BMO Field":               {"city": "Toronto, ON",          "lat": 43.6333,  "lon": -79.4179,  "country": "Canada", "altitude_m": 76},
    "Stade Olympique":         {"city": "Montreal, QC",         "lat": 45.5597,  "lon": -73.5515,  "country": "Canada", "altitude_m": 30},
    "Estadio Azteca":          {"city": "Mexico City",          "lat": 19.3029,  "lon": -99.1505,  "country": "Mexico", "altitude_m": 2240},
    "Estadio BBVA":            {"city": "Monterrey",            "lat": 25.6694,  "lon": -100.3102, "country": "Mexico", "altitude_m": 540},
    "Estadio Akron":           {"city": "Guadalajara",          "lat": 20.7139,  "lon": -103.4058, "country": "Mexico", "altitude_m": 1566},
}

CURATED_ELO = {
    "Argentina":     2110, "France":       2060, "Spain":         2045,
    "England":       2030, "Brazil":       2015, "Portugal":      2010,
    "Italy":         1995, "Germany":       1990, "Netherlands":  1985, 
    "Belgium":       1965, "Croatia":       1955, "Uruguay":      1945, 
    "Colombia":      1935, "Morocco":       1920, "Switzerland":   1895,
    "USA":          1890, "Mexico":        1885, "Japan":         1870,
    "Senegal":      1860, "Serbia":       1865, "Denmark":       1855,
    "Ivory Coast":   1845, "Ecuador":       1840, "South Korea":   1835, 
    "Austria":      1825, "Turkey":        1815, "Iran":          1805, 
    "Australia":    1795, "Egypt":         1785, "Algeria":      1775, 
    "Scotland":      1765, "Peru":          1755, "Tunisia":      1745, 
    "Czechia":      1735, "Paraguay":      1725, "Chile":         1715, 
    "Cameroon":     1705, "Saudi Arabia":  1695, "Canada":        1690, 
    "Iraq":         1685, "DR Congo":      1675, "South Africa":  1665, 
    "Ghana":        1655, "Uzbekistan":    1645, "Bosnia":        1635,
    "Panama":       1625, "Costa Rica":    1615, "New Zealand":   1605,
    "Haiti":        1595,
}

TEAM_TO_ISO2 = {
    "Argentina": "AR", "France": "FR", "Spain": "ES", "England": "GB",
    "Brazil": "BR", "Portugal": "PT", "Germany": "DE", "Netherlands": "NL",
    "Belgium": "BE", "Croatia": "HR", "Uruguay": "UY", "Colombia": "CO",
    "Morocco": "MA", "USA": "US", "Mexico": "MX", "Switzerland": "CH",
    "Japan": "JP", "Serbia": "RS", "Norway": "NO", "Senegal": "SN",
    "Ecuador": "EC", "South Korea": "KR", "Austria": "AT", "Turkey": "TR",
    "Iran": "IR", "Australia": "AU", "Nigeria": "NG", "Egypt": "EG",
    "Algeria": "DZ", "Scotland": "GB", "Tunisia": "TN", "Czechia": "CZ",
    "Paraguay": "PY", "Chile": "CL", "Cameroon": "CM", "Saudi Arabia": "SA",
    "Canada": "CA", "Iraq": "IQ", "DR Congo": "CD", "South Africa": "ZA",
    "Qatar": "QA", "Jordan": "JO", "Uzbekistan": "UZ", "Haiti": "HT",
    "Bosnia": "BA", "Suriname": "SR", "New Caledonia": "NC", "Curacao": "CW",
}

TEAM_TO_FRED_COUNTRY = {
    "USA": "USA", "Germany": "DEU", "France": "FRA", "England": "GBR",
    "Spain": "ESP", "Brazil": "BRA", "Argentina": "ARG", "Mexico": "MEX",
    "Japan": "JPN", "South Korea": "KOR", "Australia": "AUS", "Canada": "CAN",
    "Netherlands": "NLD", "Belgium": "BEL", "Portugal": "PRT", "Switzerland": "CHE",
    "Italy": "ITA", "Austria": "AUT", "Czechia": "CZE", "Croatia": "HRV",
    "Serbia": "SRB", "Turkey": "TUR", "Morocco": "MAR", "Senegal": "SEN",
    "Ivory Coast": "CIV", "Egypt": "EGY", "Algeria": "DZA", "Tunisia": "TUN",
    "Cameroon": "CMR", "South Africa": "ZAF", "Saudi Arabia": "SAU",
    "Iran": "IRN", "Iraq": "IRQ", "Ghana": "GHA", "Uruguay": "URY",
    "Colombia": "COL", "Ecuador": "ECU", "Paraguay": "PRY", "Chile": "CHL",
    "Peru": "PER", "Haiti": "HTI", "Panama": "PAN", "Uzbekistan": "UZB",
    "Bosnia": "BIH", "DR Congo": "COD", "Costa Rica": "CRI", "New Zealand": "NZL"
}

# ─────────────────────────────────────────────────────────────
# VERTICAL II — Prediction Market Calibration
# ─────────────────────────────────────────────────────────────
TRACKED_MARKET_EVENTS = {
    # Polymarket slugs / Kalshi tickers
    "wc2026_winner":          {"type": "sports",    "description": "FIFA WC 2026 winner", "preferred_source": "polymarket"},
    "fed_rate_june":          {"type": "economics", "description": "Fed rate decision June 2026", "preferred_source": "kalshi"},
    "fed_rate_july":          {"type": "economics", "description": "Fed rate decision July 2026", "preferred_source": "kalshi"},
    "us_recession_2026":      {"type": "economics", "description": "US recession probability 2026", "preferred_source": "kalshi"},
    "ai_agi_2026":            {"type": "technology","description": "AGI milestone by end 2026", "preferred_source": "polymarket"},
    "btc_100k_2026":          {"type": "crypto",    "description": "BTC reaches $100k in 2026", "preferred_source": "polymarket"},
    "sp500_5000_eoy":         {"type": "finance",   "description": "S&P 500 above 5000 end 2026", "preferred_source": "kalshi"},
    "ukraine_ceasefire_2026": {"type": "geopolitics","description": "Ukraine ceasefire agreement", "preferred_source": "polymarket"},
}

MARKET_DIVERGENCE_THRESHOLD = 0.10   # 10pp divergence triggers alert
MARKET_ALPHA_STRONG         = 0.15   # 15pp = strong mispricing signal

# ─────────────────────────────────────────────────────────────
# VERTICAL III — Climate Risk Intelligence
# ─────────────────────────────────────────────────────────────
TRACKED_CLIMATE_REGIONS = {
    "texas":       {"lat": 31.0,  "lon": -100.0, "risk_type": "heat_grid",   "eia_region": "TRE"},
    "california":  {"lat": 36.7,  "lon": -119.4, "risk_type": "wildfire",    "eia_region": "CALI"},
    "florida":     {"lat": 27.7,  "lon": -81.7,  "risk_type": "hurricane",   "eia_region": "FLA"},
    "uk":          {"lat": 52.4,  "lon": -1.7,   "risk_type": "flooding",    "eia_region": None},
    "india":       {"lat": 20.6,  "lon": 78.9,   "risk_type": "heat_stress", "eia_region": None},
    "australia":   {"lat": -25.3, "lon": 133.8,  "risk_type": "wildfire",    "eia_region": None},
    "sahel":       {"lat": 14.5,  "lon": -4.2,   "risk_type": "drought",     "eia_region": None},
}

HEAT_STRESS_THRESHOLDS = {
    "optimal":  {"max_temp": 22, "max_humidity": 50, "penalty": 0.00},
    "mild":     {"max_temp": 28, "max_humidity": 65, "penalty": 0.03},
    "moderate": {"max_temp": 33, "max_humidity": 75, "penalty": 0.07},
    "high":     {"max_temp": 38, "max_humidity": 85, "penalty": 0.12},
    "extreme":  {"max_temp": 99, "max_humidity": 99, "penalty": 0.18},
}

ALTITUDE_THRESHOLDS = {
    "sea_level": {"max_m": 500,  "penalty": 0.00},
    "moderate":  {"max_m": 1200, "penalty": 0.03},
    "high":      {"max_m": 2000, "penalty": 0.07},
    "extreme":   {"max_m": 9999, "penalty": 0.14},
}

# ─────────────────────────────────────────────────────────────
# VERTICAL IV — Cultural Moment Detection
# ─────────────────────────────────────────────────────────────
TRACKED_CULTURAL_TOPICS = {
    "solar_energy":      {"category": "technology", "market_proxy": "TAN"},     # Solar ETF
    "ai_agents":         {"category": "technology", "market_proxy": "BOTZ"},
    "weight_loss_drugs": {"category": "health",     "market_proxy": "NVO"},
    "pickleball":        {"category": "sports",     "market_proxy": None},
    "plant_based_food":  {"category": "food",       "market_proxy": "BYND"},
    "quantum_computing": {"category": "technology", "market_proxy": "QTUM"},
    "space_tourism":     {"category": "technology", "market_proxy": "SPCE"},
    "ev_adoption":       {"category": "automotive", "market_proxy": "DRIV"},
}

TIPPING_POINT_THRESHOLD = 0.72   # Score above which we flag imminent breakthrough

# ─────────────────────────────────────────────────────────────
# SIGNAL FUSION WEIGHTS (per vertical)
# ─────────────────────────────────────────────────────────────
SIGNAL_WEIGHTS = {
    "wc2026":          {"sports": 0.45, "markets": 0.25, "finance": 0.10, "climate": 0.10, "social": 0.10},
    "market_calib":    {"sports": 0.05, "markets": 0.55, "finance": 0.25, "climate": 0.05, "social": 0.10},
    "climate_risk":    {"sports": 0.00, "markets": 0.05, "finance": 0.20, "climate": 0.60, "social": 0.15},
    "cultural_moment": {"sports": 0.10, "markets": 0.20, "finance": 0.20, "climate": 0.05, "social": 0.45},
}

# ─────────────────────────────────────────────────────────────
# MODEL CONFIG
# ─────────────────────────────────────────────────────────────
MONTE_CARLO_SIMS    = 10_000
BASE_GOALS_PER_GAME = 1.35
ELO_K_FACTOR        = 40
FORM_WINDOW_GAMES   = 5
LOOKBACK_DAYS       = 365 * 3

STAGE_WEIGHTS = {
    "FIFA World Cup":           1.00,
    "UEFA Euro":                0.85,
    "Copa America":             0.85,
    "Africa Cup of Nations":    0.75,
    "FIFA World Cup qualifier": 0.60,
    "UEFA Nations League":      0.55,
    "Friendly":                 0.20,
}

# Cross-domain divergence thresholds
DIVERGENCE_MILD     = 0.08
DIVERGENCE_MODERATE = 0.15
DIVERGENCE_STRONG   = 0.22

DATA_REFRESH_SCHEDULE = {
    "sports":  "48h",
    "markets": "6h",
    "finance": "168h",   # weekly
    "climate": "24h",
    "social":  "24h",
}