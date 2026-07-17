import streamlit as st
from datetime import datetime

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Signal Hunter AI",
    page_icon="📈",
    layout="wide"
)

# ---------------------------
# CUSTOM CSS
# ---------------------------
st.markdown("""
<style>
body {
    background-color: #0E1117;
}

.main-title {
    font-size: 38px;
    font-weight: bold;
    color: #FFD700;
}

.card {
    background-color: #1B1F2A;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #333;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.title("⚙️ Signal Hunter AI")

symbol = st.sidebar.selectbox(
    "Trading Pair",
    [
        "EURUSD",
        "GBPUSD",
        "USDJPY",
        "XAUUSD",
        "BTCUSD"
    ]
)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    [
        "M5",
        "M15",
        "H1",
        "H4",
        "D1"
    ]
)

# ---------------------------
# MAIN
# ---------------------------
st.markdown("<div class='main-title'>📈 SIGNAL HUNTER AI</div>", unsafe_allow_html=True)

st.write("Institutional AI Trading Assistant")

st.write("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Selected Pair", symbol)

with col2:
    st.metric("Timeframe", timeframe)

with col3:
    st.metric("Status", "ONLINE")

st.write("---")

st.subheader("Market Analysis")

st.info("AI Engine will appear here in Phase 2.")

st.subheader("Trading Signal")

st.warning("Waiting for analysis...")

st.write("---")

st.caption("Version 1.0 | Railway Deployment")
st.caption(datetime.now().strftime("%d %B %Y %H:%M:%S"))
