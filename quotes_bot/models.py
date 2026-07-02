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
class PersonCard:
    person: Person
    quote: Quote | None
    quote_index: int
    quote_total: int
    person_index: int
    person_total: int


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


def get_person_by_name(name: str) -> Person | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM people WHERE LOWER(name) = LOWER(?)", (name.strip(),)
        ).fetchone()
    return _row_to_person(row) if row else None


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


def get_quote_by_id(quote_id: int) -> Quote | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM quotes WHERE id = ?", (quote_id,)
        ).fetchone()
    return _row_to_quote(row) if row else None


def get_random_card() -> PersonCard | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT
                p.id AS person_id,
                p.name,
                p.bio,
                p.years,
                p.photo_url,
                q.id AS quote_id,
                q.text AS quote_text
            FROM people p
            JOIN quotes q ON q.person_id = p.id
            ORDER BY RANDOM()
            LIMIT 1
            """
        ).fetchone()
        if row:
            person = Person(
                id=row["person_id"],
                name=row["name"],
                bio=row["bio"],
                years=row["years"],
                photo_url=row["photo_url"],
            )
            quote = Quote(id=row["quote_id"], person_id=person.id, text=row["quote_text"])
            return _build_card(conn, person, quote)

        person_row = conn.execute(
            "SELECT * FROM people ORDER BY RANDOM() LIMIT 1"
        ).fetchone()
        if not person_row:
            return None

        person = _row_to_person(person_row)
        return _build_card(conn, person, quote=None)


def get_card_for_person(person_id: int, quote_index: int = 0) -> PersonCard | None:
    with connect() as conn:
        person_row = conn.execute(
            "SELECT * FROM people WHERE id = ?", (person_id,)
        ).fetchone()
        if not person_row:
            return None

        person = _row_to_person(person_row)
        quotes = conn.execute(
            "SELECT * FROM quotes WHERE person_id = ? ORDER BY id",
            (person_id,),
        ).fetchall()
        if not quotes:
            return _build_card(conn, person, quote=None)

        quote_index = quote_index % len(quotes)
        quote = _row_to_quote(quotes[quote_index])
        return _build_card(conn, person, quote)


def get_card_by_quote_id(quote_id: int) -> PersonCard | None:
    quote = get_quote_by_id(quote_id)
    if not quote:
        return None

    with connect() as conn:
        person_row = conn.execute(
            "SELECT * FROM people WHERE id = ?", (quote.person_id,)
        ).fetchone()
        if not person_row:
            return None

        person = _row_to_person(person_row)
        return _build_card(conn, person, quote)


def get_adjacent_person_id(current_person_id: int, direction: int) -> int | None:
    people = list_people()
    if not people:
        return None

    ids = [person.id for person in people]
    try:
        index = ids.index(current_person_id)
    except ValueError:
        return people[0].id

    next_index = (index + direction) % len(ids)
    return ids[next_index]


def _build_card(conn, person: Person, quote: Quote | None = None) -> PersonCard:
    quote_rows = conn.execute(
        "SELECT id FROM quotes WHERE person_id = ? ORDER BY id",
        (person.id,),
    ).fetchall()
    quote_ids = [row["id"] for row in quote_rows]

    if quote and quote.id in quote_ids:
        quote_index = quote_ids.index(quote.id)
    elif quote_ids:
        quote_index = 0
        if quote is None or quote.id not in quote_ids:
            quote_row = conn.execute(
                "SELECT * FROM quotes WHERE id = ?", (quote_ids[0],)
            ).fetchone()
            quote = _row_to_quote(quote_row)
    else:
        quote_index = 0
        quote = None

    people_rows = conn.execute(
        "SELECT id FROM people ORDER BY name COLLATE NOCASE"
    ).fetchall()
    person_ids = [row["id"] for row in people_rows]
    person_index = person_ids.index(person.id)

    return PersonCard(
        person=person,
        quote=quote,
        quote_index=quote_index,
        quote_total=len(quote_ids),
        person_index=person_index,
        person_total=len(person_ids),
    )
