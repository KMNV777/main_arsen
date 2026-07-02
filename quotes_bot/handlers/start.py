from telegram import Update
from telegram.ext import ContextTypes

from quotes_bot.collection import DUST_FOR_CARD, DUST_FOR_TICKET, ensure_user, touch_user
from quotes_bot.keyboards import MAIN_KEYBOARD


WELCOME_TEXT = (
    "🎮 <b>Quote Cards — кибер-коллекция</b>\n\n"
    "Собирай карточки с цитатами как в паках:\n"
    "• 4 пака по 2 игрока\n"
    "• 1 цитата = 1 карточка\n"
    "• Открывай паки за билеты 🎫\n"
    "• Дубликаты → 🔁 пыль → обмен на билеты и карты\n"
    "• 🏆 Таблица лидеров по размеру коллекции\n\n"
    "У тебя <b>5 стартовых билетов</b>.\n"
    "Жми 🎁 <b>Открыть пак</b> и начинай коллекцию!\n\n"
    "Фото обновляется через /photo Имя"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user:
        user = update.effective_user
        touch_user(user.id, username=user.username, display_name=user.full_name)
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
        "👤 Профиль — билеты, пыль и прогресс\n"
        f"🔁 Обмен — {DUST_FOR_TICKET} пыли → 🎫, {DUST_FOR_CARD} пыли → 🃏\n"
        "🏆 Лидеры — топ коллекционеров\n"
        "/photo Имя — обновить фото",
        reply_markup=MAIN_KEYBOARD,
        parse_mode="HTML",
    )
