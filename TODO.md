# ◈ ORACLE-26: Universal Intelligence Hub — Project Roadmap

This document tracks the end-to-end development of the ORACLE-26 intelligence terminal for the Zerve Hackathon.

---

## ✅ PHASE 1: Core Signal Engines (COMPLETED)
- [x] **Sports Engine**: Dixon-Coles Poisson + Elo ranking logic.
- [x] **Markets Engine**: Polymarket integration + Market Alpha (Vertical II).
- [x] **Economics Engine**: FRED/World Bank macro stability scoring.
- [x] **Climate Engine**: NOAA/Open-Meteo risk intelligence (Vertical III).
- [x] **Social Engine**: Google Trends + Reddit momentum detection (Vertical IV).

## ✅ PHASE 2: Signal Fusion & Interaction (COMPLETED)
- [x] **Fusion Engine**: Dynamic weighting logic implemented in `src/features/fusion.py`.
- [x] **Interaction Rules**: Economic crisis penalties, Social-Market alpha, Climate-Econ risk escalation.
- [x] **Explainability**: "Key Drivers" reasoning tokens added to fusion results.

## 🔄 PHASE 3: Intelligence Backend (FINALIZING)
- [x] **Dynamic API**: FastAPI endpoints with custom weighting support (`w_sports`, etc.).
- [x] **Alpha Discovery**: `/v1/alpha/opportunities` endpoint to surface market mispricing.
- [x] **Executive Briefing**: `/v1/analyst/briefing` endpoint for summarized intelligence.
- [ ] **Agent Gateway**: Integrate Groq (Llama 3) for real-time natural language analysis.
- [ ] **Background Sync**: Implement simple scheduler to refresh signal CSVs daily.

## ⬜ PHASE 4: React Premium Terminal (THE FRONTEND)
- [ ] **P4.1: Foundation & Shell**
  - [ ] Initialize Vite + React project.
  - [ ] Setup Tailwind CSS + Framer Motion.
  - [ ] Build the "Cinematic Terminal" shell (Scanlines, CRT effects, Sidebar).
- [ ] **P4.2: The Intelligence Hub (Dashboard)**
  - [ ] **Interactive Leaderboard**: Real-time rank changes using Framer Motion.
  - [ ] **What-If Sliders**: Connect UI weights to the dynamic API.
  - [ ] **Signal Breakdown**: Visualize "Key Drivers" for every team.
- [ ] **P4.3: Alpha Radar & Climate Map**
  - [ ] **Alert Feed**: Real-time ticker for "Value" and "Hype" opportunities.
  - [ ] **Venue Stress Map**: Interactive map of WC2026 host cities colored by risk.
- [ ] **P4.4: Conflux Match Predictor**
  - [ ] Detailed comparison view for H2H match simulation.
  - [ ] "Signal Chord" diagram showing domain clashes.

## ⬜ PHASE 5: The Zerve Analyst (AI Agentic UI)
- [ ] **Analyst Command Center**: Sidebar chat interface using Groq.
- [ ] **Actionable Insights**: Agent can trigger UI changes (e.g., "Show me high-risk venues").
- [ ] **Intelligence Reports**: Agent-generated scouting briefs for teams and groups.

## ⬜ PHASE 6: Production & Submission
- [ ] **Optimization**: Bundle React for production.
- [ ] **Documentation**: Finalize README.md and API documentation.
- [ ] **Submission**: Package for ZerveHack 2026 (Project, Video, Summary).

---

### **◈ Project Vision**
*"ORACLE-26 is not a dashboard; it is a multi-modal reasoning engine that uncovers insights where others only see data."*
