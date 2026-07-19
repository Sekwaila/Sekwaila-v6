"""
=========================================
SEKWAILA OMEGA X
Telegram Bot (Interactive + Alerts)
Version: 2.1
=========================================
"""

import os
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from brain import (
    best_setups,
    analyze_symbol,
    process_command,
)

load_dotenv()

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("8739054815:AAGCIGmES43JxGuF4TfBotPRSD-EOxA6SCM")
CHAT_ID = os.getenv("5870791602")   # optional – if set, alerts go here

# In-memory tracker to prevent duplicate alerts
# key: symbol, value: last signal (e.g. "BUY", "SELL", "NO TRADE")
LAST_ALERTED = {}

# =========================================
# START COMMAND
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 Welcome to SEKWAILA OMEGA X\n\n"
        "Available commands:\n\n"
        "/best - Best trading setup\n"
        "/scan - Scan all markets\n"
        "/analyze BTCUSD - Analyze a market\n\n"
        "Or just ask naturally, e.g.:\n"
        "'how's btc looking' or 'scan markets'\n\n"
        "⚠️ Alerts are enabled if configured."
    )
    await update.message.reply_text(text)

# =========================================
# BEST COMMAND (with error handling)
# =========================================

async def best(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        setups = best_setups()
        if not setups:
            await update.message.reply_text("❌ No high-confidence setups found.")
            return
        trade = setups[0]
        message = (
            f"🏆 BEST TRADE\n\n"
            f"📊 Symbol: {trade.get('symbol', 'Unknown')}\n"
            f"📈 Signal: {trade.get('signal', 'N/A')}\n"
            f"🎯 Confidence: {trade.get('confidence', 0)}%\n"
            f"💰 Entry: {trade.get('entry', '--')}\n"
            f"🛑 Stop Loss: {trade.get('stop_loss', '--')}\n"
            f"🎯 Take Profit: {trade.get('take_profit', '--')}"
        )
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error in /best: {e}")
        await update.message.reply_text("❌ An error occurred while fetching the best trade. Please try again later.")

# =========================================
# ANALYZE COMMAND (with error handling)
# =========================================

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage:\n/analyze BTCUSD")
        return
    symbol = context.args[0].upper()
    try:
        result = analyze_symbol(symbol)
        await update.message.reply_text(result)
    except Exception as e:
        logger.error(f"Error in /analyze {symbol}: {e}")
        await update.message.reply_text(f"❌ Could not analyze {symbol}. Please check the symbol or try again later.")

# =========================================
# SCAN COMMAND (with error handling)
# =========================================

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        setups = best_setups()
        if not setups:
            await update.message.reply_text("❌ No high-confidence setups found.")
            return
        message = "📊 SEKWAILA OMEGA X\n\n"
        for trade in setups[:10]:
            message += (
                f"📈 {trade.get('symbol', 'Unknown')}\n"
                f"Signal: {trade.get('signal', 'N/A')}\n"
                f"Confidence: {trade.get('confidence', 0)}%\n\n"
            )
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error in /scan: {e}")
        await update.message.reply_text("❌ An error occurred while scanning markets. Please try again later.")

# =========================================
# CHAT MESSAGE (natural language) with error handling
# =========================================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        response = process_command(text)
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error in chat handler: {e}")
        await update.message.reply_text("❌ I couldn't understand that. Try /help or use a known command.")

# =========================================
# SCHEDULED ALERT FUNCTION (with duplicate suppression)
# =========================================

async def send_alerts(context: ContextTypes.DEFAULT_TYPE):
    """Background job: scans for best setups and pushes only *new* signals."""
    chat_id = CHAT_ID
    if not chat_id:
        logger.warning("Skipping alert job: TELEGRAM_CHAT_ID not set.")
        return

    try:
        setups = best_setups()
        if not setups:
            logger.info("No high-confidence setups found during alert scan.")
            return

        new_alerts = []
        for trade in setups[:3]:   # top 3
            symbol = trade.get('symbol')
            signal = trade.get('signal')
            if not symbol or not signal:
                continue

            # If we haven't seen this symbol or the signal changed
            if symbol not in LAST_ALERTED or LAST_ALERTED[symbol] != signal:
                LAST_ALERTED[symbol] = signal
                new_alerts.append(trade)

        if not new_alerts:
            logger.info("No new signals detected – skipping alert.")
            return

        # Build the alert message with HTML formatting
        message = "🚨 <b>Alert: New High-Confidence Setup Detected!</b>\n\n"
        for trade in new_alerts:
            message += (
                f"📈 <b>{trade.get('symbol', 'Unknown')}</b>\n"
                f"Signal: {trade.get('signal', 'N/A')} | "
                f"Confidence: {trade.get('confidence', 0)}%\n\n"
            )
        message += "Use /best for more details."

        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="HTML"
        )
        logger.info(f"Alert sent to {chat_id}")

    except Exception as e:
        logger.error(f"Error in alert job: {e}")

# =========================================
# RUN BOT
# =========================================

def run_bot():
    # Check token here, not at import time
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set. Check your .env file.")

    app = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("best", best))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Schedule alerts if CHAT_ID is set
    if CHAT_ID:
        # Run every 5 minutes (300 seconds), first run after 1 minute
        app.job_queue.run_repeating(send_alerts, interval=300, first=60)
        logger.info(f"Alert job scheduled (every 5 minutes) for chat {CHAT_ID}")
    else:
        logger.warning("TELEGRAM_CHAT_ID not set. Proactive alerts are disabled.")

    logger.info("✅ SEKWAILA Telegram Bot is running...")
    print("   Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
