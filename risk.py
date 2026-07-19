"""
=========================================
SEKWAILA OMEGA X
Risk Management Engine
Version: 4.0 (adds Discipline Guard)
=========================================
"""

import sqlite3
from datetime import datetime, timedelta, timezone

# =========================================
# DISCIPLINE GUARD CONFIG
# =========================================

DB_PATH = "sekwaila_risk.db"
LOSS_STREAK_TRIGGER = 2       # consecutive losses that trigger a lockout
COOLDOWN_MINUTES = 30         # how long the lockout lasts


# ---------------------------------------
# POSITION SIZE
# ---------------------------------------

def calculate_position_size(balance, risk_percent, entry, stop_loss):

    risk_amount = balance * (risk_percent / 100)

    stop_distance = abs(entry - stop_loss)

    if stop_distance == 0:
        return 0

    return round(risk_amount / stop_distance, 2)


# ---------------------------------------
# RISK : REWARD
# ---------------------------------------

def calculate_rr(entry, stop_loss, take_profit):

    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)

    if risk == 0:
        return 0

    return round(reward / risk, 2)


# ---------------------------------------
# COMPLETE RISK REPORT
# ---------------------------------------

def calculate_risk(balance,
                   risk_percent,
                   entry,
                   stop_loss,
                   take_profit):

    position = calculate_position_size(
        balance,
        risk_percent,
        entry,
        stop_loss
    )

    rr = calculate_rr(
        entry,
        stop_loss,
        take_profit
    )

    return {
        "balance": balance,
        "risk_percent": risk_percent,
        "risk_amount": round(balance * risk_percent / 100, 2),
        "entry": round(entry, 2),
        "stop_loss": round(stop_loss, 2),
        "take_profit": round(take_profit, 2),
        "position_size": position,
        "risk_reward": rr
    }


# =========================================
# DISCIPLINE GUARD
#
# Tracks closed trade outcomes in a local SQLite database and
# blocks new trades for COOLDOWN_MINUTES after LOSS_STREAK_TRIGGER
# consecutive losses. This is a standalone module — nothing else
# in the codebase currently reports trade outcomes to it yet.
# Something (a future trade-tracking feature, or manual logging
# via the dashboard/bot) needs to call record_trade_result()
# whenever a trade actually closes for this to have real data
# to work with.
# =========================================

def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            direction TEXT NOT NULL,
            result TEXT NOT NULL,
            closed_at TEXT NOT NULL
        )
    """)
    return conn


def record_trade_result(symbol, direction, result):
    """
    Record a closed trade's outcome.

    result must be "WIN" or "LOSS". Call this whenever a trade
    is actually closed — e.g. from a manual "mark as won/lost"
    button in the dashboard, or an automated position-close check.
    """
    result = result.upper()
    if result not in ("WIN", "LOSS"):
        raise ValueError('result must be "WIN" or "LOSS"')

    conn = _get_connection()
    try:
        conn.execute(
            "INSERT INTO trade_history (symbol, direction, result, closed_at) VALUES (?, ?, ?, ?)",
            (symbol, direction, result, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
    finally:
        conn.close()


def get_recent_results(limit=10):
    """Returns the most recent trade results, newest first."""
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT symbol, direction, result, closed_at FROM trade_history "
            "ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    finally:
        conn.close()

    return [
        {"symbol": r[0], "direction": r[1], "result": r[2], "closed_at": r[3]}
        for r in rows
    ]


def is_discipline_locked():
    """
    Checks whether trading should currently be blocked.

    Returns a dict:
        {
            "locked": bool,
            "reason": str or None,
            "minutes_remaining": float or None
        }

    Locked when the most recent LOSS_STREAK_TRIGGER trades were
    all losses AND the most recent one closed within the last
    COOLDOWN_MINUTES.
    """
    recent = get_recent_results(limit=LOSS_STREAK_TRIGGER)

    if len(recent) < LOSS_STREAK_TRIGGER:
        return {"locked": False, "reason": None, "minutes_remaining": None}

    all_losses = all(trade["result"] == "LOSS" for trade in recent)

    if not all_losses:
        return {"locked": False, "reason": None, "minutes_remaining": None}

    most_recent_close = datetime.fromisoformat(recent[0]["closed_at"])
    if most_recent_close.tzinfo is None:
        most_recent_close = most_recent_close.replace(tzinfo=timezone.utc)

    elapsed = datetime.now(timezone.utc) - most_recent_close
    cooldown = timedelta(minutes=COOLDOWN_MINUTES)

    if elapsed < cooldown:
        remaining = (cooldown - elapsed).total_seconds() / 60
        return {
            "locked": True,
            "reason": f"{LOSS_STREAK_TRIGGER} consecutive losses — cooling down.",
            "minutes_remaining": round(remaining, 1)
        }

    return {"locked": False, "reason": None, "minutes_remaining": None}


def calculate_risk_with_guard(balance, risk_percent, entry, stop_loss, take_profit):
    """
    Same as calculate_risk(), but also checks the Discipline Guard
    first. If locked, position_size is forced to 0 and a warning
    is included, regardless of what the raw math would say.
    """
    guard = is_discipline_locked()

    report = calculate_risk(balance, risk_percent, entry, stop_loss, take_profit)
    report["discipline_locked"] = guard["locked"]
    report["discipline_reason"] = guard["reason"]
    report["discipline_minutes_remaining"] = guard["minutes_remaining"]

    if guard["locked"]:
        report["position_size"] = 0

    return report
    
