"""
=======================
SEKWAILA OMEGA X
Smart Money Concepts Engine
Version: 6.0 (real detection, no stubs)
=======================
"""

import pandas as pd


# ========================
# SWING HIGH / LOW DETECTION
# ========================

def get_swing_points(df, lookback=2):
    """
    Detect swing highs/lows using a simple fractal method:
    a swing high is a bar whose high is the max within a
    window of `lookback` bars on either side (same for lows).

    Returns two lists of (index, price) tuples, oldest to newest.
    """
    swing_highs = []
    swing_lows = []

    if len(df) < (lookback * 2 + 1):
        return swing_highs, swing_lows

    highs = df["high"].values
    lows = df["low"].values

    for i in range(lookback, len(df) - lookback):
        window_high = highs[i - lookback:i + lookback + 1]
        if highs[i] == window_high.max():
            swing_highs.append((i, float(highs[i])))

        window_low = lows[i - lookback:i + lookback + 1]
        if lows[i] == window_low.min():
            swing_lows.append((i, float(lows[i])))

    return swing_highs, swing_lows


# ========================
# BREAK OF STRUCTURE
# ========================

def detect_bos(df, swing_highs, swing_lows):
    """
    BOS = price closes beyond the most recent confirmed swing
    high (bullish) or swing low (bearish), continuing the
    existing structure.
    """
    if not swing_highs or not swing_lows:
        return "NONE"

    last_close = float(df["close"].iloc[-1])
    last_swing_high = swing_highs[-1][1]
    last_swing_low = swing_lows[-1][1]

    if last_close > last_swing_high:
        return "BULLISH"
    elif last_close < last_swing_low:
        return "BEARISH"

    return "NONE"


# ========================
# CHANGE OF CHARACTER
# ========================

def detect_choch(df, swing_highs, swing_lows):
    """
    CHoCH = price breaks structure in the OPPOSITE direction of
    the prior trend, signaling a possible reversal. Requires at
    least two swing highs and two swing lows to establish what
    the prior trend was.
    """
    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return "NONE"

    last_close = float(df["close"].iloc[-1])

    prior_trend = "NONE"
    if swing_highs[-1][1] > swing_highs[-2][1] and swing_lows[-1][1] > swing_lows[-2][1]:
        prior_trend = "BULLISH"
    elif swing_highs[-1][1] < swing_highs[-2][1] and swing_lows[-1][1] < swing_lows[-2][1]:
        prior_trend = "BEARISH"

    if prior_trend == "BULLISH" and last_close < swing_lows[-1][1]:
        return "BEARISH"
    elif prior_trend == "BEARISH" and last_close > swing_highs[-1][1]:
        return "BULLISH"

    return "NONE"


# ========================
# LIQUIDITY (equal highs/lows)
# ========================

def detect_liquidity(swing_highs, swing_lows, tolerance=0.001):
    """
    Flags equal highs/lows (within tolerance) as resting liquidity
    pools — a common SMC target for stop hunts.
    """
    if len(swing_highs) >= 2:
        h1 = swing_highs[-1][1]
        h2 = swing_highs[-2][1]
        if h2 != 0 and abs(h1 - h2) / h2 < tolerance:
            return "EQUAL HIGHS"

    if len(swing_lows) >= 2:
        l1 = swing_lows[-1][1]
        l2 = swing_lows[-2][1]
        if l2 != 0 and abs(l1 - l2) / l2 < tolerance:
            return "EQUAL LOWS"

    return "NEUTRAL"


# ========================
# PREMIUM / DISCOUNT ZONE
# ========================

def detect_zone(df, swing_highs, swing_lows):
    """
    Discount/Premium via the Fibonacci midpoint (50%) between the
    most recent swing high and swing low.
    """
    if not swing_highs or not swing_lows:
        return "NEUTRAL"

    recent_high = swing_highs[-1][1]
    recent_low = swing_lows[-1][1]
    midpoint = (recent_high + recent_low) / 2
    last_close = float(df["close"].iloc[-1])

    if last_close < midpoint:
        return "DISCOUNT"
    elif last_close > midpoint:
        return "PREMIUM"

    return "NEUTRAL"


# ========================
# ORDER BLOCK (simplified)
# ========================

def detect_order_block(df):
    """
    Simplified order block: the last opposite-colored candle
    immediately before a strong impulsive move that closes
    beyond it. Bullish OB = last down-candle before an up-move
    that breaks its high; bearish OB = mirror case.
    """
    if len(df) < 2:
        return {"type": "None", "level": 0, "direction": "N/A"}

    last = df.iloc[-1]
    prev = df.iloc[-2]

    bullish_impulse = last["close"] > last["open"] and last["close"] > prev["high"]
    prev_was_down = prev["close"] < prev["open"]

    bearish_impulse = last["close"] < last["open"] and last["close"] < prev["low"]
    prev_was_up = prev["close"] > prev["open"]

    if prev_was_down and bullish_impulse:
        return {
            "type": "Bullish OB",
            "level": round(float(prev["low"]), 2),
            "direction": "BUY",
        }

    if prev_was_up and bearish_impulse:
        return {
            "type": "Bearish OB",
            "level": round(float(prev["high"]), 2),
            "direction": "SELL",
        }

    return {"type": "None", "level": 0, "direction": "N/A"}


# ========================
# FAIR VALUE GAP
# ========================

def detect_fvg(df, lookback=10):
    """
    Three-candle Fair Value Gap: a bullish FVG exists when
    candle[i]'s low is above candle[i-2]'s high (a gap up that
    price hasn't filled); bearish FVG is the mirror case.
    Checks the most recent `lookback` candles.
    """
    if len(df) < 3:
        return False

    recent = df.tail(lookback).reset_index(drop=True)

    for i in range(2, len(recent)):
        if recent["low"].iloc[i] > recent["high"].iloc[i - 2]:
            return True
        if recent["high"].iloc[i] < recent["low"].iloc[i - 2]:
            return True

    return False


# ========================
# MAIN SMC ENGINE
# ========================

def analyze_smc(df):
    """
    Main Smart Money Concepts analysis.
    Returns a dictionary with all required SMC data.
    """
    if df.empty or len(df) < 10:
        return {
            "bos": "NONE",
            "choch": "NONE",
            "liquidity": "NEUTRAL",
            "zone": "NEUTRAL",
            "order_block": {"type": "None", "level": 0, "direction": "N/A"},
            "fvg": False,
        }

    swing_highs, swing_lows = get_swing_points(df)

    bos = detect_bos(df, swing_highs, swing_lows)
    choch = detect_choch(df, swing_highs, swing_lows)
    liquidity = detect_liquidity(swing_highs, swing_lows)
    zone = detect_zone(df, swing_highs, swing_lows)
    order_block = detect_order_block(df)
    fvg = detect_fvg(df)

    return {
        "bos": bos,
        "choch": choch,
        "liquidity": liquidity,
        "zone": zone,
        "order_block": order_block,
        "fvg": fvg,
    }
