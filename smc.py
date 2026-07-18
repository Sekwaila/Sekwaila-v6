"""
=========================================
SEKWAILA OMEGA X
Smart Money Concepts Engine
Version: 5.0
=========================================
"""

import pandas as pd


# =========================================
# SWING HIGH / LOW
# =========================================

def detect_swings(df, lookback=3):

    swings = []

    if len(df) < (lookback * 2 + 1):
        return swings

    for i in range(lookback, len(df) - lookback):

        high = df["high"].iloc[i]
        low = df["low"].iloc[i]

        left_high = df["high"].iloc[i-lookback:i]
        right_high = df["high"].iloc[i+1:i+lookback+1]

        left_low = df["low"].iloc[i-lookback:i]
        right_low = df["low"].iloc[i+1:i+lookback+1]

        if high > left_high.max() and high > right_high.max():

            swings.append({
                "type": "HIGH",
                "index": i,
                "price": high
            })

        if low < left_low.min() and low < right_low.min():

            swings.append({
                "type": "LOW",
                "index": i,
                "price": low
            })

    return swings


# =========================================
# BREAK OF STRUCTURE
# =========================================

def detect_bos(df):

    swings = detect_swings(df)

    highs = [s for s in swings if s["type"] == "HIGH"]
    lows = [s for s in swings if s["type"] == "LOW"]

    if len(highs) < 1 or len(lows) < 1:
        return "NONE"

    close = df["close"].iloc[-1]

    if close > highs[-1]["price"]:
        return "BULLISH"

    if close < lows[-1]["price"]:
        return "BEARISH"

    return "NONE"


# =========================================
# CHANGE OF CHARACTER
# =========================================

def detect_choch(df):

    ema50 = df["ema50"].iloc[-1]
    ema200 = df["ema200"].iloc[-1]

    if ema50 > ema200:
        return "BULLISH"

    if ema50 < ema200:
        return "BEARISH"

    return "NONE"


# =========================================
# FAIR VALUE GAP
# =========================================

def detect_fvg(df):

    if len(df) < 3:
        return False

    c1 = df.iloc[-3]
    c3 = df.iloc[-1]

    bullish = c1["high"] < c3["low"]
    bearish = c1["low"] > c3["high"]

    return bullish or bearish


# =========================================
# ORDER BLOCK
# =========================================

def detect_order_block(df):

    candle = df.iloc[-2]

    return {
        "high": round(candle["high"], 2),
        "low": round(candle["low"], 2),
        "type": "Bullish" if candle["close"] > candle["open"] else "Bearish"
    }


# =========================================
# PREMIUM / DISCOUNT
# =========================================

def premium_discount(df):

    high = df["high"].tail(100).max()
    low = df["low"].tail(100).min()

    equilibrium = (high + low) / 2

    if df["close"].iloc[-1] >= equilibrium:
        return "PREMIUM"

    return "DISCOUNT"


# =========================================
# LIQUIDITY
# =========================================

def detect_liquidity(df):

    high = df["high"].tail(20).max()
    low = df["low"].tail(20).min()

    close = df["close"].iloc[-1]

    if close > high:
        return "BUY SIDE"

    if close < low:
        return "SELL SIDE"

    return "NONE"


# =========================================
# MAIN
# =========================================

def analyze_smc(df):

    return {

        "bos": detect_bos(df),

        "choch": detect_choch(df),

        "liquidity": detect_liquidity(df),

        "fvg": detect_fvg(df),

        "order_block": detect_order_block(df),

        "zone": premium_discount(df),

        "swings": detect_swings(df)

    }
