from telegram import Update
from telegram.ext import ContextTypes

from quotes_bot.keyboards import MAIN_KEYBOARD


WELCOME_TEXT = (
    "Привет! Я бот с <b>карточками людей и их цитатами</b>.\n\n"
    "Каждая цитата — отдельная карточка: сверху фото, снизу ник и текст.\n\n"
    "Чтобы обновить фото — отправь картинку с подписью, например: <b>Машинка</b>.\n\n"
    "Нажми «🎴 Случайная карточка» или «📚 Все карточки», "
    "чтобы начать листать."
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=MAIN_KEYBOARD,
        parse_mode="HTML",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=MAIN_KEYBOARD,
        parse_mode="HTML",
    )
