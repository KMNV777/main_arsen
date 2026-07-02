from pathlib import Path

from telegram import BotCommand

from quotes_bot.config import BASE_DIR, TELEGRAM_BOT_TOKEN

LOGO_PATH = BASE_DIR / "assets" / "bot_logo.png"

BOT_SHORT_DESCRIPTION = "Киберспортивные карточки с цитатами. 1 цитата = 1 карточка."
BOT_DESCRIPTION = (
    "🎮 Карточки людей и их цитат в кибер-стиле.\n\n"
    "• Случайная карточка и листание\n"
    "• Фото + ник + цитата на одной картинке\n"
    "• Поиск по имени и тексту\n"
    "• Обновление фото: /photo Имя"
)


async def configure_bot_profile(application) -> None:
    await application.bot.set_my_short_description(BOT_SHORT_DESCRIPTION)
    await application.bot.set_my_description(BOT_DESCRIPTION)
    await application.bot.set_my_commands(
        [
            BotCommand("start", "Главное меню"),
            BotCommand("photo", "Обновить фото человека"),
            BotCommand("search", "Поиск карточек"),
            BotCommand("help", "Справка"),
        ]
    )


def logo_setup_hint() -> str:
    if LOGO_PATH.exists():
        return (
            f"Логотип сохранён: {LOGO_PATH}\n"
            "Чтобы поставить аватар бота:\n"
            "1. Открой @BotFather\n"
            "2. /mybots → выбери бота → Edit Botpic\n"
            "3. Загрузи файл bot_logo.png"
        )
    return "Логотип не найден."


async def configure_if_token_present(application) -> None:
    if not TELEGRAM_BOT_TOKEN:
        return
    await configure_bot_profile(application)
