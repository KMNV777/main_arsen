from quotes_bot.models import PersonCard


def format_card(card: PersonCard) -> str:
    years_line = f"📅 {card.person.years}\n" if card.person.years else ""
    bio_line = f"{card.person.bio}\n\n" if card.person.bio else "\n"

    return (
        f"👤 <b>{card.person.name}</b>\n"
        f"{years_line}"
        f"{bio_line}"
        f"💬 «{card.quote.text}»\n\n"
        f"<i>Цитата {card.quote_index + 1} из {card.quote_total} · "
        f"Карточка {card.person_index + 1} из {card.person_total}</i>"
    )


def format_person_list_item(index: int, name: str, quote_count: int) -> str:
    return f"{index}. <b>{name}</b> — {quote_count} цит."
