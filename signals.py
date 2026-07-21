"""
=====================================================
SEKWAILA OMEGA X
Institutional Signal Engine
Version: 7.0
Part 1/2
=====================================================
"""

from datetime import datetime, timezone
from smc import analyze_smc


# =====================================================
# CONFIGURATION
# =====================================================

BUY_THRESHOLD = 70
SELL_THRESHOLD = 70
MIN_SCORE_GAP = 15

RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

ATR_MIN = 0.0001

CRYPTO_SYMBOLS = {
    "BTCUSD",
    "ETHUSD"
}


# =====================================================
# REQUIRED INDICATORS
# =====================================================

REQUIRED_COLUMNS = [

    "ema20",
    "ema50",
    "ema200",

    "rsi",

    "atr"

]


# =====================================================
# VALIDATE DATA
# =====================================================

def validate_dataframe(df):

    if df is None:
        raise ValueError("Dataframe is None.")

    if df.empty:
        raise ValueError("Dataframe is empty.")

    for column in REQUIRED_COLUMNS:

        if column not in df.columns:

            raise ValueError(
                f"Missing indicator column: {column}"
            )

    return True


# =====================================================
# MARKET SESSION
# =====================================================

def get_current_session(symbol=None):

    now = datetime.now(timezone.utc)

    hour = now.hour

    crypto = symbol in CRYPTO_SYMBOLS


    if now.weekday() >= 5 and not crypto:
        return "CLOSED"


    if 12 <= hour < 16:
        return "OVERLAP"

    elif 7 <= hour < 12:
        return "LONDON"

    elif 16 <= hour < 21:
        return "NEW YORK"

    return "ASIAN"



def session_bonus(session):

    if session == "OVERLAP":
        return 5

    if session in ("LONDON", "NEW YORK"):
        return 3

    return 0


# =====================================================
# SCORE HELPERS
# =====================================================

def add_buy(score, points):

    return score + points


def add_sell(score, points):

    return score + points


# =====================================================
# MAIN SIGNAL ENGINE
# =====================================================

def generate_signal(

        df,

        smc=None,

        symbol=None

):

    validate_dataframe(df)


    if smc is None:

        smc = analyze_smc(df)


    buy_score = 0

    sell_score = 0

    checks = {}


    # =================================================
    # EMA TREND
    # =================================================

    ema20 = float(df["ema20"].iloc[-1])
    ema50 = float(df["ema50"].iloc[-1])
    ema200 = float(df["ema200"].iloc[-1])


    trend = "NEUTRAL"


    if ema20 > ema50 > ema200:

        trend = "BULLISH"

        buy_score = add_buy(
            buy_score,
            20
        )


    elif ema20 < ema50 < ema200:

        trend = "BEARISH"

        sell_score = add_sell(
            sell_score,
            20
        )


    checks["Trend"] = trend


    # =================================================
    # BOS
    # =================================================

    bos = smc.get(
        "bos",
        "NONE"
    )


    if bos == "BULLISH":

        buy_score = add_buy(
            buy_score,
            20
        )


    elif bos == "BEARISH":

        sell_score = add_sell(
            sell_score,
            20
        )


    checks["BOS"] = bos


    # =================================================
    # CHOCH
    # =================================================

    choch = smc.get(
        "choch",
        "NONE"
    )


    if choch == "BULLISH":

        buy_score = add_buy(
            buy_score,
            15
        )


    elif choch == "BEARISH":

        sell_score = add_sell(
            sell_score,
            15
        )


    checks["CHOCH"] = choch


    # =================================================
    # ORDER BLOCK
    # =================================================

    order_block = smc.get(
        "order_block",
        {}
    )


    ob_direction = order_block.get(
        "direction",
        "NONE"
    )


    if ob_direction == "BUY":

        buy_score = add_buy(
            buy_score,
            15
        )


    elif ob_direction == "SELL":

        sell_score = add_sell(
            sell_score,
            15
        )


    checks["Order Block"] = order_block.get(
        "type",
        "NONE"
    )


    # =================================================
    # PREMIUM / DISCOUNT
    # =================================================

    zone = smc.get(
        "zone",
        "NEUTRAL"
    )


    if zone == "DISCOUNT":

        buy_score = add_buy(
            buy_score,
            10
        )


    elif zone == "PREMIUM":

        sell_score = add_sell(
            sell_score,
            10
        )


    checks["Zone"] = zone
       # =================================================
    # FAIR VALUE GAP
    # =================================================

    fvg = smc.get("fvg", {})

    fvg_type = fvg.get(
        "type",
        "NONE"
    )


    if fvg_type == "BULLISH FVG":

        buy_score = add_buy(
            buy_score,
            10
        )


    elif fvg_type == "BEARISH FVG":

        sell_score = add_sell(
            sell_score,
            10
        )


    checks["FVG"] = fvg_type


    # =================================================
    # LIQUIDITY
    # =================================================

    liquidity = smc.get(
        "liquidity",
        {}
    )


    liquidity_type = liquidity.get(
        "type",
        "NONE"
    )


    if liquidity_type == "EQUAL LOWS":

        buy_score = add_buy(
            buy_score,
            5
        )


    elif liquidity_type == "EQUAL HIGHS":

        sell_score = add_sell(
            sell_score,
            5
        )


    checks["Liquidity"] = liquidity_type


    # =================================================
    # RSI
    # =================================================

    rsi = float(
        df["rsi"].iloc[-1]
    )


    checks["RSI"] = round(
        rsi,
        2
    )


    if 50 <= rsi <= 65:

        buy_score = add_buy(
            buy_score,
            5
        )


    elif 35 <= rsi < 50:

        sell_score = add_sell(
            sell_score,
            5
        )


    # =================================================
    # ATR
    # =================================================

    atr = float(
        df["atr"].iloc[-1]
    )


    checks["ATR"] = round(
        atr,
        5
    )


    if atr >= ATR_MIN:

        buy_score = add_buy(
            buy_score,
            5
        )

        sell_score = add_sell(
            sell_score,
            5
        )


    # =================================================
    # SESSION BONUS
    # =================================================

    session = get_current_session(
        symbol
    )


    bonus = session_bonus(
        session
    )


    buy_score += bonus
    sell_score += bonus


    checks["Session"] = session


    # =================================================
    # RSI SAFETY VETO
    # =================================================

    if rsi >= RSI_OVERBOUGHT:

        buy_score = 0

        checks["Buy Veto"] = True

    else:

        checks["Buy Veto"] = False


    if rsi <= RSI_OVERSOLD:

        sell_score = 0

        checks["Sell Veto"] = True

    else:

        checks["Sell Veto"] = False


    # =================================================
    # FINAL DECISION
    # =================================================

    score_gap = abs(
        buy_score -
        sell_score
    )


    direction = "NO TRADE"


    confidence = max(
        buy_score,
        sell_score
    )


    if (

        buy_score >= BUY_THRESHOLD

        and

        buy_score > sell_score

        and

        score_gap >= MIN_SCORE_GAP

    ):

        direction = "BUY"

        confidence = buy_score


    elif (

        sell_score >= SELL_THRESHOLD

        and

        sell_score > buy_score

        and

        score_gap >= MIN_SCORE_GAP

    ):

        direction = "SELL"

        confidence = sell_score


    # =================================================
    # SIGNAL LABEL
    # =================================================

    if direction == "BUY":

        if confidence >= 95:

            signal = "⭐⭐⭐⭐⭐ STRONG BUY"

        elif confidence >= 85:

            signal = "⭐⭐⭐⭐ BUY"

        else:

            signal = "⭐⭐⭐ BUY"


    elif direction == "SELL":

        if confidence >= 95:

            signal = "⭐⭐⭐⭐⭐ STRONG SELL"

        elif confidence >= 85:

            signal = "⭐⭐⭐⭐ SELL"

        else:

            signal = "⭐⭐⭐ SELL"


    else:

        signal = "NO TRADE"


    # =================================================
    # GRADE
    # =================================================

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


    # =================================================
    # RETURN
    # =================================================

    return {

        "signal": signal,

        "direction": direction,

        "confidence": confidence,

        "rating": round(
            confidence / 20,
            1
        ),

        "buy_score": buy_score,

        "sell_score": sell_score,

        "score_gap": score_gap,

        "checks": checks

    } 
