from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🎴 Случайная карточка", "📚 Все люди"],
        ["🔍 Поиск"],
    ],
    resize_keyboard=True,
)

SEARCH_HINT = (
    "Введите имя, профессию или фрагмент цитаты.\n"
    "Например: <i>Ваня</i> или <i>круассаны</i>"
)


def card_keyboard(card) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []

    if card.quote_total > 1:
        quote_prev = (card.quote_index - 1) % card.quote_total
        quote_next = (card.quote_index + 1) % card.quote_total
        rows.append(
            [
                InlineKeyboardButton(
                    "◀️ Цитата",
                    callback_data=f"quote:{card.person.id}:{quote_prev}",
                ),
                InlineKeyboardButton(
                    "🎲 Случайная",
                    callback_data="random",
                ),
                InlineKeyboardButton(
                    "Цитата ▶️",
                    callback_data=f"quote:{card.person.id}:{quote_next}",
                ),
            ]
        )
    else:
        rows.append(
            [
                InlineKeyboardButton(
                    "🎲 Случайная",
                    callback_data="random",
                ),
            ]
        )

    rows.append(
        [
            InlineKeyboardButton(
                "◀️ Человек",
                callback_data=f"person_prev:{card.person.id}",
            ),
            InlineKeyboardButton(
                "Человек ▶️",
                callback_data=f"person_next:{card.person.id}",
            ),
        ]
    )

    return InlineKeyboardMarkup(rows)


def people_list_keyboard(people: list, page: int = 0, page_size: int = 8) -> InlineKeyboardMarkup:
    start = page * page_size
    chunk = people[start : start + page_size]
    rows = [
        [
            InlineKeyboardButton(
                person.name,
                callback_data=f"person:{person.id}:0",
            )
        ]
        for person in chunk
    ]

    nav_row: list[InlineKeyboardButton] = []
    if start > 0:
        nav_row.append(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"people_page:{page - 1}")
        )
    if start + page_size < len(people):
        nav_row.append(
            InlineKeyboardButton("Вперёд ➡️", callback_data=f"people_page:{page + 1}")
        )
    if nav_row:
        rows.append(nav_row)

    return InlineKeyboardMarkup(rows)


def search_results_keyboard(people: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    person.name,
                    callback_data=f"person:{person.id}:0",
                )
            ]
            for person in people
        ]
    )
