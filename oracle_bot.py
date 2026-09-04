import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- ТОКЕН (лучше вынести в переменную окружения) ----------
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8816274174:AAEENQCe3bbtjbtT0hUfqyczyYvt4KDtzvQ")
# Если ты добавишь переменную на Render, код будет использовать её.
# Если нет – использует токен, который прописан здесь.
# --------------------------------------------------------

# ---------- ТЕКСТЫ ЗАГОВОРОВ (без изменений) ----------
SPELLS = {
    "feminine": {
        "name": "🌙 Красота и женственность",
        "instruction": (
            "Сегодня вечером, когда стемнеет, возьмите блюдечко и налейте в него молоко, "
            "зажгите рядом любую свечу от спичек, устраивайтесь поудобнее, "
            "желательно без одежды и украшений, начните набирать молоко на кончики пальцев "
            "и наносить на лицо, как бы умываясь. "
            "Во время «умывания» произнесите заговор трижды. "
            "После ритуала дождитесь пока свеча сама догорит, в это время можете вглядываться "
            "в пламя и представлять все моменты, связанные с вашей красотой и счастьем."
        ),
        "text": (
            "«О великая матушка Лада, Богиня женственности и любви, услышь мое воззвание, "
            "пришла к тебе (Ваше имя), темной ночкой надежду свою принесла, "
            "помоги мне матушка ладной твоей энергии набрать, чтобы век мне одиночества "
            "и лютушки не знать, позволь красоту твою познать, "
            "женскую сущность свою раскрывать. "
            "Помоги мне, матушка Лада, лик твой дивен и велик!»"
        )
    },
    "roads": {
        "name": "🍀 Пути-дороги",
        "instruction": (
            "Для этого нужно сорвать лист папоротника и прочитать заговор 3 раза. "
            "После этого заговоренный листочек папоротника носить при себе."
        ),
        "text": (
            "«Гой Мать Земля, папоротник сорвала и засушила. "
            "Силы у тебя попросила, папоротник намерением своим зарядила, "
            "дороги себе открыла, да денюжки прианила. "
            "Земля Матушка, ты изобильна, так и пути мои изобилием будут полны. "
            "Да будет так, так и будет!»"
        )
    },
    "intuition_fire": {
        "name": "🔥 Колдовская сила (Огонь)",
        "instruction": (
            "Как стемнеет — зажгите фиолетовую свечу от спичек, "
            "смотрите на пламя и прочтите 3 раза."
        ),
        "text": (
            "«О великая и могучая стихия Огня! Взывает к тебе, слуга твоя (имя), "
            "Прошу, надели меня богомочностью сокрытое видеть, "
            "сокрытое слышать, сокрытое ощущать. Заклинаю!»"
        )
    },
    "intuition_water": {
        "name": "🌊 Колдовская сила (Вода)",
        "instruction": (
            "Возле озера, реки или моря, как стемнеет — коснитесь воды рукой "
            "и произнесите 3 раза."
        ),
        "text": (
            "«Водица-сестрица, гладь твоя чиста, ты прозрачна, как слеза! "
            "Увидеть через себя помоги, Принеси истину во снах, "
            "По водной глади в душу мою донеси!»"
        )
    }
}

# ---------- ОБРАБОТЧИКИ (без изменений) ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🌙 Красота и женственность", callback_data="feminine")],
        [InlineKeyboardButton("🍀 Пути-дороги", callback_data="roads")],
        [InlineKeyboardButton("🕯️ Колдовская сила", callback_data="intuition_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌙 **Вещие заговоры**\n\n"
        "Выбери, чего сейчас хочет твоя душенька:\n"
        "• Наполниться женской красотой\n"
        "• Открыть пути-дороги\n"
        "• Призвать колдовскую силу\n\n"
        "_Славянское сердечко замирает._",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def intuition_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔥 Огонь", callback_data="intuition_fire")],
        [InlineKeyboardButton("🌊 Вода", callback_data="intuition_water")],
        [InlineKeyboardButton("🔙 Вернуться", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "🕯️ **Колдовская сила**\n\n"
        "Через какую стихию будешь говорить с миром?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def show_spell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    spell_key = query.data
    spell = SPELLS.get(spell_key)
    if not spell:
        await query.edit_message_text("❌ Такого заговора нет.")
        return
    text = (
        f"**{spell['name']}**\n\n"
        f"📖 **Как выполнять:**\n{spell['instruction']}\n\n"
        f"🗣 **Заговор:**\n{spell['text']}\n\n"
        "#Заговоры"
    )
    keyboard = [[InlineKeyboardButton("🔙 В главное меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🌙 Красота и женственность", callback_data="feminine")],
        [InlineKeyboardButton("🍀 Пути-дороги", callback_data="roads")],
        [InlineKeyboardButton("🕯️ Колдовская сила", callback_data="intuition_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "🌙 **Вещие заговоры**\n\n"
        "Выбери, чего сейчас хочет твоя душенька:\n"
        "• Наполниться женской красотой\n"
        "• Открыть пути-дороги\n"
        "• Призвать колдовскую силу\n\n"
        "_Славянское сердечко замирает._",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ---------- HTTP-сервер для Render (чтобы не было ошибки порта) ----------
def run_http_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), Handler)
    server.serve_forever()

# ---------- ЗАПУСК ----------
def main():
    # Запускаем HTTP-сервер в отдельном потоке
    thread = threading.Thread(target=run_http_server, daemon=True)
    thread.start()

    # Запускаем Telegram-бота
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(intuition_menu, pattern="^intuition_menu$"))
    application.add_handler(CallbackQueryHandler(show_spell, pattern="^(feminine|roads|intuition_fire|intuition_water)$"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    print("🔮 Бот Векши Настасьи запущен. Ожидание сообщений...")
    application.run_polling()

if __name__ == "__main__":
    main()
