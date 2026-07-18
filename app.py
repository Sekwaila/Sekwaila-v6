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
# =====================================
# PART 3 - CHART & SMC ANALYSIS
# =====================================

import plotly.graph_objects as go
from indicators import calculate_indicators

# Calculate indicators for chart
df = calculate_indicators(df)

st.divider()

st.subheader("📈 Live Market Chart")

fig = go.Figure()

# Candlestick
fig.add_trace(
    go.Candlestick(
        x=df["datetime"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price"
    )
)

# EMA 20
fig.add_trace(
    go.Scatter(
        x=df["datetime"],
        y=df["ema20"],
        mode="lines",
        name="EMA 20"
    )
)

# EMA 50
fig.add_trace(
    go.Scatter(
        x=df["datetime"],
        y=df["ema50"],
        mode="lines",
        name="EMA 50"
    )
)

# EMA 200
fig.add_trace(
    go.Scatter(
        x=df["datetime"],
        y=df["ema200"],
        mode="lines",
        name="EMA 200"
    )
)

fig.update_layout(
    template="plotly_dark",
    height=650,
    xaxis_rangeslider_visible=False,
    margin=dict(l=5, r=5, t=5, b=5),
    legend=dict(orientation="h")
)

st.plotly_chart(fig, use_container_width=True)

# =====================================
# SMART MONEY CONCEPTS
# =====================================

st.divider()

st.subheader("🧠 Smart Money Concepts")

smc = analysis["smc"]

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Break of Structure", smc["bos"])

with c2:
    st.metric("CHoCH", smc["choch"])

with c3:
    st.metric("Liquidity", smc["liquidity"])

c4, c5 = st.columns(2)

with c4:
    st.metric("Premium / Discount", smc["zone"])

with c5:

    if smc["fvg"]:
        st.success("Fair Value Gap Detected")
    else:
        st.info("No Fair Value Gap")

st.subheader("Order Block")

if smc["order_block"]:

    st.json(smc["order_block"])

else:

    st.info("No Order Block Found")

st.subheader("Market Summary")

st.write(f"**Signal:** {analysis['signal']}")

st.write(f"**Confidence:** {analysis['confidence']}%")

st.write(f"**Buy Score:** {analysis['buy_score']}")

st.write(f"**Sell Score:** {analysis['sell_score']}")
# =====================================
# PART 4 - SIGNAL PANEL & FOOTER
# =====================================

st.divider()

st.subheader("🚦 Trading Signal")

signal = analysis["signal"]

if signal == "STRONG BUY":
    st.success("🟢 STRONG BUY")

elif signal == "BUY":
    st.success("🟢 BUY")

elif signal == "STRONG SELL":
    st.error("🔴 STRONG SELL")

elif signal == "SELL":
    st.error("🔴 SELL")

else:
    st.warning("🟡 NO TRADE")

# =====================================
# AI CONFIDENCE
# =====================================

st.subheader("🤖 AI Confidence")

confidence = analysis["confidence"]

st.progress(confidence / 100)

st.write(f"Confidence Score: **{confidence}%**")

# =====================================
# TRADE LEVELS
# =====================================

st.subheader("🎯 Trade Levels")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Entry", analysis["entry"])

with col2:
    st.metric("Stop Loss", analysis["stop_loss"])

with col3:
    st.metric("Take Profit", analysis["take_profit"])

# =====================================
# AI REASONS
# =====================================

st.subheader("📝 AI Reasons")

for reason in analysis["reasons"]:
    st.write(f"✅ {reason}")

# =====================================
# REFRESH
# =====================================

st.divider()

if st.button("🔄 Refresh Analysis"):
    st.rerun()

# =====================================
# FOOTER
# =====================================

st.divider()

st.caption("SEKWAILA OMEGA X")
st.caption("Institutional AI Trading Dashboard")
st.caption("Version 2.0")
