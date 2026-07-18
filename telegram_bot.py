from telegram import Update  # <-- ADD THIS IMPORT
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from brain import (
    best_setups,
    analyze_symbol,
    process_command,
)
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 Welcome to SEKWAILA OMEGA X\n\n"
        "Available commands:\n\n"
        "/best - Best trading setup\n"
        "/scan - Scan all markets\n"
        "/analyze BTCUSD - Analyze a market"
    )
    await update.message.reply_text(text)

async def best(update: Update, context: ContextTypes.DEFAULT_TYPE):
    setups = best_setups()
    if not setups:
        await update.message.reply_text("❌ No high-confidence setups found.")
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

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage:\n/analyze BTCUSD")
        return
    symbol = context.args[0].upper()
    result = analyze_symbol(symbol)
    await update.message.reply_text(result)

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    setups = best_setups()
    if not setups:
        await update.message.reply_text("❌ No high-confidence setups found.")
        return
    message = "📊 SEKWAILA OMEGA X\n\n"
    for trade in setups:
        message += (
            f"📈 {trade['symbol']}\n"
            f"Signal: {trade['signal']}\n"
            f"Confidence: {trade['confidence']}%\n\n"
        )
    await update.message.reply_text(message)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = process_command(text)
    await update.message.reply_text(response)

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("best", best))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("✅ SEKWAILA Telegram Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
