"""
=========================================
SEKWAILA OMEGA X
Market Data Module
Version: 3.0
=========================================
"""

import yfinance as yf
import pandas as pd


# ---------------------------------------
# YAHOO SYMBOL MAP
# ---------------------------------------

SYMBOLS = {
    "XAUUSD": "GC=F",
    "BTCUSD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "JPY=X",
    "US30": "^DJI",
    "SP500": "^GSPC",
}


# ---------------------------------------
# TIMEFRAME MAP
# ---------------------------------------

TIMEFRAMES = {
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "60m",
    "1d": "1d",
}


# ---------------------------------------
# DOWNLOAD DATA
# ---------------------------------------

def get_market_data(symbol="XAUUSD", timeframe="15m", bars=300):

    ticker = SYMBOLS.get(symbol, symbol)
    interval = TIMEFRAMES.get(timeframe, "15m")

    try:

        df = yf.download(
            ticker,
            period="60d",
            interval=interval,
            progress=False,
            auto_adjust=True,
            threads=False,
        )

        if df.empty:
            return pd.DataFrame()

        df.reset_index(inplace=True)

        # Standardize column names
        df.columns = [str(c).lower() for c in df.columns]

        # Rename date column
        if "date" in df.columns:
            df.rename(columns={"date": "datetime"}, inplace=True)

        if "datetime" not in df.columns:
            df.rename(columns={df.columns[0]: "datetime"}, inplace=True)

        # Keep only the columns used by the project
        df = df[
            [
                "datetime",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
        ]

        return df.tail(bars).reset_index(drop=True)

    except Exception as e:

        print("DATA ERROR:", e)

        return pd.DataFrame()


# ---------------------------------------
# LATEST PRICE
# ---------------------------------------

def latest_price(df):

    if df.empty:
        return None

    return float(df.iloc[-1]["close"])


# ---------------------------------------
# LATEST CANDLE
# ---------------------------------------

def latest_candle(df):

    if df.empty:
        return None

    return df.iloc[-1]
