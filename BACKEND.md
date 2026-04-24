# ◈ CONFLUX Backend Intelligence

This document outlines the architecture and operation of the CONFLUX backend — a universal multi-signal intelligence hub.

## 🧠 Core Architecture

CONFLUX is built on the thesis that **cross-domain signal interaction** predicts outcomes better than single-domain models.

### 1. Signal Engines (`src/data/`)
Five independent engines collect and normalize data into `[0, 1]` scores:
- **Sports** (`sports.py`): Dixon-Coles Poisson model + Elo + Form.
- **Markets** (`markets.py`): Real-money odds from Polymarket/Kalshi.
- **Economics** (`economics.py`): Macro indicators (GDP, Inflation) from FRED/World Bank.
- **Climate** (`climate.py`): Weather risk and heat stress from NOAA/Open-Meteo.
- **Social** (`social.py`): Search momentum (Google Trends) and Reddit sentiment.

### 2. Fusion Engine (`src/features/fusion.py`)
The "Heart" of CONFLUX. It performs:
- **Normalization**: Ensuring all signals are on the same scale.
- **Weighting**: Applying vertical-specific weights (e.g., Sports is 45% for WC2026 but 5% for Market Calibration).
- **Interaction Logic**: Applying non-linear rules (e.g., Economic crisis → Sports performance penalty).
- **Divergence Detection**: Surfacing "surprises" where signals disagree.

### 3. Intelligence Verticals
- **Vertical I: World Cup 2026**: High-fidelity match and tournament predictions.
- **Vertical II: Market Calibration**: Detecting mispricing in prediction markets.
- **Vertical III: Climate Risk**: Predicting grid stress and environmental costs.
- **Vertical IV: Cultural Moment**: Detecting tipping points in social trends.

---

## 🛠 Operation

### 1. Run Data Pipeline
To refresh all intelligence signals and generate the latest predictions:
```bash
source venv/bin/activate
python wc2026_pipeline.py --all
```
Outputs are saved to `data/processed/conflux_*.csv`.

### 2. Start REST API
To expose the intelligence via a high-performance API:
```bash
source venv/bin/activate
python api.py
```
The API will be available at `http://localhost:8000`.

---

## 🔌 API Documentation

### World Cup 2026
- `GET /v1/predict/wc2026/rankings`: Get current Conflux rankings for all 48 teams.
- `GET /v1/predict/wc2026/match?team1=Brazil&team2=Germany`: Run a live match simulation.

### Market Intelligence
- `GET /v1/predict/market/alpha`: Get market mispricing (alpha) signals.

### Climate & Social
- `GET /v1/predict/climate/risk`: Get regional climate risk intelligence.
- `GET /v1/predict/cultural/moments`: Get trending cultural moment scores.

### System
- `GET /health`: Check API and pipeline status.

---

## 📊 Data Schema (Processed)

Each `conflux_*.csv` contains:
- `subject`: The entity (Team, Market Event, Region, Topic).
- `conflux_score`: The final intelligence score `[0, 1]`.
- `confidence`: `high | medium | low` based on signal agreement.
- `signal_breakdown`: Individual scores for all 5 domains.
- `interpretation`: Human-readable explanation of the result.

---

*CONFLUX Intelligence Engine · Developed for ZerveHack 2026*
