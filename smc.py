"""
=============================
SEKWAILA OMEGA X
Smart Money Concepts Engine
Version: 7.0
Part 1/2
=============================
"""

import pandas as pd


# =====================================
# DATA VALIDATION
# =====================================

def validate_dataframe(df):

    required = [
        "open",
        "high",
        "low",
        "close"
    ]

    for col in required:
        if col not in df.columns:
            raise ValueError(
                f"Missing required OHLC column: {col}"
            )

    if df.empty:
        raise ValueError(
            "Dataframe is empty"
        )

    return True



# =====================================
# SWING HIGH / LOW DETECTION
# =====================================

def get_swing_points(df, lookback=3):

    swing_highs = []
    swing_lows = []

    if len(df) < (lookback * 2 + 1):
        return swing_highs, swing_lows


    highs = df["high"].values
    lows = df["low"].values


    for i in range(
        lookback,
        len(df) - lookback
    ):

        high_window = highs[
            i-lookback:i+lookback+1
        ]

        low_window = lows[
            i-lookback:i+lookback+1
        ]


        # Swing High

        if highs[i] == max(high_window):

            swing_highs.append(
                (
                    i,
                    float(highs[i])
                )
            )


        # Swing Low

        if lows[i] == min(low_window):

            swing_lows.append(
                (
                    i,
                    float(lows[i])
                )
            )


    return (
        swing_highs,
        swing_lows
    )



# =====================================
# MARKET STRUCTURE DIRECTION
# =====================================

def get_market_structure(
        swing_highs,
        swing_lows
):

    if len(swing_highs) < 2:
        return "NEUTRAL"

    if len(swing_lows) < 2:
        return "NEUTRAL"



    last_high = swing_highs[-1][1]
    prev_high = swing_highs[-2][1]

    last_low = swing_lows[-1][1]
    prev_low = swing_lows[-2][1]


    # Higher High + Higher Low

    if (
        last_high > prev_high
        and
        last_low > prev_low
    ):
        return "BULLISH"



    # Lower High + Lower Low

    if (
        last_high < prev_high
        and
        last_low < prev_low
    ):
        return "BEARISH"



    return "RANGE"



# =====================================
# BREAK OF STRUCTURE
# =====================================

def detect_bos(
        df,
        swing_highs,
        swing_lows
):

    if not swing_highs or not swing_lows:
        return "NONE"


    close = float(
        df["close"].iloc[-1]
    )


    structure = get_market_structure(
        swing_highs,
        swing_lows
    )


    last_high = swing_highs[-1][1]
    last_low = swing_lows[-1][1]



    # Bullish BOS

    if (
        structure == "BULLISH"
        and
        close > last_high
    ):
        return "BULLISH"



    # Bearish BOS

    if (
        structure == "BEARISH"
        and
        close < last_low
    ):
        return "BEARISH"



    return "NONE"




# =====================================
# CHANGE OF CHARACTER
# =====================================

def detect_choch(
        df,
        swing_highs,
        swing_lows
):

    if len(swing_highs) < 2:
        return "NONE"

    if len(swing_lows) < 2:
        return "NONE"



    close = float(
        df["close"].iloc[-1]
    )


    structure = get_market_structure(
        swing_highs,
        swing_lows
    )



    last_high = swing_highs[-1][1]
    last_low = swing_lows[-1][1]



    # Bullish trend breaks down

    if (
        structure == "BULLISH"
        and
        close < last_low
    ):
        return "BEARISH"



    # Bearish trend breaks upward

    if (
        structure == "BEARISH"
        and
        close > last_high
    ):
        return "BULLISH"



    return "NONE"




# =====================================
# LIQUIDITY DETECTION
# =====================================

def detect_liquidity(
        swing_highs,
        swing_lows,
        tolerance=0.0015
):


    # Equal High Liquidity

    if len(swing_highs) >= 2:

        high1 = swing_highs[-1][1]
        high2 = swing_highs[-2][1]


        if abs(high1-high2) <= (
            high2*tolerance
        ):

            return {
                "type":
                "EQUAL HIGHS",

                "level":
                round(high1,5)
            }




    # Equal Low Liquidity

    if len(swing_lows) >= 2:

        low1 = swing_lows[-1][1]
        low2 = swing_lows[-2][1]


        if abs(low1-low2) <= (
            low2*tolerance
        ):

            return {
                "type":
                "EQUAL LOWS",

                "level":
                round(low1,5)
            }




    return {
        "type":
        "NONE",

        "level":
        0
        }
    

# =====================================
# FAIR VALUE GAP DETECTION
# =====================================

def detect_fvg(df, lookback=20):

    if len(df) < 3:
        return {
            "type": "NONE",
            "top": 0,
            "bottom": 0
        }


    candles = (
        df.tail(lookback)
        .reset_index(drop=True)
    )


    for i in range(2, len(candles)):

        candle1_high = float(
            candles["high"].iloc[i-2]
        )

        candle1_low = float(
            candles["low"].iloc[i-2]
        )


        candle3_high = float(
            candles["high"].iloc[i]
        )

        candle3_low = float(
            candles["low"].iloc[i]
        )



        # Bullish FVG

        if candle3_low > candle1_high:

            return {
                "type":
                "BULLISH FVG",

                "top":
                round(candle3_low,5),

                "bottom":
                round(candle1_high,5)
            }



        # Bearish FVG

        if candle3_high < candle1_low:

            return {
                "type":
                "BEARISH FVG",

                "top":
                round(candle1_low,5),

                "bottom":
                round(candle3_high,5)
            }



    return {
        "type":
        "NONE",

        "top":
        0,

        "bottom":
        0
    }




# =====================================
# ORDER BLOCK DETECTION
# =====================================

def detect_order_block(df, lookback=30):


    if len(df) < 5:

        return {
            "type":"NONE",
            "level":0,
            "direction":"NONE"
        }



    candles = (
        df.tail(lookback)
        .reset_index(drop=True)
    )



    for i in range(
        len(candles)-2,
        1,
        -1
    ):


        previous_open = float(
            candles["open"].iloc[i-1]
        )

        previous_close = float(
            candles["close"].iloc[i-1]
        )


        current_close = float(
            candles["close"].iloc[i]
        )

        current_high = float(
            candles["high"].iloc[i]
        )

        current_low = float(
            candles["low"].iloc[i]
        )



        # Bullish Order Block

        if (
            previous_close < previous_open
            and
            current_close > previous_open
        ):

            return {

                "type":
                "BULLISH OB",

                "level":
                round(
                    candles["low"].iloc[i-1],
                    5
                ),

                "direction":
                "BUY"
            }




        # Bearish Order Block

        if (
            previous_close > previous_open
            and
            current_close < previous_open
        ):

            return {

                "type":
                "BEARISH OB",

                "level":
                round(
                    candles["high"].iloc[i-1],
                    5
                ),

                "direction":
                "SELL"
            }



    return {

        "type":
        "NONE",

        "level":
        0,

        "direction":
        "NONE"
    }





# =====================================
# PREMIUM / DISCOUNT ZONE
# =====================================

def detect_zone(
        df,
        swing_highs,
        swing_lows
):


    if not swing_highs:
        return "NEUTRAL"

    if not swing_lows:
        return "NEUTRAL"



    high = max(
        x[1]
        for x in swing_highs
    )


    low = min(
        x[1]
        for x in swing_lows
    )



    price = float(
        df["close"].iloc[-1]
    )



    equilibrium = (
        high + low
    ) / 2



    if price > equilibrium:

        return "PREMIUM"



    if price < equilibrium:

        return "DISCOUNT"



    return "EQUILIBRIUM"





# =====================================
# COMPLETE SMC ENGINE
# =====================================

def analyze_smc(df):


    validate_dataframe(df)



    if len(df) < 20:

        return {

            "status":
            "NOT ENOUGH DATA",

            "bos":
            "NONE",

            "choch":
            "NONE",

            "structure":
            "NEUTRAL",

            "liquidity":
            {},

            "zone":
            "NEUTRAL",

            "fvg":
            {},

            "order_block":
            {}

        }




    swing_highs, swing_lows = (
        get_swing_points(df)
    )



    structure = get_market_structure(
        swing_highs,
        swing_lows
    )


    bos = detect_bos(
        df,
        swing_highs,
        swing_lows
    )


    choch = detect_choch(
        df,
        swing_highs,
        swing_lows
    )


    liquidity = detect_liquidity(
        swing_highs,
        swing_lows
    )


    zone = detect_zone(
        df,
        swing_highs,
        swing_lows
    )


    fvg = detect_fvg(df)


    order_block = detect_order_block(df)




    return {


        "status":
        "OK",


        "structure":
        structure,


        "bos":
        bos,


        "choch":
        choch,


        "liquidity":
        liquidity,


        "zone":
        zone,


        "fvg":
        fvg,


        "order_block":
        order_block

    }
