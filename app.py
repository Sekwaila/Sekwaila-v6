"""
=========================================
SEKWAILA OMEGA X
Institutional AI Trading Dashboard
Version: 3.0
=========================================
"""

import streamlit as st

from main import run_engine

st.set_page_config(
    page_title="SEKWAILA OMEGA X",
    page_icon="📈",
    layout="wide"
)

st.title("📈 SEKWAILA OMEGA X")
st.caption("Institutional AI Trading Dashboard")

st.divider()

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.header("Market Settings")

symbol = st.sidebar.selectbox(
    "Symbol",
    [
        "XAUUSD",
        "EURUSD",
        "GBPUSD",
        "USDJPY",
        "BTCUSD",
        "US30",
        "SP500",
    ]
)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    [
        "5m",
        "15m",
        "30m",
        "1h",
        "1d",
    ],
    index=1
)

st.sidebar.divider()

run = st.sidebar.button("🚀 Analyze Market")
