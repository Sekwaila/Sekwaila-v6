import os
import time
import requests
from brain import analyze_market

# =========================================
# TELEGRAM
# =========================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ TELEGRAM_TOKEN or CHAT_ID missing")
        return False

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            return True

        print(response.text)
        return False

    except Exception as e:
        print(f"Telegram Error: {e}")
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

CHECK_INTERVAL = 300  # 5 minutes

# Remember last BUY/SELL alert
last_signals = {}

print("🚀 SEKWAILA OMEGA X Bot Started")


# =========================================
# MAIN LOOP
# =========================================

while True:

    for symbol in SYMBOLS:

        for timeframe in TIMEFRAMES:

            try:

                result = analyze_market(symbol, timeframe)

                if result is None:
                    continue

                signal = result.get("signal", "NO TRADE")
                direction = result.get("direction", "NO TRADE")

                # Ignore NO TRADE completely
                if direction not in ["BUY", "SELL"]:
                    print(f"⏭️ {symbol} {timeframe}: NO TRADE")
                    continue

                confidence = result.get("confidence", 0)
                rating = result.get("rating", 0)
                entry = result.get("entry", "--")
                sl = result.get("stop_loss", "--")
                tp = result.get("take_profit", "--")

                key = f"{symbol}_{timeframe}"

                # Send only when direction changes
                if last_signals.get(key) == direction:
                    print(f"⏭️ {symbol} {timeframe}: Duplicate {direction}")
                    continue

                message = f"""
🚨 *SEKWAILA OMEGA X*

📈 *{symbol}*
⏰ *{timeframe}*

📊 Signal: *{signal}*
🎯 Confidence: *{confidence}%*
⭐ Rating: *{rating}/5*

💰 Entry: `{entry}`
🛑 Stop Loss: `{sl}`
🎯 Take Profit: `{tp}`
"""

                if send_telegram_alert(message):
                    print(f"✅ Alert sent: {symbol} {timeframe} {direction}")
                    last_signals[key] = direction
                else:
                    print(f"❌ Failed sending {symbol}")

            except Exception as e:
                print(f"❌ {symbol} {timeframe}: {e}")

    print(f"\n⏳ Waiting {CHECK_INTERVAL//60} minutes...\n")
    time.sleep(CHECK_INTERVAL)
