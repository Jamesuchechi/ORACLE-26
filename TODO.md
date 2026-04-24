# ◈ CONFLUX — Gap Analysis & Updated Roadmap
> Last updated: April 2026 | Priority: CRITICAL → HIGH → MEDIUM → LOW

---

## 🔴 CRITICAL — Breaks the App

### C1. Missing Constant: `ALL_TEAMS` vs `ALL_WC_TEAMS`
- **Files affected:** `src/api/routes.py`, `src/models/train.py`, `src/features/sports_features.py`
- **Problem:** `from src.constants import ALL_TEAMS` fails — only `ALL_WC_TEAMS` exists
- **Fix:** Add alias `ALL_TEAMS = ALL_WC_TEAMS` in `src/constants.py` OR rename all imports
- [x] Add `ALL_TEAMS = ALL_WC_TEAMS` to `src/constants.py`

### C2. Missing Constant: `TEAM_TO_RESULTS_NAME`
- **Files affected:** `src/features/sports_features.py` (used in 6+ places)
- **Problem:** `from src.constants import TEAM_TO_RESULTS_NAME` — not defined anywhere
- **Fix:** Add mapping dict to `src/constants.py` (team display name → FBref/results CSV name)
- [ ] Define `TEAM_TO_RESULTS_NAME` in `src/constants.py`

### C3. Two Competing FastAPI Apps
- **Files:** `api.py` (root) vs `src/api/main.py`
- **Problem:** Frontend vite proxy targets port 8000. Which app runs? Routes differ.
  - Root `api.py` has `/v1/predict/wc2026/rankings` ✓
  - `src/api/main.py` has `/predict` (different schema) ✓
  - Frontend calls `/v1/predict/climate/venues` — only in root `api.py`
- **Fix:** Consolidate into single app. Root `api.py` is the correct one. Delete or archive `src/api/`.
- [ ] Delete `src/api/routes.py`, `src/api/schemas.py`, `src/api/main.py`
- [ ] Update `BACKEND.md` to reflect single entry point: `python api.py`

### C4. `bootstrap_signals.py` — `random_variation` Called Before Definition
- **File:** `src/data/bootstrap_signals.py` line ~85
- **Problem:** `random_variation(team)` called in main `bootstrap()` function but defined below it
- **Fix:** Move `random_variation` function above `bootstrap()` 
- [ ] Reorder function definitions in `bootstrap_signals.py`

### C5. `SportsDataCollector` Import Does Not Exist
- **File:** `src/models/train.py`
- **Problem:** `from src.data.sports import SportsDataCollector` — class is named `SportsSignalEngine`
- **Fix:** Update import to `from src.data.sports import SportsSignalEngine as SportsDataCollector`
- [ ] Fix import in `train.py`

### C6. Frontend `SignalRadar` Data Shape Mismatch
- **File:** `frontend/src/components/SignalRadar.jsx`
- **Problem:** Expects `data.sports`, `data.markets` etc. directly. API returns:
  ```json
  { "signal_breakdown": { "sports": 0.8, ... } }
  ```
  But rankings endpoint returns flat: `{ "sports": 0.8, "markets": 0.7, ... }`
  TeamDetail fetches squad — squad has no `signal_breakdown` key at all.
- **Fix:** Normalize shape in `useIntelligence.js` hook; ensure `team.signal_breakdown` is always populated
- [ ] In `useIntelligence.js`, after fetching rankings, map each team to add `signal_breakdown: { sports, markets, finance, climate, social }`

---

## 🟠 HIGH — Incorrect Logic / Misleading Output

### H1. Climate Signal Hardcoded in WC2026 Pipeline
- **File:** `wc2026_pipeline.py` line ~118
- **Problem:** `climate = 0.75` — every team gets identical climate signal. 
  Climate IS computed per venue, but never mapped to teams based on their group's venue.
- **Fix:** Map each team's group to their likely venues, average venue climate signals
- [ ] Create `team_to_venue_climate()` helper in pipeline using `WC2026_GROUPS` + `WC2026_VENUES`
- [ ] Replace hardcoded `0.75` with computed per-team climate resilience

### H2. `fuse_match` Draw Probability Can Go Negative
- **File:** `src/features/fusion.py` `fuse_match()` method
- **Problem:** 
  ```python
  raw_loss = sports_draw_prob - adjustment  # This is DRAW, not loss — naming bug
  raw_draw = 1 - raw_win - max(0, raw_loss)  # Can be negative
  ```
  Variable naming is wrong: `raw_loss` is assigned `sports_draw_prob - adjustment` which makes no sense.
- **Fix:** Rewrite probability adjustment logic clearly:
  ```python
  base_win = sports_win_prob
  base_draw = sports_draw_prob  
  base_loss = 1 - base_win - base_draw
  # Apply delta adjustment to win/loss symmetrically, preserve draw
  win_p = np.clip(base_win + adjustment, 0.02, 0.95)
  loss_p = np.clip(base_loss - adjustment, 0.02, 0.95)
  draw_p = np.clip(1 - win_p - loss_p, 0.05, 0.40)
  ```
- [ ] Rewrite `fuse_match` probability adjustment in `fusion.py`

### H3. Alpha Detection Compares Incompatible Scales
- **File:** `api.py` `/v1/alpha/opportunities` and `wc2026_pipeline.py`
- **Problem:** `alpha_gap = conflux_score - markets` 
  - `conflux_score` is a weighted composite across 5 domains [0,1]
  - `markets` is a single domain signal, normalized differently
  - Comparing them directly is mathematically wrong
- **Fix:** Alpha should compare market-implied win probability vs sports-model win probability
  ```python
  # True alpha: what does Polymarket say vs what does our Poisson model say
  df["alpha_gap"] = df["market_signal_raw"] - df["sports_signal"]
  ```
- [ ] Redefine alpha computation to use raw market probability vs sports model probability

### H4. `SquadEngine` `generate_squad` Has Duplicate `return` Statement
- **File:** `src/data/squads.py` end of `generate_squad()`
- **Problem:** Two `return sorted(squad, ...)` statements — dead code after first return
- [ ] Remove duplicate return statement

### H5. Market Signals Fall Back to Synthetic for All 48 Teams
- **File:** `src/data/markets.py` `scan_wc_markets()`
- **Problem:** Polymarket slug format `fifa-world-cup-2026-winner-{team-name}` almost certainly returns no data for most teams. Falls back to `_fallback_market_prob()` silently.
- **Fix:** Add explicit logging of how many teams got real vs synthetic data. Add Metaculus as additional source.
- [ ] Log real vs synthetic signal count in `scan_wc_markets()`
- [ ] Add Metaculus API fallback for WC2026 team probabilities

### H6. Google Trends Rate Limiting — Silent Failures
- **File:** `src/data/social.py`
- **Problem:** `fetch_team_trends()` processes 48 teams in batches of 5, sleeping 2s between. Trends API will block after ~10 requests. Falls to synthetic silently.
- **Fix:** Implement proper exponential backoff + cache results to avoid re-fetching
- [ ] Add exponential backoff in `fetch_trends_batch()`
- [ ] Cache results to `data/raw/trends_cache.json` with 24h TTL

---

## 🟡 MEDIUM — Missing Features / Incomplete Verticals

### M1. `zerve_analyst` Cannot Handle Cross-Domain Queries
- **File:** `src/features/analyst.py`
- **Problem:** TODO.md Phase 4 item: "Handle cross-domain queries (e.g., 'How does US inflation affect WC2026 venue logistics?')" — not implemented. Currently just dumps `context_data` as JSON to LLM without structured cross-domain reasoning.
- **Fix:** Add structured context builder that pulls from all 4 verticals before calling LLM
  ```python
  def build_cross_domain_context(self, query: str) -> dict:
      # Detect query intent (WC / market / climate / cultural)
      # Pull relevant signals from each CSV
      # Return structured context with cross-domain links
  ```
- [ ] Implement `build_cross_domain_context()` in `analyst.py`
- [ ] Update `/v1/analyst/chat` to use cross-domain context

### M2. MatchPredictor Venue Climate Not Used in Prediction
- **File:** `frontend/src/components/MatchPredictor.jsx` + `api.py` `/v1/predict/wc2026/match`
- **Problem:** Venue is selected in UI and passed to API. API adds `venue_context` to response but the climate signal in the prediction is the team's generic climate score, not the venue-specific one.
- **Fix:** In `predict_match` endpoint, look up venue climate from `venue_climate_signals.csv` and apply altitude/heat penalty to both teams' climate scores before fusion
- [ ] Fetch venue climate data in match prediction endpoint
- [ ] Apply venue-specific climate penalty to team signals

### M3. Zerve Notebooks — Not Created
- **TODO Phase 4:** "Finalize the public Zerve project with executable analysis blocks"
- **Problem:** No notebooks exist. The `notebooks/` directory structure is planned but empty.
- **Fix:** Create 4 key notebooks mirroring the pipeline phases
- [ ] `01_sports_signal.ipynb` — Elo, form, Dixon-Coles fitting
- [ ] `02_market_calibration.ipynb` — Alpha detection walkthrough  
- [ ] `03_climate_risk.ipynb` — Venue heat/altitude analysis
- [ ] `04_signal_fusion.ipynb` — Full CONFLUX fusion + rankings

### M4. API Not Secured / No Rate Limiting
- **TODO Phase 4:** "Secure and document all endpoints for external consumption"
- **Problem:** All endpoints are fully open, no API key, no rate limiting
- **Fix:** Add simple API key header check + slowapi rate limiter
- [ ] Add `X-API-Key` header validation middleware
- [ ] Add `slowapi` rate limiting (100 req/min per IP)
- [ ] Add OpenAPI tag descriptions to all endpoints

### M5. Finance View Crashes When FRED Key Missing
- **File:** `frontend/src/views/Finance.jsx` + `src/data/economics.py`
- **Problem:** Finance view fetches `/v1/finance/dashboard`. If `data/raw/economic_signals.csv` doesn't exist AND FRED key is missing, the `build_all_signals()` call silently uses tier-based estimates but `gdp_growth` field may be None, causing pandas errors.
- [ ] Add null-safe fallback in `EconomicSignalEngine.score_nation()` 
- [ ] Add error boundary in `Finance.jsx`

### M6. Social View: `momentum` Field Missing from API Response
- **File:** `frontend/src/views/Social.jsx`
- **Problem:** Renders `t.momentum` but `cultural_moment_signals.csv` has `momentum_score` not `momentum`
  ```jsx
  momentum: `+${(t.momentum * 100).toFixed(0)}%`  // t.momentum is undefined
  ```
- [ ] Fix field name: `t.momentum_score` in `Social.jsx`
- [ ] Also fix: `t.tipping_point` → `t.is_tipping`

### M7. TeamDetail Squad Valuation Display Bug
- **File:** `frontend/src/views/TeamDetail.jsx`  
- **Problem:** `€${(squadData?.total_valuation / 1000000).toFixed(0)}M` — if `total_valuation` is 0 or undefined, shows `NaN M`
- [ ] Add null guard: `squadData?.total_valuation ? `€${...}M` : 'N/A'`

---

## 🔵 LOW — Polish / Enhancement

### L1. Countdown is Wrong
- **File:** `frontend/src/App.jsx` line ~192
- **Problem:** Shows `782 DAYS` hardcoded. World Cup starts June 11, 2026 — from April 2026 that's ~48 days.
- [ ] Replace hardcoded `782` with dynamic calculation: `Math.ceil((new Date('2026-06-11') - new Date()) / 86400000)`

### L2. `terminal.html` Standalone vs React App Inconsistency  
- **Problem:** `terminal.html` is a beautiful standalone HTML terminal with hardcoded data. The React app in `frontend/` is the live version but has different data/styling. Submitters might be confused which to demo.
- [ ] Add comment to `terminal.html`: "Static demo — see frontend/ for live version"
- [ ] Or: Use `terminal.html` as the Zerve-deployed static app and React as local dev

### L3. Flag API for Scotland Returns Wrong Code
- **File:** `frontend/src/utils/flags.js`
- **Problem:** `'Scotland': 'gb-sct'` — `flagcdn.com` uses `gb-sct` but many flag APIs don't support subdivision codes
- [ ] Test and fix Scotland, Bosnia flag codes

### L4. `BACKEND.md` Refers to `wc2026_pipeline.py --all` but File is Named That — OK
- Actually fine. But `BACKEND.md` says "outputs saved to `data/processed/conflux_*.csv`" — the actual output files are named differently than documented.
- [ ] Update `BACKEND.md` output file list to match actual filenames

### L5. No Loading State for Heavy API Calls
- **Files:** Multiple views
- **Problem:** Climate, Finance, Social views show "Scanning..." text but if API is down, they hang forever — no timeout or error state.
- [ ] Add `AbortController` with 10s timeout to all `fetch()` calls in views
- [ ] Add error UI state to all views

---

## 📋 PHASE 4 COMPLETION CHECKLIST (from original TODO)

### Phase 4: Zerve Integration & Deployment
- [ ] **C1–C6** above must be fixed first (app must run cleanly)
- [ ] **Autonomous Reasoning**: Implement `build_cross_domain_context()` (see M1)
- [ ] **API Production**: 
  - [ ] Fix route conflicts (C3)
  - [ ] Add auth + rate limiting (M4)
  - [ ] Write API documentation in `API_DOCS.md`
- [ ] **Zerve Notebooks**: Create 4 notebooks (M3)
- [ ] **Deploy to Zerve**:
  - [ ] Run `wc2026_pipeline.py --all` successfully (requires C1–C6 fixed)
  - [ ] Start `api.py` and verify all endpoints return data
  - [ ] Publish Zerve project URL
  - [ ] Deploy frontend (Vercel/Netlify or Zerve App)

---

## 🗂 File Health Summary

| File | Status | Issue |
|------|--------|-------|
| `src/constants.py` | 🔴 Broken | Missing `ALL_TEAMS`, `TEAM_TO_RESULTS_NAME` |
| `api.py` | 🟡 Partial | Climate signal hardcoded; alpha logic wrong |
| `src/features/fusion.py` | 🟠 Bug | `fuse_match` probability math wrong |
| `src/data/bootstrap_signals.py` | 🔴 Broken | Function called before definition |
| `src/models/train.py` | 🔴 Broken | Wrong class import |
| `src/api/` (whole dir) | 🔴 Conflict | Duplicate app, wrong imports |
| `src/data/squads.py` | 🟡 Minor | Duplicate return statement |
| `frontend/src/hooks/useIntelligence.js` | 🟠 Bug | Missing `signal_breakdown` mapping |
| `frontend/src/views/Social.jsx` | 🟠 Bug | Wrong field names |
| `frontend/src/views/TeamDetail.jsx` | 🟡 Minor | Null guard missing |
| `frontend/src/App.jsx` | 🟡 Minor | Hardcoded countdown |
| `wc2026_pipeline.py` | 🟠 Bug | Hardcoded climate `0.75` |

---

*CONFLUX Intelligence Engine · Gap Analysis v2 · April 2026*