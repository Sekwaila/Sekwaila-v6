"""
=========================================
SEKWAILA OMEGA X
Backtesting Engine
Version: 1.0
=========================================
"""

import pandas as pd
from signals import generate_signal


class Backtester:

    def __init__(self, data):

        self.data = data.copy()

        self.total_trades = 0
        self.wins = 0
        self.losses = 0

    def run(self):

        if len(self.data) < 250:

            return {
                "Total Trades": 0,
                "Wins": 0,
                "Losses": 0,
                "Win Rate": 0
            }

        for i in range(200, len(self.data) - 1):

            df = self.data.iloc[: i + 1]

            signal = generate_signal(df)

            entry = signal["price"]

            next_close = float(self.data["Close"].iloc[i + 1])

            if signal["signal"] in ["BUY", "STRONG BUY"]:

                self.total_trades += 1

                if next_close > entry:
                    self.wins += 1
                else:
                    self.losses += 1

            elif signal["signal"] in ["SELL", "STRONG SELL"]:

                self.total_trades += 1

                if next_close < entry:
                    self.wins += 1
                else:
                    self.losses += 1

        if self.total_trades == 0:

            win_rate = 0

        else:

            win_rate = round(
                (self.wins / self.total_trades) * 100,
                2
            )

        return {

            "Total Trades": self.total_trades,

            "Wins": self.wins,

            "Losses": self.losses,

            "Win Rate": win_rate

        }


def print_results(results):

    print("\n========== BACKTEST RESULTS ==========\n")

    for key, value in results.items():

        print(f"{key}: {value}")

    print("\n======================================")
