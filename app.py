import streamlit as st
import requests
from brain import analyze_market

# =========================================
# TELEGRAM ALERT FUNCTION
# =========================================
def send_telegram_alert(message):
    try:
        token = st.secrets["telegram"]["bot_token=8739054815:AAF3ZCbjRhTB91TX26PnpuGyAte2wfdnTfs"]
        chat_id = st.secrets["telegram"]["chat_id= 5870791602 "]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200
    except Exception as e:
        st.warning(f"Telegram alert failed: {e}")
        return False

# =========================================
# HELPER: Convert numeric rating to stars
# =========================================
def rating_to_stars(rating):
    try:
        rating = float(rating)
    except:
        rating = 0
    if rating >= 4.5:
        return "⭐⭐⭐⭐⭐"
    elif rating >= 3.5:
        return "⭐⭐⭐⭐"
    elif rating >= 2.5:
        return "⭐⭐⭐"
    elif rating >= 1.5:
        return "⭐⭐"
    else:
        return "⭐"

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="SEKWAILA OMEGA X",
    page_icon="📈",
    layout="wide"
)

st.title("📈 SEKWAILA OMEGA X")
st.caption("Institutional AI Trading Dashboard")
st.divider()

# =========================================
# SIDEBAR
# =========================================
st.sidebar.header("Market Settings")

symbol = st.sidebar.selectbox(
    "Symbol",
    ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "US30", "SP500"]
)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["5m", "15m", "30m", "1h", "1d"],
    index=1
)

# Toggle: allow manual alerts or not
alert_on_click = st.sidebar.checkbox("📨 Send alert on click", value=True)

st.sidebar.divider()

run = st.sidebar.button("🚀 Analyze Market")

# =========================================
# SESSION STATE INIT (for duplicate suppression)
# =========================================
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
        # ----- SAFELY EXTRACT VALUES (coerce None to 0 or "--") -----
        signal = result.get("signal", "HOLD")
        confidence = result.get("confidence", 0)
        rating = result.get("rating") or 0           # <-- fixes None bug
        entry = result.get("entry", "--")
        sl = result.get("stop_loss", "--") or "--"
        tp = result.get("take_profit", "--") or "--"
        stars = rating_to_stars(rating)              # now safe

        # ----- Display metrics (use the coerced rating) -----
        st.subheader("📊 AI Trade Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Signal", signal)
        col2.metric("Confidence", f"{confidence}%")
        col3.metric("Rating", rating)                # <-- now uses int/float, not None

        st.divider()

        col4, col5, col6 = st.columns(3)
        col4.metric("Entry", entry)
        col5.metric("Stop Loss", sl)
        col6.metric("Take Profit", tp)

        # ----- Build alert message (uses same coerced values) -----
        alert_msg = f"""
🚨 *NEW AI TRADE SIGNAL* 🚨

*Symbol:* {symbol}
*Timeframe:* {timeframe}

*Signal:* {signal}
*Confidence:* {confidence}%
*Rating:* {rating} ({stars})

*Entry:* {entry}
*Stop Loss:* {sl}
*Take Profit:* {tp}

Dashboard: sekwaila-omega-x.streamlit.app
        """

        # ----- Deduplication: only send if signal changed -----
        should_send = False
        key = f"{symbol}_{timeframe}"
        if alert_on_click:
            if key not in st.session_state.last_alerted:
                should_send = True
            elif st.session_state.last_alerted[key] != signal:
                should_send = True

            if should_send:
                success = send_telegram_alert(alert_msg)
                if success:
                    st.success("📲 Alert sent to Telegram!")
                    st.session_state.last_alerted[key] = signal
                else:
                    st.warning("⚠️ Telegram alert failed – check secrets.")
            else:
                st.info("ℹ️ Signal unchanged – no duplicate alert sent.")
        else:
            st.info("ℹ️ Manual alerts are disabled (checkbox in sidebar).")

# =========================================
# FOOTER
# =========================================
st.divider()
st.caption("🚀 SEKWAILA OMEGA X")
st.caption("Institutional AI Trading Dashboard")
st.caption("Version 3.0")
st.caption("Developed by Johnny Sekwaila")

# =========================================
# MANUAL REFRESH BUTTON
# =========================================
if st.sidebar.button("🔄 Refresh"):
    st.rerun()
