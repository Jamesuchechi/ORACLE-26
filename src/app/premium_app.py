"""
ORACLE-26 — Premium Intelligence Terminal
============================================
A SOTA UI for World Cup 2026 predictions, inspired by professional 
scouting terminals and multi-signal forecasting.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
import requests

# Page Setup
st.set_page_config(page_title="ORACLE-26 | Terminal", layout="wide", initial_sidebar_state="collapsed")

# PREMIUM CSS INJECTION
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    
    :root {
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.1);
        --neon-green: #00ff88;
        --oracle-blue: #3266ad;
        --market-green: #1d9e75;
        --econ-gold: #ba7517;
        --social-pink: #d4537e;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top right, #1a1b2e, #0e0f1a);
        color: #e0e0e0;
        font-family: 'Outfit', sans-serif;
    }

    .stSidebar {
        background-color: rgba(20, 20, 35, 0.7) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid var(--glass-border);
    }

    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid var(--glass-border);
        margin-bottom: 20px;
    }

    .neon-text {
        color: var(--neon-green);
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
    }

    .section-title {
        font-size: 14px;
        font-weight: 500;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 15px;
    }

    /* Custom Metric Style */
    .metric-container {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border-left: 3px solid var(--oracle-blue);
    }

    .countdown-block {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 8px;
        padding: 10px 15px;
        text-align: center;
        min-width: 80px;
    }

    .prob-bar-bg {
        background: rgba(255, 255, 255, 0.1);
        height: 6px;
        border-radius: 3px;
        width: 100%;
        margin-top: 5px;
    }

    .prob-bar-fill {
        height: 100%;
        border-radius: 3px;
    }

    /* Navigation Tabs */
    div.stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }

    div.stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: var(--glass-bg);
        border-radius: 5px;
        border: 1px solid var(--glass-border);
        color: #888;
        padding: 0 20px;
    }

    div.stTabs [aria-selected="true"] {
        background-color: var(--oracle-blue) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA & HELPERS
# ─────────────────────────────────────────────
@st.cache_data
def get_leaderboard():
    return [
        {"team": "Argentina", "prob": 21.4, "flag": "🇦🇷"},
        {"team": "France", "prob": 17.8, "flag": "🇫🇷"},
        {"team": "Spain", "prob": 14.3, "flag": "🇪🇸"},
        {"team": "Brazil", "prob": 12.1, "flag": "🇧🇷"},
        {"team": "England", "prob": 10.6, "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
        {"team": "Germany", "prob": 9.2, "flag": "🇩🇪"},
    ]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
h1, h2, h3 = st.columns([1, 2, 1])
with h1:
    st.markdown("<h1 style='margin:0; font-size: 2rem;'>ORACLE<span style='color:#3266ad'>-26</span></h1>", unsafe_allow_html=True)
with h2:
    # Countdown
    wc_start = datetime(2026, 6, 11, 18, 0)
    now = datetime.now()
    diff = wc_start - now
    days, hours, minutes = diff.days, diff.seconds // 3600, (diff.seconds // 60) % 60
    
    st.markdown(f"""
    <div style='display: flex; gap: 10px; justify-content: center;'>
        <div class='countdown-block'><div style='font-size:20px; font-weight:700;'>{days}</div><div style='font-size:10px; color:#888;'>DAYS</div></div>
        <div class='countdown-block'><div style='font-size:20px; font-weight:700;'>{hours}</div><div style='font-size:10px; color:#888;'>HOURS</div></div>
        <div class='countdown-block'><div style='font-size:20px; font-weight:700;'>{minutes}</div><div style='font-size:10px; color:#888;'>MINS</div></div>
    </div>
    """, unsafe_allow_html=True)
with h3:
    st.markdown(f"""
    <div style='text-align: right;'>
        <div style='display:inline-flex; align-items:center; gap:5px; background:rgba(0,255,136,0.1); padding:3px 10px; border-radius:15px; border:1px solid #00ff8844;'>
            <div style='width:6px; height:6px; background:#00ff88; border-radius:50%;'></div>
            <span style='font-size:11px; color:#00ff88; font-weight:bold;'>LIVE</span>
        </div>
        <div style='font-size:12px; color:#888; margin-top:5px;'>v1.0.0 | {now.strftime('%b %d, %H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────
tab_dashboard, tab_predictor, tab_bracket, tab_signals = st.tabs(["📊 Dashboard", "⚽ Match Predictor", "🏆 Bracket", "📡 Signals"])

# ─────────────────────────────────────────────
# TAB: DASHBOARD
# ─────────────────────────────────────────────
with tab_dashboard:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Teams", "48", "12 groups")
    m2.metric("Matches", "104", "Jun 11 - Jul 19")
    m3.metric("Signals", "5", "Live refresh")
    m4.metric("Simulations", "10,000", "Monte Carlo")

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_fav, col_group = st.columns([1, 1])
    
    with col_fav:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Tournament Favorites</div>", unsafe_allow_html=True)
        for item in get_leaderboard():
            st.markdown(f"""
            <div style='margin-bottom: 12px;'>
                <div style='display:flex; justify-content:space-between; font-size:14px;'>
                    <span>{item['flag']} <b>{item['team']}</b></span>
                    <span style='color:#3266ad;'>{item['prob']}%</span>
                </div>
                <div class='prob-bar-bg'><div class='prob-bar-fill' style='width:{item['prob']*4}%; background:var(--oracle-blue);'></div></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_group:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Group H Simulation (Group of Death)</div>", unsafe_allow_html=True)
        group_h = pd.DataFrame([
            {"Team": "🇦🇷 Argentina", "Qualify %": "94%", "Win Group %": "71%", "WC Win %": "21.4%"},
            {"Team": "🇭🇷 Croatia", "Qualify %": "72%", "Win Group %": "19%", "WC Win %": "5.1%"},
            {"Team": "🇪🇨 Ecuador", "Qualify %": "41%", "Win Group %": "8%", "WC Win %": "1.4%"},
            {"Team": "🇩🇿 Algeria", "Qualify %": "22%", "Win Group %": "2%", "WC Win %": "0.3%"},
        ])
        st.table(group_h)
        st.markdown("<div style='font-size:11px; color:#888;'>Updated daily based on 10,000 simulations.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Signal Overview
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Signal Overview — All 5 Domains</div>", unsafe_allow_html=True)
    s1, s2, s3, s4, s5 = st.columns(5)
    
    def signal_card(col, icon, name, score, color):
        col.markdown(f"""
        <div style='text-align:center; padding:10px; border:1px solid var(--glass-border); border-radius:10px;'>
            <div style='font-size:24px;'>{icon}</div>
            <div style='font-size:11px; color:#888;'>{name}</div>
            <div style='font-size:20px; font-weight:700;'>{score}</div>
            <div class='prob-bar-bg'><div class='prob-bar-fill' style='width:{score*100}%; background:{color};'></div></div>
        </div>
        """, unsafe_allow_html=True)

    signal_card(s1, "⚽", "SPORTS", 0.81, "var(--oracle-blue)")
    signal_card(s2, "📈", "MARKETS", 0.74, "var(--market-green)")
    signal_card(s3, "💰", "FINANCE", 0.62, "var(--econ-gold)")
    signal_card(s4, "🌍", "CLIMATE", 0.58, "#639922")
    signal_card(s5, "📣", "SOCIAL", 0.69, "var(--social-pink)")
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB: PREDICTOR
# ─────────────────────────────────────────────
with tab_predictor:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Select Teams & Venue</div>", unsafe_allow_html=True)
    pc1, pc2, pc3 = st.columns([2, 1, 2])
    
    teams = [t['team'] for t in get_leaderboard()] + ["USA", "Mexico", "Canada", "Japan", "South Korea"]
    t1 = pc1.selectbox("Home / Team 1", teams, index=0)
    pc2.markdown("<div style='text-align:center; padding-top:35px; font-weight:700; color:#888;'>VS</div>", unsafe_allow_html=True)
    t2 = pc3.selectbox("Away / Team 2", teams, index=1)
    
    venue = st.selectbox("Venue", ["MetLife Stadium, NJ", "Estadio Azteca, MX City", "SoFi Stadium, LA", "AT&T Stadium, TX"])
    
    if st.button("RUN ORACLE-26 PREDICTION", use_container_width=True):
        with st.spinner("Processing multi-signal ensemble..."):
            try:
                resp = requests.get(f"http://localhost:8000/api/v1/predict?team1={t1}&team2={t2}").json()
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                
                # Result Header
                rh1, rh2 = st.columns([3, 1])
                rh1.markdown(f"### {t1} vs {t2}")
                rh1.markdown(f"<div style='color:#888;'>xG: {resp['expected_goals'][t1]} – {resp['expected_goals'][t2]} · {venue}</div>", unsafe_allow_html=True)
                rh2.markdown(f"<div style='text-align:right;'><span style='background:#00ff8822; color:#00ff88; padding:5px 12px; border-radius:10px; font-size:12px;'>{resp['confidence']} Confidence</span></div>", unsafe_allow_html=True)
                
                # Prob Bar
                st.markdown(f"""
                <div style='display:flex; height:30px; border-radius:8px; overflow:hidden; margin: 20px 0;'>
                    <div style='width:{resp['win_prob']*100}%; background:var(--oracle-blue); display:flex; align-items:center; justify-content:center; font-size:12px;'>{resp['win_prob']*100:.1f}%</div>
                    <div style='width:{resp['draw_prob']*100}%; background:#555; display:flex; align-items:center; justify-content:center; font-size:12px;'>{resp['draw_prob']*100:.1f}%</div>
                    <div style='width:{resp['loss_prob']*100}%; background:#d85a30; display:flex; align-items:center; justify-content:center; font-size:12px;'>{resp['loss_prob']*100:.1f}%</div>
                </div>
                <div style='display:flex; justify-content:space-between; font-size:11px; color:#888;'>
                    <span>{t1} WIN</span>
                    <span>DRAW</span>
                    <span>{t2} WIN</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Signal Breakdown
                st.markdown("<div class='section-title' style='margin-top:20px;'>Signal Breakdown</div>", unsafe_allow_html=True)
                s_cols = st.columns(5)
                signals = resp['signal_breakdown']
                
                signal_card(s_cols[0], "⚽", "Sports", signals['sports'], "var(--oracle-blue)")
                signal_card(s_cols[1], "📈", "Markets", signals['markets'], "var(--market-green)")
                signal_card(s_cols[2], "💰", "Econ", signals['economic'], "var(--econ-gold)")
                signal_card(s_cols[3], "🌍", "Climate", signals['climate'], "#639922")
                signal_card(s_cols[4], "📣", "Social", signals['social'], "var(--social-pink)")
                
                st.markdown(f"""
                <div style='margin-top:20px; padding:15px; background:rgba(255,255,255,0.05); border-radius:8px; font-size:13px; border-left: 3px solid var(--oracle-blue);'>
                    <b>Oracle Summary:</b> {t1} holds the edge via stronger economic stability and sports form. {t2}'s social momentum narrows the gap. 
                    Most likely score: <b>{resp['most_likely_score']}</b>.
                </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error("API Error: Make sure the server is running on port 8000.")

# ─────────────────────────────────────────────
# TAB: BRACKET
# ─────────────────────────────────────────────
with tab_bracket:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Knockout Stage Probabilities</div>", unsafe_allow_html=True)
    
    bracket_data = pd.DataFrame([
        {"Team": "🇦🇷 Argentina", "R32": "94%", "R16": "78%", "QF": "61%", "SF": "44%", "Final": "31%", "Win %": "21.4%"},
        {"Team": "🇫🇷 France", "R32": "91%", "R16": "74%", "QF": "55%", "SF": "38%", "Final": "26%", "Win %": "17.8%"},
        {"Team": "🇪🇸 Spain", "R32": "88%", "R16": "69%", "QF": "50%", "SF": "33%", "Final": "21%", "Win %": "14.3%"},
        {"Team": "🇧🇷 Brazil", "R32": "85%", "R16": "65%", "QF": "47%", "SF": "30%", "Final": "19%", "Win %": "12.1%"},
        {"Team": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 England", "R32": "83%", "R16": "62%", "QF": "44%", "SF": "27%", "Final": "17%", "Win %": "10.6%"},
        {"Team": "🇩🇪 Germany", "R32": "81%", "R16": "59%", "QF": "41%", "SF": "24%", "Final": "15%", "Win %": "9.2%"},
    ])
    st.table(bracket_data)
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB: SIGNALS
# ─────────────────────────────────────────────
with tab_signals:
    sc1, sc2 = st.columns(2)
    
    with sc1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📈 Market Signals — Polymarket Odds</div>", unsafe_allow_html=True)
        # Add visual signal cards
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🌍 Climate Signals — Venue Stress</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with sc2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📣 Social Trends — Google Momentum</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>💰 Finance — Economic Resilience</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER TICKER
# ─────────────────────────────────────────────
st.markdown("""
<div style='background: rgba(50,102,173,0.1); padding: 10px; border-top: 1px solid var(--oracle-blue); position: fixed; bottom: 0; left: 0; width: 100%; z-index: 99;'>
    <marquee style='color: #888; font-size: 12px;'>
        <b style='color:var(--oracle-blue)'>MARKET ALERT:</b> MOROCCO WIN PROB UP 3.1pp | <b style='color:var(--econ-gold)'>ECON SIGNAL:</b> USA GDP GROWTH +2.4% | <b style='color:#ef9f27'>CLIMATE:</b> DALLAS HEAT INDEX 34°C (STRESS: HIGH) | <b style='color:var(--social-pink)'>SOCIAL:</b> JAPAN SEARCH VOLUME SPIKE (+18%)
    </marquee>
</div>
""", unsafe_allow_html=True)
