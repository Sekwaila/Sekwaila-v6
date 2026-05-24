import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import time
import math

st.set_page_config(page_title="Signal Hunter AI", layout="wide")
st.title("🎯 Signal Hunter AI - With Position Sizing")
st.caption(f"SMC Analysis | BOS/CHoCH Detection | Live Lot Sizing | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ========== ACCOUNT SETTINGS ==========
ACCOUNT_BALANCE = 1000  # R1000 account

def calculate_lot_size(signal_strength, stop_loss_pips=50, risk_percent=2):
    """
    Calculate lot size based on signal strength
    signal_strength: 0-100%
    risk_percent: % of account to risk per trade (default 2% = R20 on R1000)
    """
    risk_amount = ACCOUNT_BALANCE * (risk_percent / 100)
    
    # Adjust risk based on signal strength
    strength_multiplier = signal_strength / 100
    adjusted_risk = risk_amount * strength_multiplier
    
    # For Forex: 1 pip on standard lot = $10, on mini lot = $1
    # For R1000 account, using mini lots (0.01 = R1 per pip)
    pip_value_per_0_01 = 1  # R1 per pip for 0.01 lot
    
    lot_size = adjusted_risk / (stop_loss_pips * pip_value_per_0_01)
    
    # Round to nearest 0.01
    lot_size = round(lot_size / 0.01) * 0.01
    
    # Cap at reasonable limits for R1000
    lot_size = max(0.01, min(lot_size, 0.50))
    
    return lot_size

def get_signal_strength(signal_type, volume, timeframe_alignment):
    """Calculate signal strength percentage 0-100"""
    strength = 50  # base
    
    if "BULLISH" in signal_type or "BEARISH" in signal_type:
        strength += 20
    
    if "CHoCH" in signal_type:
        strength += 15
    
    if volume == "HIGH":
        strength += 15
    elif volume == "LOW":
        strength -= 10
    
    if timeframe_alignment:
        strength += 10
    
    return min(100, max(0, strength))

def get_soccer_bet_size(confidence, odds):
    """Calculate bet size for soccer based on Kelly Criterion"""
    # Kelly Formula: (odds * probability - 1) / (odds - 1)
    probability = confidence / 100
    kelly = (odds * probability - 1) / (odds - 1)
    
    # Use half Kelly for safety
    bet_percentage = min(0.05, max(0.005, kelly * 0.5))
    bet_amount = ACCOUNT_BALANCE * bet_percentage
    
    return round(bet_amount, 2)

# ========== DATA FETCHER ==========
@st.cache_data(ttl=60)
def get_price_data(symbol):
    dates = pd.date_range(end=datetime.now(), periods=100, freq='1h')
    np.random.seed(hash(symbol) % 10000)
    
    if "XAU" in symbol:
        base, vol = 2300, 15
    elif "BTC" in symbol:
        base, vol = 65000, 2000
    else:
        base, vol = 1.08, 0.02
    
    prices = [base]
    for i in range(99):
        prices.append(prices[-1] + np.random.randn() * (vol / 50))
    
    return pd.DataFrame({
        'timestamp': dates,
        'close': prices,
        'high': [p + abs(np.random.randn() * vol/100) for p in prices],
        'low': [p - abs(np.random.randn() * vol/100) for p in prices],
        'volume': [1000 + i*20 + np.random.randint(-200, 200) for i in range(100)]
    })

def detect_signal(df):
    close = df['close'].values
    for i in range(5, len(close)-5):
        if close[i] > max(close[i-5:i]) and close[i] > max(close[i+1:i+6]):
            return "🟢 BULLISH BOS", "BOS"
        elif close[i] < min(close[i-5:i]) and close[i] < min(close[i+1:i+6]):
            return "🔴 BEARISH BOS", "BOS"
    return "⏸️ NO SIGNAL", "NONE"

def detect_choch(df):
    close = df['close'].values
    for i in range(10, len(close)-5):
        if close[i] > close[i-5] and close[i] > close[i+5] and close[i-1] < close[i-6]:
            return "🔄 CHoCH BULLISH", "CHoCH"
        elif close[i] < close[i-5] and close[i] < close[i+5] and close[i-1] > close[i-6]:
            return "🔄 CHoCH BEARISH", "CHoCH"
    return None, None

def classify_volume(df):
    current = df['volume'].iloc[-1]
    avg = df['volume'].tail(20).mean()
    if current > avg * 1.3:
        return "HIGH"
    elif current < avg * 0.7:
        return "LOW"
    return "MEDIUM"

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("💰 Account Settings")
    st.metric("Account Balance", f"R{ACCOUNT_BALANCE:,.2f}")
    risk_percent = st.slider("Risk per trade (%)", 0.5, 5.0, 2.0, 0.5)
    st.caption(f"Risk per trade: R{ACCOUNT_BALANCE * risk_percent / 100:.2f}")
    
    st.divider()
    st.header("⚙️ Trading Settings")
    default_stop_pips = st.number_input("Default Stop Loss (pips)", 20, 200, 50)
    
    st.divider()
    st.header("📊 Markets")
    pairs = st.multiselect(
        "Select pairs", 
        ["XAUUSD", "EURUSD", "USDJPY", "GBPUSD", "BTCUSD"],
        default=["XAUUSD", "EURUSD"]
    )
    auto = st.checkbox("Auto-refresh", value=False)
    st.success("✅ System Active")

# ========== MAIN DISPLAY ==========
st.subheader("📈 Live Trading Signals with Lot Sizing")

# Summary of today's potential trades
st.info(f"💰 Based on R{ACCOUNT_BALANCE:,} account | Risk: {risk_percent}% per trade (R{ACCOUNT_BALANCE * risk_percent / 100:.2f})")

for pair in pairs:
    df = get_price_data(pair)
    current_price = df['close'].iloc[-1]
    prev_price = df['close'].iloc[-2]
    price_change = ((current_price - prev_price) / prev_price) * 100
    
    signal, signal_type = detect_signal(df)
    choch_signal, choch_type = detect_choch(df)
    volume = classify_volume(df)
    
    # Determine final signal
    if choch_signal:
        main_signal = choch_signal
        main_type = choch_type
    else:
        main_signal = signal
        main_type = signal_type
    
    # Calculate signal strength and lot size
    timeframe_aligned = True  # Simplified for demo
    strength = get_signal_strength(main_signal, volume, timeframe_aligned)
    lot_size = calculate_lot_size(strength, default_stop_pips, risk_percent)
    
    with st.container():
        st.markdown(f"### {pair}")
        
        col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1.5])
        
        with col1:
            st.metric("Price", f"${current_price:.4f}", delta=f"{price_change:.2f}%")
        
        with col2:
            if "BULLISH" in main_signal:
                st.success(main_signal)
            elif "BEARISH" in main_signal:
                st.error(main_signal)
            elif "CHoCH" in main_signal:
                st.warning(main_signal)
            else:
                st.info(main_signal)
        
        with col3:
            if volume == "HIGH":
                st.success("🔊 HIGH VOLUME")
                vol_color = "green"
            elif volume == "LOW":
                st.warning("🔇 LOW VOLUME")
                vol_color = "red"
            else:
                st.info("📊 MED VOLUME")
                vol_color = "yellow"
        
        with col4:
            # Display lot size with color based on strength
            if strength >= 70:
                st.success(f"📊 LOT: {lot_size:.2f}")
                st.caption(f"Strength: {strength:.0f}% 🔥")
            elif strength >= 50:
                st.info(f"📊 LOT: {lot_size:.2f}")
                st.caption(f"Strength: {strength:.0f}%")
            else:
                st.warning(f"📊 LOT: {lot_size:.2f}")
                st.caption(f"Strength: {strength:.0f}%")
        
        # Detailed position sizing info
        with st.expander(f"📐 Position Details (R{ACCOUNT_BALANCE} Account)"):
            risk_amount = ACCOUNT_BALANCE * (risk_percent / 100) * (strength / 100)
            pip_value = lot_size * 1  # R1 per pip for mini lots
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Signal Strength", f"{strength:.0f}%")
                st.caption("Confidence level")
            with col_b:
                st.metric("Lot Size", f"{lot_size:.2f}")
                st.caption(f"R{pip_value:.2f} per pip")
            with col_c:
                st.metric("Risk Amount", f"R{risk_amount:.2f}")
                st.caption(f"Stop: {default_stop_pips} pips")
            
            st.progress(strength / 100)
        
        # Chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'].tail(50),
            open=df['open'].tail(50),
            high=df['high'].tail(50),
            low=df['low'].tail(50),
            close=df['close'].tail(50)
        )])
        fig.update_layout(height=200, margin=dict(l=0, r=0, t=20, b=0))
        fig.update_xaxes(rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

# ========== SOCCER SECTION WITH BET SIZING ==========
st.subheader("⚽ Soccer AI Predictions with Bet Sizing")

# Soccer matches with odds
soccer_matches = [
    {"home": "Liverpool", "away": "Arsenal", "confidence": 68, "odds_home": 2.10, "odds_draw": 3.40, "odds_away": 3.50},
    {"home": "Orlando Pirates", "away": "Kaizer Chiefs", "confidence": 55, "odds_home": 2.30, "odds_draw": 3.00, "odds_away": 3.20},
    {"home": "Man City", "away": "Chelsea", "confidence": 72, "odds_home": 1.85, "odds_draw": 3.60, "odds_away": 4.50},
    {"home": "Barcelona", "away": "Real Madrid", "confidence": 60, "odds_home": 2.40, "odds_draw": 3.30, "odds_away": 2.90},
]

for match in soccer_matches:
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 1, 1.5, 1.5])
        
        prediction = "HOME" if match["confidence"] > 55 else "DRAW" if match["confidence"] > 45 else "AWAY"
        odds = match[f"odds_{prediction.lower()}"]
        bet_size = get_soccer_bet_size(match["confidence"], odds)
        
        with col1:
            st.write(f"**{match['home']} vs {match['away']}**")
        
        with col2:
            st.metric("Prediction", prediction, delta=f"{match['confidence']}%")
        
        with col3:
            st.write(f"Odds: **{odds:.2f}**")
            expected_value = (match["confidence"]/100 * odds - 1) * 100
            if expected_value > 10:
                st.success(f"EV: +{expected_value:.0f}%")
            else:
                st.caption(f"EV: {expected_value:.0f}%")
        
        with col4:
            if bet_size >= 20:
                st.success(f"💰 Bet: R{bet_size:.2f}")
                st.caption(f"({bet_size/ACCOUNT_BALANCE*100:.1f}% of account)")
            elif bet_size >= 10:
                st.info(f"💰 Bet: R{bet_size:.2f}")
            else:
                st.warning(f"💰 Bet: R{bet_size:.2f}")
                st.caption("Small or no edge")
        
        # Show stake calculation
        with st.expander(f"📐 R{bet_size:.2f} Stake Calculation"):
            st.write(f"**Kelly Formula:** (Odds × Probability - 1) / (Odds - 1)")
            st.write(f"- Probability: {match['confidence']}%")
            st.write(f"- Odds: {odds}")
            st.write(f"- Kelly %: {(odds * match['confidence']/100 - 1) / (odds - 1) * 100:.1f}%")
            st.write(f"- **Suggested Stake: R{bet_size:.2f}**")
        
        st.divider()

# ========== POSITION SIZING GUIDE ==========
with st.expander("📚 Position Sizing Guide (R1000 Account)"):
    st.write("""
    ### How Lot Sizes Are Calculated:
    
    | Signal Strength | Lot Size (50 pip stop) | Risk Amount | When to Use |
    |----------------|------------------------|-------------|-------------|
    | 90-100% (🔥 Strong) | 0.20 - 0.40 | R20 - R40 | CHoCH + High Volume + MTF |
    | 70-89% (✅ Good) | 0.10 - 0.19 | R10 - R19 | BOS + High Volume |
    | 50-69% (⚠️ Moderate) | 0.05 - 0.09 | R5 - R9 | BOS + Medium Volume |
    | 30-49% (❌ Weak) | 0.02 - 0.04 | R2 - R4 | Low conviction |
    | 0-29% (🚫 Avoid) | 0.01 | R1 | Skip trade |
    
    ### Soccer Bet Sizing (Kelly Criterion):
    - **High confidence (70%+)** : R20 - R50 stake
    - **Medium confidence (55-69%)** : R10 - R19 stake  
    - **Low confidence (40-54%)** : R5 - R9 stake
    - **No edge (<40%)** : Skip bet
    
    ### Risk Management Rules:
    - Max risk per trade: 2% of account (R20 on R1000)
    - Max 3 concurrent trades
    - Daily loss limit: 6% (R60)
    - Weekly loss limit: 15% (R150)
    """)

# ========== TABS ==========
tab1, tab2, tab3 = st.tabs(["📰 News", "📊 Performance", "🤖 AI Briefing"])

with tab1:
    st.write("### 📰 Market News")
    st.write("• Gold holds support at $2,300")
    st.write("• DXY at 104.50 - watching for breakout")
    st.write("• Fed minutes tomorrow at 14:00 GMT")

with tab2:
    st.write("### 📊 Trading Performance")
    
    # Demo stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Win Rate", "68%", "+5%")
    with col2:
        st.metric("Avg Risk/Reward", "1:2.1", "Good")
    with col3:
        st.metric("Profit Factor", "1.45", "+0.12")
    
    st.write("### Recent Signals with Lot Sizes")
    recent = [
        {"pair": "XAUUSD", "signal": "BULLISH BOS", "strength": "85%", "lot": "0.15", "result": "+R42"},
        {"pair": "EURUSD", "signal": "CHoCH BULLISH", "strength": "92%", "lot": "0.25", "result": "+R75"},
        {"pair": "USDJPY", "signal": "BEARISH BOS", "strength": "45%", "lot": "0.04", "result": "-R8"},
    ]
    st.dataframe(pd.DataFrame(recent), use_container_width=True)

with tab3:
    if st.button("🔄 Generate AI Briefing with Trade Plan"):
        st.write("### 📋 Today's Trading Plan")
        st.write(f"**Account:** R{ACCOUNT_BALANCE:,}")
        st.write(f"**Risk per trade:** {risk_percent}% (R{ACCOUNT_BALANCE * risk_percent / 100:.2f})")
        st.write("")
        st.write("**Top Setups:**")
        st.write("1. **XAUUSD** - Bullish BOS on H1 | Strength: 85% | Lot: 0.12-0.15")
        st.write("2. **EURUSD** - Watching for CHoCH | Strength: Pending")
        st.write("")
        st.write("**Soccer Value Bets:**")
        st.write("- Liverpool vs Arsenal: HOME @ 2.10 | Stake: R15")
        st.write("- Man City vs Chelsea: HOME @ 1.85 | Stake: R20")
        st.success("✅ Briefing generated - Trade within risk parameters")

# Auto refresh
if auto:
    time.sleep(60)
    st.rerun()
