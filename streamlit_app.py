import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(page_title="SEKWAILA V7", layout="wide")

st.markdown("""
<style>
.stApp { background: #050510; color: white; }
.main-title { text-align:center; font-size:34px; font-weight:bold; color:#00ff99; }
.glass { background:rgba(20,20,35,0.9); border:1px solid #00ff9933; padding:15px; border-radius:16px; margin-bottom:12px; }
.buy { background:#002b1a; color:#00ff99; padding:14px; border-radius:14px; text-align:center; font-weight:bold; font-size:22px; border:1px solid #00ff99; }
.sell { background:#2b0000; color:#ff4d6d; padding:14px; border-radius:14px; text-align:center; font-weight:bold; font-size:22px; border:1px solid #ff4d6d; }
.neutral { background:#1a1a2a; color:#888; padding:14px; border-radius:14px; text-align:center; font-weight:bold; font-size:22px; }
.metric { font-size:20px; font-weight:bold; color:#00ff99; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚀 SEKWAILA V7</div>', unsafe_allow_html=True)

# Time
sa_time = datetime.utcnow() + timedelta(hours=2)
hour = sa_time.hour
session = "ASIAN" if hour < 7 else "LONDON" if hour < 13 else "OVERLAP" if hour < 17 else "NEW YORK"

c1, c2 = st.columns(2)
with c1:
    st.markdown(f'<div class="glass"><div style="color:#666;font-size:10px;">SA TIME</div><div class="metric">{sa_time.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="glass"><div style="color:#666;font-size:10px;">SESSION</div><div class="metric" style="color:#ffcc44;">{session}</div></div>', unsafe_allow_html=True)

# Pairs
pairs = {"XAUUSD":"GC=F","EURUSD":"EURUSD=X","BTCUSD":"BTC-USD","GBPUSD":"GBPUSD=X","USDJPY":"JPY=X"}
selected = st.selectbox("Select Pair", list(pairs.keys()))
ticker = pairs[selected]

@st.cache_data(ttl=60)
def get_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="15m", progress=False)
        return df if not df.empty else None
    except:
        return None

df = get_data(ticker)
if df is None:
    st.error(f"⚠️ No data for {selected}. Please try another pair.")
    st.stop()

# Calculate everything safely
close = df['Close']
price = float(close.iloc[-1])

ema50 = close.ewm(span=50).mean().iloc[-1]
ema200 = close.ewm(span=200).mean().iloc[-1]

# RSI
def calc_rsi(data, period=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

rsi_val = float(calc_rsi(close).iloc[-1])

# ATR
def calc_atr(df, period=14):
    high, low, close = df['High'], df['Low'], df['Close']
    tr = pd.concat([high-low, abs(high-close.shift()), abs(low-close.shift())], axis=1).max(axis=1)
    return float(tr.rolling(period).mean().iloc[-1])

atr_val = calc_atr(df)

# Trend
if price > ema50 > ema200:
    trend = "BULLISH"
elif price < ema50 < ema200:
    trend = "BEARISH"
else:
    trend = "NEUTRAL"

# DXY
@st.cache_data(ttl=120)
def get_dxy():
    try:
        dxy = yf.download("DX-Y.NYB", period="5d", interval="15m", progress=False)
        if dxy.empty:
            return 50
        ema = dxy['Close'].ewm(span=50).mean().iloc[-1]
        return 80 if dxy['Close'].iloc[-1] > ema else 20
    except:
        return 50

dxy_strength = get_dxy()
dxy_status = "STRONG" if dxy_strength > 70 else "WEAK" if dxy_strength < 30 else "NEUTRAL"

# Zone
recent_high = float(df['High'].tail(40).max())
recent_low = float(df['Low'].tail(40).min())
equilibrium = (recent_high + recent_low) / 2
zone = "DISCOUNT" if price < equilibrium else "PREMIUM"

# Liquidity Sweep
last_high = float(df['High'].tail(10).max())
last_low = float(df['Low'].tail(10).min())
buy_sweep = df['Low'].iloc[-1] < last_low and price > last_low
sell_sweep = df['High'].iloc[-1] > last_high and price < last_high

# BOS
bos_bull = 1 if price > float(df['High'].shift(1).rolling(5).max().iloc[-1]) else 0
bos_bear = 1 if price < float(df['Low'].shift(1).rolling(5).min().iloc[-1]) else 0

# Scoring
buy_score, sell_score = 0, 0

if trend == "BULLISH": buy_score += 3
elif trend == "BEARISH": sell_score += 3

if zone == "DISCOUNT": buy_score += 2
else: sell_score += 2

if rsi_val < 30: buy_score += 2
elif rsi_val > 70: sell_score += 2

buy_score += bos_bull
sell_score += bos_bear

if buy_sweep: buy_score += 2
if sell_sweep: sell_score += 2

if selected in ["XAUUSD", "EURUSD", "GBPUSD"]:
    if dxy_status == "WEAK": buy_score += 2
    elif dxy_status == "STRONG": sell_score += 2

# Signal
if buy_score >= 8: signal = "EXTREME BUY"
elif buy_score >= 5: signal = "BUY"
elif sell_score >= 8: signal = "EXTREME SELL"
elif sell_score >= 5: signal = "SELL"
else: signal = "NO TRADE"

# TP/SL
if "BUY" in signal:
    sl = round(price - atr_val * 1.2, 2)
    tp1, tp2, tp3 = round(price + atr_val * 1.5, 2), round(price + atr_val * 2.5, 2), round(price + atr_val * 4.0, 2)
elif "SELL" in signal:
    sl = round(price + atr_val * 1.2, 2)
    tp1, tp2, tp3 = round(price - atr_val * 1.5, 2), round(price - atr_val * 2.5, 2), round(price - atr_val * 4.0, 2)
else:
    sl = tp1 = tp2 = tp3 = price

# Lot Size
risk_amount = 20
sl_dist = abs(price - sl)
units = risk_amount / sl_dist if sl_dist > 0 else 0
lot_size = round(units / 100, 2) if selected == "XAUUSD" else round(units / 100000, 2)

# Display
if "BUY" in signal:
    st.markdown(f'<div class="buy">🔥 {signal}</div>', unsafe_allow_html=True)
elif "SELL" in signal:
    st.markdown(f'<div class="sell">🔥 {signal}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="neutral">⏳ {signal}</div>', unsafe_allow_html=True)

# Metrics
a, b, c = st.columns(3)
a.metric("💰 PRICE", round(price, 2))
b.metric("⚡ RSI", round(rsi_val, 1))
c.metric("📊 ATR", round(atr_val, 2))

d, e, f = st.columns(3)
d.metric("📈 TREND", trend)
e.metric("📍 ZONE", zone)
f.metric("💲 DXY", dxy_status)

# Targets
st.markdown("### 🎯 Targets")
col1, col2, col3, col4 = st.columns(4)
col1.metric("TP1", tp1)
col2.metric("TP2", tp2)
col3.metric("TP3", tp3)
col4.metric("SL", sl)

# Risk
st.markdown("### 💰 Risk")
col1, col2 = st.columns(2)
col1.metric("Lot Size", lot_size)
col2.metric("Risk $", round(risk_amount, 2))

# Chart
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
fig.add_trace(go.Scatter(x=df.index, y=close.ewm(span=50).mean(), name="EMA50"))
fig.add_trace(go.Scatter(x=df.index, y=close.ewm(span=200).mean(), name="EMA200"))

if "BUY" in signal or "SELL" in signal:
    fig.add_hline(y=price, line_dash="dash", line_color="white")
    fig.add_hline(y=tp1, line_dash="dot", line_color="#66aaff")
    fig.add_hline(y=tp2, line_dash="dot", line_color="#4488dd")
    fig.add_hline(y=tp3, line_dash="dot", line_color="#2266bb")
    fig.add_hline(y=sl, line_dash="dash", line_color="#ff4444")

fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# AI Analysis
st.markdown("### 🤖 AI Analysis")
analysis = [
    f"Trend: **{trend}** | DXY: **{dxy_status}** | Zone: **{zone}**",
    f"RSI: **{round(rsi_val,1)}** | Buy Score: **{buy_score}** | Sell Score: **{sell_score}**",
]
if buy_sweep: analysis.append("✅ Buy-side liquidity swept")
if sell_sweep: analysis.append("✅ Sell-side liquidity swept")
analysis.append(f"Entry: **{round(price,2)}** | SL: **{sl}** | Risk: **${round(risk_amount,2)}**")

for item in analysis:
    st.write(f"• {item}")

st.markdown('<div style="text-align:center;color:#555;padding:20px;font-size:10px;">SEKWAILA V7 • SMART MONEY ENGINE</div>', unsafe_allow_html=True)
