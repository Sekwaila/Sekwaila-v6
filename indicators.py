"""
=========================================
SEKWAILA OMEGA X
Technical Indicators Module
Version: 1.0
=========================================
"""

import pandas as pd
import numpy as np


# ---------------------------------------
# EMA
# ---------------------------------------

def ema(data, period):
    """
    Exponential Moving Average
    """
    return data.ewm(span=period, adjust=False).mean()


# ---------------------------------------
# RSI
# ---------------------------------------

def rsi(data, period=14):
    """
    Relative Strength Index
    """

    delta = data.diff()

    gain = delta.where(delta > 0, 0)

    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


# ---------------------------------------
# ATR
# ---------------------------------------

def atr(df, period=14):
    """
    Average True Range
    """

    high = df["High"]

    low = df["Low"]

    close = df["Close"]

    tr1 = high - low

    tr2 = abs(high - close.shift())

    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    return tr.rolling(period).mean()


# ---------------------------------------
# MACD
# ---------------------------------------

def macd(data):

    ema12 = ema(data, 12)

    ema26 = ema(data, 26)

    macd_line = ema12 - ema26

    signal = macd_line.ewm(span=9, adjust=False).mean()

    histogram = macd_line - signal

    return macd_line, signal, histogram


# ---------------------------------------
# VWAP
# ---------------------------------------

def vwap(df):
    """
    Volume Weighted Average Price
    """

    price = (df["High"] + df["Low"] + df["Close"]) / 3

    return (price * df["Volume"]).cumsum() / df["Volume"].cumsum()


# ---------------------------------------
# VOLUME MOVING AVERAGE
# ---------------------------------------

def volume_ma(df, period=20):

    return df["Volume"].rolling(period).mean()


# ---------------------------------------
# TREND DETECTION
# ---------------------------------------

def trend(close):

    ema50 = ema(close, 50)

    ema200 = ema(close, 200)

    latest = close.iloc[-1]

    if latest > ema50.iloc[-1] > ema200.iloc[-1]:
        return "BULLISH"

    elif latest < ema50.iloc[-1] < ema200.iloc[-1]:
        return "BEARISH"

    return "RANGING"


# ---------------------------------------
# MOMENTUM SCORE
# ---------------------------------------

def momentum_score(close):

    score = 0

    if rsi(close).iloc[-1] > 55:
        score += 1

    if macd(close)[0].iloc[-1] > macd(close)[1].iloc[-1]:
        score += 1

    if close.iloc[-1] > ema(close, 50).iloc[-1]:
        score += 1

    return score
