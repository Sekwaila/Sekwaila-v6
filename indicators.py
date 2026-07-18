"""
=========================================
SEKWAILA OMEGA X
Indicators Engine
Version: 3.0
=========================================
"""

import pandas as pd


# ---------------------------------------
# EMA
# ---------------------------------------

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


# ---------------------------------------
# RSI
# ---------------------------------------

def rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


# ---------------------------------------
# ATR
# ---------------------------------------

def atr(df, period=14):

    high_low = df["high"] - df["low"]

    high_close = (df["high"] - df["close"].shift()).abs()

    low_close = (df["low"] - df["close"].shift()).abs()

    tr = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    ).max(axis=1)

    return tr.rolling(period).mean()


# ---------------------------------------
# ADD INDICATORS
# ---------------------------------------

def calculate_indicators(df):

    if df.empty:
        return df

    df = df.copy()

    df["ema20"] = ema(df["close"], 20)

    df["ema50"] = ema(df["close"], 50)

    df["ema200"] = ema(df["close"], 200)

    df["rsi"] = rsi(df["close"])

    df["atr"] = atr(df)

    return df
