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
# -----------------------------
# RUN ENGINE
# -----------------------------

if run:

    with st.spinner("Analyzing market..."):

        result = run_engine(symbol, timeframe)

    if result is None:

        st.error("No market data available.")

    else:

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Signal",
            result["signal"]
        )

        col2.metric(
            "Confidence",
            f"{result['confidence']}%"
        )

        col3.metric(
            "Entry Price",
            result["entry"]
        )

        st.divider()

        st.subheader("Trade Levels")

        a, b = st.columns(2)

        a.metric(
            "Stop Loss",
            result["stop_loss"]
        )

        b.metric(
            "Take Profit",
            result["take_profit"]
        )

        st.divider()
# -----------------------------
# AI ANALYSIS
# -----------------------------

        st.subheader("AI Decision")

        c1, c2 = st.columns(2)

        c1.metric(
            "Buy Score",
            result["buy_score"]
        )

        c2.metric(
            "Sell Score",
            result["sell_score"]
        )

        st.divider()

        st.subheader("AI Reasons")

        if result["reasons"]:

            for reason in result["reasons"]:
                st.success(reason)

        else:

            st.info("No strong confirmation found.")

        st.divider()

# -----------------------------
# SMART MONEY CONCEPTS
# -----------------------------

        st.subheader("Smart Money Concepts")

        smc = result["smc"]

        x1, x2 = st.columns(2)

        x1.metric(
            "Break of Structure",
            smc["bos"]
        )

        x2.metric(
            "Change of Character",
            smc["choch"]
        )

        y1, y2 = st.columns(2)

        y1.metric(
            "Liquidity",
            smc["liquidity"]
        )

        y2.metric(
            "Premium / Discount",
            smc["zone"]
        )

        st.write("### Order Block")

        st.json(smc["order_block"])

        st.write("### Fair Value Gap")

        st.write("Detected" if smc["fvg"] else "Not Detected")
# =========================================
# FOOTER
# =========================================

st.divider()

st.caption("🚀 SEKWAILA OMEGA X")
st.caption("Institutional AI Trading Dashboard")
st.caption("Version 3.0")
st.caption("Developed by Johnny Sekwaila")

# =========================================
# AUTO REFRESH BUTTON
# =========================================

if st.sidebar.button("🔄 Refresh"):

    st.rerun()
