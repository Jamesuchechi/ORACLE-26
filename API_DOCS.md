# ◈ CONFLUX API Documentation
v1.0.0 // April 2026 Live

Universal Multi-Signal Intelligence Engine providing real-time predictive analytics across sports, markets, economics, and climate.

---

## 🔐 Security & Rate Limiting

### Authentication
All requests must include the following header for validation:
- **Header**: `X-API-Key`
- **Development Key**: `conflux_dev_2026`

### Rate Limits
- **Limit**: 100 requests per minute per IP.
- **Exemptions**: `/health`, `/docs`, `/redoc`.

---

## 🌍 Core Endpoints

### I. Sports Vertical (World Cup 2026)

#### `GET /v1/predict/wc2026/rankings`
Returns the current Conflux power rankings for all 48 teams.
- **Parameters**:
    - `w_sports` (float): Weight for sports signal (default 0.40).
    - `w_markets` (float): Weight for market signal (default 0.25).
- **Response**: List of team objects with `conflux_score` and `signal_breakdown`.

#### `GET /v1/predict/wc2026/match`
Simulates a matchup between two teams at a specific venue.
- **Parameters**:
    - `team1` (string): Required.
    - `team2` (string): Required.
    - `venue` (string): Optional. If provided, applies specific climate penalties.

---

### II. Market Calibration

#### `GET /v1/predict/market/alpha`
Surfaces systematic mispricing by comparing internal models to Polymarket/Metaculus odds.

#### `GET /v1/alpha/opportunities`
Surfaces the Top 3 **Value** and **Hype** opportunities across the 2026 World Cup vertical.

---

### III. Climate & Economics

#### `GET /v1/finance/dashboard`
Returns macro-economic stability indicators from FRED (unemployment) and World Bank (GDP/Inflation).

#### `GET /v1/predict/climate/risk`
Regional climate risk assessment (Heat, Humidity, Altitude) for tournament host zones.

---

### IV. Agentic Intelligence

#### `GET /v1/analyst/briefing`
Generates a multi-signal executive briefing using the cross-domain inference engine.

#### `POST /v1/analyst/chat`
**[PUBLIC]** Interactive conversational interface. Accepts `{ "message": "query" }`.

---

## 🛠 Status Codes
- `200 OK`: Request successful.
- `403 Forbidden`: Invalid or missing API Key.
- `429 Too Many Requests`: Rate limit exceeded.
- `500 Internal Error`: Intelligence engine sync failure.

---
*Developed for ZerveHack 2026*
