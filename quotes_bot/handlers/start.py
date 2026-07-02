from telegram import Update
from telegram.ext import ContextTypes

from quotes_bot.collection import ensure_user, get_owned_cards
from quotes_bot.keyboards import MAIN_KEYBOARD


WELCOME_TEXT = (
    "🎮 <b>Quote Cards — кибер-коллекция</b>\n\n"
    "Собирай карточки с цитатами как в паках:\n"
    "• 4 пака по 2 игрока\n"
    "• 1 цитата = 1 карточка\n"
    "• Открывай паки за билеты 🎫\n\n"
    "У тебя <b>5 стартовых билетов</b>.\n"
    "Жми 🎁 <b>Открыть пак</b> и начинай коллекцию!\n\n"
    "Фото обновляется через /photo Имя"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user:
        ensure_user(update.effective_user.id)
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=MAIN_KEYBOARD,
        parse_mode="HTML",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        WELCOME_TEXT
        + "\n\n<b>Команды:</b>\n"
        "🎁 Открыть пак — выбрать пак и получить 2 карточки\n"
        "📚 Коллекция — твои карточки\n"
        "🎴 Моя карточка — случайная из коллекции\n"
        "👤 Профиль — билеты и прогресс\n"
        "/photo Имя — обновить фото",
        reply_markup=MAIN_KEYBOARD,
        parse_mode="HTML",
    )
