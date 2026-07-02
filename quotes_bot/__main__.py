import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from quotes_bot.config import TELEGRAM_BOT_TOKEN
from quotes_bot.db import init_db
from quotes_bot.handlers import cards, search, start
from quotes_bot.seed import seed_database

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_application() -> Application:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN не задан. Скопируйте quotes_bot/.env.example в .env "
            "и укажите токен от @BotFather."
        )

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    search_conversation = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🔍 Поиск$"), search.search_prompt_handler),
            CommandHandler("search", search.search_prompt_handler),
        ],
        states={
            search.SEARCH_QUERY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search.search_query_handler),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", search.cancel_search),
            MessageHandler(filters.Regex("^/cancel$"), search.cancel_search),
        ],
    )

    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(CommandHandler("help", start.help_command))
    application.add_handler(search_conversation)
    application.add_handler(
        MessageHandler(filters.Regex("^🎴 Случайная карточка$"), cards.random_card_handler)
    )
    application.add_handler(
        MessageHandler(filters.Regex("^📚 Все люди$"), cards.all_people_handler)
    )
    application.add_handler(CallbackQueryHandler(cards.callback_handler))

    return application


def main() -> None:
    init_db()
    seed_database()
    application = build_application()
    logger.info("Quotes bot started")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
