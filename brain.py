"""
=========================================
SEKWAILA OMEGA X
AI Brain
Version: 1.0
=========================================
"""

from ai import ai_confidence
from data import get_market_data
from indicators import calculate_indicators


# Markets to scan
MARKETS = [

    "BTCUSD",
    "ETHUSD",
    "XAUUSD",
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "US30",
    "SP500",

]


def analyze_market(symbol, timeframe="15m"):
    """
    Analyze one market.
    """

    df = get_market_data(symbol, timeframe)

    if df.empty:
        return None

    df = calculate_indicators(df)

    result = ai_confidence(df)

    result["symbol"] = symbol
    result["timeframe"] = timeframe

    return result
# =========================================
# SCAN ALL MARKETS
# =========================================

def scan_markets(timeframe="15m"):
    """
    Scan all configured markets and rank them by confidence.
    """

    results = []

    for symbol in MARKETS:

        print(f"Scanning {symbol}...")

        analysis = analyze_market(symbol, timeframe)

        if analysis is not None:
            results.append(analysis)

    # Highest confidence first
    results.sort(
        key=lambda x: x["confidence"],
        reverse=True
    )

    return results
