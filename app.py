import streamlit as st
import requests
from brain import analyze_market

# =========================================
# TELEGRAM (HARDCODED – NO SECRETS)
# =========================================
def send_telegram_alert(message):
    try:
        token = "8739054815:AAGCIGmES43JxGuF4TfBotPRSD-EOxA6SCM"
        chat_id = "5870791602"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200
    except Exception as e:
        st.warning(f"Telegram error: {e}")
        return False

# =========================================
# RATING TO STARS – HANDLES ANYTHING
# =========================================
def rating_to_stars(rating):
    # If rating is a dict, try to get 'score' or 'rating' key
    if isinstance(rating, dict):
        rating = rating.get("score") or rating.get("rating") or 0
    # Convert to float, if fails -> 0
    try:
        rating = float(rating)
    except:
        rating = 0
    # Clamp between 0 and 5, then return stars
    stars = min(5, max(0, int(rating / 1.5 + 0.5)))
    return "⭐" * stars

# =========================================
# PAGE SETUP
# =========================================
st.set_page_config(page_title="SEKWAILA OMEGA X", page_icon="📈", layout="wide")
st.title("📈 SEKWAILA OMEGA X")
st.caption("Institutional AI Trading Dashboard")
st.divider()

# =========================================
# SIDEBAR
# =========================================
st.sidebar.header("Market Settings")
symbol = st.sidebar.selectbox("Symbol", ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "US30", "SP500"])
timeframe = st.sidebar.selectbox("Timeframe", ["5m", "15m", "30m", "1h", "1d"], index=1)
alert_on_click = st.sidebar.checkbox("📨 Send alert on click", value=True)
st.sidebar.divider()
run = st.sidebar.button("🚀 Analyze Market")

# SESSION STATE
if "last_alerted" not in st.session_state:
    st.session_state.last_alerted = {}

# =========================================
# RUN ENGINE
# =========================================
if run:
    with st.spinner("Analyzing market..."):
        result = analyze_market(symbol, timeframe)

    if result is None:
        st.error("No market data available.")
    else:
        # SAFE EXTRACTION (with fallbacks)
        signal = result.get("signal", "HOLD")
        confidence = result.get("confidence", 0)
        rating_val = result.get("rating", 0)  # could be dict, string, number
        entry = result.get("entry", "--")
        sl = result.get("stop_loss", "--") or "--"
        tp = result.get("take_profit", "--") or "--"
        stars = rating_to_stars(rating_val)   # handles everything

        # DISPLAY
        st.subheader("📊 AI Trade Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Signal", signal)
        col2.metric("Confidence", f"{confidence}%")
        col3.metric("Rating", rating_val if isinstance(rating_val, (int, float)) else "N/A")

        st.divider()
        col4, col5, col6 = st.columns(3)
        col4.metric("Entry", entry)
        col5.metric("Stop Loss", sl)
        col6.metric("Take Profit", tp)

        # ALERT MESSAGE
        alert_msg = f"""
🚨 *NEW AI TRADE SIGNAL* 🚨

*Symbol:* {symbol}
*Timeframe:* {timeframe}
*Signal:* {signal}
*Confidence:* {confidence}%
*Rating:* {rating_val} ({stars})
*Entry:* {entry}
*Stop Loss:* {sl}
*Take Profit:* {tp}

Dashboard: sekwaila-omega-x.streamlit.app
        """

        # DEDUP & SEND
        key = f"{symbol}_{timeframe}"
        if alert_on_click:
            if key not in st.session_state.last_alerted or st.session_state.last_alerted[key] != signal:
                if send_telegram_alert(alert_msg):
                    st.success("📲 Alert sent to Telegram!")
                    st.session_state.last_alerted[key] = signal
                else:
                    st.warning("⚠️ Telegram alert failed.")
            else:
                st.info("ℹ️ Signal unchanged – no duplicate.")
        else:
            st.info("ℹ️ Manual alerts disabled.")

# =========================================
# FOOTER & REFRESH
# =========================================
st.divider()
st.caption("🚀 SEKWAILA OMEGA X")
st.caption("Institutional AI Trading Dashboard")
st.caption("Version 3.0")
st.caption("Developed by Johnny Sekwaila")

if st.sidebar.button("🔄 Refresh"):
    st.rerun()
