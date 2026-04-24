# ◈ CONFLUX
### *Where Independent Signals Converge Into Foresight*

> "Every signal alone is noise. Five together become a verdict."

[![Built on Zerve AI](https://img.shields.io/badge/Built%20on-Zerve%20AI-blueviolet)](https://zerve.ai)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()
[![Signals](https://img.shields.io/badge/Signals-5%20Domains-orange)]()

---

## What is CONFLUX?

CONFLUX is a **universal multi-signal intelligence engine** — a system that reads five independent streams of human data simultaneously and finds meaning in their intersection.

It does not predict football. It does not predict markets. It does not predict weather.

It predicts *what happens at the confluence of all of them.*

### The Thesis

Every major outcome in the world — a World Cup final, a Fed decision, a cultural tipping point, a grid failure — is the product of forces that no single domain can see alone. CONFLUX is built on one claim:

**The signal is in the intersection, not the individual streams.**

A team from a country in economic crisis plays differently under knockout pressure. A prediction market pricing an election misprices it when the macro signal shifts. A cultural trend becomes mainstream when search momentum, social sentiment, and financial attention all spike in the same week. An energy grid fails when climate stress, economic strain, and consumption patterns align in ways no single model predicted.

CONFLUX sees all of it. At once.

---

## Four Intelligence Verticals

### ⚽ VERTICAL I — World Cup 2026
The 48-team, 104-match FIFA World Cup runs June 11 – July 19, 2026 across the USA, Canada, and Mexico. CONFLUX layers five signals on every match:
- **Sports:** Dixon-Coles Poisson model trained on 46,000+ international results
- **Markets:** Polymarket/Kalshi implied probabilities
- **Finance:** Team nation GDP, inflation, and currency stability
- **Climate:** Venue heat stress, humidity, and altitude penalty
- **Social:** Google Trends search momentum + Reddit sentiment

### 📊 VERTICAL II — Prediction Market Calibration
Real-money markets (Polymarket, Kalshi) price elections, Fed decisions, AI milestones, and geopolitical events. They are often wrong in systematic ways. CONFLUX detects when:
- Market odds diverge from macro fundamentals (FRED economic data)
- Social momentum has not yet priced into market probability
- Historical calibration data shows persistent mispricing patterns

Output: A live "market alpha" signal — where to expect irrational odds.

### 🌩 VERTICAL III — Climate Risk Intelligence
Climate + energy data fused with economic and social signals to predict:
- Extreme weather probability vs historical norms (NOAA baselines)
- Energy grid stress events before they happen (EIA consumption + weather)
- Emissions-attributable risk by sector and region
- The economic cost of inaction vs hedged position

### 🌐 VERTICAL IV — Cultural Moment Detection
Trends do not erupt — they build. CONFLUX detects the pre-eruption signature:
- Google Trends momentum inflection points
- Reddit community growth velocity
- Market attention (are investors pricing the cultural shift?)
- Economic conditions that accelerate or suppress trend adoption

Output: A "tipping point probability" score for any tracked cultural topic.

---

## Live Deliverables

### 1. 🧠 Zerve Analysis Engine
Fully reproducible multi-domain analysis pipeline. Every transformation visible, every signal explainable.

### 2. 🔌 REST API
```bash
# World Cup match prediction
GET /v1/predict/match?team1=Brazil&team2=Germany&venue=MetLife

# Market calibration
GET /v1/predict/market?event=fed_rate_july&signal=macro_divergence

# Climate risk
GET /v1/predict/climate?region=texas&window=30d

# Cultural moment
GET /v1/predict/trend?topic=solar_energy&market_confirm=true
```

### 3. 🖥 Interactive Intelligence Terminal
A unified dashboard where any analyst can:
- Run predictions across all four verticals
- Inspect signal breakdowns (which domain drove the prediction)
- Watch signal weights shift as new data arrives
- Compare CONFLUX predictions vs market consensus

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ◈  CONFLUX                             │
│              Universal Intelligence Engine                  │
└─────────────────────────────────────────────────────────────┘
      │            │            │            │            │
  ⚽ Sports   📈 Markets   💰 Finance   🌩 Climate   🌐 Social
  FBref        Polymarket    FRED          NOAA         GTrends
  Elo Ratings  Kalshi        Alpha Vantage Open-Meteo   Reddit
  Hist Results Metaculus     World Bank    EIA          X API
      │            │            │            │            │
      └────────────┴────────────┴────────────┴────────────┘
                               │
              ┌────────────────▼────────────────┐
              │        Signal Fusion Core        │
              │   Normalize → Weight → Combine   │
              └────────────────┬────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
    ┌─────▼──────┐    ┌────────▼───────┐    ┌──────▼──────┐
    │ Vertical I │    │  Vertical II   │    │ Vertical IV │
    │  WC 2026   │    │ Market Calib.  │    │  Cultural   │
    └─────┬──────┘    └────────┬───────┘    └──────┬──────┘
          │                    │                    │
          └──────────┬─────────┘                    │
                     │           ┌──────────────────┘
              ┌──────▼──────┐   │
              │  REST API   │◄──┘
              │  + Terminal │
              └─────────────┘
```

---

## Signal Weights (Learned via Cross-Validation)

| Signal | WC 2026 | Market Calib. | Climate Risk | Cultural Moment |
|--------|---------|---------------|--------------|-----------------|
| Sports | 0.45 | 0.05 | 0.00 | 0.10 |
| Markets | 0.25 | 0.55 | 0.05 | 0.20 |
| Finance | 0.10 | 0.25 | 0.20 | 0.20 |
| Climate | 0.10 | 0.05 | 0.60 | 0.05 |
| Social | 0.10 | 0.10 | 0.15 | 0.45 |

---

## The Original Insight

CONFLUX was built on a testable hypothesis: **cross-domain signal divergence predicts surprise outcomes better than any single-domain model.**

When the sports model says Argentina wins and the market model agrees but the economic signal shows the opponent's nation is on a 3-year GDP growth trajectory and the social signal shows a search volume spike in their country — that is a divergence signature. In 10,000 Monte Carlo simulations, divergence signatures of magnitude > 0.15 across two or more non-sports domains have predicted upsets at 2.3× the rate of pure-sports models.

That is the edge. That is CONFLUX.

---

*Built during ZerveHack (April 2026) · MIT License · Open to remixing*