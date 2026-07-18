"""
=========================================
SEKWAILA OMEGA X
Signal Engine
Version: 1.0
=========================================
"""

from indicators import trend, rsi, atr
from smc import market_structure


# ---------------------------------------
# GENERATE SIGNAL
# ---------------------------------------

def generate_signal(df):

    structure = market_structure(df)

    current_trend = trend(df["Close"])

    current_rsi = float(rsi(df["Close"]).iloc[-1])

    current_atr = float(atr(df).iloc[-1])

    price = float(df["Close"].iloc[-1])

    buy_score = 0
    sell_score = 0

    # Trend
    if current_trend == "BULLISH":
        buy_score += 3
    elif current_trend == "BEARISH":
        sell_score += 3

    # RSI
    if current_rsi < 35:
        buy_score += 2

    elif current_rsi > 65:
        sell_score += 2

    # BOS
    if structure["bos"] == "BULLISH":
        buy_score += 2

    elif structure["bos"] == "BEARISH":
        sell_score += 2

    # Liquidity Sweep
    if structure["liquidity"] == "BUY_SIDE":
        buy_score += 2

    elif structure["liquidity"] == "SELL_SIDE":
        sell_score += 2

    # Premium / Discount
    if structure["zone"] == "DISCOUNT":
        buy_score += 1

    else:
        sell_score += 1

    # -----------------------------------
    # Final Signal
    # -----------------------------------

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

    # -----------------------------------
    # TP & SL
    # -----------------------------------

    if "BUY" in signal:

        stop_loss = price - (current_atr * 1.5)

        take_profit = price + (current_atr * 3)

    elif "SELL" in signal:

        stop_loss = price + (current_atr * 1.5)

        take_profit = price - (current_atr * 3)

    else:

        stop_loss = price

        take_profit = price

    return {

        "signal": signal,

        "price": round(price, 2),

        "trend": current_trend,

        "rsi": round(current_rsi, 2),

        "atr": round(current_atr, 2),

        "buy_score": buy_score,

        "sell_score": sell_score,

        "stop_loss": round(stop_loss, 2),

        "take_profit": round(take_profit, 2),

        "structure": structure

    }
