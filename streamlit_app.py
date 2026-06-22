import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(page_title="SEKWAILA V7", layout="wide", page_icon="🚀")
st_autorefresh(interval=60000, key="refresh")

st.markdown("""
<style>
.stApp { background: #050510; }
.main-title { text-align:center; font-size:34px; font-weight:900; color:#00ff99; font-family:monospace; }
.glass { background:rgba(20,20,35,0.9); border:1px solid rgba(0,255,153,0.15); padding:15px; border-radius:16px; margin-bottom:12px; }
.buy { background:#002b1a; color:#00ff99; padding:14px; border-radius:14px; text-align:center; font-weight:bold; font-size:22px; border:1px solid #00ff99; }
.sell { background:#2b0000; color:#ff4d6d; padding:14px; border-radius:14px; text-align:center; font-weight:bold; font-size:22px; border:1px solid #ff4d6d; }
.neutral { background:#1a1a2a; color:#888; padding:14px; border-radius:14px; text-align:center; font-weight:bold; font-size:22px; }
.metric { text-align:center; font-size:24px; color:#00ff99; font-weight:bold; }
.small { color:#666; text-align:center; font-size:10px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚀 SEKWAILA V7</div>', unsafe_allow_html=True)

sa_time = datetime.utcnow() + timedelta(hours=2)
hour = sa_time.hour

if hour < 7: session, vol = "ASIAN", "LOW"
elif hour < 13: session, vol = "LONDON", "HIGH"
elif hour < 17: session, vol = "OVERLAP", "EXTREME"
else: session, vol = "NEW YORK", "HIGH"

c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="glass"><div class="small">SA TIME</div><div class="metric">{sa_time.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="glass"><div class="small">SESSION</div><div class="metric">{session}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="glass"><div class="small">VOLATILITY</div><div class="metric">{vol}</div></div>', unsafe_allow_html=True)

symbols = {"XAUUSD":"GC=F","EURUSD":"EURUSD=X","BTCUSD":"BTC-USD","GBPUSD":"GBPUSD=X","USDJPY":"JPY=X","NAS100":"^NDX","US30":"^DJI"}
selected = st.selectbox("Select Pair", list(symbols.keys()))
ticker = symbols[selected]

@st.cache_data(ttl=60)
def load_data(symbol):
    return yf.download(symbol, period="7d", interval="15m", auto_adjust=True, progress=False)

df = load_data(ticker)
if df.empty: st.error("No Data"); st.stop()

close = df["Close"]
price = float(close.iloc[-1])

ema50 = close.ewm(span=50).mean()
ema200 = close.ewm(span=200).mean()

def rsi(data, p=14):
    d = data.diff()
    g = d.where(d > 0, 0)
    l = -d.where(d < 0, 0)
    return 100 - (100 / (1 + (g.rolling(p).mean() / l.rolling(p).mean())))

rsi_val = round(float(rsi(close).iloc[-1]), 2)

def atr(df, p=14):
    tr = pd.concat([df["High"]-df["Low"], abs(df["High"]-df["Close"].shift()), abs(df["Low"]-df["Close"].shift())], axis=1).max(axis=1)
    return tr.rolling(p).mean()

atr_val = float(atr(df).iloc[-1])

if price > ema50.iloc[-1] > ema200.iloc[-1]: trend = "BULLISH"
elif price < ema50.iloc[-1] < ema200.iloc[-1]: trend = "BEARISH"
else: trend = "NEUTRAL"

rh = df["High"].tail(40).max()
rl = df["Low"].tail(40).min()
eq = (rh + rl) / 2
zone = "DISCOUNT" if price < eq else "PREMIUM"

@st.cache_data(ttl=120)
def load_dxy():
    return yf.download("DX-Y.NYB", period="5d", interval="15m", auto_adjust=True, progress=False)

dxy_df = load_dxy()
if not dxy_df.empty:
    dxy_ema = dxy_df["Close"].ewm(span=50).mean()
    dxy_strength = 80 if dxy_df["Close"].iloc[-1] > dxy_ema.iloc[-1] else 20
    dxy_status = "STRONG" if dxy_strength > 70 else "WEAK" if dxy_strength < 30 else "NEUTRAL"
else:
    dxy_strength, dxy_status = 50, "NEUTRAL"

lh = df["High"].tail(10).max()
ll = df["Low"].tail(10).min()
buy_sweep = df["Low"].iloc[-1] < ll and price > ll
sell_sweep = df["High"].iloc[-1] > lh and price < lh

bos_bull = 1 if price > df["High"].shift(1).rolling(5).max().iloc[-1] else 0
bos_bear = 1 if price < df["Low"].shift(1).rolling(5).min().iloc[-1] else 0

bs, ss = 0, 0
if trend == "BULLISH": bs += 3
elif trend == "BEARISH": ss += 3
if zone == "DISCOUNT": bs += 2
else: ss += 2
if rsi_val < 30: bs += 2
elif rsi_val > 70: ss += 2
bs += bos_bull; ss += bos_bear
if buy_sweep: bs += 2
if sell_sweep: ss += 2
if selected in ["XAUUSD","EURUSD","GBPUSD"]:
    if dxy_status == "WEAK": bs += 2
    elif dxy_status == "STRONG": ss += 2
if vol in ["HIGH","EXTREME"]: bs += 1; ss += 1

if bs >= 8: signal = "EXTREME BUY"
elif bs >= 5: signal = "BUY"
elif ss >= 8: signal = "EXTREME SELL"
elif ss >= 5: signal = "SELL"
else: signal = "NO TRADE"

atr_adj = atr_val * 0.5 if selected in ["NAS100","US30"] else atr_val
if "BUY" in signal:
    sl = round(price - atr_adj * 1.2, 2)
    tp1, tp2, tp3 = round(price + atr_adj * 1.5, 2), round(price + atr_adj * 2.5, 2), round(price + atr_adj * 4, 2)
elif "SELL" in signal:
    sl = round(price + atr_adj * 1.2, 2)
    tp1, tp2, tp3 = round(price - atr_adj * 1.5, 2), round(price - atr_adj * 2.5, 2), round(price - atr_adj * 4, 2)
else:
    sl = tp1 = tp2 = tp3 = price

risk_amount = 20
sl_dist = abs(price - sl)
units = risk_amount / sl_dist if sl_dist > 0 else 0
lot_size = round(units / 100, 2) if selected == "XAUUSD" else round(units / 100000, 2)

if "BUY" in signal:
    st.markdown(f'<div class="buy">🔥 {signal}</div>', unsafe_allow_html=True)
elif "SELL" in signal:
    st.markdown(f'<div class="sell">🔥 {signal}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="neutral">⏳ {signal}</div>', unsafe_allow_html=True)

a,b,c = st.columns(3)
a.metric("PRICE", round(price,2))
b.metric("RSI", rsi_val)
c.metric("ATR", round(atr_val,2))

d,e,f = st.columns(3)
d.metric("TREND", trend)
e.metric("ZONE", zone)
f.metric("DXY", dxy_status)

st.markdown("### 🎯 Targets")
x,y,z,w = st.columns(4)
x.metric("TP1", tp1)
y.metric("TP2", tp2)
z.metric("TP3", tp3)
w.metric("SL", sl)

st.markdown("### 💰 Risk")
r1, r2 = st.columns(2)
r1.metric("Lot Size", lot_size)
r2.metric("Risk $", round(risk_amount,2))

fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"))
fig.add_trace(go.Scatter(x=df.index, y=ema50, name="EMA50"))
fig.add_trace(go.Scatter(x=df.index, y=ema200, name="EMA200"))
if "BUY" in signal or "SELL" in signal:
    fig.add_hline(y=price, line_dash="dash", line_color="white")
    fig.add_hline(y=tp1, line_dash="dot", line_color="#66aaff")
    fig.add_hline(y=tp2, line_dash="dot", line_color="#4488dd")
    fig.add_hline(y=tp3, line_dash="dot", line_color="#2266bb")
    fig.add_hline(y=sl, line_dash="dash", line_color="#ff4444")
fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

analysis = []
analysis.append(f"Trend: {trend} | DXY: {dxy_status} | Zone: {zone}")
analysis.append(f"RSI: {rsi_val} | Buy Score: {bs} | Sell Score: {ss}")
if buy_sweep: analysis.append("✅ Buy-side liquidity swept")
if sell_sweep: analysis.append("✅ Sell-side liquidity swept")
st.markdown("### 🤖 AI Analysis")
for item in analysis: st.write("•", item)

st.markdown('<div style="text-align:center;color:#555;padding:20px;font-size:10px;">SEKWAILA V7 • SMART MONEY ENGINE</div>', unsafe_allow_html=True)
