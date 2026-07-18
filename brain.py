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

# =========================================
# GLOBALS
# =========================================

# Brain memory (stores last analyzed symbol)
BRAIN_MEMORY = {
    "last_symbol": None,
    "last_timeframe": "15m"
}

# =========================================
# MARKETS TO SCAN
# =========================================

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

# =========================================
# SYMBOL ALIASES
# =========================================

SYMBOL_ALIASES = {
    "gold": "XAUUSD",
    "xau": "XAUUSD",
    "bitcoin": "BTCUSD",
    "btc": "BTCUSD",
    "ethereum": "ETHUSD",
    "eth": "ETHUSD",
    "euro": "EURUSD",
    "eurusd": "EURUSD",
    "gbpusd": "GBPUSD",
    "pound": "GBPUSD",
    "us30": "US30",
    "nas100": "NAS100",
}

# =========================================
# ANALYZE ONE MARKET
# =========================================

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
            "ACTIVE" if result["signal"] != "NO TRADE" else "WAITING"
        )
    })

    return result   # <-- only one return

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
    results.sort(key=lambda x: x["confidence"], reverse=True)
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
        if market["confidence"] >= minimum_confidence and market["signal"] != "NO TRADE":
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

    # Best trade
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

    # Scan everything
    if "scan" in question or "markets" in question:
        setups = best_setups(timeframe)
        if not setups:
            return "No high-confidence setups found."
        response = "Today's best setups:\n\n"
        for trade in setups:
            response += f"{trade['symbol']} | {trade['signal']} | {trade['confidence']}%\n"
        return response

    # Trend of last analyzed market
    if "trend" in question:
        symbol = BRAIN_MEMORY["last_symbol"]
        if symbol is None:
            return "Analyze a market first."
        return analyze_symbol(symbol, timeframe)

    return "I don't understand that question yet."

# =========================================
# ANALYZE ANY SYMBOL
# =========================================

def analyze_symbol(symbol, timeframe="15m"):
    """
    Return a detailed analysis for one symbol.
    """
    result = analyze_market(symbol, timeframe)
    if result is None:
        return f"No market data available for {symbol}."

    response = f"""
📈 {symbol}

Signal: {result['signal']}
Confidence: {result['confidence']}%
Status: {result['market_status']}

Entry: {result['entry']}
Stop Loss: {result['stop_loss']}
Take Profit: {result['take_profit']}

AI Rating: {result['rating']}
Reason:
{chr(10).join(result["coach"])}
"""
    # Remember the last market analyzed
    BRAIN_MEMORY["last_symbol"] = symbol
    BRAIN_MEMORY["last_timeframe"] = timeframe
    return response.strip()

# =========================================
# COMMAND ROUTER
# =========================================

def process_command(command, timeframe="15m"):
    """
    Route user commands to the correct Brain function.
    """
    command = command.strip().lower()

    if any(word in command for word in ["scan", "markets", "pairs", "opportunities"]):
        return ask_brain("scan", timeframe)

    if any(word in command for word in ["best", "strongest", "highest", "top"]):
        return ask_brain("best", timeframe)

    return "Command not recognised yet."
