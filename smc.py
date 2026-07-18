"""
=========================================
SEKWAILA OMEGA X
Smart Money Concepts
Version 2.0
=========================================
"""

import pandas as pd


# ---------------------------------
# Swing Highs / Lows
# ---------------------------------

def swing_high(df, lookback=5):

    return df["high"].rolling(lookback, center=True).max()


def swing_low(df, lookback=5):

    return df["low"].rolling(lookback, center=True).min()


# ---------------------------------
# Break Of Structure
# ---------------------------------

def break_of_structure(df):

    high = df["high"].iloc[-2]

    low = df["low"].iloc[-2]

    close = df["close"].iloc[-1]

    if close > high:
        return "BULLISH"

    if close < low:
        return "BEARISH"

    return "NONE"


# ---------------------------------
# Change Of Character
# ---------------------------------

def choch(df):

    bos = break_of_structure(df)

    if bos == "BULLISH":
        return "Bullish"

    if bos == "BEARISH":
        return "Bearish"

    return "None"


# ---------------------------------
# Fair Value Gap
# ---------------------------------

def fair_value_gap(df):

    if len(df) < 3:
        return None

    first = df.iloc[-3]

    third = df.iloc[-1]

    if third["low"] > first["high"]:

        return {

            "type": "Bullish",

            "top": third["low"],

            "bottom": first["high"]

        }

    if third["high"] < first["low"]:

        return {

            "type": "Bearish",

            "top": first["low"],

            "bottom": third["high"]

        }

    return None


# ---------------------------------
# Order Block
# ---------------------------------

def order_block(df):

    candle = df.iloc[-2]

    if candle["close"] < candle["open"]:

        return {

            "type": "Bullish",

            "high": candle["high"],

            "low": candle["low"]

        }

    return {

        "type": "Bearish",

        "high": candle["high"],

        "low": candle["low"]

    }


# ---------------------------------
# Liquidity Sweep
# ---------------------------------

def liquidity(df):

    recent_high = df["high"].tail(10).max()

    recent_low = df["low"].tail(10).min()

    last = df.iloc[-1]

    if last["low"] < recent_low:

        return "BUY_SIDE"

    if last["high"] > recent_high:

        return "SELL_SIDE"

    return "NONE"


# ---------------------------------
# Premium / Discount
# ---------------------------------

def premium_discount(df):

    highest = df["high"].tail(50).max()

    lowest = df["low"].tail(50).min()

    eq = (highest + lowest) / 2

    if df["close"].iloc[-1] > eq:

        return "PREMIUM"

    return "DISCOUNT"


# ---------------------------------
# Full SMC Analysis
# ---------------------------------

def analyze_smc(df):

    return {

        "bos": break_of_structure(df),

        "choch": choch(df),

        "fvg": fair_value_gap(df),

        "order_block": order_block(df),

        "liquidity": liquidity(df),

        "zone": premium_discount(df)

    }
