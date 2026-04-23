# 🔮 ORACLE-26
### *The Multi-Signal Intelligence Engine for FIFA World Cup 2026*

> "We don't just watch the game. We watch everything that predicts it."

[![Zerve AI](https://img.shields.io/badge/Built%20on-Zerve%20AI-blueviolet)](https://zerve.ai)
[![WC2026](https://img.shields.io/badge/FIFA-World%20Cup%202026-green)](https://fifa.com)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange)]()

---

## What is ORACLE-26?

ORACLE-26 is a live, multi-signal prediction engine for the 2026 FIFA World Cup — the first tournament ever to feature 48 teams across 104 matches in the United States, Canada, and Mexico (June 11 – July 19, 2026).

While every other prediction model looks at football data alone, ORACLE-26 fuses **five independent data domains** into a single unified intelligence layer:

| Signal Domain | What It Captures |
|---|---|
| ⚽ **Sports & Performance** | Team Elo, form, xG, historical WC results |
| 📈 **Prediction Markets** | Real-money odds from Polymarket & Kalshi |
| 💰 **Finance & Economics** | Host nation macro health, GDP, team country stability |
| 🌍 **Climate & Energy** | Venue weather forecasts, heat stress, travel distance |
| 📣 **Social & Cultural Trends** | Google Trends momentum, Reddit/X sentiment per team |

The thesis: **Football outcomes are not determined by football data alone.** A team playing in 40°C heat after a 14-hour flight, in a country with political instability, against a nation whose prediction market odds just shifted 8 points — that team's probability changes. ORACLE-26 captures all of it.

---

## Live Deliverables

### 1. 🧠 Analysis Engine (Zerve Project)
A fully documented, reproducible analysis pipeline running inside Zerve. From raw data ingestion to final predictions — every step visible, every model explainable.

### 2. 🔌 Prediction API
A live REST endpoint deployable from Zerve:

```bash
GET /predict?team1=Brazil&team2=Germany&match_date=2026-07-01&venue=MetLife

# Response:
{
  "team1": "Brazil",
  "team2": "Germany",
  "venue": "MetLife Stadium, New Jersey",
  "match_date": "2026-07-01",
  "predictions": {
    "win_prob":  0.412,
    "draw_prob": 0.231,
    "loss_prob": 0.357,
    "xg_team1":  1.73,
    "xg_team2":  1.60
  },
  "signal_breakdown": {
    "sports_score":    0.55,
    "market_signal":   0.62,
    "economic_signal": 0.48,
    "climate_signal":  0.71,
    "social_signal":   0.59
  },
  "confidence": "high",
  "model_version": "oracle26-v1"
}
```

### 3. 🖥️ Interactive App
A publicly shareable web app where anyone can:
- **Simulate any match** — pick two teams, get instant multi-signal prediction
- **Explore the bracket** — see full tournament simulation with win probabilities
- **Track signal shifts** — watch how market odds, sentiment, and weather change predictions in real time
- **Compare models** — see how ORACLE-26 stacks up against single-signal baselines

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        ORACLE-26                            │
│                  Multi-Signal Pipeline                      │
└─────────────────────────────────────────────────────────────┘
         │           │           │           │           │
    ⚽ Sports   📈 Markets  💰 Finance  🌍 Climate  📣 Social
    FBref       Polymarket   FRED        NOAA        Google
    Elo Ratings Kalshi       Alpha Vant  OpenMeteo   Trends
    Stathead    Metaculus    SEC EDGAR   EIA         Reddit
         │           │           │           │           │
         └───────────┴───────────┴───────────┴───────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Feature Engineering   │
                    │  (Per-match, Per-team)  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    ORACLE-26 Model      │
                    │  XGBoost + Poisson +    │
                    │  Monte Carlo Ensemble   │
                    └────────────┬────────────┘
                                 │
               ┌─────────────────┼─────────────────┐
               │                 │                 │
    ┌──────────▼──────┐ ┌───────▼──────┐ ┌───────▼──────┐
    │  Zerve Analysis │ │  Live API    │ │ Interactive  │
    │  (Reproducible) │ │  Endpoint    │ │    App       │
    └─────────────────┘ └──────────────┘ └──────────────┘
```

---

## Data Sources

### ⚽ Sports & Performance
| Source | Data | Usage |
|--------|------|-------|
| [FBref](https://fbref.com) | Match stats, xG, player ratings | Core match features |
| [Eloratings.net](https://eloratings.net) | National team Elo history | Team strength baseline |
| [martj42/international_results](https://github.com/martj42/international_results) | All international results 1872–2026 | Historical training data |
| [Stathead](https://stathead.com) | Advanced historical WC stats | Tournament-specific patterns |

### 📈 Prediction Markets
| Source | Data | Usage |
|--------|------|-------|
| [Polymarket API](https://polymarket.com) | WC winner odds, match odds | Market-implied probability |
| [Kalshi API](https://kalshi.com) | Regulated US market odds | Arbitrage signal |
| [Metaculus](https://metaculus.com) | Community forecast accuracy | Calibration reference |

### 💰 Finance & Economics
| Source | Data | Usage |
|--------|------|-------|
| [FRED API](https://fred.stlouisfed.org) | GDP, inflation, employment | Host/team country health |
| [Alpha Vantage](https://alphavantage.co) | Forex, stock indices | Economic sentiment |
| [World Bank Open Data](https://data.worldbank.org) | Country economic indicators | Long-term stability signal |

### 🌍 Climate & Energy
| Source | Data | Usage |
|--------|------|-------|
| [Open-Meteo API](https://open-meteo.com) | Venue weather forecasts | Match-day conditions |
| [NOAA](https://noaa.gov) | Historical climate norms | Expected conditions |
| [EIA](https://eia.gov) | Energy/travel data | Host logistics signal |

### 📣 Social & Cultural Trends
| Source | Data | Usage |
|--------|------|-------|
| [Google Trends (pytrends)](https://trends.google.com) | Search volume per team | Public attention momentum |
| [Reddit API](https://reddit.com/dev/api) | r/soccer sentiment | Fan sentiment signal |
| [Twitter/X API](https://developer.x.com) | Hashtag volume & sentiment | Real-time buzz tracking |

---

## Model Details

### Core Prediction: Dixon-Coles Poisson Model
- Estimates expected goals (xG) for each team per match
- Accounts for attack strength, defensive weakness, home/neutral advantage
- Corrected for low-scoring game correlation (Dixon-Coles adjustment)

### Ensemble Layer: XGBoost Classifier
- Trained on 10,000+ historical international matches (2000–2025)
- Features: Elo difference, form, xG, head-to-head, tournament stage
- Output: win/draw/loss probability distribution

### Signal Fusion: Weighted Multi-Signal Aggregation
```
Final Probability = w1*Sports + w2*Markets + w3*Economic + w4*Climate + w5*Social

Weights (learned via cross-validation on WC2018 + WC2022):
  w1 (Sports)    = 0.45
  w2 (Markets)   = 0.25
  w3 (Economic)  = 0.10
  w4 (Climate)   = 0.10
  w5 (Social)    = 0.10
```

### Tournament Simulation: Monte Carlo
- 10,000 full tournament simulations per prediction run
- Covers group stage → Round of 32 → Round of 16 → QF → SF → Final
- Outputs: group qualification %, knockout stage reach %, tournament win %

---

## Why ORACLE-26 Wins

| Feature | Typical WC Model | ORACLE-26 |
|---------|-----------------|-----------|
| Data sources | 1 (football stats) | 5 domains |
| Market signals | ❌ | ✅ Real-money odds |
| Weather at venue | ❌ | ✅ Match-day forecast |
| Economic context | ❌ | ✅ GDP, forex, stability |
| Social momentum | ❌ | ✅ Trends + sentiment |
| Live updates | ❌ | ✅ Refreshes daily |
| Deployed API | ❌ | ✅ Public endpoint |
| Interactive app | ❌ | ✅ Anyone can use it |
| Explainability | ❌ | ✅ Signal breakdown per match |

---

## Team

Built during the **ZerveHack Hackathon** (April 2026) using Zerve AI as the primary platform for data analysis, model deployment, and app hosting.

---

## License

MIT License — open source, shareable, remixable.

---

*ORACLE-26 — Because the beautiful game deserves beautiful intelligence.*
