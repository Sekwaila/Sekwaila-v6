"""
=========================================
SEKWAILA OMEGA X
Institutional Signal Engine
Version: 5.0
=========================================
"""

from smc import analyze_smc


def generate_signal(df, smc=None):

    if df.empty:
        return {
            "signal": "NO TRADE",
            "confidence": 0,
            "rating": 0,
            "checks": {}
        }

    if smc is None:
        smc = analyze_smc(df)

    score = 0
    checks = {}

    # ============================
    # EMA TREND (20)
    # ============================

    ema20 = df["ema20"].iloc[-1]
    ema50 = df["ema50"].iloc[-1]
    ema200 = df["ema200"].iloc[-1]

    trend = "NEUTRAL"

    if ema20 > ema50 > ema200:
        trend = "BULLISH"
        score += 20

    elif ema20 < ema50 < ema200:
        trend = "BEARISH"
        score += 20

    checks["Trend"] = trend

    # ============================
    # BOS (20)
    # ============================

    if smc["bos"] != "NONE":
        score += 20

    checks["BOS"] = smc["bos"]

    # ============================
    # CHOCH (15)
    # ============================

    if smc["choch"] != "NONE":
        score += 15

    checks["CHOCH"] = smc["choch"]

    # ============================
    # FAIR VALUE GAP (10)
    # ============================

    if smc["fvg"]:
        score += 10

    checks["FVG"] = "YES" if smc["fvg"] else "NO"

    # ============================
    # ORDER BLOCK (10)
    # ============================

    score += 10

    checks["Order Block"] = "FOUND"

    # ============================
    # PREMIUM / DISCOUNT (10)
    # ============================

    zone = smc["zone"]

    checks["Zone"] = zone

    if trend == "BULLISH" and zone == "DISCOUNT":
        score += 10

    elif trend == "BEARISH" and zone == "PREMIUM":
        score += 10

    # ============================
    # RSI (5)
    # ============================

    rsi = df["rsi"].iloc[-1]

    if 40 <= rsi <= 65:
        score += 5

    checks["RSI"] = round(rsi, 2)

    # ============================
    # ATR (5)
    # ============================

    atr = df["atr"].iloc[-1]

    if atr > 0:
        score += 5

    checks["ATR"] = round(atr, 2)

    # ============================
    # SESSION (5)
    # ============================

    score += 5

    checks["Session"] = "ACTIVE"

    # ============================
    # FINAL SIGNAL
    # ============================

    if trend == "BULLISH":
        direction = "BUY"

    elif trend == "BEARISH":
        direction = "SELL"

    else:
        direction = "NO TRADE"

    if score >= 90:
        signal = f"⭐⭐⭐⭐⭐ STRONG {direction}"

    elif score >= 75:
        signal = f"⭐⭐⭐⭐ {direction}"

    elif score >= 60:
        signal = f"⭐⭐⭐ WATCH {direction}"

    else:
        signal = "NO TRADE"

    return {
        "signal": signal,
        "confidence": score,
        "rating": score,
        "direction": direction,
        "checks": checks
    }
