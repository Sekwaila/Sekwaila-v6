"""
===========================================
SEKWAILA OMEGA X
Market Data Module
Version: 2.0.0
===========================================
"""

import yfinance as yf
import pandas as pd
from logger import setup_logger

logger = setup_logger()


def get_market_data(symbol="XAUUSD", timeframe="15m", bars=300):
    """
    Downloads market data from Yahoo Finance.

    Parameters:
        symbol (str): Trading symbol
        timeframe (str): Candle timeframe
        bars (int): Number of candles

    Returns:
        pandas.DataFrame
    """

    symbol_map = {
        "XAUUSD": "GC=F",
        "BTCUSD": "BTC-USD",
        "EURUSD": "EURUSD=X",
        "USDJPY": "JPY=X",
        "US30": "^DJI",
        "SP500": "^GSPC",
    }

    ticker = symbol_map.get(symbol, symbol)

    try:

        df = yf.download(
            ticker,
            period="60d",
            interval=timeframe,
            progress=False,
            auto_adjust=True,
        )

        if df.empty:
            logger.warning(f"No data received for {symbol}")
            return pd.DataFrame()

        df.reset_index(inplace=True)

        df.columns = [c.lower() for c in df.columns]

        logger.info(f"{len(df)} candles loaded for {symbol}")

        return df.tail(bars)

    except Exception as e:

        logger.error(f"Market data error: {e}")

        return pd.DataFrame()


def latest_price(df):
    """
    Returns the latest closing price.
    """

    if df.empty:
        return None

    return float(df["close"].iloc[-1])


def latest_candle(df):
    """
    Returns the latest candle.
    """

    if df.empty:
        return None

    return df.iloc[-1]


if __name__ == "__main__":

    data = get_market_data()

    print(data.tail())

    print("Latest Price:", latest_price(data))
