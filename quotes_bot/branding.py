from pathlib import Path

from telegram import BotCommand, MenuButtonWebApp, WebAppInfo

from quotes_bot.config import BASE_DIR, TELEGRAM_BOT_TOKEN, WEBAPP_URL, get_webapp_url

LOGO_PATH = BASE_DIR / "assets" / "bot_logo.png"

BOT_SHORT_DESCRIPTION = "Кибер-коллекция цитат: Mini App, паки, билеты, карточки."
BOT_DESCRIPTION = (
    "🎮 Мини-приложение с карточками цитат в кибер-стиле.\n\n"
    "• Нажми 🎮 Играть — откроется Mini App\n"
    "• 4 пака по 2 игрока\n"
    "• Открывай паки за билеты 🎫\n"
    "• Дубликаты → пыль → обмен\n"
    "• Таблица лидеров\n"
    "• /photo Имя — обновить фото"
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
    webapp_url = get_webapp_url()
    if webapp_url:
        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="🎮 Играть",
                web_app=WebAppInfo(url=webapp_url),
            )
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
