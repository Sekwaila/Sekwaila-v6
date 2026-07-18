"""
=========================================
SEKWAILA OMEGA X
Institutional AI Engine
Version: 5.0
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
            "rating": "☆☆☆☆☆",
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
    # STAR RATING
    # -----------------------------

    if score >= 90:

        rating = "★★★★★"

    elif score >= 80:

        rating = "★★★★☆"

    elif score >= 70:

        rating = "★★★☆☆"

    elif score >= 60:

        rating = "★★☆☆☆"

    else:

        rating = "★☆☆☆☆"
