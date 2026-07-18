"""
=========================================
SEKWAILA OMEGA X
Smart Money Concepts Engine
Version: 3.0
=========================================
"""

import pandas as pd


# ---------------------------------------
# BREAK OF STRUCTURE
# ---------------------------------------

def detect_bos(df):

    if len(df) < 20:
        return "NONE"

    last_close = df["close"].iloc[-1]

    recent_high = df["high"].rolling(20).max().iloc[-2]
    recent_low = df["low"].rolling(20).min().iloc[-2]

    if last_close > recent_high:
        return "BULLISH"

    if last_close < recent_low:
        return "BEARISH"

    return "NONE"


# ---------------------------------------
# CHANGE OF CHARACTER
# ---------------------------------------

def detect_choch(df):

    if len(df) < 50:
        return "NONE"

    ema50 = df["ema50"].iloc[-1]
    ema200 = df["ema200"].iloc[-1]

    if ema50 > ema200:
        return "BULLISH"

    if ema50 < ema200:
        return "BEARISH"

    return "NONE"


# ---------------------------------------
# LIQUIDITY SWEEP
# ---------------------------------------

def detect_liquidity(df):

    high = df["high"].tail(10).max()
    low = df["low"].tail(10).min()

    close = df["close"].iloc[-1]

    if close > high:
        return "BUY SIDE"

    if close < low:
        return "SELL SIDE"

    return "NONE"


# ---------------------------------------
# FAIR VALUE GAP
# ---------------------------------------

def detect_fvg(df):

    if len(df) < 3:
        return False

    c1 = df.iloc[-3]
    c3 = df.iloc[-1]

    if c1["high"] < c3["low"]:
        return True

    if c1["low"] > c3["high"]:
        return True

    return False


# ---------------------------------------
# ORDER BLOCK
# ---------------------------------------

def detect_order_block(df):

    last = df.iloc[-1]

    return {
        "high": round(last["high"], 2),
        "low": round(last["low"], 2)
    }


# ---------------------------------------
# PREMIUM / DISCOUNT
# ---------------------------------------

def premium_discount(df):

    highest = df["high"].tail(100).max()
    lowest = df["low"].tail(100).min()

    equilibrium = (highest + lowest) / 2

    current = df["close"].iloc[-1]

    if current > equilibrium:
        return "PREMIUM"

    return "DISCOUNT"


# ---------------------------------------
# MAIN ANALYSIS
# ---------------------------------------

def analyze_smc(df):

    return {

        "bos": detect_bos(df),

        "choch": detect_choch(df),

        "liquidity": detect_liquidity(df),

        "fvg": detect_fvg(df),

        "order_block": detect_order_block(df),

        "zone": premium_discount(df)

    }
