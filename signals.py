"""
=========================================
SEKWAILA OMEGA X
Institutional Signal Engine
Version: 6.0
Dual Buy/Sell Scoring Engine
=========================================
"""

from datetime import datetime, timezone
from smc import analyze_smc

# =========================================
# SESSIONS
# =========================================

CRYPTO_SYMBOLS = {"BTCUSD", "ETHUSD"}

BUY_THRESHOLD = 70
SELL_THRESHOLD = 70
MIN_SCORE_GAP = 15

RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30


# =========================================
# SESSION DETECTION
# =========================================

def get_current_session(symbol=None):

    now = datetime.now(timezone.utc)

    hour = now.hour

    crypto = symbol in CRYPTO_SYMBOLS

    if 12 <= hour < 16:
        session = "OVERLAP"

    elif 7 <= hour < 12:
        session = "LONDON"

    elif 16 <= hour < 21:
        session = "NEW YORK"

    else:
        session = "ASIAN"

    if now.weekday() >= 5 and not crypto:
        return "CLOSED"

    return session


def session_points(session):

    if session == "OVERLAP":
        return 5

    elif session in ("LONDON", "NEW YORK"):
        return 3

    return 0


# =========================================
# MAIN ENGINE
# =========================================

def generate_signal(df, smc=None, symbol=None):

    if df.empty:

        return {

            "signal": "NO TRADE",

            "confidence": 0,

            "rating": 0,

            "direction": "NO TRADE",

            "buy_score": 0,

            "sell_score": 0,

            "checks": {}

        }

    if smc is None:

        smc = analyze_smc(df)

    buy_score = 0
    sell_score = 0

    checks = {}

    # =====================================
    # EMA TREND
    # =====================================

    ema20 = float(df["ema20"].iloc[-1])
    ema50 = float(df["ema50"].iloc[-1])
    ema200 = float(df["ema200"].iloc[-1])

    trend = "NEUTRAL"

    if ema20 > ema50 > ema200:

        trend = "BULLISH"

        buy_score += 20

    elif ema20 < ema50 < ema200:

        trend = "BEARISH"

        sell_score += 20

    checks["Trend"] = trend

    # =====================================
    # BOS
    # =====================================

    bos = smc["bos"]

    if bos == "BULLISH":
        buy_score += 20

    elif bos == "BEARISH":
        sell_score += 20

    checks["BOS"] = bos

    # =====================================
    # CHOCH
    # =====================================

    choch = smc["choch"]

    if choch == "BULLISH":
        buy_score += 15

    elif choch == "BEARISH":
        sell_score += 15

    checks["CHOCH"] = choch

    # =====================================
    # ORDER BLOCK
    # =====================================

    ob = smc["order_block"]

    if ob["direction"] == "BUY":

        buy_score += 15

    elif ob["direction"] == "SELL":

        sell_score += 15

    checks["Order Block"] = ob["type"]

    # =====================================
    # PREMIUM / DISCOUNT
    # =====================================

    zone = smc["zone"]

    if zone == "DISCOUNT":

        buy_score += 10

    elif zone == "PREMIUM":

        sell_score += 10

    checks["Zone"] = zone

    # =====================================
    # FAIR VALUE GAP
    # =====================================

    if smc["fvg"]:

        if trend == "BULLISH":
            buy_score += 10

        elif trend == "BEARISH":
            sell_score += 10

    checks["FVG"] = "YES" if smc["fvg"] else "NO"

    # =====================================
    # RSI
    # =====================================

    rsi = float(df["rsi"].iloc[-1])

    checks["RSI"] = round(rsi, 2)

    if 45 <= rsi <= 65:
        buy_score += 5

    if 35 <= rsi <= 55:
        sell_score += 5

    # =====================================
    # ATR
    # =====================================

    atr = float(df["atr"].iloc[-1])

    if atr > 0:

        buy_score += 5

        sell_score += 5

    checks["ATR"] = round(atr, 2)

    # =====================================
    # SESSION
    # =====================================

    session = get_current_session(symbol)

    points = session_points(session)

    buy_score += points
    sell_score += points

    checks["Session"] = session
        # =====================================
    # LIQUIDITY BONUS
    # =====================================

    liquidity = smc.get("liquidity", "NEUTRAL")

    checks["Liquidity"] = liquidity

    if liquidity == "EQUAL LOWS":
        buy_score += 5

    elif liquidity == "EQUAL HIGHS":
        sell_score += 5

    # =====================================
    # RSI HARD VETO
    # =====================================

    buy_veto = rsi >= RSI_OVERBOUGHT
    sell_veto = rsi <= RSI_OVERSOLD

    checks["RSI Veto"] = "YES" if (buy_veto or sell_veto) else "NO"

    if buy_veto:
        buy_score = 0

    if sell_veto:
        sell_score = 0

    # =====================================
    # FINAL DECISION
    # =====================================

    score_gap = abs(buy_score - sell_score)

    if (
        buy_score >= BUY_THRESHOLD
        and buy_score > sell_score
        and score_gap >= MIN_SCORE_GAP
    ):

        direction = "BUY"
        confidence = buy_score

    elif (
        sell_score >= SELL_THRESHOLD
        and sell_score > buy_score
        and score_gap >= MIN_SCORE_GAP
    ):

        direction = "SELL"
        confidence = sell_score

    else:

        direction = "NO TRADE"
        confidence = max(buy_score, sell_score)

    # =====================================
    # SIGNAL STRENGTH
    # =====================================

    if direction == "BUY":

        if confidence >= 95:
            signal = "⭐⭐⭐⭐⭐ STRONG BUY"

        elif confidence >= 85:
            signal = "⭐⭐⭐⭐ BUY"

        else:
            signal = "⭐⭐⭐ WATCH BUY"

    elif direction == "SELL":

        if confidence >= 95:
            signal = "⭐⭐⭐⭐⭐ STRONG SELL"

        elif confidence >= 85:
            signal = "⭐⭐⭐⭐ SELL"

        else:
            signal = "⭐⭐⭐ WATCH SELL"

    else:

        signal = "NO TRADE"

    # =====================================
    # TRADE GRADE
    # =====================================

    if confidence >= 95:
        grade = "A+"

    elif confidence >= 90:
        grade = "A"

    elif confidence >= 80:
        grade = "B"

    elif confidence >= 70:
        grade = "C"

    else:
        grade = "D"

    checks["Grade"] = grade

    # =====================================
    # RETURN
    # =====================================

    return {

        "signal": signal,

        "direction": direction,

        "confidence": confidence,

        "rating": round(confidence / 20, 1),

        "buy_score": buy_score,

        "sell_score": sell_score,

        "checks": checks

    }
