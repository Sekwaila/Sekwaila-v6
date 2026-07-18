"""
=========================================
SEKWAILA OMEGA X
Smart Money Concepts (SMC)
Version: 1.0
=========================================
"""

import pandas as pd


# ---------------------------------------
# BREAK OF STRUCTURE (BOS)
# ---------------------------------------

def break_of_structure(df, lookback=5):

    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    recent_high = high.shift(1).rolling(lookback).max()
    recent_low = low.shift(1).rolling(lookback).min()

    if close.iloc[-1] > recent_high.iloc[-1]:
        return "BULLISH"

    if close.iloc[-1] < recent_low.iloc[-1]:
        return "BEARISH"

    return "NONE"


# ---------------------------------------
# CHANGE OF CHARACTER (CHoCH)
# ---------------------------------------

def choch(df):

    bos = break_of_structure(df)

    if bos == "BULLISH":
        return "Bullish CHoCH"

    if bos == "BEARISH":
        return "Bearish CHoCH"

    return "None"


# ---------------------------------------
# LIQUIDITY SWEEP
# ---------------------------------------

def liquidity_sweep(df):

    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    recent_high = high.tail(10).max()
    recent_low = low.tail(10).min()

    if low.iloc[-1] < recent_low and close.iloc[-1] > recent_low:
        return "BUY_SIDE"

    if high.iloc[-1] > recent_high and close.iloc[-1] < recent_high:
        return "SELL_SIDE"

    return "NONE"


# ---------------------------------------
# FAIR VALUE GAP (FVG)
# ---------------------------------------

def fair_value_gap(df):

    if len(df) < 3:
        return None

    candle1 = df.iloc[-3]
    candle2 = df.iloc[-2]
    candle3 = df.iloc[-1]

    if candle3["Low"] > candle1["High"]:
        return {
            "type": "BULLISH",
            "top": candle3["Low"],
            "bottom": candle1["High"]
        }

    if candle3["High"] < candle1["Low"]:
        return {
            "type": "BEARISH",
            "top": candle1["Low"],
            "bottom": candle3["High"]
        }

    return None


# ---------------------------------------
# PREMIUM / DISCOUNT
# ---------------------------------------

def premium_discount(df):

    highest = df["High"].tail(50).max()
    lowest = df["Low"].tail(50).min()

    equilibrium = (highest + lowest) / 2

    price = df["Close"].iloc[-1]

    if price > equilibrium:
        return "PREMIUM"

    return "DISCOUNT"


# ---------------------------------------
# SIMPLE ORDER BLOCK
# ---------------------------------------

def order_block(df):

    last = df.iloc[-2]

    if last["Close"] < last["Open"]:
        return {
            "type": "Bullish",
            "high": last["High"],
            "low": last["Low"]
        }

    return {
        "type": "Bearish",
        "high": last["High"],
        "low": last["Low"]
    }


# ---------------------------------------
# MARKET STRUCTURE SUMMARY
# ---------------------------------------

def market_structure(df):

    return {
        "bos": break_of_structure(df),
        "choch": choch(df),
        "liquidity": liquidity_sweep(df),
        "fvg": fair_value_gap(df),
        "zone": premium_discount(df),
        "order_block": order_block(df)
    }
