from quotes_bot.formatters import truncate
from quotes_bot.models import get_adjacent_quote_id
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🎴 Случайная карточка", "📚 Все карточки"],
        ["🔍 Поиск"],
    ],
    resize_keyboard=True,
)

SEARCH_HINT = (
    "Введите имя или фрагмент цитаты.\n"
    "Например: <i>Ваня</i> или <i>круассаны</i>"
)


def card_keyboard(card) -> InlineKeyboardMarkup:
    prev_id = get_adjacent_quote_id(card.quote.id, -1)
    next_id = get_adjacent_quote_id(card.quote.id, 1)
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "◀️",
                    callback_data=f"card_prev:{prev_id}",
                ),
                InlineKeyboardButton(
                    "🎲",
                    callback_data="random",
                ),
                InlineKeyboardButton(
                    "▶️",
                    callback_data=f"card_next:{next_id}",
                ),
            ]
        ]
    )


def all_cards_keyboard(cards, page: int = 0, page_size: int = 8) -> InlineKeyboardMarkup:
    start = page * page_size
    chunk = cards[start : start + page_size]
    rows = [
        [
            InlineKeyboardButton(
                f"{card.person.name} — {truncate(card.quote.text)}",
                callback_data=f"card:{card.quote.id}",
            )
        ]
        for card in chunk
    ]

    nav_row: list[InlineKeyboardButton] = []
    if start > 0:
        nav_row.append(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"cards_page:{page - 1}")
        )
    if start + page_size < len(cards):
        nav_row.append(
            InlineKeyboardButton("Вперёд ➡️", callback_data=f"cards_page:{page + 1}")
        )
    if nav_row:
        rows.append(nav_row)

    return InlineKeyboardMarkup(rows)


def search_results_keyboard(cards) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"{card.person.name} — {truncate(card.quote.text)}",
                    callback_data=f"card:{card.quote.id}",
                )
            ]
            for card in cards
        ]
    )
