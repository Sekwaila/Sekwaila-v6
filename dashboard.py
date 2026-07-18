"""
=========================================
SEKWAILA OMEGA X
Dashboard Module
Version: 1.0
=========================================
"""

import streamlit as st


def header():

    st.title("🚀 SEKWAILA OMEGA X")

    st.caption("Institutional AI Trading Dashboard")


def market_summary(symbol, timeframe, signal):

    st.subheader("📊 Market Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Instrument", symbol)

    col2.metric("Timeframe", timeframe)

    col3.metric("Signal", signal["signal"])


def ai_panel(ai):

    st.subheader("🧠 AI Confidence")

    st.metric("Confidence", f"{ai['confidence']}%")

    st.write("Reasons")

    for reason in ai["reasons"]:
        st.success(reason)


def trade_panel(trade):

    st.subheader("💰 Trade Setup")

    col1, col2, col3 = st.columns(3)

    col1.metric("Entry", trade["Entry"])

    col2.metric("Stop Loss", trade["Stop Loss"])

    col3.metric("Take Profit", trade["Take Profit"])

    st.metric("Risk Reward", f"1:{trade['Risk Reward']}")
