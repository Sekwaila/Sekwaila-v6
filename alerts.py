"""
===========================================
SEKWAILA OMEGA X
Alerts Module
Version: 1.0
===========================================
"""

from scanner import scan_all_markets
from telegram_bot import send_telegram_message
import time

# Minimum confidence required
MIN_CONFIDENCE = 80

# Prevent duplicate alerts
sent_alerts = set()


def format_alert(signal):
    return (
        f"🚨 SEKWAILA OMEGA X\n\n"
        f"Symbol: {signal['symbol']}\n"
        f"Timeframe: {signal['timeframe']}\n"
        f"Signal: {signal['signal']}\n"
        f"Confidence: {signal['confidence']}%\n"
        f"Price: {signal['price']}"
    )


def monitor_market():
    print("Monitoring markets...")

    while True:
        signals = scan_all_markets()

        for signal in signals:

            key = (
                signal["symbol"],
                signal["timeframe"],
                signal["signal"]
            )

            if (
                signal["confidence"] >= MIN_CONFIDENCE
                and key not in sent_alerts
            ):
                message = format_alert(signal)
                send_telegram_message(message)

                print(message)

                sent_alerts.add(key)

        # Scan every 60 seconds
        time.sleep(60)


if __name__ == "__main__":
    monitor_market()
