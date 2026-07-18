"""
=========================================
SEKWAILA OMEGA X
Institutional Signal Engine
Version: 4.0
=========================================
"""

from smc import analyze_smc


def generate_signal(df, smc=None):

    if df.empty:
        return {
            "signal": "NO TRADE",
            "confidence": 0,
            "buy_score": 0,
            "sell_score": 0,
            "reasons": []
        }

    if smc is None:
        smc = analyze_smc(df)

    buy_score = 0
    sell_score = 0
    reasons = []

    # =============================
    # EMA TREND
    # =============================

    ema20 = df["ema20"].iloc[-1]
    ema50 = df["ema50"].iloc[-1]
    ema200 = df["ema200"].iloc[-1]

    if ema20 > ema50 > ema200:
        buy_score += 30
        reasons.append("Strong bullish trend")

    elif ema20 < ema50 < ema200:
        sell_score += 30
        reasons.append("Strong bearish trend")

    # =============================
    # RSI
    # =============================

    rsi = df["rsi"].iloc[-1]

    if 45 <= rsi <= 65:

        if buy_score > sell_score:
            buy_score += 15
            reasons.append("Healthy bullish momentum")

        elif sell_score > buy_score:
            sell_score += 15
            reasons.append("Healthy bearish momentum")

    elif rsi < 30:
        buy_score += 10
        reasons.append("Oversold")

    elif rsi > 70:
        sell_score += 10
        reasons.append("Overbought")

    # =============================
    # BOS
    # =============================

    if smc["bos"] == "BULLISH":
        buy_score += 20
        reasons.append("Bullish Break of Structure")

    elif smc["bos"] == "BEARISH":
        sell_score += 20
        reasons.append("Bearish Break of Structure")

    # =============================
    # CHOCH
    # =============================

    if smc["choch"] == "BULLISH":
        buy_score += 15
        reasons.append("Bullish CHoCH")

    elif smc["choch"] == "BEARISH":
        sell_score += 15
        reasons.append("Bearish CHoCH")

    # =============================
    # LIQUIDITY
    # =============================

    if smc["liquidity"] == "BUY SIDE":
        buy_score += 10
        reasons.append("Buy-side liquidity")

    elif smc["liquidity"] == "SELL SIDE":
        sell_score += 10
        reasons.append("Sell-side liquidity")

    # =============================
    # PREMIUM / DISCOUNT
    # =============================

    if smc["zone"] == "DISCOUNT":
        buy_score += 10
        reasons.append("Trading from discount")

    elif smc["zone"] == "PREMIUM":
        sell_score += 10
        reasons.append("Trading from premium")

    # =============================
    # FINAL SIGNAL
    # =============================

    if buy_score >= 70:
        signal = "STRONG BUY"
        confidence = buy_score

    elif buy_score >= 55:
        signal = "BUY"
        confidence = buy_score

    elif sell_score >= 70:
        signal = "STRONG SELL"
        confidence = sell_score

    elif sell_score >= 55:
        signal = "SELL"
        confidence = sell_score

    else:
        signal = "NO TRADE"
        confidence = max(buy_score, sell_score)

    confidence = min(confidence, 100)

    return {
        "signal": signal,
        "confidence": confidence,
        "buy_score": buy_score,
        "sell_score": sell_score,
        "reasons": reasons
    }
