from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from brain import best_setups, analyze_symbol
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# ==========================================
# START COMMAND
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "🤖 Welcome to SEKWAILA OMEGA X\n\n"
        "Available commands:\n\n"
        "/best - Best trading setup\n"
        "/scan - Scan all markets\n"
        "/analyze BTCUSD - Analyze a market"
    )

    await update.message.reply_text(text)
# ==========================================
# BEST COMMAND
# ==========================================

async def best(update: Update, context: ContextTypes.DEFAULT_TYPE):

    setups = best_setups()

    if not setups:
        await update.message.reply_text(
            "❌ No high-confidence setups found."
        )
        return

    trade = setups[0]

    message = (
        f"🏆 BEST TRADE\n\n"
        f"📊 Symbol: {trade['symbol']}\n"
        f"📈 Signal: {trade['signal']}\n"
        f"🎯 Confidence: {trade['confidence']}%\n"
        f"💰 Entry: {trade['entry']}\n"
        f"🛑 Stop Loss: {trade['stop_loss']}\n"
        f"🎯 Take Profit: {trade['take_profit']}"
    )

    await update.message.reply_text(message)
# ==========================================
# RUN BOT
# ==========================================

def run_bot():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("best", best))

    print("✅ SEKWAILA Telegram Bot Running...")

    app.run_polling()


if __name__ == "__main__":
    run_bot()
