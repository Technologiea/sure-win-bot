import os
import logging
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
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
PORT = int(os.environ.get('PORT', 8080))
BOT_TOKEN = os.getenv('BOT_TOKEN')
REG_LINK = "https://1wprde.com/?open=register&p=v91c&sub1=97891"
PROMO_CODE = "BETWIN190"
MAIN_MENU, AWAITING_ID, LANGUAGE_SELECTION = range(3)
user_states = {}
user_languages = {}

# --- Enhanced HTTP Server for Render Health Checks ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running!')
        
    def log_message(self, format, *args):
        return  # Disable access logs to reduce noise

def run_http_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    logging.info(f"🌐 HTTP server running on port {PORT}")
    httpd.serve_forever()

# --- Robust Application Runner ---
def run_bot_forever():
    while True:
        try:
            logging.info("🤖 Starting SURE WIN BOT...")
            application = Application.builder().token(BOT_TOKEN).build()
            
            # Add handlers
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CallbackQueryHandler(show_instruction, pattern="^instruction$"))
            application.add_handler(CallbackQueryHandler(register_info, pattern="^register$"))
            application.add_handler(CallbackQueryHandler(get_signal, pattern="^get_signal$"))
            application.add_handler(CallbackQueryHandler(check_id, pattern="^check_id$"))
            application.add_handler(CallbackQueryHandler(start_over, pattern="^start_over$"))
            application.add_handler(CallbackQueryHandler(choose_language, pattern="^choose_language$"))
            application.add_handler(CallbackQueryHandler(set_language, pattern="^set_lang_"))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id_input))
            application.add_error_handler(error_handler)
            
            application.run_polling()
        except Exception as e:
            logging.error(f"🚨 Bot crashed: {e}")
            logging.info("🔄 Restarting bot in 10 seconds...")
            time.sleep(10)
            
# Translation dictionary
TRANSLATIONS = {
    'en': {
        'welcome': "👋 Hey {name}! Welcome to 🤖 *SURE WIN BOT!*\n\n"
                   "🎯 This bot helps you play smart & earn more from your favourite games.\n\n"
                   "🧠 Powered by our Sure Win Neural Network — trained on 10,000+ games — giving *highly accurate predictions*.\n\n"
                   "💡 Use our tips, play smart, and start earning today!\n\n"
                   "👇 Select an option to begin:",
        'how_to_use': "📘 How to Use",
        'get_signal': "📡 Get Signal",
        'choose_language': "🌐 Choose Language",
        'instruction': "📚 *How It Works:*\n\n"
                       "🧠 Trained on 10,000+ real games 🎰\n"
                       "💰 Users are earning 15–25% profit *daily!*\n"
                       "✅ Accuracy: *87% and improving!*\n\n"
                       "Just follow 3 easy steps:\n"
                       "1️⃣ Choose your game (Mines, Aviator, etc.)\n"
                       "2️⃣ Tap 'Get Signal' and bet as shown\n"
                       "3️⃣ If you lose, double your bet (X2) next round to recover\n\n"
                       "⚠ *Tip:* Use X2 strategy carefully to avoid big risks.\n\n"
                       "🚀 Try now and grow your capital with confidence!",
        'register': "📝 Register",
        'back_menu': "🔙 Back to Main Menu",
        'register_info': "💼 *How to Start Playing:*\n\n"
                         "1️⃣ Click the button below to register on *1WIN*\n"
                         "2️⃣ Use this promo code while signing up: 🔥 *{promo}*\n"
                         "3️⃣ Once registered, our system will verify and send you a confirmation here ✅\n\n"
                         "⚠ *Already have an account?*\n"
                         "👉 Just register again using a *new email*. Phone number doesn't matter.",
        'cancel': "❌ Cancel",
        'check_id': "🔍 Check My ID",
        'enter_id': "🔎 Please type your *1WIN User ID* (9 digits):",
        'invalid_id': "❌ You've entered an *invalid ID*. Please try again.",
        'invalid_format': "❌ Invalid format. Please enter a *9-digit User ID*.\n\n"
                          "🔹 Example: `123456789`\n"
                          "🔹 Or click /start to return to main menu",
        'error': "⚠️ An error occurred. Please try again or use /start",
        'language_prompt': "🌐 Please choose your language:",
        'language_set': "✅ Language set to {language}",
        'english': "English 🇬🇧",
        'spanish': "Spanish 🇪🇸",
        'russian': "Russian 🇷🇺"
    },
    'es': {
        'welcome': "👋 ¡Hola {name}! Bienvenido a 🤖 *SURE WIN BOT!*\n\n"
                   "🎯 Este bot te ayuda a jugar de manera inteligente y ganar más en tus juegos favoritos.\n\n"
                   "🧠 Impulsado por nuestra Red Neuronal Sure Win — entrenada en más de 10,000 juegos — ofreciendo *predicciones altamente precisas*.\n\n"
                   "💡 Usa nuestros consejos, juega de forma inteligente y comienza a ganar hoy.\n\n"
                   "👇 Selecciona una opción para comenzar:",
        'how_to_use': "📘 Cómo usar",
        'get_signal': "📡 Obtener señal",
        'choose_language': "🌐 Elegir idioma",
        'instruction': "📚 *Cómo funciona:*\n\n"
                       "🧠 Entrenado en más de 10,000 juegos reales 🎰\n"
                       "💰 ¡Los usuarios ganan 15–25% de beneficio *diariamente!*\n"
                       "✅ Precisión: *87% y mejorando!*\n\n"
                       "Solo sigue 3 sencillos pasos:\n"
                       "1️⃣ Elige tu juego (Minas, Aviador, etc.)\n"
                       "2️⃣ Toca 'Obtener señal' y apuesta como se muestra\n"
                       "3️⃣ Si pierdes, duplica tu apuesta (X2) en la siguiente ronda para recuperarte\n\n"
                       "⚠ *Consejo:* Usa la estrategia X2 con cuidado para evitar grandes riesgos.\n\n"
                       "🚀 ¡Pruébalo ahora y haz crecer tu capital con confianza!",
        'register': "📝 Registrarse",
        'back_menu': "🔙 Volver al menú principal",
        'register_info': "💼 *Cómo comenzar a jugar:*\n\n"
                         "1️⃣ Haz clic en el botón de abajo para registrarte en *1WIN*\n"
                         "2️⃣ Usa este código promocional al registrarte: 🔥 *{promo}*\n"
                         "3️⃣ Una vez registrado, nuestro sistema verificará y te enviará una confirmación aquí ✅\n\n"
                         "⚠ *¿Ya tienes una cuenta?*\n"
                         "👉 Simplemente regístrate nuevamente con un *nuevo correo electrónico*. El número de teléfono no importa.",
        'cancel': "❌ Cancelar",
        'check_id': "🔍 Verificar mi ID",
        'enter_id': "🔎 Por favor, escribe tu *ID de usuario de 1WIN* (9 dígitos):",
        'invalid_id': "❌ Has ingresado un *ID inválido*. Por favor, inténtalo de nuevo.",
        'invalid_format': "❌ Formato inválido. Por favor, ingresa un *ID de usuario de 9 dígitos*.\n\n"
                          "🔹 Ejemplo: `123456789`\n"
                          "🔹 O haz clic en /start para volver al menú principal",
        'error': "⚠️ Ocurrió un error. Por favor, intenta de nuevo o usa /start",
        'language_prompt': "🌐 Por favor, elige tu idioma:",
        'language_set': "✅ Idioma establecido en {language}",
        'english': "Inglés 🇬🇧",
        'spanish': "Español 🇪🇸",
        'russian': "Ruso 🇷🇺"
    },
    'ru': {
        'welcome': "👋 Привет {name}! Добро пожаловать в 🤖 *SURE WIN BOT!*\n\n"
                   "🎯 Этот бот помогает вам играть с умом и зарабатывать больше в ваших любимых играх.\n\n"
                   "🧠 Работает на основе нашей нейронной сети Sure Win, обученной на 10 000+ играх, что обеспечивает *высокую точность прогнозов*.\n\n"
                   "💡 Используйте наши подсказки, играйте с умом и начните зарабатывать уже сегодня!\n\n"
                   "👇 Выберите опцию для начала:",
        'how_to_use': "📘 Как использовать",
        'get_signal': "📡 Получить сигнал",
        'choose_language': "🌐 Выбрать язык",
        'instruction': "📚 *Как это работает:*\n\n"
                       "🧠 Обучено на 10 000+ реальных игр 🎰\n"
                       "💰 Пользователи зарабатывают 15–25% прибыли *ежедневно!*\n"
                       "✅ Точность: *87% и улучшается!*\n\n"
                       "Просто выполните 3 простых шага:\n"
                       "1️⃣ Выберите игру (Мины, Авиатор и т.д.)\n"
                       "2️⃣ Нажмите 'Получить сигнал' и делайте ставки, как показано\n"
                       "3️⃣ Если проиграете, удвойте ставку (X2) в следующем раунде, чтобы отыграться\n\n"
                       "⚠ *Совет:* Используйте стратегию X2 осторожно, чтобы избежать больших рисков.\n\n"
                       "🚀 Попробуйте сейчас и увеличивайте свой капитал с уверенностью!",
        'register': "📝 Зарегистрироваться",
        'back_menu': "🔙 Назад в главное меню",
        'register_info': "💼 *Как начать играть:*\n\n"
                         "1️⃣ Нажмите кнопку ниже, чтобы зарегистрироваться на *1WIN*\n"
                         "2️⃣ Используйте этот промокод при регистрации: 🔥 *{promo}*\n"
                         "3️⃣ После регистрации наша система проверит и отправит подтверждение сюда ✅\n\n"
                         "⚠ *Уже есть аккаунт?*\n"
                         "👉 Просто зарегистрируйтесь снова, используя *новый email*. Номер телефона не имеет значения.",
        'cancel': "❌ Отмена",
        'check_id': "🔍 Проверить мой ID",
        'enter_id': "🔎 Пожалуйста, введите ваш *ID пользователя 1WIN* (9 цифр):",
        'invalid_id': "❌ Вы ввели *неверный ID*. Пожалуйста, попробуйте еще раз.",
        'invalid_format': "❌ Неверный формат. Пожалуйста, введите *9-значный ID пользователя*.\n\n"
                          "🔹 Пример: `123456789`\n"
                          "🔹 Или нажмите /start, чтобы вернуться в главное меню",
        'error': "⚠️ Произошла ошибка. Пожалуйста, попробуйте снова или используйте /start",
        'language_prompt': "🌐 Пожалуйста, выберите язык:",
        'language_set': "✅ Язык изменен на {language}",
        'english': "Английский 🇬🇧",
        'spanish': "Испанский 🇪🇸",
        'russian': "Русский 🇷🇺"
    }
}

# Helper function to get user's language
def get_user_language(user_id):
    return user_languages.get(user_id, 'en')

# Helper function to get translation
def _(key, user_id, **kwargs):
    lang = get_user_language(user_id)
    return TRANSLATIONS[lang][key].format(**kwargs)

# --- Enhanced logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Start Handler ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_states[user_id] = MAIN_MENU
    
    # Set default language if not set
    if user_id not in user_languages:
        user_languages[user_id] = 'en'
    
    keyboard = [
        [InlineKeyboardButton(_('how_to_use', user_id), callback_data="instruction")],
        [InlineKeyboardButton(_('get_signal', user_id), callback_data="get_signal")],
        [InlineKeyboardButton(_('choose_language', user_id), callback_data="choose_language")]
    ]
    
    welcome_text = _('welcome', user_id, name=user.first_name)
    
    if update.message:
        await update.message.reply_markdown(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

# --- Language Selection ---
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_states[user_id] = LANGUAGE_SELECTION
    
    keyboard = [
        [InlineKeyboardButton(_('english', user_id), callback_data="set_lang_en")],
        [InlineKeyboardButton(_('spanish', user_id), callback_data="set_lang_es")],
        [InlineKeyboardButton(_('russian', user_id), callback_data="set_lang_ru")],
        [InlineKeyboardButton(_('back_menu', user_id), callback_data="start_over")]
    ]
    
    prompt_text = _('language_prompt', user_id)
    await query.edit_message_text(prompt_text, reply_markup=InlineKeyboardMarkup(keyboard))

# --- Set Language Handler ---
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang_code = query.data.split('_')[-1]
    user_languages[user_id] = lang_code
    
    # Show confirmation
    lang_name = _(f"{lang_code}_name", user_id)
    confirm_text = _('language_set', user_id, language=lang_name)
    await query.edit_message_text(confirm_text)
    
    # Return to main menu
    await start(query, context)

# --- Instruction Handler ---
async def show_instruction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    keyboard = [
        [InlineKeyboardButton(_('register', user_id), callback_data="register")],
        [InlineKeyboardButton(_('get_signal', user_id), callback_data="get_signal")],
        [InlineKeyboardButton(_('back_menu', user_id), callback_data="start_over")]
    ]
    
    instruction_text = _('instruction', user_id)
    await query.edit_message_text(instruction_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# --- Register Handler ---
async def register_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    keyboard = [
        [InlineKeyboardButton("🔗 1WIN", url=REG_LINK)],
        [InlineKeyboardButton(_('cancel', user_id), callback_data="start_over")],
        [InlineKeyboardButton(_('check_id', user_id), callback_data="check_id")]
    ]
    
    register_text = _('register_info', user_id, promo=PROMO_CODE)
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
    user_id = query.from_user.id
    user_states[user_id] = AWAITING_ID
    
    prompt_text = _('enter_id', user_id)
    await query.edit_message_text(prompt_text, parse_mode="Markdown")

# --- Handle ID Input ---
async def handle_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_states.get(user_id) == AWAITING_ID:
        if text.isdigit() and len(text) == 9:
            response = _('invalid_id', user_id)
        else:
            response = _('invalid_format', user_id)
        await update.message.reply_text(response, parse_mode="Markdown")
    else:
        # If not in AWAITING_ID state, send them to start
        await start(update, context)

# --- Start Over Handler ---
async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Clear any state and return to main menu
    user_id = query.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    
    await start(query, context)

# --- Error Handler ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}")
    
    user_id = None
    if isinstance(update, Update):
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
    
    error_text = _('error', user_id) if user_id else "⚠️ An error occurred. Please try again or use /start"
    
    if isinstance(update, Update):
        if update.message:
            await update.message.reply_text(error_text)
        elif update.callback_query:
            await update.callback_query.message.reply_text(error_text)

# --- Main Application ---
if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    
    # Start HTTP server in a separate thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # Give HTTP server time to start
    time.sleep(2)
    
    # Start bot with restart protection
    run_bot_forever()
