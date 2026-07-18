"""
=========================================
SEKWAILA OMEGA X
Utility Functions
Version: 1.0
=========================================
"""

from datetime import datetime
import pandas as pd


# ---------------------------------
# Current Time
# ---------------------------------
def current_time():
    """Return current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------
# Round Price
# ---------------------------------
def round_price(price, digits=2):
    """Round price safely."""
    try:
        return round(float(price), digits)
    except:
        return 0.0


# ---------------------------------
# Percentage Change
# ---------------------------------
def percent_change(old, new):
    """Calculate percentage change."""
    try:
        return ((new - old) / old) * 100
    except:
        return 0


# ---------------------------------
# Trend Emoji
# ---------------------------------
def trend_icon(trend):
    trend = str(trend).upper()

    if trend == "BULLISH":
        return "🟢"

    elif trend == "BEARISH":
        return "🔴"

    return "🟡"


# ---------------------------------
# Signal Color
# ---------------------------------
def signal_color(signal):
    signal = str(signal).upper()

    if "BUY" in signal:
        return "#00FF88"

    elif "SELL" in signal:
        return "#FF4444"

    return "#FFD700"


# ---------------------------------
# Format Money
# ---------------------------------
def money(value):
    try:
        return f"${float(value):,.2f}"
    except:
        return "$0.00"


# ---------------------------------
# Format Lot Size
# ---------------------------------
def lot(value):
    try:
        return f"{float(value):.2f}"
    except:
        return "0.00"


# ---------------------------------
# Check Empty Data
# ---------------------------------
def valid_dataframe(df):
    return isinstance(df, pd.DataFrame) and not df.empty
