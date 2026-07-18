import streamlit as st
from streamlit_autorefresh import st_autorefresh

from main import run_engine
from data import get_market_data
from ai import analyze_trade

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="SEKWAILA OMEGA X",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Auto refresh every 60 seconds
st_autorefresh(interval=60000, key="refresh")

# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""
<style>

.stApp{
    background-color:#0b1220;
    color:white;
}

.main-title{
    font-size:40px;
    font-weight:bold;
    text-align:center;
    color:#00E5A8;
}

.subtitle{
    text-align:center;
    color:#AAAAAA;
    font-size:18px;
}

.block{
    background:#111827;
    padding:15px;
    border-radius:12px;
    border:1px solid #222;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# HEADER
# =====================================

st.markdown(
    "<div class='main-title'>SEKWAILA OMEGA X</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Institutional AI Trading Dashboard</div>",
    unsafe_allow_html=True
)

st.divider()

# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("Trading Settings")

symbol = st.sidebar.selectbox(

    "Instrument",

    [

        "XAUUSD",

        "US30",

        "SP500",

        "BTCUSD",

        "EURUSD",

        "USDJPY"

    ]

)

timeframe = st.sidebar.selectbox(

    "Timeframe",

    [

        "5m",

        "15m",

        "30m",

        "1h",

        "4h",

        "1d"

    ]

)

risk_percent = st.sidebar.slider(

    "Risk (%)",

    1,

    10,

    2

)

st.sidebar.success("System Online")
