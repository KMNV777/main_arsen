from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from quotes_bot.formatters import format_card, format_person_list_item
from quotes_bot.keyboards import MAIN_KEYBOARD, card_keyboard, people_list_keyboard
from quotes_bot.models import (
    get_adjacent_person_id,
    get_card_for_person,
    get_quotes_for_person,
    get_random_card,
    list_people,
)


async def send_card(update: Update, card, *, edit: bool = False) -> None:
    text = format_card(card)
    markup = card_keyboard(card)
    photo_url = card.person.photo_url

    if edit and update.callback_query and update.callback_query.message:
        message = update.callback_query.message
        if photo_url and message.photo:
            await message.edit_caption(
                caption=text,
                reply_markup=markup,
                parse_mode="HTML",
            )
            return
        if photo_url and not message.photo:
            await message.delete()
            await update.effective_chat.send_photo(
                photo=photo_url,
                caption=text,
                reply_markup=markup,
                parse_mode="HTML",
            )
            return
        if not photo_url and message.photo:
            await message.delete()
            await update.effective_chat.send_message(
                text=text,
                reply_markup=markup,
                parse_mode="HTML",
            )
            return
        await message.edit_text(
            text=text,
            reply_markup=markup,
            parse_mode="HTML",
        )
        return

    if photo_url:
        await update.effective_chat.send_photo(
            photo=photo_url,
            caption=text,
            reply_markup=markup,
            parse_mode="HTML",
        )
    else:
        await update.effective_chat.send_message(
            text=text,
            reply_markup=markup,
            parse_mode="HTML",
        )


async def random_card_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    card = get_random_card()
    if not card:
        await update.effective_message.reply_text(
            "Пока нет карточек. Добавьте людей и цитаты в базу данных.",
            reply_markup=MAIN_KEYBOARD,
        )
        return
    await send_card(update, card)


async def all_people_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    people = list_people()
    if not people:
        await update.message.reply_text(
            "Список людей пока пуст.",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    lines = ["<b>Выберите человека:</b>\n"]
    for index, person in enumerate(people[:8], start=1):
        quote_count = len(get_quotes_for_person(person.id))
        lines.append(format_person_list_item(index, person.name, quote_count))

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=people_list_keyboard(people, page=0),
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
        try:
            await send_card(update, card, edit=True)
        except BadRequest:
            await send_card(update, card, edit=False)
        return

    if data.startswith("people_page:"):
        page = int(data.split(":")[1])
        people = list_people()
        lines = ["<b>Выберите человека:</b>\n"]
        start = page * 8
        for index, person in enumerate(people[start : start + 8], start=start + 1):
            quote_count = len(get_quotes_for_person(person.id))
            lines.append(format_person_list_item(index, person.name, quote_count))
        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=people_list_keyboard(people, page=page),
            parse_mode="HTML",
        )
        return

    if data.startswith("person:"):
        _, person_id, quote_index = data.split(":")
        card = get_card_for_person(int(person_id), int(quote_index))
        if not card:
            await query.edit_message_text("Карточка не найдена.")
            return
        try:
            await send_card(update, card, edit=True)
        except BadRequest:
            await send_card(update, card, edit=False)
        return

    if data.startswith("quote:"):
        _, person_id, quote_index = data.split(":")
        card = get_card_for_person(int(person_id), int(quote_index))
        if not card:
            await query.edit_message_text("Цитата не найдена.")
            return
        try:
            await send_card(update, card, edit=True)
        except BadRequest:
            await send_card(update, card, edit=False)
        return

    if data.startswith("person_prev:"):
        current_id = int(data.split(":")[1])
        prev_id = get_adjacent_person_id(current_id, -1)
        card = get_card_for_person(prev_id, 0) if prev_id else None
        if not card:
            await query.edit_message_text("Карточка не найдена.")
            return
        try:
            await send_card(update, card, edit=True)
        except BadRequest:
            await send_card(update, card, edit=False)
        return

    if data.startswith("person_next:"):
        current_id = int(data.split(":")[1])
        next_id = get_adjacent_person_id(current_id, 1)
        card = get_card_for_person(next_id, 0) if next_id else None
        if not card:
            await query.edit_message_text("Карточка не найдена.")
            return
        try:
            await send_card(update, card, edit=True)
        except BadRequest:
            await send_card(update, card, edit=False)
        return
