"""
=========================================
SEKWAILA OMEGA X
Telegram Alert System
Version: 1.0
=========================================
"""

import requests


class TelegramBot:

    def __init__(self, token="", chat_id=""):

        self.token = token
        self.chat_id = chat_id

    def enabled(self):

        return self.token != "" and self.chat_id != ""

    def send(self, message):

        if not self.enabled():
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:

            requests.post(url, data=data, timeout=10)

            return True

        except Exception as e:

            print(e)

            return False


def build_trade_message(ai_result, trade):

    return f"""
🚀 SEKWAILA OMEGA X

Signal:
{ai_result['signal']}

Confidence:
{ai_result['confidence']}%

Entry:
{trade['Entry']}

Stop Loss:
{trade['Stop Loss']}

Take Profit:
{trade['Take Profit']}

Risk Reward:
1:{trade['Risk Reward']}
"""
