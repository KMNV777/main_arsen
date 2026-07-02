from telegram import Update
from telegram.ext import ContextTypes

from quotes_bot.collection import DUST_FOR_CARD, DUST_FOR_TICKET, touch_user
from quotes_bot.config import WEBAPP_URL
from quotes_bot.keyboards import MAIN_KEYBOARD, start_inline_keyboard


WELCOME_TEXT = (
    "🎮 <b>Quote Cards — кибер-коллекция</b>\n\n"
    "Это <b>Mini App</b> внутри Telegram — нажми 🎮 <b>Играть</b> "
    "или кнопку меню слева от поля ввода.\n\n"
    "• 4 пака по 2 игрока · паки <b>бесплатные</b> 🆓\n"
    "• Дубликаты → 🔁 пыль → обмен\n"
    "• 🏆 Таблица лидеров\n\n"
    "У тебя <b>5 стартовых билетов</b>.\n"
    "Кнопки в чате ниже — запасной режим, основная игра в Mini App.\n\n"
    "Фото обновляется через /photo Имя"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user:
        user = update.effective_user
        touch_user(user.id, username=user.username, display_name=user.full_name)

    inline = start_inline_keyboard()
    text = WELCOME_TEXT
    if not WEBAPP_URL:
        text += (
            "\n\n⚠️ <i>Mini App URL не настроен (WEBAPP_URL в .env). "
            "Пока доступен только режим бота.</i>"
        )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_KEYBOARD,
        parse_mode="HTML",
    )
    if inline:
        await update.message.reply_text(
            "👇 Быстрый запуск Mini App",
            reply_markup=inline,
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        WELCOME_TEXT
        + "\n\n<b>Команды:</b>\n"
        "🎮 Играть — Mini App (основной режим)\n"
        "🎁 Открыть пак — выбрать пак и получить 2 карточки\n"
        "📚 Коллекция — твои карточки\n"
        "🎴 Моя карточка — случайная из коллекции\n"
        "👤 Профиль — билеты, пыль и прогресс\n"
        f"🔁 Обмен — {DUST_FOR_TICKET} пыли → 🎫, {DUST_FOR_CARD} пыли → 🃏\n"
        "🏆 Лидеры — топ коллекционеров\n"
        "/photo Имя — обновить фото",
        reply_markup=MAIN_KEYBOARD,
        parse_mode="HTML",
    )
