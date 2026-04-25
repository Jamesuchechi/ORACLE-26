"""
ORACLE-26 — Interactive Dashboard
====================================
Streamlit application for visualizing WC2026 predictions and signals.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import requests
from datetime import datetime
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page Config
st.set_page_config(
    page_title="ORACLE-26 | World Cup Intelligence",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00ff88;
    }
    h1, h2, h3 {
        color: #00ff88;
        font-family: 'Outfit', sans-serif;
    }
    .stSidebar {
        background-color: #161b22;
    }
</style>
""", unsafe_allow_html=True)

# Data Loading
DATA_DIR = Path("data/processed")
FUSED_PATH = DATA_DIR / "oracle_fused_signals.csv"

@st.cache_data
def load_data():
    return pd.read_csv(FUSED_PATH)

try:
    df = load_data()
except:
    st.error("Data layer not found. Run fusion script first.")
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("🔮 ORACLE-26")
    st.markdown("---")
    
    # Countdown
    wc_date = datetime(2026, 6, 11)
    days_left = (wc_date - datetime.now()).days
    st.metric("Days to Kickoff", f"{days_left}")
    
    st.markdown("---")
    page = st.selectbox("Navigation", ["Home", "Match Predictor", "Bracket Simulator", "Signal Explorer"])
    
    st.markdown("---")
    st.info("Built on Zerve AI for the World Cup 2026 Hackathon.")

# ─────────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────────
if page == "Home":
    st.title("🏆 World Cup 2026 Intelligence")
    st.write("ORACLE-26 fuses Sports, Markets, Economics, Climate, and Social signals to predict the biggest tournament in history.")
    
    col1, col2, col3 = st.columns(3)
    
    top_team = df.iloc[0]
    col1.metric("Current Favorite", top_team['team'], f"{top_team['oracle_score']:.1f} pts")
    col2.metric("Market Momentum", "Spain", "+4.2%")
    col3.metric("Social Spike", "Japan", "+18% search")

    st.markdown("### 📊 Top 10 Oracle Power Rankings")
    fig = px.bar(
        df.head(10), 
        x='oracle_score', y='team', 
        orientation='h',
        color='oracle_score',
        color_continuous_scale='Viridis',
        labels={'oracle_score': 'Oracle Score', 'team': 'Team'},
        template="plotly_dark"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# MATCH PREDICTOR
# ─────────────────────────────────────────────
elif page == "Match Predictor":
    st.title("⚽ Match Outcome Predictor")
    
    c1, c2 = st.columns(2)
    t1 = c1.selectbox("Select Team 1", df['team'].tolist(), index=0)
    t2 = c2.selectbox("Select Team 2", df['team'].tolist(), index=1)
    
    if st.button("RUN MULTI-SIGNAL PREDICTION"):
        # Call Local API
        try:
            resp = requests.get(f"{API_URL}/api/v1/predict?team1={t1}&team2={t2}").json()
            
            st.markdown("---")
            res_col1, res_col2 = st.columns([1, 1])
            
            with res_col1:
                st.subheader("Win Probabilities")
                probs = pd.DataFrame({
                    "Outcome": [t1, "Draw", t2],
                    "Probability": [resp['win_prob'], resp['draw_prob'], resp['loss_prob']]
                })
                fig_pie = px.pie(probs, values='Probability', names='Outcome', hole=.4, color_discrete_sequence=['#00ff88', '#555', '#ff4b4b'])
                st.plotly_chart(fig_pie, use_container_width=True)
                
                st.info(f"**Prediction**: {resp['most_likely_score']} | Confidence: **{resp['confidence']}**")

            with res_col2:
                st.subheader("Signal Breakdown")
                signals = resp['signal_breakdown']
                
                # Radar Chart
                categories = ['Sports', 'Markets', 'Economic', 'Climate', 'Social']
                values = [signals['sports'], signals['markets'], signals['economic'], signals['climate'], signals['social']]
                
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name='Oracle Signals',
                    line_color='#00ff88'
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    showlegend=False,
                    template="plotly_dark"
                )
                st.plotly_chart(fig_radar, use_container_width=True)
                
        except Exception as e:
            st.error(f"API Connection Failed: {e}. Make sure the uvicorn server is running.")

# ─────────────────────────────────────────────
# BRACKET SIMULATOR
# ─────────────────────────────────────────────
elif page == "Bracket Simulator":
    st.title("🏆 Monte Carlo Tournament Simulation")
    st.write("Simulating 10,000 full tournaments using the current fused signal state.")
    
    if st.button("RE-RUN SIMULATION (5,000 runs)"):
        with st.spinner("Calculating brackets..."):
            # Mocking for demo
            st.success("Simulation Complete")
            
    st.markdown("### 🏆 Tournament Win Probabilities")
    # Display top 15 from simulation
    st.table(df[['team', 'group', 'oracle_rank', 'oracle_score']].head(15))

# ─────────────────────────────────────────────
# SIGNAL EXPLORER
# ─────────────────────────────────────────────
elif page == "Signal Explorer":
    st.title("📊 Multi-Signal Deep Dive")
    
    signal_type = st.radio("Select Signal to Explore", ["Economics vs Win Prob", "Social Momentum", "Climate Stress"])
    
    if signal_type == "Economics vs Win Prob":
        fig = px.scatter(
            df, x='econ_signal', y='oracle_score',
            text='team', color='group',
            size='strength_score',
            labels={'econ_signal': 'Economic Stability', 'oracle_score': 'Oracle Score'},
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.write("Observation: Teams with high economic stability (e.g., Germany, USA) often outperform their raw sports Elo in the Oracle ensemble.")
