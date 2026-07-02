from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from quotes_bot.keyboards import MAIN_KEYBOARD, SEARCH_HINT, search_results_keyboard
from quotes_bot.models import search_cards

SEARCH_QUERY = 1


async def search_prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(SEARCH_HINT, parse_mode="HTML")
    return SEARCH_QUERY


async def search_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = (update.message.text or "").strip()
    if not query:
        await update.message.reply_text(
            "Введите текст для поиска.",
            reply_markup=MAIN_KEYBOARD,
        )
        return ConversationHandler.END

    results = search_cards(query)
    if not results:
        await update.message.reply_text(
            f"По запросу «{query}» ничего не найдено.",
            reply_markup=MAIN_KEYBOARD,
        )
        return ConversationHandler.END

    await update.message.reply_text(
        f"Найдено: <b>{len(results)}</b>\nВыберите карточку:",
        reply_markup=search_results_keyboard(results),
        parse_mode="HTML",
    )
    return ConversationHandler.END


async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Поиск отменён.", reply_markup=MAIN_KEYBOARD)
    return ConversationHandler.END
