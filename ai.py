"""
=========================================
SEKWAILA OMEGA X
AI Decision Engine
Version: 3.0
=========================================
"""

from signals import generate_signal
from smc import analyze_smc


def ai_confidence(df):
    """
    AI evaluates the market and assigns a confidence score.
    """

    if df.empty:
        return {
            "signal": "NO TRADE",
            "confidence": 0,
            "entry": None,
            "stop_loss": None,
            "take_profit": None,
            "buy_score": 0,
            "sell_score": 0,
            "reasons": [],
            "smc": {}
        }

    smc = analyze_smc(df)

    signal_data = generate_signal(df, smc)

    price = float(df["close"].iloc[-1])
    atr = float(df["atr"].iloc[-1])

    if signal_data["signal"] == "BUY":
        stop_loss = round(price - (atr * 1.5), 2)
        take_profit = round(price + (atr * 3), 2)

    elif signal_data["signal"] == "SELL":
        stop_loss = round(price + (atr * 1.5), 2)
        take_profit = round(price - (atr * 3), 2)

    else:
        stop_loss = price
        take_profit = price

    return {
        "signal": signal_data["signal"],
        "confidence": signal_data["confidence"],
        "buy_score": signal_data["buy_score"],
        "sell_score": signal_data["sell_score"],
        "entry": round(price, 2),
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "reasons": signal_data["reasons"],
        "smc": smc
    }
