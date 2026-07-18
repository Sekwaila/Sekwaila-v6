"""
===========================================
SEKWAILA OMEGA X
Market Scanner
Version: 1.0
===========================================
"""

from data import get_market_data
from indicators import calculate_indicators
from smc import analyze_smc
from signals import generate_signal
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


def scan_symbol(symbol, timeframe="M15"):
    """
    Scan one market.
    """

    df = get_market_data(symbol, timeframe)

    if df is None or len(df) < 50:
        return None

    df = calculate_indicators(df)

    smc = analyze_smc(df)

    signal = generate_signal(df, smc)

    confidence = ai_confidence(df, signal)

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "signal": signal,
        "confidence": confidence,
        "price": float(df["Close"].iloc[-1]),
    }


def scan_all_markets(timeframe="M15"):
    """
    Scan every symbol in the watchlist.
    """

    results = []

    for symbol in WATCHLIST:
        try:
            result = scan_symbol(symbol, timeframe)

            if result:
                results.append(result)

        except Exception as e:
            print(f"{symbol}: {e}")

    results.sort(
        key=lambda x: x["confidence"],
        reverse=True
    )

    return results


if __name__ == "__main__":

    scans = scan_all_markets()

    print("\n===== MARKET SCAN =====\n")

    for trade in scans:

        print(
            f"{trade['symbol']} | "
            f"{trade['signal']} | "
            f"{trade['confidence']}% | "
            f"{trade['price']}"
        )
