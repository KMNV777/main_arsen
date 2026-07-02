from telegram import InputFile, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from quotes_bot.card_renderer import render_card_bytes
from quotes_bot.formatters import format_card_list_item
from quotes_bot.keyboards import MAIN_KEYBOARD, all_cards_keyboard, card_keyboard
from quotes_bot.models import (
    get_adjacent_quote_id,
    get_card_by_quote_id,
    get_random_card,
    list_all_cards,
)


async def send_card(update: Update, card, *, edit: bool = False) -> None:
    chat = update.effective_chat
    markup = card_keyboard(card)
    photo = InputFile(render_card_bytes(card), filename="card.jpg")

    if edit and update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.message.delete()
        except BadRequest:
            pass

    await chat.send_photo(photo=photo, reply_markup=markup)


async def random_card_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    card = get_random_card()
    if not card:
        await update.effective_message.reply_text(
            "Пока нет карточек. Добавьте людей и цитаты в базу данных.",
            reply_markup=MAIN_KEYBOARD,
        )
        return
    await send_card(update, card)


async def all_cards_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cards = list_all_cards()
    if not cards:
        await update.message.reply_text(
            "Список карточек пока пуст.",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    lines = ["<b>Выберите карточку:</b>\n"]
    for index, card in enumerate(cards[:8], start=1):
        lines.append(format_card_list_item(index, card.person.name, card.quote.text))

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=all_cards_keyboard(cards, page=0),
        parse_mode="HTML",
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    if data == "random":
        card = get_random_card()
        if not card:
            await query.edit_message_text("Нет доступных карточек.")
            return
        await send_card(update, card, edit=True)
        return

    if data.startswith("cards_page:"):
        page = int(data.split(":")[1])
        cards = list_all_cards()
        lines = ["<b>Выберите карточку:</b>\n"]
        start = page * 8
        for index, card in enumerate(cards[start : start + 8], start=start + 1):
            lines.append(format_card_list_item(index, card.person.name, card.quote.text))
        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=all_cards_keyboard(cards, page=page),
            parse_mode="HTML",
        )
        return

    if data.startswith("card:"):
        quote_id = int(data.split(":")[1])
        card = get_card_by_quote_id(quote_id)
        if not card:
            await query.edit_message_text("Карточка не найдена.")
            return
        await send_card(update, card, edit=True)
        return

    if data.startswith("card_prev:"):
        current_id = int(data.split(":")[1])
        prev_id = get_adjacent_quote_id(current_id, -1)
        card = get_card_by_quote_id(prev_id) if prev_id else None
        if not card:
            await query.edit_message_text("Карточка не найдена.")
            return
        await send_card(update, card, edit=True)
        return

    if data.startswith("card_next:"):
        current_id = int(data.split(":")[1])
        next_id = get_adjacent_quote_id(current_id, 1)
        card = get_card_by_quote_id(next_id) if next_id else None
        if not card:
            await query.edit_message_text("Карточка не найдена.")
            return
        await send_card(update, card, edit=True)
        return
