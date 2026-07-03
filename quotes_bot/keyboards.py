from quotes_bot.config import WEBAPP_URL, get_webapp_url
from quotes_bot.formatters import truncate
from quotes_bot.models import get_adjacent_quote_id
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

SEARCH_HINT = (
    "Введите имя или фрагмент цитаты.\n"
    "Например: <i>Ваня</i> или <i>круассаны</i>"
)


def main_keyboard() -> ReplyKeyboardMarkup:
    rows = []
    webapp_url = get_webapp_url()
    if webapp_url:
        rows.append([KeyboardButton("🎮 Играть", web_app=WebAppInfo(url=webapp_url))])
    rows.extend(
        [
            ["🎁 Открыть пак", "📚 Коллекция"],
            ["🎴 Моя карточка", "👤 Профиль"],
            ["🔁 Обмен", "🏆 Лидеры"],
            ["🔍 Поиск"],
        ]
    )
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    return main_keyboard()


def start_inline_keyboard() -> InlineKeyboardMarkup | None:
    webapp_url = get_webapp_url()
    if not webapp_url:
        return None
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🎮 Открыть игру", web_app=WebAppInfo(url=webapp_url))]]
    )


def card_keyboard(card, *, owned_only: bool = False, user_id: int | None = None) -> InlineKeyboardMarkup:
    if owned_only and user_id is not None:
        from quotes_bot.collection import get_adjacent_owned_quote_id

        prev_id = get_adjacent_owned_quote_id(user_id, card.quote.id, -1)
        next_id = get_adjacent_owned_quote_id(user_id, card.quote.id, 1)
        random_data = "owned_random"
        prev_data = f"owned_prev:{prev_id}"
        next_data = f"owned_next:{next_id}"
    else:
        prev_id = get_adjacent_quote_id(card.quote.id, -1)
        next_id = get_adjacent_quote_id(card.quote.id, 1)
        random_data = "random"
        prev_data = f"card_prev:{prev_id}"
        next_data = f"card_next:{next_id}"

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("◀️", callback_data=prev_data),
                InlineKeyboardButton("🎲", callback_data=random_data),
                InlineKeyboardButton("▶️", callback_data=next_data),
            ]
        ]
    )


def pack_list_keyboard(packs) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"{pack.emoji} {pack.name}",
                    callback_data=f"open_pack:{pack.id}",
                )
            ]
            for pack in packs
        ]
    )


def exchange_keyboard(dust: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"🎫 Билет ({dust}/3 пыли)",
                    callback_data="exchange_ticket",
                )
            ],
            [
                InlineKeyboardButton(
                    f"🃏 Карта ({dust}/5 пыли)",
                    callback_data="exchange_card",
                )
            ],
        ]
    )


def profile_keyboard() -> InlineKeyboardMarkup:
    rows = []
    webapp_url = get_webapp_url()
    if webapp_url:
        rows.append(
            [InlineKeyboardButton("🎮 Mini App", web_app=WebAppInfo(url=webapp_url))]
        )
    rows.extend(
        [
            [InlineKeyboardButton("🔁 Обмен", callback_data="exchange_menu")],
            [InlineKeyboardButton("🏆 Лидеры", callback_data="leaderboard")],
            [
                InlineKeyboardButton("🎫 +2 билета (бонус)", callback_data="grant_ticket"),
            ],
        ]
    )
    return InlineKeyboardMarkup(rows)


def search_results_keyboard(cards) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"{card.person.name} — {truncate(card.quote.text)}",
                    callback_data=f"owned_view:{card.quote.id}",
                )
            ]
            for card in cards
        ]
    )
