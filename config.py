"""
=========================================
SEKWAILA OMEGA X
Configuration File
Version: 1.0
=========================================
"""

# -----------------------------
# APP SETTINGS
# -----------------------------
APP_NAME = "SEKWAILA OMEGA X"
VERSION = "1.0.0"

# -----------------------------
# DEFAULT INSTRUMENT
# -----------------------------
DEFAULT_SYMBOL = "XAUUSD"

# -----------------------------
# SUPPORTED INSTRUMENTS
# -----------------------------
INSTRUMENTS = {
    "XAUUSD": "GC=F",
    "US30": "^DJI",
    "SP500": "^GSPC",
    "BTCUSD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "USDJPY": "JPY=X",
}

# -----------------------------
# TIMEFRAMES
# -----------------------------
TIMEFRAMES = {
    "M5": "5m",
    "M15": "15m",
    "H1": "1h",
    "H4": "4h",
    "D1": "1d",
}

# -----------------------------
# RISK MANAGEMENT
# -----------------------------
RISK_PER_TRADE = 1.0          # %
DEFAULT_ACCOUNT_SIZE = 1000   # USD

# ATR Multipliers
SL_ATR = 1.5
TP1_ATR = 1.5
TP2_ATR = 2.5
TP3_ATR = 4.0

# -----------------------------
# INDICATORS
# -----------------------------
EMA_FAST = 50
EMA_SLOW = 200
RSI_PERIOD = 14
ATR_PERIOD = 14

# -----------------------------
# AI SETTINGS
# -----------------------------
BUY_THRESHOLD = 8
SELL_THRESHOLD = 8

# -----------------------------
# REFRESH
# -----------------------------
REFRESH_SECONDS = 60

# -----------------------------
# TELEGRAM
# -----------------------------
TELEGRAM_ENABLED = False
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""
