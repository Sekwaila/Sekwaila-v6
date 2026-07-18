"""
===========================================
SEKWAILA OMEGA X
Technical Indicators
Version: 2.0.0
===========================================
"""

import pandas as pd


def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def rsi(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


def atr(df, period=14):

    high = df["high"]

    low = df["low"]

    close = df["close"]

    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    return tr.rolling(period).mean()


def macd(series):

    ema12 = ema(series, 12)

    ema26 = ema(series, 26)

    macd_line = ema12 - ema26

    signal = ema(macd_line, 9)

    histogram = macd_line - signal

    return macd_line, signal, histogram


def bollinger_bands(series, period=20):

    middle = series.rolling(period).mean()

    std = series.rolling(period).std()

    upper = middle + (std * 2)

    lower = middle - (std * 2)

    return upper, middle, lower


def calculate_indicators(df):

    df = df.copy()

    df["ema20"] = ema(df["close"], 20)

    df["ema50"] = ema(df["close"], 50)

    df["ema200"] = ema(df["close"], 200)

    df["rsi"] = rsi(df["close"])

    df["atr"] = atr(df)

    macd_line, signal, histogram = macd(df["close"])

    df["macd"] = macd_line

    df["macd_signal"] = signal

    df["macd_hist"] = histogram

    upper, middle, lower = bollinger_bands(df["close"])

    df["bb_upper"] = upper

    df["bb_middle"] = middle

    df["bb_lower"] = lower

    return df
