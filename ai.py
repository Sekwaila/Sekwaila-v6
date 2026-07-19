"""
=========================================
SEKWAILA OMEGA X
Institutional AI Engine
Version: 5.1 (numeric rating, fixed dashboard compatibility)
=========================================
"""

from signals import generate_signal
from smc import analyze_smc


# =========================================
# AI DECISION ENGINE
# =========================================

def ai_confidence(df):

    if df.empty:

        return {
            "signal": "NO TRADE",
            "confidence": 0,
            "rating": 0,
            "direction": "NONE",
            "entry": None,
            "stop_loss": None,
            "take_profit": None,
            "score": 0,
            "checks": {},
            "coach": [],
            "smc": {}
        }

    # -----------------------------
    # MARKET ANALYSIS
    # -----------------------------

    smc = analyze_smc(df)

    signal = generate_signal(df, smc)

    score = signal["confidence"]

    coach = []

    checks = signal["checks"]

    # -----------------------------
    # AI EXPLANATIONS
    # -----------------------------

    if checks["Trend"] == "BULLISH":
        coach.append("Market trend is bullish.")

    elif checks["Trend"] == "BEARISH":
        coach.append("Market trend is bearish.")

    if checks["BOS"] != "NONE":
        coach.append("Break of Structure confirmed.")

    if checks["CHOCH"] != "NONE":
        coach.append("Change of Character confirmed.")

    if checks["FVG"] == "YES":
        coach.append("Fair Value Gap detected.")

    if checks["Zone"] == "DISCOUNT":
        coach.append("Price is trading in a discount zone.")

    elif checks["Zone"] == "PREMIUM":
        coach.append("Price is trading in a premium zone.")

    if checks["Session"] == "ACTIVE":
        coach.append("Trading session is active.")

    # -----------------------------
    # PRICE LEVELS
    # -----------------------------

    entry = float(df["close"].iloc[-1])

    atr = float(df["atr"].iloc[-1])

    direction = signal["direction"]

    if direction == "BUY":

        stop_loss = round(entry - (atr * 1.5), 2)

        take_profit = round(entry + (atr * 3), 2)

    elif direction == "SELL":

        stop_loss = round(entry + (atr * 1.5), 2)

        take_profit = round(entry - (atr * 3), 2)

    else:

        stop_loss = None

        take_profit = None

    # -----------------------------
    # NUMERIC RATING (0-5 scale, derived from score)
    # Kept as a number so it works with the dashboard's
    # rating_to_stars() converter and Telegram formatting —
    # do NOT change this back to a pre-formatted star string.
    # -----------------------------

    rating = round(score / 20, 1)

    # -----------------------------
    # FINAL AI RESULT
    # -----------------------------

    return {

        "signal": signal["signal"],

        "confidence": score,

        "rating": rating,

        "direction": direction,

        "entry": round(entry, 2),

        "stop_loss": stop_loss,

        "take_profit": take_profit,

        "buy_score": score if direction == "BUY" else 0,

        "sell_score": score if direction == "SELL" else 0,

        "checks": checks,

        "coach": coach,

        "smc": smc

    }


# =========================================
# TEST
# =========================================

if __name__ == "__main__":

    from data import get_market_data
    from indicators import calculate_indicators

    df = get_market_data("BTCUSD", "15m")

    if not df.empty:

        df = calculate_indicators(df)

        result = ai_confidence(df)

        print(result)

    else:

        print("No market data.")
