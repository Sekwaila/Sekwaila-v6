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
# =====================================
# LOAD MARKET DATA
# =====================================

try:

    df = get_market_data(
        symbol=symbol,
        timeframe=timeframe
    )

    if df.empty:

        st.error("No market data available.")

        st.stop()

except Exception as e:

    st.error(f"Market Data Error: {e}")

    st.stop()

# =====================================
# AI ANALYSIS
# =====================================

try:

    analysis = analyze_trade(df)

except Exception as e:

    st.error(f"Analysis Error: {e}")

    st.stop()

# =====================================
# PRICE
# =====================================

current_price = round(float(df["close"].iloc[-1]), 2)

# =====================================
# DASHBOARD METRICS
# =====================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Current Price",
    current_price
)

col2.metric(
    "Signal",
    analysis["signal"]
)

col3.metric(
    "Confidence",
    f'{analysis["confidence"]}%'
)

col4.metric(
    "Risk",
    f"{risk_percent}%"
)

st.divider()

# =====================================
# ENTRY / SL / TP
# =====================================

c1, c2, c3 = st.columns(3)

c1.metric(
    "Entry",
    analysis["entry"]
)

c2.metric(
    "Stop Loss",
    analysis["stop_loss"]
)

c3.metric(
    "Take Profit",
    analysis["take_profit"]
)

st.divider()

# =====================================
# AI REASONS
# =====================================

st.subheader("AI Analysis")

for reason in analysis["reasons"]:

    st.success(reason)
