from quotes_bot.models import QuoteCard


def format_card(card: QuoteCard) -> str:
    return (
        f"<b>{card.person.name}</b>\n\n"
        f"«{card.quote.text}»\n\n"
        f"<i>{card.card_index + 1} / {card.card_total}</i>"
    )


def truncate(text: str, max_len: int = 28) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def format_card_list_item(index: int, person_name: str, quote_text: str) -> str:
    return f"{index}. <b>{person_name}</b> — «{truncate(quote_text)}»"
