"""
=========================================
SEKWAILA OMEGA X
AI Confidence Engine
Version: 1.0
=========================================
"""

from signals import generate_signal


# ---------------------------------------
# AI ANALYSIS
# ---------------------------------------

def analyze_market(df):

    signal = generate_signal(df)

    confidence = 50
    reasons = []

    # Trend
    if signal["trend"] == "BULLISH":
        confidence += 10
        reasons.append("Bullish EMA Trend")

    elif signal["trend"] == "BEARISH":
        confidence += 10
        reasons.append("Bearish EMA Trend")

    # BOS
    if signal["structure"]["bos"] == "BULLISH":
        confidence += 10
        reasons.append("Bullish Break of Structure")

    elif signal["structure"]["bos"] == "BEARISH":
        confidence += 10
        reasons.append("Bearish Break of Structure")

    # Liquidity
    if signal["structure"]["liquidity"] != "NONE":
        confidence += 10
        reasons.append("Liquidity Sweep")

    # Fair Value Gap
    if signal["structure"]["fvg"] is not None:
        confidence += 10
        reasons.append("Fair Value Gap Present")

    # Premium / Discount
    if signal["structure"]["zone"] == "DISCOUNT":
        confidence += 5
        reasons.append("Discount Zone")

    else:
        confidence += 5
        reasons.append("Premium Zone")

    # RSI
    if signal["rsi"] < 35:
        confidence += 5
        reasons.append("RSI Oversold")

    elif signal["rsi"] > 65:
        confidence += 5
        reasons.append("RSI Overbought")

    # Limit confidence to 100%
    confidence = min(confidence, 100)

    return {
        "signal": signal["signal"],
        "confidence": confidence,
        "reasons": reasons
    }
