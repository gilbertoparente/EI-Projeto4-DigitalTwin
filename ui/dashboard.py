import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="Cyber Digital Twin | IPVC",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }
[data-testid="stSidebarNav"] { display: none !important; }

div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] > div   { gap: 2px; }
div[data-testid="stRadio"] label[data-baseweb="radio"] {
    background: transparent;
    border-radius: 8px;
    padding: 10px 14px;
    width: 100%;
    font-size: 14px;
    font-weight: 500;
    color: #8b949e;
    transition: background .15s, color .15s;
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    background: #161b22;
    color: #e6edf3;
}
div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {
    background: #1f2937;
    color: #58a6ff;
    border-left: 3px solid #58a6ff;
}

.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
.main { background-color: #0d1117; }

[data-testid="stMetric"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 14px 18px;
}
[data-testid="stMetricLabel"] p  { color: #8b949e !important; font-size: 12px !important; }
[data-testid="stMetricValue"]    { color: #e6edf3 !important; }
[data-testid="stMetricDelta"]    { font-size: 12px !important; }

.stButton > button[kind="primary"] {
    background: #238636;
    border: 1px solid #2ea043;
    color: #ffffff;
    border-radius: 8px;
    font-weight: 600;
}
.stButton > button[kind="primary"]:hover { background: #2ea043; }
.stButton > button { border-radius: 8px; }

h1 { color: #e6edf3 !important; font-size: 1.5rem !important; font-weight: 600 !important; }
h2 { color: #e6edf3 !important; font-size: 1.1rem !important; font-weight: 600 !important; }
h3 { color: #c9d1d9 !important; font-size: 1rem  !important; font-weight: 500 !important; }

hr { border-color: #21262d !important; }
[data-testid="stAlert"] { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 .5rem; display:flex; align-items:center; gap:10px;">
      <span style="font-size:22px">🛡️</span>
      <div>
        <div style="font-size:15px; font-weight:700; color:#e6edf3;">CyberTwin</div>
        <div style="font-size:11px; color:#6e7681;">Digital Twin — IPVC</div>
      </div>
    </div>
    <hr style="border-color:#21262d; margin: .5rem 0 1rem;">
    """, unsafe_allow_html=True)

    page = st.radio(
        "nav",
        ["⚗️  Experiments", "📡  Live System", "📊  Analytics", "🕸️  Network", "⚔️  Comparison", "📜  History"],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#21262d; margin:1rem 0 .75rem'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:11px; color:#484f58; padding: 0 4px; line-height:1.7">
      Project IV — Computer Engineering<br>
      Social Engineering Simulation<br>
      IPVC © 2026
    </div>
    """, unsafe_allow_html=True)

if "Experiments" in page:
    from ui.pages import experiments
    experiments.show()
elif "Live System" in page:
    from ui.pages import live_system
    live_system.show()
elif "Analytics" in page:
    from ui.pages import analytics
    analytics.show()
elif "Network" in page:
    from ui.pages import network
    network.show()
elif "Comparison" in page:
    from ui.pages import scenario_comparison
    scenario_comparison.show()
elif "History" in page:
    from ui.pages import history
    history.show()