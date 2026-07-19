"""
=========================================
SEKWAILA OMEGA X
Institutional Signal Engine
Version: 5.3 (symbol-aware session detection)
=========================================
"""

from datetime import datetime, timezone
from smc import analyze_smc


# ============================
# SESSION / KILLZONE DETECTION
#
# All times here are UTC — correct regardless of server location
# or your local SAST timezone. Crypto (BTCUSD, ETHUSD) trades
# 24/7, so it never gets marked "CLOSED" for the weekend the way
# forex/US30/SP500 do.
#
# Reference (Northern Hemisphere summer / DST in effect):
#   London session:    07:00-16:00 UTC  -> 09:00-18:00 SAST
#   New York session:  16:00-21:00 UTC  -> 18:00-23:00 SAST
#   Overlap (best):    12:00-16:00 UTC  -> 14:00-18:00 SAST
#   Asian session:     21:00-07:00 UTC  -> 23:00-09:00 SAST
# In Northern Hemisphere winter, London/NY windows shift back
# by about 1 hour in UTC terms.
# ============================

CRYPTO_SYMBOLS = {"BTCUSD", "ETHUSD"}


def get_current_session(symbol=None):
    """
    Returns one of: "OVERLAP", "LONDON", "NEW YORK", "ASIAN", "CLOSED"
    based on the current UTC time and day of week.

    Forex/CFD/index instruments are closed on weekends. Crypto
    (BTCUSD, ETHUSD) trades 24/7, so weekend "CLOSED" never
    applies to it — it still gets a session label based on time
    of day (liquidity does still ebb and flow with global
    regions even though the market never technically shuts).
    """
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
    """
    Points awarded based on session quality. Overlap gets full
    marks (highest liquidity), single sessions get partial credit,
    Asian/closed get none — thin liquidity produces less reliable
    signals.
    """
    if session == "OVERLAP":
        return 5
    elif session in ("LONDON", "NEW YORK"):
        return 3
    return 0


def generate_signal(df, smc=None, symbol=None):

    if df.empty:
        return {
            "signal": "NO TRADE",
            "confidence": 0,
            "rating": 0,
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
    # ORDER BLOCK (10) — real detection from smc.py, only
    # credited when it agrees with the current trend.
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
    # RSI (5)
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
    # SESSION (5) — symbol-aware. Crypto never shows CLOSED
    # for the weekend; other instruments correctly do.
    # ============================

    session = get_current_session(symbol=symbol)
    score += session_score(session)

    checks["Session"] = session

    # ============================
    # FINAL SIGNAL
    # ============================

    if trend == "BULLISH":
        direction = "BUY"

    elif trend == "BEARISH":
        direction = "SELL"

    else:
        direction = "NO TRADE"

    if score >= 90:
        signal = f"⭐⭐⭐⭐⭐ STRONG {direction}"

    elif score >= 75:
        signal = f"⭐⭐⭐⭐ {direction}"

    elif score >= 60:
        signal = f"⭐⭐⭐ WATCH {direction}"

    else:
        signal = "NO TRADE"

    return {
        "signal": signal,
        "confidence": score,
        "rating": score,
        "direction": direction,
        "checks": checks
    }
