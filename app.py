import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import pytz

st.set_page_config(page_title="SEKWAILA OMEGA X", layout="wide")
st_autorefresh(interval=60000, key="refresh")

# ========== STYLING ==========
st.markdown("""
<style>
    .stApp { background: #0a0a0f; color: #e0e0e0; }
    .glass {
        background: rgba(20,20,30,0.55);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,215,0,0.15);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.7);
    }
    .glass-title {
        color: #ffd700;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        border-bottom: 1px solid rgba(255,215,0,0.1);
        padding-bottom: 6px;
        margin-bottom: 10px;
    }
    .buy { background: rgba(0,200,0,0.08); border-left: 4px solid #00ff88; padding: 16px; border-radius: 12px; }
    .sell { background: rgba(255,0,0,0.08); border-left: 4px solid #ff4444; padding: 16px; border-radius: 12px; }
    .wait { background: rgba(255,200,0,0.08); border-left: 4px solid #ffcc00; padding: 16px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ========== SYMBOLS ==========
SYMBOLS = {
    "XAUUSD": "GC=F",
    "BTCUSD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "USDJPY": "JPY=X",
    "NAS100": "^NDX",
    "US30": "^DJI",
    "DXY": "DX-Y.NYB"
}

# ========== DATA LOADER ==========
@st.cache_data(ttl=60)
def load_data(symbol, interval="15m", period="7d"):
    try:
        # multi_level_index=False prevents yfinance multiindex structural leaks entirely
        df = yf.download(symbol, interval=interval, period=period, auto_adjust=True, progress=False, multi_level_index=False)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except Exception:
        return pd.DataFrame()

# ========== INDICATORS ==========
def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()

def rsi(s, n=14):
    delta = s.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(n).mean()
    avg_loss = loss.rolling(n).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def atr(df, n=14):
    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - df["Close"].shift()).abs(),
        (df["Low"] - df["Close"].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(n).mean()

# ========== SMART MONEY ==========
def liquidity_sweeps(df):
    if len(df) < 12:
        return False, False
    high = df["High"]
    low = df["Low"]
    sweep_high = bool(high.iloc[-1] > high.iloc[-12:-1].max())
    sweep_low = bool(low.iloc[-1] < low.iloc[-12:-1].min())
    return sweep_high, sweep_low

def order_blocks(df):
    obs = []
    if len(df) < 5:
        return obs
    for i in range(2, len(df)-1):
        if df['Close'].iloc[i] < df['Open'].iloc[i] and df['Close'].iloc[i+1] > df['Open'].iloc[i+1]:
            obs.append({'type':'bull','high':float(df['High'].iloc[i]),'low':float(df['Low'].iloc[i]),'idx':i})
        elif df['Close'].iloc[i] > df['Open'].iloc[i] and df['Close'].iloc[i+1] < df['Open'].iloc[i+1]:
            obs.append({'type':'bear','high':float(df['High'].iloc[i]),'low':float(df['Low'].iloc[i]),'idx':i})
    return obs[-3:]

def find_fvgs(df):
    fvgs = []
    if len(df) < 5:
        return fvgs
    for i in range(2, len(df)-2):
        if df['Low'].iloc[i] > df['High'].iloc[i+2]:
            fvgs.append({'type':'bullish','start':i,'end':i+2,'top':float(df['Low'].iloc[i]),'bottom':float(df['High'].iloc[i+2])})
        elif df['High'].iloc[i] < df['Low'].iloc[i+2]:
            fvgs.append({'type':'bearish','start':i,'end':i+2,'top':float(df['Low'].iloc[i+2]),'bottom':float(df['High'].iloc[i])})
    return fvgs

# ========== SESSION ==========
def get_session():
    tz = pytz.timezone("Africa/Johannesburg")
    hour = datetime.now(tz).hour
    if 9 <= hour < 12:
        return "LONDON OPEN", 70
    elif 12 <= hour < 16:
        return "LONDON/NY", 95
    elif 16 <= hour < 22:
        return "NEW YORK", 80
    else:
        return "ASIAN", 50

# ========== DXY ==========
def dxy_bias():
    dxy = load_data("DX-Y.NYB", "15m", "5d")
    if dxy.empty or "Close" not in dxy.columns:
        return "NEUTRAL"
    close_val = float(dxy["Close"].iloc[-1])
    ema_val = float(ema(dxy["Close"], 50).iloc[-1])
    return "BULL" if close_val > ema_val else "BEAR"

# ========== ADAPTIVE AI ==========
def adaptive_ai(df):
    if df.empty or len(df) < 30:
        return {"ema": 50, "atr": 14, "risk": 1.0, "rr": 2.0, "confidence": 50, "regime": "RANGING"}
    
    atr_series = atr(df)
    atr_val = float(atr_series.iloc[-1])
    avg_atr = float(atr_series.rolling(30).mean().iloc[-1])
    volatility_ratio = atr_val / avg_atr if avg_atr > 0 else 1
    
    close = df["Close"]
    e50 = ema(close, 50)
    close_val = float(close.iloc[-1])
    e50_val = float(e50.iloc[-1])
    
    trend_strength = abs(close_val - e50_val) / e50_val * 100 if e50_val != 0 else 0
    if trend_strength > 0.5:
        ema_period = 34
        risk_pct = 0.8
        regime = "TRENDING"
    else:
        ema_period = 50
        risk_pct = 1.2
        regime = "RANGING"
        
    atr_period = 18 if volatility_ratio > 1.5 else 14
    rr = 2.5 if trend_strength > 0.5 else 1.8
    confidence = 50 + (volatility_ratio * 10) + (trend_strength * 20)
    confidence = min(95, max(30, confidence))
    return {"ema": ema_period, "atr": atr_period, "risk": risk_pct, "rr": rr, "confidence": confidence, "regime": regime}

# ========== SIGNAL ENGINE ==========
def compute_signal(pair, df, dxy_trend, session_name, df4h=None):
    if df.empty or len(df) < 15:
        return "WAIT", 50, "RANGE", 50
    score = 0
    high = df["High"]
    low = df["Low"]
    structure = "RANGE"
    
    if high.iloc[-1] > high.iloc[-11:-1].max():
        structure = "BULLISH"
        score += 4
    elif low.iloc[-1] < low.iloc[-11:-1].min():
        structure = "BEARISH"
        score -= 4

    if df4h is not None and not df4h.empty and len(df4h) >= 200:
        e50 = ema(df4h["Close"], 50)
        e200 = ema(df4h["Close"], 200)
        if float(e50.iloc[-1]) > float(e200.iloc[-1]):
            score += 3
        else:
            score -= 3

    sweep_high, sweep_low = liquidity_sweeps(df)
    if sweep_low:
        score += 3
    if sweep_high:
        score -= 3

    rsi_series = rsi(df["Close"])
    rsi_val = float(rsi_series.iloc[-1]) if not rsi_series.empty else 50
    if rsi_val < 35:
        score += 2
    elif rsi_val > 65:
        score -= 2

    if pair in ["XAUUSD", "EURUSD"]:
        if dxy_trend == "BEAR":
            score += 2
        else:
            score -= 2

    if session_name == "LONDON/NY":
        score += 2
    elif session_name == "ASIAN":
        score -= 1

    obs = order_blocks(df)
    bull_ob = len([o for o in obs if o['type'] == 'bull'])
    bear_ob = len([o for o in obs if o['type'] == 'bear'])
    if bull_ob > bear_ob:
        score += 1
    elif bear_ob > bull_ob:
        score -= 1

    confidence = min(100, max(0, 50 + score * 5))
    if score >= 6:
        signal = "BUY"
    elif score <= -6:
        signal = "SELL"
    else:
        signal = "WAIT"
    return signal, confidence, structure, rsi_val

# ========== MAIN APP ==========
pair = st.sidebar.selectbox("Pair", list(SYMBOLS.keys()))
risk = st.sidebar.slider("Risk %", 0.5, 5.0, 2.0, 0.5)
account = st.sidebar.number_input("Account Size", value=10000.0)

ticker = SYMBOLS[pair]
df = load_data(ticker, "15m", "7d")
df4h = load_data(ticker, "1h", "30d")

if df.empty or "Close" not in df.columns:
    st.error("Market data unavailable or connection timed out. Retrying...")
    st.stop()

session_name, session_quality = get_session()
dxy_trend = dxy_bias()
signal, confidence, structure, rsi_val = compute_signal(pair, df, dxy_trend, session_name, df4h)
adaptive = adaptive_ai(df)

# Cast variables explicitly to Python floats to clean up multiindex residual data
price = float(df["Close"].iloc[-1])
atr_series = atr(df)
atr_val = float(atr_series.iloc[-1]) if not atr_series.empty else 0.0

if signal == "BUY" and atr_val > 0:
    entry = price
    sl = price - atr_val * 1.5
    tp1 = price + atr_val * 1.5
    tp2 = price + atr_val * 2.5
    tp3 = price + atr_val * 4
elif signal == "SELL" and atr_val > 0:
    entry = price
    sl = price + atr_val * 1.5
    tp1 = price - atr_val * 1.5
    tp2 = price - atr_val * 2.5
    tp3 = price - atr_val * 4
else:
    entry = sl = tp1 = tp2 = tp3 = price

# Defensive handling against potential DivisionByZero errors
risk_amount = account * risk / 100
pip_distance = abs(price - sl) * 10
lot = (risk_amount / pip_distance) if pip_distance > 0 else 0.01

# ========== UI ==========
st.title("🎯 SEKWAILA OMEGA X")
st.caption("Live Market Intelligence")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pair", pair)
col2.metric("Price", f"${price:.2f}")
col3.metric("Session", session_name, f"{session_quality}%")
col4.metric("Confidence", f"{confidence:.0f}%")

if signal == "BUY":
    st.markdown(f"""
    <div class="buy">
        <div style="font-size:24px; font-weight:bold; color:#00ff88;">⚡ BUY SIGNAL</div>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-top:8px;">
            <div>Entry: {entry:.2f}</div>
            <div>SL: {sl:.2f}</div>
            <div>TP1: {tp1:.2f}</div>
            <div>TP2: {tp2:.2f}</div>
            <div>TP3: {tp3:.2f}</div>
            <div>Lot: {lot:.2f}</div>
        </div>
        <div style="margin-top:8px; color:#aaaaaa;">
            Adaptive: EMA{adaptive['ema']} | ATR{adaptive['atr']} | Risk {adaptive['risk']:.1f}% | RR {adaptive['rr']:.1f} | Regime: {adaptive['regime']}
        </div>
    </div>
    """, unsafe_allow_html=True)
elif signal == "SELL":
    st.markdown(f"""
    <div class="sell">
        <div style="font-size:24px; font-weight:bold; color:#ff4444;">⚡ SELL SIGNAL</div>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-top:8px;">
            <div>Entry: {entry:.2f}</div>
            <div>SL: {sl:.2f}</div>
            <div>TP1: {tp1:.2f}</div>
            <div>TP2: {tp2:.2f}</div>
            <div>TP3: {tp3:.2f}</div>
            <div>Lot: {lot:.2f}</div>
        </div>
        <div style="margin-top:8px; color:#aaaaaa;">
            Adaptive: EMA{adaptive['ema']} | ATR{adaptive['atr']} | Risk {adaptive['risk']:.1f}% | RR {adaptive['rr']:.1f} | Regime: {adaptive['regime']}
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="wait">
        <div style="font-size:24px; font-weight:bold; color:#ffcc00;">⏳ WAIT</div>
        <div>No clear setups. Structure is currently {structure} with RSI at {rsi_val:.1f}.</div>
        <div style="margin-top:8px; color:#aaaaaa;">
            Adaptive: EMA{adaptive['ema']} | ATR{adaptive['atr']} | Risk {adaptive['risk']:.1f}% | RR {adaptive['rr']:.1f} | Regime: {adaptive['regime']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ========== CHART ==========
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"))
fig.add_trace(go.Scatter(x=df.index, y=ema(df["Close"], 50), name="EMA50", line=dict(color='#d4a017')))
fig.add_trace(go.Scatter(x=df.index, y=ema(df["Close"], 200), name="EMA200", line=dict(color='#cd7f32')))

# FVG Overlay
for fvg in find_fvgs(df):
    color = "rgba(0,255,0,0.08)" if fvg['type']=='bullish' else "rgba(255,0,0,0.08)"
    fig.add_shape(type="rect", x0=df.index[fvg['start']], x1=df.index[fvg['end']],
                  y0=fvg['top'], y1=fvg['bottom'], fillcolor=color, line=dict(width=0))

# Order Block Overlay using reliable timestamp referencing
for ob in order_blocks(df):
    color = "#00ff88" if ob['type']=='bull' else "#ff4444"
    end_idx = ob['idx'] + 1
    x1_val = df.index[end_idx] if end_idx < len(df) else df.index[-1]
    fig.add_shape(type="rect", x0=df.index[ob['idx']], x1=x1_val,
                  y0=ob['low'], y1=ob['high'], fillcolor="rgba(0,0,0,0)", line=dict(color=color, width=2, dash="dash"))

fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0))
st.plotly_chart(fig, use_container_width=True)

st.caption("🌀 SEKWAILA OMEGA X — Live Terminal")
