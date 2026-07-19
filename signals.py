"""
=========================================
SEKWAILA OMEGA X
Institutional Signal Engine
Version: 5.4 (RSI hard veto on overbought/oversold entries)
=========================================
"""

from datetime import datetime, timezone
from smc import analyze_smc


# ============================
# SESSION / KILLZONE DETECTION
# (unchanged from previous version — see comments there)
# ============================

CRYPTO_SYMBOLS = {"BTCUSD", "ETHUSD"}


def get_current_session(symbol=None):
    now = datetime.now(timezone.utc)
    hour = now.hour
    is_crypto = symbol in CRYPTO_SYMBOLS

    if 12 <= hour < 16:
        session = "OVERLAP"
    elif 7 <= hour < 12:
        session = "LONDON"
    elif 16 <= hour < 21:
        session = "NEW YORK"
    else:
        session = "ASIAN"

    if now.weekday() >= 5 and not is_crypto:
        return "CLOSED"

    return session


def session_score(session):
    if session == "OVERLAP":
        return 5
    elif session in ("LONDON", "NEW YORK"):
        return 3
    return 0


# ============================
# RSI VETO THRESHOLDS
#
# Unlike the old soft filter (which only shaved a few points),
# these now BLOCK a signal outright. Buying when RSI is already
# deep overbought — or selling when it's deep oversold — means
# chasing a move that's likely already extended. This is the
# fix for the original problem: BTCUSD at RSI 71+ still counting
# as a valid BUY.
# ============================

RSI_OVERBOUGHT_VETO = 70
RSI_OVERSOLD_VETO = 30


def generate_signal(df, smc=None, symbol=None):

    if df.empty:
        return {
            "signal": "NO TRADE",
            "confidence": 0,
            "rating": 0,
            "direction": "NONE",
            "checks": {}
        }

    if smc is None:
        smc = analyze_smc(df)

    score = 0
    checks = {}

    # ============================
    # EMA TREND (20)
    # ============================

    ema20 = df["ema20"].iloc[-1]
    ema50 = df["ema50"].iloc[-1]
    ema200 = df["ema200"].iloc[-1]

    trend = "NEUTRAL"

    if ema20 > ema50 > ema200:
        trend = "BULLISH"
        score += 20

    elif ema20 < ema50 < ema200:
        trend = "BEARISH"
        score += 20

    checks["Trend"] = trend

    # ============================
    # BOS (20)
    # ============================

    if smc["bos"] != "NONE":
        score += 20

    checks["BOS"] = smc["bos"]

    # ============================
    # CHOCH (15)
    # ============================

    if smc["choch"] != "NONE":
        score += 15

    checks["CHOCH"] = smc["choch"]

    # ============================
    # FAIR VALUE GAP (10)
    # ============================

    if smc["fvg"]:
        score += 10

    checks["FVG"] = "YES" if smc["fvg"] else "NO"

    # ============================
    # ORDER BLOCK (10)
    # ============================

    order_block = smc.get("order_block", {"type": "None", "level": 0, "direction": "N/A"})
    ob_direction = order_block.get("direction", "N/A")
    ob_found = order_block.get("type", "None") != "None"

    if ob_found and (
        (trend == "BULLISH" and ob_direction == "BUY") or
        (trend == "BEARISH" and ob_direction == "SELL")
    ):
        score += 10

    checks["Order Block"] = order_block.get("type", "None")

    # ============================
    # PREMIUM / DISCOUNT (10)
    # ============================

    zone = smc["zone"]

    checks["Zone"] = zone

    if trend == "BULLISH" and zone == "DISCOUNT":
        score += 10

    elif trend == "BEARISH" and zone == "PREMIUM":
        score += 10

    # ============================
    # RSI (5 points for healthy range, PLUS a hard veto)
    # ============================

    rsi = df["rsi"].iloc[-1]

    if 40 <= rsi <= 65:
        score += 5

    checks["RSI"] = round(rsi, 2)

    # ============================
    # ATR (5)
    # ============================

    atr = df["atr"].iloc[-1]

    if atr > 0:
        score += 5

    checks["ATR"] = round(atr, 2)

    # ============================
    # SESSION (5)
    # ============================

    session = get_current_session(symbol=symbol)
    score += session_score(session)

    checks["Session"] = session

    # ============================
    # DIRECTION (before RSI veto, so we know which side to check)
    # ============================

    if trend == "BULLISH":
        direction = "BUY"

    elif trend == "BEARISH":
        direction = "SELL"

    else:
        direction = "NO TRADE"

    # ============================
    # RSI HARD VETO — overrides everything above.
    # A BUY setup with RSI already overbought, or a SELL setup
    # with RSI already oversold, gets killed outright rather
    # than just scored lower. This stops the engine from
    # chasing an already-extended move.
    # ============================

    rsi_veto = False

    if direction == "BUY" and rsi > RSI_OVERBOUGHT_VETO:
        rsi_veto = True
    elif direction == "SELL" and rsi < RSI_OVERSOLD_VETO:
        rsi_veto = True

    checks["RSI Veto"] = "YES" if rsi_veto else "NO"

    if rsi_veto:
        direction = "NO TRADE"
        signal = "NO TRADE"

    else:
        if score >= 90:
            signal = f"⭐⭐⭐⭐⭐ STRONG {direction}"

        elif score >= 75:
            signal = f"⭐⭐⭐⭐ {direction}"

        elif score >= 60:
            signal = f"⭐⭐⭐ WATCH {direction}"

        else:
            direction = "NO TRADE"
            signal = "NO TRADE"

    return {
        "signal": signal,
        "confidence": score,
        "rating": score,
        "direction": direction,
        "checks": checks
    }
