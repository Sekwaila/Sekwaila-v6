import os
import time
import requests
import schedule
from brain import analyze_market

# =========================================
# CONFIG – environment variables
# =========================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN= 8739054815:AAF3ZCbjRhTB91TX26PnpuGyAte2wfdnTfs")
CHAT_ID = os.getenv("CHAT_ID")

# Local testing override (remove in production)
# TELEGRAM_TOKEN = "8739054815:AAF3ZCbjRhTB91TX26PnpuGyAte2wfdnTfs"
# CHAT_ID = "5870791602"

SYMBOLS = ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD", "USDJPY", "US30", "SP500"]
TIMEFRAME = "15m"
CHECK_INTERVAL_MINUTES = 5

# In‑memory dedup – survives as long as the process runs.
# On Railway restart, it resets, which may send one extra alert per symbol.
# That's acceptable – we prefer simplicity over persistent storage.
last_alerted = {}

# =========================================
# HELPERS
# =========================================
def rating_to_stars(rating):
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

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Missing TELEGRAM_TOKEN or CHAT_ID")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

# =========================================
# THE JOB – wrapped in try/except for resilience
# =========================================
def run_analysis():
    global last_alerted
    try:
        print(f"[{time.ctime()}] Scanning {len(SYMBOLS)} symbols...")
        
        for symbol in SYMBOLS:
            result = analyze_market(symbol, TIMEFRAME)
            if result is None:
                continue
            
            signal = result.get("signal", "HOLD")
            
            # Only alert on actionable signals – ignore everything else
            if signal not in ["BUY", "SELL"]:
                print(f"  ℹ️ {symbol}: {signal} – skipping")
                continue
            
            # Dedup: only send if signal changed
            if last_alerted.get(symbol) == signal:
                print(f"  ℹ️ {symbol}: signal unchanged ({signal}) – skip")
                continue
            
            # Build message
            confidence = result.get("confidence", 0)
            rating = result.get("rating") or 0
            entry = result.get("entry", "--")
            sl = result.get("stop_loss", "--") or "--"
            tp = result.get("take_profit", "--") or "--"
            stars = rating_to_stars(rating)

            msg = f"""
🤖 *AUTO SIGNAL ALERT*

*Symbol:* {symbol}
*Timeframe:* {TIMEFRAME}
*Signal:* {signal}
*Confidence:* {confidence}%
*Rating:* {rating} ({stars})

*Entry:* {entry}
*Stop Loss:* {sl}
*Take Profit:* {tp}
            """
            
            if send_telegram_alert(msg):
                print(f"  ✅ Alert sent for {symbol} ({signal})")
                last_alerted[symbol] = signal
            else:
                print(f"  ❌ Failed for {symbol}")
    
    except Exception as e:
        print(f"❌ CRITICAL: run_analysis() crashed: {e}")
        # We don't re-raise – the worker keeps running

# =========================================
# MAIN LOOP
# =========================================
if __name__ == "__main__":
    print("🚀 SEKWAILA OMEGA X Worker started")
    print(f"   Monitoring: {', '.join(SYMBOLS)}")
    print(f"   Interval: {CHECK_INTERVAL_MINUTES} min")
    print(f"   Dedup: in‑memory (resets on restart)")
    print("-" * 40)
    
    # Run once immediately
    run_analysis()
    
    # Schedule
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(run_analysis)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
