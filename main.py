"""
===========================================
SEKWAILA OMEGA X
Main Trading Engine
Version: 1.0.0
===========================================
"""

from data import get_market_data
from indicators import calculate_indicators
from smc import analyze_smc
from signals import generate_signal
from risk import calculate_risk
from ai import analyze_trade


def run_engine(symbol="XAUUSD", timeframe="M15"):
    """
    Runs the complete trading engine.
    """

    # 1. Get market data
    data = get_market_data(symbol, timeframe)

    # 2. Calculate indicators
    indicators = calculate_indicators(data)

    # 3. Smart Money Concept analysis
    smc = analyze_smc(data)

    # 4. Generate trading signal
    signal = generate_signal(data, indicators, smc)

    # 5. Calculate risk
    risk = calculate_risk(signal)

    # 6. AI confidence
    ai = analyze_trade(data, indicators, smc)

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "signal": signal,
        "risk": risk,
        "ai": ai,
        "indicators": indicators,
        "smc": smc,
    }


if __name__ == "__main__":
    result = run_engine()
    print(result)
