# ◈ CONFLUX — Hackathon Battle Plan
> 47 tasks · Prioritized by judging criteria weight · Your path to $5,000
> 
> **Judging weights:** Analytical Depth 35% · End-to-End Workflow 30% · Storytelling 20% · Creativity 15%

---

## Legend

| Badge | Meaning |
|-------|---------|
| 🔴 CRITICAL | Breaks the demo or costs decisive points — do these first |
| 🟠 HIGH | Significant score impact — do before submission |
| 🔵 MEDIUM | Polish and differentiation — do if time allows |
| 🟢 LOW | Nice to have — only if everything else is done |

---

## Phase 0 — Deploy First (Judges Cannot Run localhost)
> **This is prerequisite for everything. Without a live URL, judges cannot evaluate your project.**

- [x] 🔴 **CRITICAL · 1h · Impact: Decisive** — Add `VITE_API_URL` env var to `vite.config.js` and `useIntelligence.js` — replace all `localhost:8000` hardcodes with `import.meta.env.VITE_API_URL || 'http://localhost:8000'`
  > Without this, your frontend literally cannot work for judges. Do this absolute first.

- [x] 🔴 **CRITICAL · 2h · Impact: Decisive** — Deploy FastAPI backend to Railway or Render — set all env vars in dashboard, verify `/health` returns 200
  > Free tier is fine. Get a public HTTPS URL. Railway takes ~15 minutes from zero.

- [x] 🔴 **CRITICAL · 1h · Impact: Decisive** — Deploy React frontend to Vercel — connect `VITE_API_URL` to your Railway URL in Vercel env settings
  > vercel.com → import repo → add env var → done. Takes 10 minutes once backend is live.

- [x] 🔴 **CRITICAL · 30m · Impact: High** — Run `wc2026_pipeline.py --all` on the server after deploy, verify all CSV outputs exist in `data/processed/`
  > API returns 404 on most endpoints if `processed/` files are missing. Pipeline must run successfully on the server.

- [x] 🟠 **HIGH · 30m · Impact: High** — Enhance `/health` endpoint response to show data freshness timestamp, signal counts, and pipeline last-run time
  > Judges will hit `/health` first. Make it impressive — show it's a live system, not a static demo.

---

## Phase 1 — Fix Broken Logic (Stops Demo From Failing)
> **These are silent failures that will embarrass you during the demo or cost points when judges inspect the code.**

- [x] 🔴 **CRITICAL · 30m · Impact: High** — Fix `fuse_match()` probability math in `src/features/fusion.py` — `draw_p` can go negative; rewrite with `np.clip` on all three, then re-normalize so they sum to exactly 1.0
  > Current code has a `raw_loss` naming bug that corrupts match predictor output silently.

- [x] 🔴 **CRITICAL · 20m · Impact: High** — Fix alpha gap calculation — use `sports` signal vs `market_signal` (same normalized scale), not `conflux_score` vs raw `markets`
  > Current alpha is mathematically invalid — comparing a weighted composite against a raw signal. Judges who check the math will notice.

- [x] 🔴 **CRITICAL · 30m · Impact: Medium** — Add Groq fallback in `analyst.py` — if all LLM providers fail, return a structured template response built directly from `context_data`, never return an empty string or raise an exception
  > Demo dies silently if `GROQ_API_KEY` is missing or rate-limited mid-presentation. Template fallback keeps every endpoint alive.

- [x] 🔴 **CRITICAL · 20m · Impact: Medium** — Fix `Social.jsx` field names: `t.momentum` → `t.momentum_score`, `t.tipping` → `t.is_tipping`
  > Social view renders `NaN%` and `undefined` for every trend row currently.

- [x] 🔴 **CRITICAL · 10m · Impact: Low** — Fix `TeamDetail.jsx` null guard: `squadData?.total_valuation ? \`€${(squadData.total_valuation/1000000).toFixed(0)}M\` : 'N/A'`
  > Shows `NaN M` whenever squad data is missing or zero.

- [x] 🟠 **HIGH · 20m · Impact: Medium** — Add `AbortController` with 10s timeout to all `fetch()` calls in Climate, Finance, and Social views — add visible error UI state with a retry button
  > Views hang forever if the API is slow. During a live demo, a frozen screen is fatal.

- [x] 🟠 **HIGH · 15m · Impact: Low** — Verify countdown in `App.jsx` is using the dynamic `Math.ceil()` calculation, not the hardcoded `782` fallback — should show ~47 days to kickoff
  > 47 days creates real urgency and shows attention to detail. 782 destroys credibility instantly.

- [x] 🟠 **HIGH · 15m · Impact: Medium** — Move `from src.features.analyst import zerve_analyst` to top of `api.py` inside a `try/except`, set `zerve_analyst = None` on failure, check `if zerve_analyst is None` inside routes and return graceful 503 response
  > A missing API key currently throws an unhandled exception on the first request to analyst endpoints, silently killing half your API.

---

## Phase 2 — Analytical Depth (35% of Score — Your Biggest Gap)
> **This is the category that separates winners from participants. Claims need evidence. Evidence needs numbers.**

- [x] 🔴 **CRITICAL · 3h · Impact: Decisive** — Build `backtest_accuracy.py` — run CONFLUX match predictions against actual 2018 + 2022 World Cup results, compute: accuracy vs pure Elo baseline, Brier score, upset detection rate (when underdog won, did CONFLUX diverge from favorite?)
  > The "2.3x upset detection" claim in README has zero supporting evidence. Either prove it with this backtest or remove the claim. Judges will look.

- [x] 🔴 **CRITICAL · 2h · Impact: Decisive** — Add `/v1/model/validation` endpoint — return calibration curve data, accuracy by confidence tier (high/medium/low), sample size, and comparison vs Elo-only baseline
  > Judges want to see if the model actually works, not just that it exists. This endpoint is your proof.

- [x] 🔴 **CRITICAL · 2h · Impact: Decisive** — Get real Polymarket odds for top 10 teams (Argentina, France, Brazil, England, Spain, Germany, Portugal, Netherlands, Morocco, USA) — hardcode as `REAL_MARKET_ODDS` dict in `markets.py` as a verified fallback when API returns no data
  > Even static verified odds are infinitely more credible than synthetic fallback. Judges can cross-check against polymarket.com.

- [x] 🟠 **HIGH · 2h · Impact: High** — Build the divergence evidence story — find the single most compelling team where CONFLUX score differs from real Polymarket odds by 10pp+, run the full analysis, document why (economic signal? social momentum? climate advantage?), surface it as the centrepiece of the analyst briefing
  > One real, defensible divergence example beats 100 synthetic ones. This is your thesis made concrete.

- [x] 🟠 **HIGH · 1h · Impact: High** — Add model confidence calibration output — for predictions where CONFLUX says 70% win probability, calculate actual win rate in historical data, surface as a "reliability score" per confidence tier
  > Calibration is what separates serious forecasting from vibes. This one metric signals genuine analytical rigour.

- [x] 🔵 **MEDIUM · 1h · Impact: Medium** — Replace hardcoded correlation matrix in `src/data/fusion.py` with real computed Pearson correlations between the 5 signals across all 48 teams, update `/v1/fusion/hub` to return these real values
  > The current matrix uses `np.random.random() * 0.05` jitter on hardcoded values. Replace with real signal correlations from your data.

---

## Phase 3 — The Killer Feature (Win the Demo, Win the Prize)
> **These features directly demonstrate your thesis and are the most screenshot-able, share-worthy parts of the project.**

- [x] 🔴 **CRITICAL · 3h · Impact: Decisive** — Build DIVERGENCE ALERT view as the landing section of the dashboard — surface top 5 teams where CONFLUX most disagrees with Polymarket, showing: team name, direction (underpriced/overpriced), magnitude in percentage points, AI one-line explanation, confidence level
  > This IS your thesis made visible. It should be the first thing every judge sees when they open your app.

- [x] 🔴 **CRITICAL · 2h · Impact: Decisive** — Build Group Stage Bracket Simulator — run Monte Carlo for all 12 groups, show advancement probability for each team with progress bars, make each group clickable to show the full standings simulation
  > Highly shareable, visually impressive, demonstrates the full pipeline working end-to-end. This is the kind of thing that gets posted on X.

- [x] 🟠 **HIGH · 2h · Impact: High** — Add "Upset Alert" badge to match predictor — when CONFLUX win probability for the underdog exceeds the market-implied probability by 8pp+, show a highlighted UPSET ALERT with confidence level and which signal is driving the divergence
  > Makes the analytical insight immediately actionable in one click. Judges love things that are both smart and visually clear.

- [x] 🟠 **HIGH · 1h · Impact: High** — Add signal weight sensitivity analysis to match predictor — interactive sliders showing how final win probability shifts as you change each signal's weight — prove that multi-signal beats single-signal
  > This is an interactive proof of your core thesis. It takes 60 seconds to demonstrate and is unforgettable.

- [x] 🟠 **HIGH · 1.5h · Impact: High** — Build `/v1/predict/wc2026/tournament` endpoint — return full bracket simulation results with probability of reaching each round (R32, R16, QF, SF, Final, Win) for all 48 teams
  > Gives judges an API endpoint that is genuinely useful, well-designed, and demonstrates production thinking beyond the minimum.

- [x] 🔵 **MEDIUM · 1h · Impact: Medium** — Add historical WC performance context to team rankings — show average round reached 1990–2022 alongside CONFLUX score — lets judges see whether the model aligns with historical performance or is finding something new
  > Context makes rankings meaningful. Pure numbers without reference points are hard to evaluate.

---

## Phase 4 — UI Polish and Demo Flow
> **First impressions are disproportionately weighted. The dashboard landing page and first 60 seconds of video do most of the work.**

- [x] 🟠 **HIGH · 1h · Impact: High** — Redesign dashboard landing — move DIVERGENCE ALERTS section to the top above the leaderboard table — lead with your unique insight, not a ranked list every competitor has
  > First impression matters more than the depth of the app. Lead with what makes you different.

- [ ] 🟠 **HIGH · 30m · Impact: High** — Add loading skeleton screens to all views — replace "Scanning..." and "Syncing..." text with animated placeholder cards that match the final layout
  > Perceived performance matters enormously during a demo. Skeletons feel dramatically faster than spinner text.

- [ ] 🟠 **HIGH · 45m · Impact: Medium** — Add toast notifications when signals refresh — "Market signal updated · 3 new divergences detected" — pulse the live neural link indicator in the header
  > Makes the system feel alive and dynamic during a demo rather than static.

- [ ] 🔵 **MEDIUM · 30m · Impact: Medium** — Fix all 48 team flag codes in `flags.js` — test Scotland (`gb-sct`), Bosnia (`ba`), New Zealand (`nz`), South Africa (`za`), Ivory Coast (`ci`), DR Congo (`cd`), Uzbekistan (`uz`) — verify every flag loads
  > Broken flags during a live demo look unprofessional and undermine confidence in the data quality.

- [ ] 🔵 **MEDIUM · 30m · Impact: Medium** — Add mobile responsive breakpoints to Dashboard and Leaderboard — the signal fingerprint bars overflow on screens narrower than 768px
  > Judges may open the app on a phone. A broken mobile layout is a bad signal about code quality.

- [ ] 🔵 **MEDIUM · 20m · Impact: Low** — Add "Copy shareable link" button that encodes selected team and weights in URL query params
  > Shareable links = free publicity = Zerve amplification before judging ends.

- [ ] 🟢 **LOW · 15m · Impact: Low** — Add CONFLUX version string and pipeline last-run timestamp to the footer and `/health` response
  > Small production signal that shows you think like a real engineer.

---

## Phase 5 — AI Analyst Upgrade
> **The analyst is a major differentiator. Right now it's a thin wrapper. Make it earn its place.**

- [ ] 🟠 **HIGH · 2h · Impact: High** — Implement `build_cross_domain_context()` properly — detect query intent (WC / market / climate / cultural keywords), pull relevant rows from all 4 vertical CSVs, build structured context with explicit cross-domain links before calling the LLM
  > Currently dumps raw JSON to the LLM with no structure. Structured context produces 5x more insightful responses.

- [ ] 🟠 **HIGH · 1h · Impact: High** — Add 5 pre-built quick-action buttons in the analyst chat UI: "Who will win the World Cup?", "Top 3 upset picks?", "Biggest market mispricing?", "Climate risk briefing", "Cultural moment report"
  > Judges are busy. Quick prompts ensure they see your best AI outputs without having to think of questions.

- [ ] 🔵 **MEDIUM · 1h · Impact: Medium** — Add streaming response support to `/v1/analyst/chat` using FastAPI `StreamingResponse` with Server-Sent Events, update `AnalystChat.jsx` to consume the stream
  > Streaming feels dramatically more impressive than waiting 3 seconds for a wall of text to appear.

- [ ] 🔵 **MEDIUM · 30m · Impact: Medium** — Cache analyst briefing for 30 minutes in memory using a simple dict with timestamp — avoid calling the LLM on every `/v1/analyst/briefing` request during judging
  > Prevents rate limit errors during demo. The briefing content doesn't need to change every request.

- [ ] 🟢 **LOW · 1h · Impact: Medium** — Add conversation memory to analyst chat — pass the last 5 messages as context in each subsequent API call so follow-up questions work naturally
  > Currently each message is completely stateless. Memory makes it feel like a real analyst, not a one-shot query tool.

---

## Phase 6 — Zerve Notebooks and Submission Assets
> **Notebooks are required. The project summary and demo video are the two assets judges spend the most time with.**

- [ ] 🟠 **HIGH · 2h · Impact: High** — Execute all 4 existing notebooks end-to-end in Zerve — fix any import errors, cell ordering issues, or missing file dependencies — every cell must run without errors
  > Zerve notebooks are a required submission component. They must run cleanly or you lose End-to-End Workflow points.

- [ ] 🟠 **HIGH · 1h · Impact: High** — Add rich markdown narrative cells to each notebook — explain the insight above each code block: "Why does economic stability predict football performance?", "What does this divergence tell us?", "What would this mean for a bettor?"
  > Judges read notebooks. Tell the story between the code cells. Analysis without narrative is just code.

- [ ] 🟠 **HIGH · 30m · Impact: High** — Create `05_divergence_analysis.ipynb` — the centrepiece analytical notebook: load real Polymarket odds for top teams, compute CONFLUX vs market divergence, plot calibration curve, highlight the single best value opportunity with full explanation
  > This is the notebook that wins the Analytical Depth score. Make it the best thing in the repo.

- [ ] 🔴 **CRITICAL · 1h · Impact: Decisive** — Write the 300-word project summary — open with a concrete finding, not a technology description. Structure: "We found X → here is the evidence → this is why it matters → here is what we built to surface it"
  > Judges read this first. If it opens with "CONFLUX is a multi-signal intelligence engine" instead of a real finding, you lose the analytical depth category before they even open the app.

- [ ] 🔴 **CRITICAL · 3h · Impact: Decisive** — Record the 3-minute demo video with this exact structure: (0:00-0:15) state the question out loud → (0:15-0:45) show data being collected live → (0:45-1:30) show the divergence alert for your best example team → (1:30-2:15) run match predictor for that team, show upset alert → (2:15-2:45) show AI analyst explaining the cross-domain reasoning → (2:45-3:00) show a live API call from terminal proving production deployment
  > Practice this 3 times before recording. The arc — question, evidence, insight, production — is more compelling than a feature tour. Watch past hackathon winning demos before you record.

---

## Phase 7 — Production Signals and Amplification
> **These details signal to judges that you built something real, not a hackathon prototype.**

- [ ] 🟠 **HIGH · 1h · Impact: High** — Verify `slowapi` rate limiting is installed in `requirements.txt` and actually working on the deployed server — test with `curl` in a loop to confirm 429 responses fire correctly
  > Rate limit errors during judging from judges hammering the API = lost points. The middleware is coded but may not be installed.

- [ ] 🟠 **HIGH · 30m · Impact: High** — Add full OpenAPI documentation — add `description`, `summary`, `response_model`, and example responses to all major endpoints in `api.py` — make `/docs` look impressive
  > Judges will visit `/docs`. A well-documented API signals production engineering. An empty one signals a prototype.

- [ ] 🔵 **MEDIUM · 30m · Impact: Medium** — Set up data refresh on a schedule — re-run `bootstrap_signals.py` every 24h via Railway cron tab or an APScheduler job in `api.py` startup
  > Live data refresh is a production signal. "Data refreshed 3 hours ago" in the dashboard is a credibility multiplier.

- [ ] 🔵 **MEDIUM · 20m · Impact: Medium** — Post on LinkedIn and X immediately after your app is deployed — include the live URL, your single best finding (the divergence number), one screenshot of the divergence alert UI, and tag `@Zerve AI` (LinkedIn) and `@Zerve_AI` (X)
  > Zerve amplifies good submissions. Early posts get more reach before judging ends. Don't wait until the deadline.

- [ ] 🔵 **MEDIUM · 30m · Impact: Medium** — Replace `allow_origins=["*"]` in CORS middleware with your production Vercel URL only
  > Security detail that signals production thinking. Wildcard CORS is a red flag in any production review.

- [ ] 🟢 **LOW · 1h · Impact: Medium** — Write `DEPLOYMENT.md` with clear step-by-step instructions: clone → install → set env vars → run pipeline → start API → start frontend
  > Judges appreciate projects they could actually reproduce and use after the hackathon. This signals long-term thinking.

---

## Quick Reference — The 10 Highest-Impact Tasks

If you are short on time, these 10 tasks have the highest return on effort:

| # | Task | Why |
|---|------|-----|
| 1 | Deploy to Railway + Vercel | Judges need a live URL |
| 2 | Run pipeline on server | Most endpoints 404 without it |
| 3 | Build divergence alert view | Your thesis made visible |
| 4 | Get real Polymarket odds | Credibility for all alpha claims |
| 5 | Build backtest module | Proves the 2.3x claim |
| 6 | Write project summary | Judges read this first |
| 7 | Record demo video | Most-watched submission asset |
| 8 | Fix fuse_match() probability math | Silent crash in match predictor |
| 9 | Build bracket simulator | Shareable, impressive, end-to-end |
| 10 | Execute all Zerve notebooks | Required deliverable |

---

## The One Thing That Wins It

Before anything else, run this in a Python shell against your real data:

```python
import pandas as pd

df = pd.read_csv('data/processed/conflux_wc2026.csv')
df['alpha'] = df['sports'] - df['markets']
df['abs_alpha'] = df['alpha'].abs()

high_div = df[df['abs_alpha'] > 0.10].sort_values('alpha', ascending=False)
print(high_div[['subject','sports','markets','alpha','conflux_score']])
```

Whatever comes out of that — **that is your story**. Find the team with the biggest divergence. That number becomes your project summary opener, your video hook, your LinkedIn post, and the centrepiece of your demo. Everything else in CONFLUX exists to explain why that number is meaningful.

---

*Built for ZerveHack 2026 · CONFLUX Intelligence Engine · We need to win this.*