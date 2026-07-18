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

    result.update({

    "symbol": symbol,

    "timeframe": timeframe,

    "market_status": (
        "ACTIVE"
        if result["signal"] != "NO TRADE"
        else "WAITING"
    )

})

return result

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
# =========================================
# BEST SETUPS
# =========================================

def best_setups(timeframe="15m", minimum_confidence=75):
    """
    Return only high-confidence trading setups.
    """

    markets = scan_markets(timeframe)

    setups = []

    for market in markets:

        if (
            market["confidence"] >= minimum_confidence
            and market["signal"] != "NO TRADE"
        ):
            setups.append(market)

    return setups
# =========================================
# ASK THE BRAIN
# =========================================

def ask_brain(question, timeframe="15m"):
    """
    Answer trading questions.
    """

    question = question.lower()

    # -----------------------------
    # Best trade
    # -----------------------------
    if "best" in question or "strongest" in question:

        setups = best_setups(timeframe)

        if not setups:
            return "No high-confidence setups found."

        trade = setups[0]

        return (
            f"Best setup is {trade['symbol']}.\n"
            f"Signal: {trade['signal']}\n"
            f"Confidence: {trade['confidence']}%"
        )

    # -----------------------------
    # Scan everything
    # -----------------------------
    if "scan" in question or "markets" in question:

        setups = best_setups(timeframe)

        if not setups:
            return "No high-confidence setups found."

        response = "Today's best setups:\n\n"

        for trade in setups:

            response += (
                f"{trade['symbol']} | "
                f"{trade['signal']} | "
                f"{trade['confidence']}%\n"
            )

        return response

    return "I don't understand that question yet."
