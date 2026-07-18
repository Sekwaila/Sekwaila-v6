"""
=========================================
SEKWAILA OMEGA X
AI Brain
Version: 1.2 (fully defensive)
=========================================
"""

from ai import ai_confidence
from data import get_market_data
from indicators import calculate_indicators

# =========================================
# GLOBALS
# =========================================

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
    "NAS100",
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
# HELPER: resolve alias
# =========================================

def resolve_symbol(symbol):
    """Convert alias to real symbol if possible, else return uppercase."""
    symbol_lower = symbol.lower()
    return SYMBOL_ALIASES.get(symbol_lower, symbol.upper())

# =========================================
# ANALYZE ONE MARKET (with error handling)
# =========================================

def analyze_market(symbol, timeframe="15m"):
    try:
        df = get_market_data(symbol, timeframe)
        if df.empty:
            return None
        df = calculate_indicators(df)
        result = ai_confidence(df)
        # Ensure required keys exist
        required_keys = ["signal", "confidence", "entry", "stop_loss", "take_profit", "rating"]
        for key in required_keys:
            if key not in result:
                result[key] = None if key != "confidence" else 0
        result.update({
            "symbol": symbol,
            "timeframe": timeframe,
            "market_status": "ACTIVE" if result.get("signal") != "NO TRADE" else "WAITING"
        })
        return result
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

# =========================================
# SCAN ALL MARKETS (skip failures)
# =========================================

def scan_markets(timeframe="15m"):
    results = []
    for symbol in MARKETS:
        print(f"Scanning {symbol}...")
        analysis = analyze_market(symbol, timeframe)
        if analysis is not None:
            results.append(analysis)
        else:
            print(f"Skipping {symbol} (no data or error)")
    results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    return results

# =========================================
# BEST SETUPS
# =========================================

def best_setups(timeframe="15m", minimum_confidence=75):
    markets = scan_markets(timeframe)
    setups = []
    for market in markets:
        if market.get("confidence", 0) >= minimum_confidence and market.get("signal") != "NO TRADE":
            setups.append(market)
    return setups

# =========================================
# ASK THE BRAIN (defensive access)
# =========================================

def ask_brain(question, timeframe="15m"):
    question = question.lower()
    if "best" in question or "strongest" in question:
        setups = best_setups(timeframe)
        if not setups:
            return "No high-confidence setups found."
        trade = setups[0]
        return (f"Best setup is {trade.get('symbol', 'Unknown')}.\n"
                f"Signal: {trade.get('signal', 'N/A')}\n"
                f"Confidence: {trade.get('confidence', 0)}%")
    if "scan" in question or "markets" in question:
        setups = best_setups(timeframe)
        if not setups:
            return "No high-confidence setups found."
        response = "Today's best setups:\n\n"
        for trade in setups:
            response += f"{trade.get('symbol', 'Unknown')} | {trade.get('signal', 'N/A')} | {trade.get('confidence', 0)}%\n"
        return response
    if "trend" in question:
        symbol = BRAIN_MEMORY.get("last_symbol")
        if symbol is None:
            return "Analyze a market first."
        return analyze_symbol(symbol, timeframe)
    return "I don't understand that question yet."

# =========================================
# ANALYZE ANY SYMBOL (with alias resolution and defensive access)
# =========================================

def analyze_symbol(symbol, timeframe="15m"):
    real_symbol = resolve_symbol(symbol)
    result = analyze_market(real_symbol, timeframe)
    if result is None:
        return f"No market data available for {real_symbol} (alias: {symbol})."
    # Build response with .get() defaults
    signal = result.get('signal', 'N/A')
    confidence = result.get('confidence', 0)
    status = result.get('market_status', 'Unknown')
    entry = result.get('entry', '--')
    stop_loss = result.get('stop_loss', '--')
    take_profit = result.get('take_profit', '--')
    rating = result.get('rating', 'N/A')
    coach = result.get('coach', ['No coach details'])
    if isinstance(coach, list):
        coach_text = "\n".join(coach)
    else:
        coach_text = str(coach)

    response = f"""
📈 {real_symbol}

Signal: {signal}
Confidence: {confidence}%
Status: {status}

Entry: {entry}
Stop Loss: {stop_loss}
Take Profit: {take_profit}

AI Rating: {rating}
Reason:
{coach_text}
"""
    BRAIN_MEMORY["last_symbol"] = real_symbol
    BRAIN_MEMORY["last_timeframe"] = timeframe
    return response.strip()

# =========================================
# COMMAND ROUTER – detects symbols in natural language
# =========================================

def process_command(command, timeframe="15m"):
    command = command.strip().lower()
    # 1. Check for scan/opportunities
    if any(word in command for word in ["scan", "markets", "pairs", "opportunities"]):
        return ask_brain("scan", timeframe)
    # 2. Check for best/strongest
    if any(word in command for word in ["best", "strongest", "highest", "top"]):
        return ask_brain("best", timeframe)
    # 3. Check if the command contains any known symbol or alias
    words = command.replace("/", " ").replace(",", " ").split()
    for word in words:
        resolved = resolve_symbol(word)
        if resolved in MARKETS:
            return analyze_symbol(resolved, timeframe)
    # 4. If nothing matches
    return "Command not recognised yet. Try /best, /scan, or ask about a symbol like BTCUSD."
