"""
=========================================
SEKWAILA OMEGA X
Main Trading Engine
Version: 3.0
=========================================
"""

from data import get_market_data
from indicators import calculate_indicators
from ai import ai_confidence


def run_engine(symbol="XAUUSD", timeframe="15m"):
    """
    Runs the complete trading engine.
    """

    # Download market data
    df = get_market_data(symbol, timeframe)

    if df.empty:
        return None

    # Calculate indicators
    df = calculate_indicators(df)

    # AI Analysis
    analysis = ai_confidence(df)

    analysis["symbol"] = symbol
    analysis["timeframe"] = timeframe

    return analysis


if __name__ == "__main__":

    result = run_engine()

    print(result)
