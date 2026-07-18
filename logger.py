"""
=========================================
SEKWAILA OMEGA X
Logging Module
Version: 1.0
=========================================
"""

import logging
from pathlib import Path

# Create logs folder if it doesn't exist
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    filename="logs/sekwaila.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def info(message):
    """Write an info message."""
    logging.info(message)


def warning(message):
    """Write a warning message."""
    logging.warning(message)


def error(message):
    """Write an error message."""
    logging.error(message)


def trade(signal, entry, stop_loss, take_profit):
    """Log a generated trade."""
    logging.info(
        f"TRADE | Signal={signal} | Entry={entry} | SL={stop_loss} | TP={take_profit}"
    )
