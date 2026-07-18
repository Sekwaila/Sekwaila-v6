"""
=========================================
SEKWAILA OMEGA X
Risk Management Engine
Version: 1.0
=========================================
"""


# ---------------------------------------
# POSITION SIZE
# ---------------------------------------

def calculate_position_size(account_balance,
                            risk_percent,
                            entry,
                            stop_loss):

    risk_amount = account_balance * (risk_percent / 100)

    stop_distance = abs(entry - stop_loss)

    if stop_distance == 0:
        return 0

    position_size = risk_amount / stop_distance

    return round(position_size, 2)


# ---------------------------------------
# RISK / REWARD
# ---------------------------------------

def risk_reward(entry,
                stop_loss,
                take_profit):

    risk = abs(entry - stop_loss)

    reward = abs(take_profit - entry)

    if risk == 0:
        return 0

    return round(reward / risk, 2)


# ---------------------------------------
# TRADE SUMMARY
# ---------------------------------------

def trade_summary(account_balance,
                  risk_percent,
                  entry,
                  stop_loss,
                  take_profit):

    return {

        "Entry": round(entry, 2),

        "Stop Loss": round(stop_loss, 2),

        "Take Profit": round(take_profit, 2),

        "Risk %": risk_percent,

        "Risk Amount": round(account_balance * risk_percent / 100, 2),

        "Position Size": calculate_position_size(
            account_balance,
            risk_percent,
            entry,
            stop_loss
        ),

        "Risk Reward": risk_reward(
            entry,
            stop_loss,
            take_profit
        )

    }
