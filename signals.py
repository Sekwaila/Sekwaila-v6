"""
=========================================
SEKWAILA OMEGA X
Signal Engine
Version: 3.0
=========================================
"""

from smc import analyze_smc


# ---------------------------------------
# GENERATE TRADING SIGNAL
# ---------------------------------------

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

    # Trend
    ema20 = df["ema20"].iloc[-1]
    ema50 = df["ema50"].iloc[-1]
    ema200 = df["ema200"].iloc[-1]

    if ema20 > ema50 > ema200:
        buy_score += 3
        reasons.append("Bullish EMA alignment")

    elif ema20 < ema50 < ema200:
        sell_score += 3
        reasons.append("Bearish EMA alignment")

    # RSI
    rsi = df["rsi"].iloc[-1]

    if rsi < 30:
        buy_score += 2
        reasons.append("RSI Oversold")

    elif rsi > 70:
        sell_score += 2
        reasons.append("RSI Overbought")

    # BOS
    if smc["bos"] == "BULLISH":
        buy_score += 2
        reasons.append("Bullish BOS")

    elif smc["bos"] == "BEARISH":
        sell_score += 2
        reasons.append("Bearish BOS")

    # CHoCH
    if smc["choch"] == "BULLISH":
        buy_score += 1

    elif smc["choch"] == "BEARISH":
        sell_score += 1

    # Liquidity
    if smc["liquidity"] == "BUY SIDE":
        buy_score += 1

    elif smc["liquidity"] == "SELL SIDE":
        sell_score += 1

    # Premium / Discount
    if smc["zone"] == "DISCOUNT":
        buy_score += 1

    else:
        sell_score += 1

    # Signal decision
    if buy_score >= sell_score and buy_score >= 6:
        signal = "BUY"

    elif sell_score > buy_score and sell_score >= 6:
        signal = "SELL"

    else:
        signal = "NO TRADE"

    confidence = min(max(buy_score, sell_score) * 10, 100)

    return {
        "signal": signal,
        "confidence": confidence,
        "buy_score": buy_score,
        "sell_score": sell_score,
        "reasons": reasons
    }
