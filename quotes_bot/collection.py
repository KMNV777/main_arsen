import random
from dataclasses import dataclass

from quotes_bot.db import connect
from quotes_bot.models import QuoteCard, get_card_by_quote_id, get_quotes_for_person


@dataclass
class Pack:
    id: int
    slug: str
    name: str
    emoji: str
    description: str


@dataclass
class UserProfile:
    user_id: int
    tickets: int
    packs_opened: int
    cards_owned: int


@dataclass
class PackProgress:
    pack: Pack
    owned: int
    total: int
    members: list[str]


STARTER_TICKETS = 5
PACK_OPEN_COST = 1


def ensure_user(user_id: int) -> UserProfile:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        if row:
            return _row_to_profile(row, conn)

        conn.execute(
            "INSERT INTO user_profiles (user_id, tickets) VALUES (?, ?)",
            (user_id, STARTER_TICKETS),
        )
        return UserProfile(
            user_id=user_id,
            tickets=STARTER_TICKETS,
            packs_opened=0,
            cards_owned=0,
        )


def _row_to_profile(row, conn) -> UserProfile:
    cards_owned = conn.execute(
        "SELECT COUNT(*) FROM user_cards WHERE user_id = ?", (row["user_id"],)
    ).fetchone()[0]
    return UserProfile(
        user_id=row["user_id"],
        tickets=row["tickets"],
        packs_opened=row["packs_opened"],
        cards_owned=cards_owned,
    )


def get_user_profile(user_id: int) -> UserProfile:
    return ensure_user(user_id)


def list_packs() -> list[Pack]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM packs ORDER BY id").fetchall()
    return [_row_to_pack(row) for row in rows]


def get_pack_by_id(pack_id: int) -> Pack | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM packs WHERE id = ?", (pack_id,)).fetchone()
    return _row_to_pack(row) if row else None


def get_pack_by_slug(slug: str) -> Pack | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM packs WHERE slug = ?", (slug,)).fetchone()
    return _row_to_pack(row) if row else None


def _row_to_pack(row) -> Pack:
    return Pack(
        id=row["id"],
        slug=row["slug"],
        name=row["name"],
        emoji=row["emoji"],
        description=row["description"],
    )


def get_pack_member_ids(pack_id: int) -> list[int]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT person_id FROM pack_members WHERE pack_id = ? ORDER BY person_id",
            (pack_id,),
        ).fetchall()
    return [row["person_id"] for row in rows]


def get_pack_progress(user_id: int, pack_id: int) -> PackProgress | None:
    pack = get_pack_by_id(pack_id)
    if not pack:
        return None

    with connect() as conn:
        member_rows = conn.execute(
            """
            SELECT p.name
            FROM pack_members pm
            JOIN people p ON p.id = pm.person_id
            WHERE pm.pack_id = ?
            ORDER BY p.name COLLATE NOCASE
            """,
            (pack_id,),
        ).fetchall()
        total = conn.execute(
            """
            SELECT COUNT(*)
            FROM quotes q
            JOIN pack_members pm ON pm.person_id = q.person_id
            WHERE pm.pack_id = ?
            """,
            (pack_id,),
        ).fetchone()[0]
        owned = conn.execute(
            """
            SELECT COUNT(*)
            FROM user_cards uc
            JOIN quotes q ON q.id = uc.quote_id
            JOIN pack_members pm ON pm.person_id = q.person_id
            WHERE uc.user_id = ? AND pm.pack_id = ?
            """,
            (user_id, pack_id),
        ).fetchone()[0]

    return PackProgress(
        pack=pack,
        owned=owned,
        total=total,
        members=[row["name"] for row in member_rows],
    )


def user_owns_quote(user_id: int, quote_id: int) -> bool:
    with connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM user_cards WHERE user_id = ? AND quote_id = ?",
            (user_id, quote_id),
        ).fetchone()
    return row is not None


def get_owned_quote_ids(user_id: int) -> list[int]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT quote_id FROM user_cards WHERE user_id = ? ORDER BY quote_id",
            (user_id,),
        ).fetchall()
    return [row["quote_id"] for row in rows]


def get_owned_cards(user_id: int) -> list[QuoteCard]:
    cards: list[QuoteCard] = []
    for quote_id in get_owned_quote_ids(user_id):
        card = get_card_by_quote_id(quote_id)
        if card:
            cards.append(card)
    return cards


def get_person_collection_progress(user_id: int, person_id: int) -> tuple[int, int]:
    with connect() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM quotes WHERE person_id = ?", (person_id,)
        ).fetchone()[0]
        owned = conn.execute(
            """
            SELECT COUNT(*)
            FROM user_cards uc
            JOIN quotes q ON q.id = uc.quote_id
            WHERE uc.user_id = ? AND q.person_id = ?
            """,
            (user_id, person_id),
        ).fetchone()[0]
    return owned, total


def _pick_quote_for_person(user_id: int, person_id: int) -> int | None:
    quotes = get_quotes_for_person(person_id)
    if not quotes:
        return None

    unowned = [quote for quote in quotes if not user_owns_quote(user_id, quote.id)]
    pool = unowned or quotes
    return random.choice(pool).id


def add_card_to_collection(user_id: int, quote_id: int) -> bool:
    with connect() as conn:
        existing = conn.execute(
            "SELECT 1 FROM user_cards WHERE user_id = ? AND quote_id = ?",
            (user_id, quote_id),
        ).fetchone()
        if existing:
            return False
        conn.execute(
            "INSERT INTO user_cards (user_id, quote_id) VALUES (?, ?)",
            (user_id, quote_id),
        )
        return True


def spend_ticket(user_id: int, amount: int = PACK_OPEN_COST) -> bool:
    profile = ensure_user(user_id)
    if profile.tickets < amount:
        return False
    with connect() as conn:
        conn.execute(
            "UPDATE user_profiles SET tickets = tickets - ? WHERE user_id = ?",
            (amount, user_id),
        )
    return True


def open_pack(user_id: int, pack_id: int) -> tuple[list[QuoteCard], list[QuoteCard], str | None]:
    pack = get_pack_by_id(pack_id)
    if not pack:
        return [], [], "Пак не найден."

    profile = ensure_user(user_id)
    if profile.tickets < PACK_OPEN_COST:
        return [], [], "Не хватает билетов 🎫. Открой «👤 Профиль» — там баланс."

    member_ids = get_pack_member_ids(pack_id)
    if len(member_ids) < 2:
        return [], [], "В паке недостаточно игроков."

    if not spend_ticket(user_id):
        return [], [], "Не удалось списать билет."

    new_cards: list[QuoteCard] = []
    all_revealed: list[QuoteCard] = []

    for person_id in member_ids[:2]:
        quote_id = _pick_quote_for_person(user_id, person_id)
        if not quote_id:
            continue
        is_new = add_card_to_collection(user_id, quote_id)
        card = get_card_by_quote_id(quote_id)
        if not card:
            continue
        all_revealed.append(card)
        if is_new:
            new_cards.append(card)

    with connect() as conn:
        conn.execute(
            "UPDATE user_profiles SET packs_opened = packs_opened + 1 WHERE user_id = ?",
            (user_id,),
        )

    if not all_revealed:
        return [], [], "Не удалось выдать карточки из пака."

    return new_cards, all_revealed, None


def grant_tickets(user_id: int, amount: int) -> None:
    ensure_user(user_id)
    with connect() as conn:
        conn.execute(
            "UPDATE user_profiles SET tickets = tickets + ? WHERE user_id = ?",
            (amount, user_id),
        )


def get_random_owned_card(user_id: int) -> QuoteCard | None:
    quote_ids = get_owned_quote_ids(user_id)
    if not quote_ids:
        return None
    quote_id = random.choice(quote_ids)
    return get_card_by_quote_id(quote_id)


def get_adjacent_owned_quote_id(user_id: int, current_quote_id: int, direction: int) -> int | None:
    quote_ids = get_owned_quote_ids(user_id)
    if not quote_ids:
        return None
    try:
        index = quote_ids.index(current_quote_id)
    except ValueError:
        return quote_ids[0]
    return quote_ids[(index + direction) % len(quote_ids)]
