# 🛠️ ORACLE-26 — Setup Guide

> Complete setup instructions for getting ORACLE-26 running locally and on Zerve AI.

---

## Prerequisites

| Requirement     | Version | Notes                                 |
| --------------- | ------- | ------------------------------------- |
| Python          | 3.10+   | 3.11 recommended                      |
| pip             | 23.0+   | `pip install --upgrade pip`           |
| Git             | Any     | For cloning & version control         |
| Zerve Account   | —       | Sign up at zerve.ai (Antigravity Pro) |
| Internet access | —       | Required for all API data pulls       |

---

## 1. Clone & Install

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/oracle-26.git
cd oracle-26

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# Install all dependencies
pip install -r requirements.txt
```

---

## 2. Dependencies (requirements.txt)

```txt
# Core Data
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
python-dotenv>=1.0.0

# Football Data
soccerdata>=1.6.0
pytrends>=4.9.2

# Machine Learning
scikit-learn>=1.3.0
xgboost>=2.0.0
shap>=0.43.0
scipy>=1.11.0

# APIs & Data Sources
fredapi>=0.5.1
alpha-vantage>=2.3.1
praw>=7.7.1                     # Reddit API

# Climate
openmeteo-requests>=1.1.0
retry-requests>=2.0.0

# Visualization
plotly>=5.18.0
matplotlib>=3.7.0
seaborn>=0.12.0
folium>=0.15.0

# App / API
fastapi>=0.104.0
uvicorn>=0.24.0

# Utilities
tqdm>=4.66.0
joblib>=1.3.0
python-dateutil>=2.8.2
```

---

## 3. API Keys Setup

ORACLE-26 uses several free APIs. Get your keys here:

### 3.1 FRED (Federal Reserve Economic Data)

- Sign up: https://fred.stlouisfed.org/docs/api/api_key.html
- Free tier: 120 requests/min, unlimited calls
- Add to `.env`:
  ```
  FRED_API_KEY=your_fred_key_here
  ```

### 3.2 Alpha Vantage (Forex/Stock Data)

- Sign up: https://www.alphavantage.co/support/#api-key
- Free tier: 25 requests/day (sufficient for our use)
- Add to `.env`:
  ```
  ALPHA_VANTAGE_KEY=your_av_key_here
  ```

### 3.3 Reddit API (Social Sentiment)

- Sign up: https://www.reddit.com/prefs/apps → create "script" app
- Free tier: 60 requests/min
- Add to `.env`:
  ```
  REDDIT_CLIENT_ID=your_client_id
  REDDIT_CLIENT_SECRET=your_client_secret
  REDDIT_USER_AGENT=oracle26/1.0 by YOUR_USERNAME
  ```

### 3.4 Polymarket (Prediction Markets)

- No API key required for public endpoints
- Docs: https://docs.polymarket.com
- Rate limit: 10 req/s (we use well under this)

### 3.5 Kalshi (Prediction Markets)

- Sign up: https://kalshi.com/sign-up
- Free demo account works for read-only market data
- Add to `.env`:
  ```
  KALSHI_EMAIL=your_kalshi_email
  KALSHI_PASSWORD=your_kalshi_password
  ```

### 3.6 Open-Meteo (Climate Data)

- **No API key required** — completely free and open
- Docs: https://open-meteo.com/en/docs
- Rate limit: 10,000 req/day (generous)

### 3.7 Google Trends (pytrends)

- **No API key required** — uses unofficial Google Trends API
- Note: Use respectful delays (60s between requests) to avoid blocks

---

## 4. Environment File

Create a `.env` file in the project root:

```bash
cp .env.example .env
# Then fill in your keys
```

**.env.example:**

```env
# FRED Economic Data
FRED_API_KEY=

# Alpha Vantage Financial Data
ALPHA_VANTAGE_KEY=

# Reddit Social Data
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=oracle26/1.0

# Kalshi Prediction Markets
KALSHI_EMAIL=
KALSHI_PASSWORD=

# App Settings
APP_ENV=development
MODEL_VERSION=oracle26-v1
DATA_REFRESH_HOURS=24
MONTE_CARLO_SIMS=10000

# Zerve Settings (filled after Zerve deploy)
ZERVE_PROJECT_ID=
ZERVE_API_ENDPOINT=
```

---

## 5. Project Structure

```
oracle-26/
│
├── README.md                   # Project overview
├── TODO.md                     # Build phases & task tracker
├── SETUP.md                    # This file
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .env                        # Your actual keys (gitignored)
├── .gitignore
│
├── data/                       # Raw & processed data (gitignored)
│   ├── raw/
│   │   ├── international_results.csv
│   │   ├── elo_ratings.csv
│   │   └── wc_historical.csv
│   ├── processed/
│   │   ├── team_features.csv
│   │   ├── match_features.csv
│   │   └── group_simulations.csv
│   └── signals/
│       ├── market_signals.csv
│       ├── economic_signals.csv
│       ├── climate_signals.csv
│       └── social_signals.csv
│
├── src/                        # Source code
│   ├── __init__.py
│   │
│   ├── data/                   # Data collection modules
│   │   ├── sports.py           # FBref, Elo, historical results
│   │   ├── markets.py          # Polymarket, Kalshi
│   │   ├── economics.py        # FRED, Alpha Vantage, World Bank
│   │   ├── climate.py          # Open-Meteo, NOAA
│   │   └── social.py           # Google Trends, Reddit
│   │
│   ├── features/               # Feature engineering
│   │   ├── sports_features.py
│   │   ├── market_features.py
│   │   ├── economic_features.py
│   │   ├── climate_features.py
│   │   ├── social_features.py
│   │   └── fusion.py           # Signal fusion & weighting
│   │
│   ├── models/                 # ML models
│   │   ├── poisson.py          # Dixon-Coles Poisson model
│   │   ├── xgboost_model.py    # XGBoost ensemble
│   │   ├── monte_carlo.py      # Tournament simulation
│   │   └── calibration.py      # Probability calibration
│   │
│   ├── api/                    # REST API
│   │   ├── main.py             # FastAPI app
│   │   ├── routes.py           # Endpoint definitions
│   │   └── schemas.py          # Request/response models
│
├── notebooks/                  # Zerve notebooks (analysis)
│   ├── 01_sports_eda.ipynb
│   ├── 02_market_analysis.ipynb
│   ├── 03_economic_signals.ipynb
│   ├── 04_climate_analysis.ipynb
│   ├── 05_social_trends.ipynb
│   ├── 06_model_training.ipynb
│   ├── 07_signal_fusion.ipynb
│   └── 08_tournament_simulation.ipynb
│
├── models/                     # Saved model artifacts
│   ├── poisson_model.pkl
│   ├── xgboost_model.pkl
│   └── signal_weights.json
│
└── tests/                      # Unit tests
    ├── test_poisson.py
    ├── test_features.py
    └── test_api.py
```

---

## 6. Running Locally

### Step 1: Collect all data

```bash
python src/data/sports.py       # ~2 min, pulls FBref + historical results
python src/data/markets.py      # ~30 sec, pulls Polymarket + Kalshi
python src/data/economics.py    # ~1 min, pulls FRED + Alpha Vantage
python src/data/climate.py      # ~1 min, pulls Open-Meteo forecasts
python src/data/social.py       # ~3 min, pulls Google Trends + Reddit
```

### Step 2: Run pipeline

```bash
# Or run everything at once:
python pipeline.py --all

# Or individual phases:
python pipeline.py --phase sports
python pipeline.py --phase signals
python pipeline.py --phase model
python pipeline.py --phase simulate
```

### Step 3: Launch local API

```bash
uvicorn src.api.main:app --reload --port 8000

# Test it:
curl "http://localhost:8000/predict?team1=Brazil&team2=Germany"
```

---

## 7. Deploying to Zerve

### Step 1: Upload project to Zerve

1. Log in to zerve.ai with your Antigravity Pro account
2. Create a new project: **"ORACLE-26"**
3. Upload the `src/` directory and `notebooks/` directory
4. Upload `requirements.txt`

### Step 2: Set environment variables in Zerve

In your Zerve project settings, add all keys from your `.env` file.

### Step 3: Run notebooks in order

Run notebooks `01` through `08` in sequence inside Zerve. Each notebook saves its outputs for the next one to pick up.

### Step 4: Deploy the API

1. In Zerve, navigate to your API deployment section
2. Point it to `src/api/main.py`
3. Click **Deploy**
4. Copy the public endpoint URL → add to README as `ZERVE_API_ENDPOINT`

### Step 5: Deploy the Frontend

1. Go to Vercel (or similar)
2. Connect your repo
3. Set `VITE_API_URL` to your Zerve/Render API endpoint
4. Deploy

### Step 6: Verify everything is live

```bash
# Test live API
curl "https://YOUR_ZERVE_ENDPOINT/predict?team1=Argentina&team2=France"

# Should return full JSON response with signal breakdown
```

---

## 8. Data Refresh Schedule

Once deployed, ORACLE-26 refreshes data on this schedule:

| Signal              | Refresh Frequency | Trigger   |
| ------------------- | ----------------- | --------- |
| Sports (Elo/form)   | Every 48 hours    | Scheduled |
| Market odds         | Every 6 hours     | Scheduled |
| Economic indicators | Weekly            | Scheduled |
| Weather forecasts   | Every 24 hours    | Scheduled |
| Google Trends       | Every 24 hours    | Scheduled |
| Reddit sentiment    | Every 12 hours    | Scheduled |

---

## 9. Troubleshooting

### `soccerdata` rate limit / blocked by FBref

```python
# Add delay between requests
import time
time.sleep(5)  # 5 seconds between requests
```

### Google Trends returns empty data

```python
# Use longer timeframe and add retry
from pytrends.exceptions import TooManyRequestsError
import time
try:
    pytrends.build_payload(kw_list=['Brazil'], timeframe='today 3-m')
except TooManyRequestsError:
    time.sleep(60)  # Wait 1 minute
    pytrends.build_payload(kw_list=['Brazil'], timeframe='today 3-m')
```

### FRED API key not found

```bash
# Make sure .env is loaded
from dotenv import load_dotenv
load_dotenv()
import os
print(os.getenv("FRED_API_KEY"))  # Should not be None
```

### Open-Meteo returns no forecast for June dates

```python
# Use historical climate averages instead
# Open-Meteo's /climate endpoint works for historical normals
url = "https://climate-api.open-meteo.com/v1/climate"
```

### Zerve deployment timeout

- Ensure model training runs are cached/saved as `.pkl` files
- On Zerve, load the model from file rather than retraining on each request

---

## 10. Contributing

This is a hackathon project. For now:

1. Create a feature branch: `git checkout -b feature/climate-signal`
2. Make your changes
3. Test locally
4. Push and open a PR

---

## Support

Running into issues? Open a GitHub issue or reach out via the ZerveHack Discord.

---

_ORACLE-26 — Built in 5 days. Powered by 5 signals. For the biggest tournament on Earth._
