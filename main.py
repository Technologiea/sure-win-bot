import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

# --- Configuration ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
REG_LINK = "https://1wprde.com/?open=register&p=v91c&sub1=97891"
PROMO_CODE = "BETWIN190"
MAIN_MENU, AWAITING_ID = range(2)
user_states = {}

# --- Enhanced logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Start Handler ---
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
    if update.message:
        await update.message.reply_markdown(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

# --- Instruction Handler ---
async def show_instruction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    instruction_text = (
        "📚 *How It Works:*\n\n"
        "🧠 Trained on 10,000+ real games 🎰\n"
        "💰 Users are earning 15–25% profit *daily!*\n"
        "✅ Accuracy: *87% and improving!*\n\n"
        "Just follow 3 easy steps:\n"
        "1️⃣ Choose your game (Mines, Aviator, etc.)\n"
        "2️⃣ Tap 'Get Signal' and bet as shown\n"
        "3️⃣ If you lose, double your bet (X2) next round to recover\n\n"
        "⚠ *Tip:* Use X2 strategy carefully to avoid big risks.\n\n"
        "🚀 Try now and grow your capital with confidence!"
    )
    keyboard = [
        [InlineKeyboardButton("📝 Register", callback_data="register")],
        [InlineKeyboardButton("📡 Get Signal", callback_data="get_signal")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="start_over")]
    ]
    await query.edit_message_text(instruction_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# --- Register Handler ---
async def register_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    register_text = (
        "💼 *How to Start Playing:*\n\n"
        "1️⃣ Click the button below to register on *1WIN*\n"
        f"2️⃣ Use this promo code while signing up: 🔥 *{PROMO_CODE}*\n"
        "3️⃣ Once registered, our system will verify and send you a confirmation here ✅\n\n"
        "⚠ *Already have an account?*\n"
        "👉 Just register again using a *new email*. Phone number doesn't matter."
    )
    keyboard = [
        [InlineKeyboardButton("🔗 1WIN", url=REG_LINK)],
        [InlineKeyboardButton("❌ Cancel", callback_data="start_over")],
        [InlineKeyboardButton("🔍 Check My ID", callback_data="check_id")]
    ]
    await query.edit_message_text(register_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# --- Get Signal Handler ---
async def get_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await register_info(update, context)

# --- Check ID Prompt ---
async def check_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_states[query.from_user.id] = AWAITING_ID
    await query.edit_message_text("🔎 Please type your *1WIN User ID* (9 digits):", parse_mode="Markdown")

# --- Handle ID Input ---
async def handle_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if user_states.get(user_id) == AWAITING_ID:
        if text.isdigit() and len(text) == 9:
            await update.message.reply_text("❌ You've entered an *invalid ID*. Please try again.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Invalid format. Please enter a *9-digit* User ID.", parse_mode="Markdown")
    else:
        await start(update, context)

# --- Start Over Handler ---
async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(query, context)

# --- Error Handler ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}")
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("⚠️ An error occurred. Please try again or use /start")
    elif isinstance(update, Update) and update.callback_query:
        await update.callback_query.message.reply_text("⚠️ An error occurred. Please try again or use /start")

# --- Main Application ---
def main():
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_instruction, pattern="^instruction$"))
    application.add_handler(CallbackQueryHandler(register_info, pattern="^register$"))
    application.add_handler(CallbackQueryHandler(get_signal, pattern="^get_signal$"))
    application.add_handler(CallbackQueryHandler(check_id, pattern="^check_id$"))
    application.add_handler(CallbackQueryHandler(start_over, pattern="^start_over$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id_input))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("🤖 Starting SURE WIN BOT...")
    application.run_polling()

if __name__ == '__main__':
    main()
