"""
=========================================
SEKWAILA OMEGA X
AI Analysis Engine
Version 2.0
=========================================
"""

from signals import generate_signal


def analyze_trade(df):
    """
    AI trading analysis based on generated signal.
    """

    signal = generate_signal(df)

    confidence = 50
    reasons = []

    # -----------------------------
    # Signal Strength
    # -----------------------------
    if signal["signal"] == "STRONG BUY":
        confidence += 25
        reasons.append("Strong bullish confirmation")

    elif signal["signal"] == "BUY":
        confidence += 15
        reasons.append("Bullish setup detected")

    elif signal["signal"] == "STRONG SELL":
        confidence += 25
        reasons.append("Strong bearish confirmation")

    elif signal["signal"] == "SELL":
        confidence += 15
        reasons.append("Bearish setup detected")

    else:
        reasons.append("No high probability setup")

    # -----------------------------
    # Buy / Sell Score
    # -----------------------------
    score = max(signal["buy_score"], signal["sell_score"])

    confidence += score * 2

    # -----------------------------
    # Smart Money Concepts
    # -----------------------------
    smc = signal["smc"]

    if smc["bos"] != "NONE":
        confidence += 5
        reasons.append("Break of Structure confirmed")

    if smc["choch"] != "None":
        confidence += 5
        reasons.append("Change of Character detected")

    if smc["liquidity"] != "NONE":
        confidence += 5
        reasons.append("Liquidity sweep identified")

    if smc["fvg"] is not None:
        confidence += 5
        reasons.append("Fair Value Gap detected")

    if smc["order_block"] is not None:
        confidence += 5
        reasons.append("Order Block identified")

    # -----------------------------
    # Limit Confidence
    # -----------------------------
    confidence = min(confidence, 100)

    return {

        "signal": signal["signal"],

        "confidence": confidence,

        "buy_score": signal["buy_score"],

        "sell_score": signal["sell_score"],

        "entry": signal["price"],

        "stop_loss": signal["stop_loss"],

        "take_profit": signal["take_profit"],

        "reasons": reasons

    }
