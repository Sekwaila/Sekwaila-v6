"""
=========================================
SEKWAILA OMEGA X
Logging Module
Version: 1.1
=========================================
"""

import logging
from pathlib import Path

# Create logs folder safely
log_dir = Path("logs")

try:
    if log_dir.exists() and not log_dir.is_dir():
        log_dir.unlink()
    log_dir.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

# Configure logging
logging.basicConfig(
    filename=log_dir / "sekwaila.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True,
)

logger = logging.getLogger("SEKWAILA_OMEGA_X")


def setup_logger():
    """Return configured logger."""
    return logger


def info(message):
    logger.info(message)


def warning(message):
    logger.warning(message)


def error(message):
    logger.error(message)


def trade(signal, entry, stop_loss, take_profit):
    logger.info(
        f"TRADE | Signal={signal} | Entry={entry} | SL={stop_loss} | TP={take_profit}"
    )
