"""
=========================================
SEKWAILA OMEGA X
Market Data Module
Version: 1.0
=========================================
"""

import yfinance as yf
import pandas as pd


# ---------------------------------------
# SYMBOL MAPPING
# ---------------------------------------

SYMBOLS = {
    "XAUUSD": "GC=F",
    "BTCUSD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "USDJPY": "JPY=X",
    "US30": "^DJI",
    "SP500": "^GSPC",
}


# ---------------------------------------
# TIMEFRAME MAPPING
# ---------------------------------------

TIMEFRAMES = {
    "M5": "5m",
    "M15": "15m",
    "H1": "1h",
    "H4": "4h",
    "D1": "1d",
}


# ---------------------------------------
# DOWNLOAD MARKET DATA
# ---------------------------------------

def get_market_data(symbol="XAUUSD", timeframe="M15", period="7d"):
    """
    Downloads OHLC market data.
    """

    ticker = SYMBOLS.get(symbol)

    interval = TIMEFRAMES.get(timeframe)

    if ticker is None:
        raise ValueError(f"Unsupported symbol: {symbol}")

    if interval is None:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    try:

        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False
        )

        if df.empty:
            return None

        df = df.dropna()

        return df

    except Exception as e:

        print(f"Market Data Error: {e}")

        return None


# ---------------------------------------
# GET LATEST PRICE
# ---------------------------------------

def get_current_price(symbol="XAUUSD"):

    df = get_market_data(symbol, "M5", "1d")

    if df is None:
        return None

    return float(df["Close"].iloc[-1])


# ---------------------------------------
# CHECK CONNECTION
# ---------------------------------------

def data_available(symbol="XAUUSD"):

    df = get_market_data(symbol)

    return df is not None
