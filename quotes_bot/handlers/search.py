from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from quotes_bot.collection import get_owned_cards
from quotes_bot.keyboards import SEARCH_HINT, get_main_keyboard, search_results_keyboard

SEARCH_QUERY = 1


async def search_prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(SEARCH_HINT, parse_mode="HTML")
    return SEARCH_QUERY


async def search_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = (update.message.text or "").strip()
    if not query:
        await update.message.reply_text(
            "Введите текст для поиска.",
            reply_markup=get_main_keyboard(),
        )
        return ConversationHandler.END

    needle = query.casefold()
    owned = get_owned_cards(update.effective_user.id)
    results = [
        card
        for card in owned
        if needle in card.person.name.casefold() or needle in card.quote.text.casefold()
    ]

    if not results:
        await update.message.reply_text(
            f"В твоей коллекции по запросу «{query}» ничего не найдено.",
            reply_markup=get_main_keyboard(),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        f"Найдено: <b>{len(results)}</b>\nВыберите карточку:",
        reply_markup=search_results_keyboard(results[:10]),
        parse_mode="HTML",
    )
    return ConversationHandler.END


async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Поиск отменён.", reply_markup=get_main_keyboard())
    return ConversationHandler.END
