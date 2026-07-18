"""
=========================================
SEKWAILA OMEGA X
Market Scanner
Version: 3.0
=========================================
"""

from data import get_market_data
from indicators import calculate_indicators
from ai import ai_confidence


WATCHLIST = [
    "XAUUSD",
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "BTCUSD",
    "US30",
    "SP500",
]


def scan_symbol(symbol="XAUUSD", timeframe="15m"):
    """
    Scan a single market.
    """

    df = get_market_data(symbol, timeframe)

    if df.empty:
        return None

    df = calculate_indicators(df)

    result = ai_confidence(df)

    result["symbol"] = symbol
    result["timeframe"] = timeframe

    return result


def scan_all_markets(timeframe="15m"):
    """
    Scan every symbol in the watchlist.
    """

    trades = []

    for symbol in WATCHLIST:

        try:

            trade = scan_symbol(symbol, timeframe)

            if trade is not None:
                trades.append(trade)

        except Exception as e:

            print(f"{symbol}: {e}")

    trades.sort(
        key=lambda x: x["confidence"],
        reverse=True
    )

    return trades


if __name__ == "__main__":

    results = scan_all_markets()

    print("\n===== SEKWAILA OMEGA X =====\n")

    for trade in results:

        print(
            f"{trade['symbol']} | "
            f"{trade['signal']} | "
            f"{trade['confidence']}%"
        )
