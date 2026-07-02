import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from quotes_bot.collection import (
    DUST_FOR_CARD,
    DUST_FOR_TICKET,
    PACK_OPEN_COST,
    ensure_user,
    exchange_dust_for_card,
    exchange_dust_for_ticket,
    format_leaderboard,
    get_leaderboard,
    get_owned_cards,
    get_pack_by_id,
    get_pack_progress,
    get_person_collection_progress,
    get_user_profile,
    get_user_rank,
    grant_tickets,
    list_packs,
    open_pack,
    touch_user,
)
from quotes_bot.handlers.cards import send_card
from quotes_bot.keyboards import (
    MAIN_KEYBOARD,
    exchange_keyboard,
    pack_list_keyboard,
    profile_keyboard,
)
from quotes_bot.models import get_first_card_for_person, list_people


async def _sync_user(update: Update) -> None:
    user = update.effective_user
    if user:
        touch_user(user.id, username=user.username, display_name=user.full_name)


async def open_pack_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _sync_user(update)
    user_id = update.effective_user.id
    profile = ensure_user(user_id)
    lines = [
        "<b>🎁 Открыть пак</b>",
        f"Билетов: <b>{profile.tickets}</b> 🎫 · паки <b>бесплатные</b> 🆓",
        f"🔁 Пыль: <b>{profile.duplicate_dust}</b> (за дубликаты)",
        "",
    ]
    for progress in [get_pack_progress(user_id, pack.id) for pack in list_packs()]:
        if progress:
            lines.append(
                f"{progress.pack.emoji} <b>{progress.pack.name}</b> — "
                f"{progress.owned}/{progress.total}"
            )
            lines.append(f"<i>{progress.pack.description}</i>\n")

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=pack_list_keyboard(list_packs()),
        parse_mode="HTML",
    )


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _sync_user(update)
    user_id = update.effective_user.id
    profile = ensure_user(user_id)
    rank, _ = get_user_rank(user_id)
    packs = list_packs()
    total_cards = sum(
        get_pack_progress(user_id, pack.id).total
        for pack in packs
        if get_pack_progress(user_id, pack.id)
    )
    rank_line = f"🏆 Место в рейтинге: <b>#{rank}</b>\n" if rank else ""
    lines = [
        "<b>👤 Твой профиль</b>",
        rank_line,
        f"🎫 Билеты: <b>{profile.tickets}</b>",
        f"🔁 Пыль: <b>{profile.duplicate_dust}</b>",
        f"🃏 Карточек: <b>{profile.cards_owned}</b> / {total_cards}",
        f"📦 Паков открыто: <b>{profile.packs_opened}</b>",
        "",
        f"Обмен: {DUST_FOR_TICKET} пыли → 🎫 · {DUST_FOR_CARD} пыли → 🃏",
        "",
        "<b>Прогресс по пакам:</b>",
    ]
    for pack in packs:
        progress = get_pack_progress(user_id, pack.id)
        if progress:
            lines.append(
                f"{progress.pack.emoji} {progress.pack.name}: "
                f"{progress.owned}/{progress.total}"
            )

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=profile_keyboard(),
        parse_mode="HTML",
    )


async def collection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _sync_user(update)
    user_id = update.effective_user.id
    profile = ensure_user(user_id)
    if profile.cards_owned == 0:
        await update.message.reply_text(
            "Коллекция пуста.\nОткрой пак через 🎁 <b>Открыть пак</b>!",
            parse_mode="HTML",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    lines = ["<b>📚 Коллекция</b>\n"]
    for person in list_people():
        owned, total = get_person_collection_progress(user_id, person.id)
        if owned == 0:
            continue
        bar = "█" * owned + "░" * max(total - owned, 0)
        lines.append(f"<b>{person.name}</b> {owned}/{total}\n<code>{bar}</code>\n")

    owned_cards = get_owned_cards(user_id)
    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=collection_people_keyboard(owned_cards),
        parse_mode="HTML",
    )


def collection_people_keyboard(cards) -> InlineKeyboardMarkup:
    seen: set[int] = set()
    rows = []
    for card in cards:
        if card.person.id in seen:
            continue
        seen.add(card.person.id)
        rows.append(
            [
                InlineKeyboardButton(
                    card.person.name,
                    callback_data=f"owned_person:{card.person.id}",
                )
            ]
        )
    return InlineKeyboardMarkup(rows)


async def exchange_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _sync_user(update)
    profile = get_user_profile(update.effective_user.id)
    text = (
        "🔁 <b>Обмен дубликатов</b>\n\n"
        f"Пыль: <b>{profile.duplicate_dust}</b>\n\n"
        f"• <b>{DUST_FOR_TICKET}</b> пыли → 1 🎫 билет\n"
        f"• <b>{DUST_FOR_CARD}</b> пыли → 1 🃏 случайная карта\n\n"
        "Пыль копится за каждый дубликат при открытии пака."
    )
    await update.message.reply_text(
        text,
        reply_markup=exchange_keyboard(profile.duplicate_dust),
        parse_mode="HTML",
    )


async def leaderboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _sync_user(update)
    user_id = update.effective_user.id
    entries = get_leaderboard(10)
    rank, cards = get_user_rank(user_id)
    profile = get_user_profile(user_id)

    text = format_leaderboard(entries, highlight_user_id=user_id)
    if rank:
        text += (
            f"\n\n👤 Твоё место: <b>#{rank}</b>\n"
            f"📚 {profile.cards_owned} карточек · 📦 {profile.packs_opened} паков"
        )
    else:
        text += f"\n\n👤 Твоя коллекция: {cards} карточек"

    await update.message.reply_text(text, parse_mode="HTML")


async def game_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await _sync_user(update)
    data = query.data or ""
    user_id = update.effective_user.id

    if data == "exchange_menu":
        profile = get_user_profile(user_id)
        await query.edit_message_text(
            "🔁 <b>Обмен дубликатов</b>\n\n"
            f"Пыль: <b>{profile.duplicate_dust}</b>\n\n"
            f"• <b>{DUST_FOR_TICKET}</b> пыли → 1 🎫\n"
            f"• <b>{DUST_FOR_CARD}</b> пыли → 1 🃏",
            reply_markup=exchange_keyboard(profile.duplicate_dust),
            parse_mode="HTML",
        )
        return

    if data == "exchange_ticket":
        ok, msg = exchange_dust_for_ticket(user_id)
        profile = get_user_profile(user_id)
        if ok:
            await query.edit_message_text(
                f"✅ {msg}",
                reply_markup=exchange_keyboard(profile.duplicate_dust),
                parse_mode="HTML",
            )
        else:
            await query.answer(msg.replace("<b>", "").replace("</b>", ""), show_alert=True)
        return

    if data == "exchange_card":
        ok, msg, card = exchange_dust_for_card(user_id)
        profile = get_user_profile(user_id)
        if not ok:
            await query.answer(msg.replace("<b>", "").replace("</b>", ""), show_alert=True)
            return
        await query.edit_message_text(
            f"✅ {msg}",
            reply_markup=exchange_keyboard(profile.duplicate_dust),
            parse_mode="HTML",
        )
        if card:
            await send_card(update, card, edit=False, is_new=True, owned_only=True, user_id=user_id)
        return

    if data == "leaderboard":
        entries = get_leaderboard(10)
        rank, cards = get_user_rank(user_id)
        profile = get_user_profile(user_id)
        text = format_leaderboard(entries, highlight_user_id=user_id)
        if rank:
            text += (
                f"\n\n👤 Твоё место: <b>#{rank}</b>\n"
                f"📚 {profile.cards_owned} карточек"
            )
        else:
            text += f"\n\n👤 Твоя коллекция: {cards} карточек"
        await query.edit_message_text(text, parse_mode="HTML")
        return

    if data.startswith("open_pack:"):
        pack_id = int(data.split(":")[1])
        pack = get_pack_by_id(pack_id)
        if not pack:
            await query.edit_message_text("Пак не найден.")
            return

        await query.edit_message_text(f"{pack.emoji} Открываем <b>{pack.name}</b>...", parse_mode="HTML")
        await asyncio.sleep(0.7)

        new_cards, revealed, error = open_pack(user_id, pack_id)
        if error:
            await query.edit_message_text(error, reply_markup=MAIN_KEYBOARD)
            return

        for index, card in enumerate(revealed):
            is_new = any(item.quote.id == card.quote.id for item in new_cards)
            await send_card(update, card, edit=False, is_new=is_new, owned_only=True, user_id=user_id)
            if index < len(revealed) - 1:
                await asyncio.sleep(0.4)

        new_count = len(new_cards)
        dup_count = len(revealed) - new_count
        profile = ensure_user(user_id)
        summary = [f"✅ Пак <b>{pack.name}</b> открыт!"]
        if new_count:
            summary.append(f"✨ Новых карточек: <b>{new_count}</b>")
        if dup_count:
            summary.append(f"🔁 Дубликатов: <b>{dup_count}</b> (+{dup_count} пыли)")
        summary.append(f"🔁 Пыль: <b>{profile.duplicate_dust}</b>")
        summary.append(f"🎫 Билетов осталось: <b>{profile.tickets}</b>")

        await update.effective_chat.send_message(
            "\n".join(summary),
            parse_mode="HTML",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    if data == "grant_ticket":
        grant_tickets(user_id, 2)
        profile = ensure_user(user_id)
        await query.edit_message_text(
            f"+2 билета 🎫\nТеперь у тебя: <b>{profile.tickets}</b>",
            parse_mode="HTML",
        )
        return

    if data.startswith("owned_person:"):
        person_id = int(data.split(":")[1])
        card = get_first_card_for_person(person_id)
        if not card or not get_person_collection_progress(user_id, person_id)[0]:
            await query.edit_message_text("Карточки не найдены.")
            return
        await send_card(update, card, edit=True, owned_only=True, user_id=user_id)
        return
