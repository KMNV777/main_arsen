from telegram import InputFile, Update
from telegram.ext import ContextTypes

from quotes_bot.card_renderer import render_card_bytes
from quotes_bot.collection import get_random_owned_card
from quotes_bot.keyboards import MAIN_KEYBOARD, card_keyboard
from quotes_bot.models import get_card_by_quote_id


async def send_card(
    update: Update,
    card,
    *,
    edit: bool = False,
    is_new: bool = False,
    owned_only: bool = False,
    user_id: int | None = None,
) -> None:
    chat = update.effective_chat
    uid = user_id or (update.effective_user.id if update.effective_user else None)
    markup = card_keyboard(card, owned_only=owned_only, user_id=uid)
    photo = InputFile(render_card_bytes(card, is_new=is_new), filename="card.jpg")

    if edit and update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.message.delete()
        except Exception:
            pass

    await chat.send_photo(photo=photo, reply_markup=markup)


async def random_card_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    card = get_random_owned_card(user_id)
    if not card:
        await update.effective_message.reply_text(
            "У тебя пока нет карточек.\nОткрой пак через 🎁 <b>Открыть пак</b>!",
            parse_mode="HTML",
            reply_markup=MAIN_KEYBOARD,
        )
        return
    await send_card(update, card, owned_only=True, user_id=user_id)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    user_id = update.effective_user.id

    if data == "random":
        card = get_random_owned_card(user_id)
        if not card:
            await query.edit_message_text("Нет карточек в коллекции.")
            return
        await send_card(update, card, edit=True, owned_only=True, user_id=user_id)
        return

    if data == "owned_random":
        card = get_random_owned_card(user_id)
        if not card:
            await query.answer("Коллекция пуста", show_alert=True)
            return
        await send_card(update, card, edit=True, owned_only=True, user_id=user_id)
        return

    if data.startswith("owned_view:") or data.startswith("card:"):
        quote_id = int(data.split(":")[1])
        card = get_card_by_quote_id(quote_id)
        if not card:
            await query.edit_message_text("Карточка не найдена.")
            return
        await send_card(update, card, edit=True, owned_only=True, user_id=user_id)
        return

    if data.startswith("owned_prev:") or data.startswith("card_prev:"):
        quote_id = int(data.split(":")[1])
        card = get_card_by_quote_id(quote_id)
        if not card:
            await query.edit_message_text("Карточка не найдена.")
            return
        await send_card(update, card, edit=True, owned_only=True, user_id=user_id)
        return

    if data.startswith("owned_next:") or data.startswith("card_next:"):
        quote_id = int(data.split(":")[1])
        card = get_card_by_quote_id(quote_id)
        if not card:
            await query.edit_message_text("Карточка не найдена.")
            return
        await send_card(update, card, edit=True, owned_only=True, user_id=user_id)
        return
