import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from quotes_bot.branding import configure_if_token_present
from quotes_bot.config import TELEGRAM_BOT_TOKEN
from quotes_bot.db import init_db
from quotes_bot.filters import person_name_filter
from quotes_bot.generate_placeholders import generate_all_placeholders
from quotes_bot.handlers import cards, game, photo_upload, search, start
from quotes_bot.import_photos import import_inbox_photos
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

    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(configure_if_token_present)
        .build()
    )

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
    application.add_handler(CommandHandler("photo", photo_upload.photo_help_handler))
    application.add_handler(search_conversation)
    application.add_handler(
        MessageHandler(
            filters.PHOTO & filters.CAPTION,
            photo_upload.upload_person_photo_handler,
        )
    )
    application.add_handler(
        MessageHandler(
            filters.PHOTO & ~filters.CAPTION,
            photo_upload.upload_person_photo_handler,
        )
    )
    application.add_handler(
        MessageHandler(filters.Document.IMAGE, photo_upload.upload_person_photo_handler)
    )
    person_names = person_name_filter()
    if person_names:
        application.add_handler(
            MessageHandler(
                filters.Regex(person_names) & ~filters.COMMAND,
                photo_upload.prepare_photo_handler,
            )
        )
    application.add_handler(
        MessageHandler(filters.Regex("^🎁 Открыть пак$"), game.open_pack_menu_handler)
    )
    application.add_handler(
        MessageHandler(filters.Regex("^📚 Коллекция$"), game.collection_handler)
    )
    application.add_handler(
        MessageHandler(filters.Regex("^🎴 Моя карточка$"), cards.random_card_handler)
    )
    application.add_handler(
        MessageHandler(filters.Regex("^👤 Профиль$"), game.profile_handler)
    )
    application.add_handler(CallbackQueryHandler(game.game_callback_handler, pattern=r"^(open_pack:|grant_ticket|owned_person:)"))
    application.add_handler(CallbackQueryHandler(cards.callback_handler))

    return application


def main() -> None:
    init_db()
    imported = import_inbox_photos()
    if imported:
        logger.info("Imported photos: %s", ", ".join(imported))
    generate_all_placeholders()
    seed_database()
    application = build_application()
    logger.info("Quotes bot started")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
