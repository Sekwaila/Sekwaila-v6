"""
====================================================
SEKWAILA OMEGA X
Indicators Engine
Version: 4.0
Part 1/2
====================================================
"""

import pandas as pd


# ====================================================
# REQUIRED OHLC COLUMNS
# ====================================================

REQUIRED_COLUMNS = [
    "open",
    "high",
    "low",
    "close"
]


# ====================================================
# VALIDATE DATAFRAME
# ====================================================

def validate_dataframe(df):

    if df is None:
        raise ValueError("Dataframe is None.")

    if df.empty:
        raise ValueError("Dataframe is empty.")

    for column in REQUIRED_COLUMNS:

        if column not in df.columns:

            raise ValueError(
                f"Missing required column: {column}"
            )

    return True


# ====================================================
# EXPONENTIAL MOVING AVERAGE
# ====================================================

def ema(series, period):

    return series.ewm(
        span=period,
        adjust=False
    ).mean()


# ====================================================
# WILDER RSI
# ====================================================

def rsi(series, period=14):

    delta = series.diff()

    gain = delta.where(
        delta > 0,
        0.0
    )

    loss = -delta.where(
        delta < 0,
        0.0
    )


    average_gain = gain.ewm(
        alpha=1/period,
        adjust=False
    ).mean()


    average_loss = loss.ewm(
        alpha=1/period,
        adjust=False
    ).mean()


    rs = average_gain / average_loss


    rsi = 100 - (

        100 /

        (1 + rs)

    )


    return rsi


# ====================================================
# TRUE RANGE
# ====================================================

def true_range(df):

    high_low = (

        df["high"]

        -

        df["low"]

    )


    high_close = (

        df["high"]

        -

        df["close"].shift()

    ).abs()


    low_close = (

        df["low"]

        -

        df["close"].shift()

    ).abs()


    tr = pd.concat(

        [

            high_low,

            high_close,

            low_close

        ],

        axis=1

    ).max(axis=1)


    return tr
    # ====================================================
# AVERAGE TRUE RANGE (WILDER)
# ====================================================

def atr(df, period=14):

    tr = true_range(df)

    atr = tr.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    return atr


# ====================================================
# CALCULATE ALL INDICATORS
# ====================================================

def calculate_indicators(df):

    validate_dataframe(df)

    df = df.copy()

    # ===============================================
    # EMA
    # ===============================================

    df["ema20"] = ema(
        df["close"],
        20
    )

    df["ema50"] = ema(
        df["close"],
        50
    )

    df["ema200"] = ema(
        df["close"],
        200
    )

    # ===============================================
    # RSI
    # ===============================================

    df["rsi"] = rsi(
        df["close"],
        14
    )

    # ===============================================
    # ATR
    # ===============================================

    df["atr"] = atr(
        df,
        14
    )

    # ===============================================
    # CLEAN DATA
    # ===============================================

    df = df.dropna()

    df = df.reset_index(
        drop=True
    )

    return df


# ====================================================
# EXPORT
# ====================================================

__all__ = [

    "ema",

    "rsi",

    "atr",

    "calculate_indicators"

            ]
