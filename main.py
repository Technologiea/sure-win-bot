import logging
import os
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
REG_LINK = "https://1wprde.com/?open=register&p=v91c&sub1=97891"
PROMO_CODE = "BETWIN190"
MAIN_MENU, AWAITING_ID = range(2)
user_states = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_states[user.id] = MAIN_MENU
    keyboard = [
        [InlineKeyboardButton("📘 How to Use", callback_data="instruction")],
        [InlineKeyboardButton("📡 Get Signal", callback_data="get_signal")],
        [InlineKeyboardButton("🌐 Choose Language", callback_data="choose_language")]
    ]
    welcome_text = (
        f"👋 Hey {user.first_name}! Welcome to 🤖 *SURE WIN BOT!*\n\n"
        "🎯 This bot helps you play smart & earn more from your favourite games.\n\n"
        "🧠 Powered by our Sure Win Neural Network — trained on 10,000+ games — giving *highly accurate predictions*.\n\n"
        "💡 Use our tips, play smart, and start earning today!\n\n"
        "👇 Select an option to begin:"
    )
    await update.message.reply_markdown(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_instruction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    instruction_text = (
        "📚 *How It Works:*\n\n"
        "🧠 Trained on 10,000+ real games 🎰\n"
        "💰 Users are earning 15–25% profit *daily!*\n"
        "✅ Accuracy: *87% and improving!*\n\n"
        "1️⃣ Choose your game\n"
        "2️⃣ Tap 'Get Signal' and bet as shown\n"
        "3️⃣ If you lose, double your bet (X2) next round\n\n"
        "⚠ *Use X2 strategy with care to avoid big risk!*"
    )
    keyboard = [
        [InlineKeyboardButton("📝 Register", callback_data="register")],
        [InlineKeyboardButton("📡 Get Signal", callback_data="get_signal")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="start_over")]
    ]
    await query.edit_message_text(instruction_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def register_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    register_text = (
        "💼 *How to Start Playing:*\n\n"
        "1️⃣ Click the button below to register on *1WIN*\n"
        f"2️⃣ Use this promo code: 🔥 *{PROMO_CODE}*\n"
        "3️⃣ System will verify and notify you ✅\n\n"
        "⚠ Already have account? Register again with new email!"
    )
    keyboard = [
        [InlineKeyboardButton("🔗 1WIN", url=REG_LINK)],
        [InlineKeyboardButton("❌ Cancel", callback_data="start_over")],
        [InlineKeyboardButton("🔍 Check My ID", callback_data="check_id")]
    ]
    await query.edit_message_text(register_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def get_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await register_info(update, context)

async def check_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_states[query.from_user.id] = AWAITING_ID
    await query.edit_message_text("🔎 Enter your *1WIN ID* (9 digits):", parse_mode="Markdown")

async def handle_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if user_states.get(user_id) == AWAITING_ID:
        if text.isdigit() and len(text) == 9:
            await update.message.reply_text("✅ ID received. We will verify it shortly!")
        else:
            await update.message.reply_text("❌ Invalid format. Enter a *9-digit* ID.", parse_mode="Markdown")
    else:
        await start(update, context)

async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(query, context)

async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_instruction, pattern="^instruction$"))
    application.add_handler(CallbackQueryHandler(register_info, pattern="^register$"))
    application.add_handler(CallbackQueryHandler(get_signal, pattern="^get_signal$"))
    application.add_handler(CallbackQueryHandler(check_id, pattern="^check_id$"))
    application.add_handler(CallbackQueryHandler(start_over, pattern="^start_over$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id_input))

    print("✅ SURE WIN BOT is now live!")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
