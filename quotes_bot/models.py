from dataclasses import dataclass

from quotes_bot.db import connect


@dataclass
class Person:
    id: int
    name: str
    bio: str
    years: str
    photo_url: str | None


@dataclass
class Quote:
    id: int
    person_id: int
    text: str


@dataclass
class QuoteCard:
    person: Person
    quote: Quote
    card_index: int
    card_total: int


def _row_to_person(row) -> Person:
    return Person(
        id=row["id"],
        name=row["name"],
        bio=row["bio"],
        years=row["years"],
        photo_url=row["photo_url"],
    )


def _row_to_quote(row) -> Quote:
    return Quote(id=row["id"], person_id=row["person_id"], text=row["text"])


def _list_all_quote_rows(conn) -> list:
    return conn.execute(
        """
        SELECT
            q.id AS quote_id,
            q.person_id,
            q.text AS quote_text,
            p.id AS person_id,
            p.name,
            p.bio,
            p.years,
            p.photo_url
        FROM quotes q
        JOIN people p ON p.id = q.person_id
        ORDER BY p.name COLLATE NOCASE, q.id
        """
    ).fetchall()


def _row_to_card(row, card_index: int, card_total: int) -> QuoteCard:
    person = Person(
        id=row["person_id"],
        name=row["name"],
        bio=row["bio"],
        years=row["years"],
        photo_url=row["photo_url"],
    )
    quote = Quote(id=row["quote_id"], person_id=person.id, text=row["quote_text"])
    return QuoteCard(
        person=person,
        quote=quote,
        card_index=card_index,
        card_total=card_total,
    )


def get_people_count() -> int:
    with connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM people").fetchone()[0]


def list_people() -> list[Person]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM people ORDER BY name COLLATE NOCASE"
        ).fetchall()
    return [_row_to_person(row) for row in rows]


def get_person_by_id(person_id: int) -> Person | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM people WHERE id = ?", (person_id,)
        ).fetchone()
    return _row_to_person(row) if row else None


def find_person_by_name(name: str) -> Person | None:
    needle = name.strip().casefold()
    if not needle:
        return None
    for person in list_people():
        if person.name.casefold() == needle:
            return person
    return None


def search_people(query: str, limit: int = 10) -> list[Person]:
    needle = query.strip().casefold()
    if not needle:
        return []

    results: list[Person] = []
    for person in list_people():
        quotes = get_quotes_for_person(person.id)
        haystacks = [person.name, person.bio, *[quote.text for quote in quotes]]
        if any(needle in text.casefold() for text in haystacks if text):
            results.append(person)
        if len(results) >= limit:
            break
    return results


def get_quotes_for_person(person_id: int) -> list[Quote]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM quotes WHERE person_id = ? ORDER BY id",
            (person_id,),
        ).fetchall()
    return [_row_to_quote(row) for row in rows]


def list_all_cards() -> list[QuoteCard]:
    with connect() as conn:
        rows = _list_all_quote_rows(conn)
    total = len(rows)
    return [_row_to_card(row, index, total) for index, row in enumerate(rows)]


def get_card_by_quote_id(quote_id: int) -> QuoteCard | None:
    with connect() as conn:
        rows = _list_all_quote_rows(conn)
        total = len(rows)
        for index, row in enumerate(rows):
            if row["quote_id"] == quote_id:
                return _row_to_card(row, index, total)
    return None


def get_first_card_for_person(person_id: int) -> QuoteCard | None:
    with connect() as conn:
        rows = _list_all_quote_rows(conn)
        total = len(rows)
        for index, row in enumerate(rows):
            if row["person_id"] == person_id:
                return _row_to_card(row, index, total)
    return None


def get_random_card() -> QuoteCard | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT
                q.id AS quote_id,
                q.person_id,
                q.text AS quote_text,
                p.id AS person_id,
                p.name,
                p.bio,
                p.years,
                p.photo_url
            FROM quotes q
            JOIN people p ON p.id = q.person_id
            ORDER BY RANDOM()
            LIMIT 1
            """
        ).fetchone()
        if not row:
            return None
        return get_card_by_quote_id(row["quote_id"])


def get_adjacent_quote_id(current_quote_id: int, direction: int) -> int | None:
    cards = list_all_cards()
    if not cards:
        return None

    quote_ids = [card.quote.id for card in cards]
    try:
        index = quote_ids.index(current_quote_id)
    except ValueError:
        return cards[0].quote.id

    next_index = (index + direction) % len(quote_ids)
    return quote_ids[next_index]


def search_cards(query: str, limit: int = 10) -> list[QuoteCard]:
    needle = query.strip().casefold()
    if not needle:
        return []

    results: list[QuoteCard] = []
    for card in list_all_cards():
        haystacks = [card.person.name, card.quote.text]
        if any(needle in text.casefold() for text in haystacks if text):
            results.append(card)
        if len(results) >= limit:
            break
    return results
