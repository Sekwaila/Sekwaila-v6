"""
=========================================
SEKWAILA OMEGA X
Market Data Module
Version: 4.1 (cached + retry/backoff)
=========================================
"""

import time
import pandas as pd
import yfinance as yf


# =========================================
# SYMBOL MAPPING
# =========================================

SYMBOLS = {
    "XAUUSD": "GC=F",
    "BTCUSD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "JPY=X",
    "US30": "^DJI",
    "SP500": "^GSPC",
}


# =========================================
# TIMEFRAME MAPPING
# =========================================

INTERVALS = {
    "1m": "1m",
    "2m": "2m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "60m": "60m",
    "1h": "60m",
    "90m": "90m",
    "1d": "1d",
    "5d": "5d",
    "1wk": "1wk",
}


# =========================================
# SIMPLE TTL CACHE (shared across callers —
# works for both the Streamlit dashboard and
# the Railway worker, since it's plain Python
# and doesn't depend on st.cache_data)
# =========================================

_CACHE = {}
_CACHE_TTL = 60  # seconds — raise this if you're still getting rate-limited


# =========================================
# DOWNLOAD MARKET DATA (cached + retry/backoff)
# =========================================

def get_market_data(symbol="BTCUSD", timeframe="15m", bars=300, retries=3):

    ticker = SYMBOLS.get(symbol, symbol)
    interval = INTERVALS.get(timeframe, "15m")
    cache_key = f"{ticker}_{interval}"
    now = time.time()

    # Serve from cache if still fresh — avoids hammering Yahoo on
    # every Streamlit rerun or every worker scan cycle
    if cache_key in _CACHE:
        cached_df, cached_time = _CACHE[cache_key]
        if now - cached_time < _CACHE_TTL:
            print(f"Using cached data for {cache_key} ({int(now - cached_time)}s old)")
            return cached_df

    for attempt in range(retries):
        try:
            print("=" * 50)
            print("SEKWAILA DATA ENGINE")
            print("Ticker:", ticker)
            print("Interval:", interval)
            print(f"Attempt {attempt + 1}/{retries}")
            print("=" * 50)

            df = yf.download(
                tickers=ticker,
                period="60d",
                interval=interval,
                auto_adjust=True,
                progress=False,
                threads=False,
                prepost=True,
            )

            if df is None or df.empty:
                print("Yahoo Finance returned NO DATA.")
                if attempt < retries - 1:
                    wait = 5 * (attempt + 1)
                    print(f"Retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                return pd.DataFrame()

            df = df.reset_index()

            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]

            df.columns = [str(c).lower() for c in df.columns]

            # Rename first column to datetime
            if "date" in df.columns:
                df.rename(columns={"date": "datetime"}, inplace=True)

            if "datetime" not in df.columns:
                first = df.columns[0]
                df.rename(columns={first: "datetime"}, inplace=True)

            # Ensure required columns exist
            required = ["datetime", "open", "high", "low", "close"]

            for col in required:
                if col not in df.columns:
                    print(f"Missing column: {col}")
                    return pd.DataFrame()

            if "volume" not in df.columns:
                df["volume"] = 0

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

            df = df.tail(bars).reset_index(drop=True)

            print(f"Downloaded {len(df)} candles successfully.")

            _CACHE[cache_key] = (df, now)
            return df

        except Exception as e:
            print("=" * 50)
            print("DATA DOWNLOAD ERROR")
            print(e)
            print("=" * 50)
            if attempt < retries - 1:
                wait = 5 * (attempt + 1)
                print(f"Retrying in {wait}s...")
                time.sleep(wait)
                continue
            return pd.DataFrame()

    return pd.DataFrame()


# =========================================
# LATEST PRICE
# =========================================

def latest_price(df):

    if df.empty:
        return None

    return float(df["close"].iloc[-1])


# =========================================
# LATEST CANDLE
# =========================================

def latest_candle(df):

    if df.empty:
        return None

    return df.iloc[-1]


# =========================================
# TEST
# =========================================

if __name__ == "__main__":

    data = get_market_data("BTCUSD", "15m")

    print(data.tail())

    print("Latest Price:", latest_price(data))
