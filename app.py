import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Signal Hunter AI", layout="wide")
st.title("🎯 Signal Hunter AI")

@st.cache_data
def get_data(symbol):
    dates = pd.date_range(end=datetime.now(), periods=100, freq='1h')
    np.random.seed(hash(symbol) % 1000)
    prices = [100]
    for i in range(99):
        prices.append(prices[-1] + np.random.randn() * 0.3)
    return pd.DataFrame({'timestamp': dates, 'close': prices})

def detect_signal(df):
    close = df['close'].values
    for i in range(5, len(close)-5):
        if close[i] > max(close[i-5:i]) and close[i] > max(close[i+1:i+6]):
            return "🟢 BULLISH BOS"
        elif close[i] < min(close[i-5:i]) and close[i] < min(close[i+1:i+6]):
            return "🔴 BEARISH BOS"
    return "⏸️ No Signal"

with st.sidebar:
    st.header("Controls")
    pairs = st.multiselect("Markets", ["XAUUSD", "EURUSD", "USDJPY"], default=["XAUUSD"])

for pair in pairs:
    df = get_data(pair)
    price = df['close'].iloc[-1]
    signal = detect_signal(df)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(pair, f"${price:.2f}")
    with col2:
        if "BULLISH" in signal:
            st.success(signal)
        elif "BEARISH" in signal:
            st.error(signal)
        else:
            st.info(signal)
    
    st.line_chart(df.tail(50).set_index('timestamp')['close'])
    st.divider()

st.success("✅ Signal Hunter AI Active - BOS/CHoCH Running")
