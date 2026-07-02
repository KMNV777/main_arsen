from telegram import Update
from telegram.ext import ContextTypes

from quotes_bot.keyboards import MAIN_KEYBOARD


WELCOME_TEXT = (
    "Привет! Я бот с <b>карточками людей и их цитатами</b>.\n\n"
    "Нажми «🎴 Случайная карточка», чтобы увидеть случайную цитату, "
    "или «📚 Все люди», чтобы выбрать автора.\n\n"
    "На каждой карточке можно листать цитаты и переходить между людьми."
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
