import time
import requests
from brain import analyze_market

# =========================================
# TELEGRAM
# =========================================
def send_telegram_alert(message):
    try:
        token = "8739054815:AAGCIGmES43JxGuF4TfBotPRSD-EOxA6SCM"
        chat_id = "5870791602"

        url = f"https://api.telegram.org/bot{token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        r = requests.post(url, json=payload, timeout=5)

        return r.status_code == 200

    except Exception as e:
        print(e)
        return False
      # =========================================
# SETTINGS
# =========================================
SYMBOLS = [
    "XAUUSD",
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "BTCUSD",
    "US30",
    "SP500",
]

TIMEFRAMES = [
    "5m",
    "15m",
    "30m",
    "1h",
]

CHECK_INTERVAL = 300  # 300 seconds = 5 minutes

last_signals = {}

print("🚀 SEKWAILA OMEGA X Bot Started")

while True:

    for symbol in SYMBOLS:

        for timeframe in TIMEFRAMES:

            try:
                result = analyze_market(symbol, timeframe)

                if not result:
                    continue

                signal = result.get("signal", "HOLD")
                direction = result.get("direction", "NO TRADE")

# Skip anything that isn't a BUY or SELL
if direction not in ["BUY", "SELL"]:
    print(f"⏭️ {symbol} {timeframe}: NO TRADE")
    continue
                confidence = result.get("confidence", 0)
                rating = result.get("rating", 0)
                entry = result.get("entry", "--")
                sl = result.get("stop_loss", "--")
                tp = result.get("take_profit", "--")

                key = f"{symbol}_{timeframe}"

                # Only send if the signal changed
                if last_signals.get(key) != signal:

                    message = f"""
🚨 *NEW AI TRADE SIGNAL*

*Symbol:* {symbol}
*Timeframe:* {timeframe}
*Signal:* {signal}
*Confidence:* {confidence}%
*Rating:* {rating}
*Entry:* {entry}
*Stop Loss:* {sl}
*Take Profit:* {tp}
"""

                    if send_telegram_alert(message):
                        print(f"✅ Alert sent: {symbol} {timeframe} {signal}")

                    last_signals[key] = signal

            except Exception as e:
                print(f"{symbol} {timeframe}: {e}")

    print("⏳ Waiting 5 minutes...")
    time.sleep(CHECK_INTERVAL)
