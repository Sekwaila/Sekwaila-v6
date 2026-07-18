"""
=========================================
SEKWAILA OMEGA X
Signal Engine
Version 2.0
=========================================
"""

from indicators import calculate_indicators
from smc import analyze_smc


def generate_signal(df):

    # Calculate indicators
    df = calculate_indicators(df)

    # Smart Money Concepts
    smc = analyze_smc(df)

    latest = df.iloc[-1]

    buy_score = 0
    sell_score = 0

    # -----------------------------
    # EMA Trend
    # -----------------------------
    if latest["ema20"] > latest["ema50"] > latest["ema200"]:
        buy_score += 3

    elif latest["ema20"] < latest["ema50"] < latest["ema200"]:
        sell_score += 3

    # -----------------------------
    # RSI
    # -----------------------------
    if latest["rsi"] < 35:
        buy_score += 2

    elif latest["rsi"] > 65:
        sell_score += 2

    # -----------------------------
    # BOS
    # -----------------------------
    if smc["bos"] == "BULLISH":
        buy_score += 2

    elif smc["bos"] == "BEARISH":
        sell_score += 2

    # -----------------------------
    # CHoCH
    # -----------------------------
    if smc["choch"] == "Bullish":
        buy_score += 1

    elif smc["choch"] == "Bearish":
        sell_score += 1

    # -----------------------------
    # Liquidity
    # -----------------------------
    if smc["liquidity"] == "BUY_SIDE":
        buy_score += 2

    elif smc["liquidity"] == "SELL_SIDE":
        sell_score += 2

    # -----------------------------
    # Premium / Discount
    # -----------------------------
    if smc["zone"] == "DISCOUNT":
        buy_score += 1

    else:
        sell_score += 1

    # -----------------------------
    # Final Signal
    # -----------------------------
    if buy_score >= 8:
        signal = "STRONG BUY"

    elif buy_score >= 5:
        signal = "BUY"

    elif sell_score >= 8:
        signal = "STRONG SELL"

    elif sell_score >= 5:
        signal = "SELL"

    else:
        signal = "NO TRADE"

    price = float(latest["close"])

    atr = float(latest["atr"])

    if "BUY" in signal:

        sl = price - (atr * 1.5)

        tp = price + (atr * 3)

    elif "SELL" in signal:

        sl = price + (atr * 1.5)

        tp = price - (atr * 3)

    else:

        sl = price

        tp = price

    return {

        "signal": signal,

        "price": round(price, 2),

        "buy_score": buy_score,

        "sell_score": sell_score,

        "stop_loss": round(sl, 2),

        "take_profit": round(tp, 2),

        "atr": round(atr, 2),

        "smc": smc
    }
