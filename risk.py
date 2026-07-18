"""
=========================================
SEKWAILA OMEGA X
Risk Management Engine
Version: 3.0
=========================================
"""


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
