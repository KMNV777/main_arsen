"""Player-to-player card trading."""

from __future__ import annotations

from dataclasses import dataclass

from quotes_bot.collection import (
    ensure_user,
    format_player_name,
    get_card_by_quote_id,
    get_user_profile,
    user_owns_quote,
)
from quotes_bot.db import connect
from quotes_bot.models import QuoteCard


@dataclass
class TradeOffer:
    id: int
    from_user_id: int
    to_user_id: int
    offered_quote_id: int
    requested_quote_id: int | None
    returned_quote_id: int | None
    status: str
    created_at: str
    from_name: str
    to_name: str


def find_user_id_by_username(username: str) -> int | None:
    needle = username.strip().lstrip("@").casefold()
    if not needle:
        return None
    with connect() as conn:
        row = conn.execute(
            """
            SELECT user_id FROM user_profiles
            WHERE username IS NOT NULL AND LOWER(username) = ?
            """,
            (needle,),
        ).fetchone()
    return int(row["user_id"]) if row else None


def _profile_name(user_id: int) -> str:
    profile = get_user_profile(user_id)
    return format_player_name(user_id, profile.username, profile.display_name)


def _transfer_card(from_user_id: int, to_user_id: int, quote_id: int, conn) -> None:
    conn.execute(
        "DELETE FROM user_cards WHERE user_id = ? AND quote_id = ?",
        (from_user_id, quote_id),
    )
    conn.execute(
        "DELETE FROM user_card_stats WHERE user_id = ? AND quote_id = ?",
        (from_user_id, quote_id),
    )
    conn.execute(
        "INSERT OR IGNORE INTO user_cards (user_id, quote_id) VALUES (?, ?)",
        (to_user_id, quote_id),
    )
    conn.execute(
        """
        INSERT INTO user_card_stats (user_id, quote_id, duplicate_count)
        VALUES (?, ?, 0)
        ON CONFLICT(user_id, quote_id) DO NOTHING
        """,
        (to_user_id, quote_id),
    )


def _get_trade_row(trade_id: int):
    with connect() as conn:
        return conn.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone()


def _row_to_trade(row) -> TradeOffer:
    return TradeOffer(
        id=row["id"],
        from_user_id=row["from_user_id"],
        to_user_id=row["to_user_id"],
        offered_quote_id=row["offered_quote_id"],
        requested_quote_id=row["requested_quote_id"],
        returned_quote_id=row["returned_quote_id"],
        status=row["status"],
        created_at=row["created_at"],
        from_name=_profile_name(row["from_user_id"]),
        to_name=_profile_name(row["to_user_id"]),
    )


def trade_card_payload(card: QuoteCard, *, duplicate_count: int = 0) -> dict:
    from quotes_bot.rarity import get_quote_rarity, rarity_payload

    payload = {
        "quote_id": card.quote.id,
        "person_name": card.person.name,
        "quote_text": card.quote.text,
        "duplicate_count": duplicate_count,
        "is_duplicate": duplicate_count > 0,
        "image_url": f"/api/card/{card.quote.id}/image",
    }
    payload.update(rarity_payload(get_quote_rarity(card.quote.id)))
    return payload


def get_partner_trade_cards(partner_user_id: int) -> list[dict]:
    from quotes_bot.collection import get_owned_cards_with_stats

    return [
        trade_card_payload(card, duplicate_count=dup)
        for card, dup in get_owned_cards_with_stats(partner_user_id)
    ]


def list_trades(user_id: int) -> dict:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM trades
            WHERE (from_user_id = ? OR to_user_id = ?)
              AND status = 'pending'
            ORDER BY id DESC
            LIMIT 30
            """,
            (user_id, user_id),
        ).fetchall()

    incoming: list[dict] = []
    outgoing: list[dict] = []

    for row in rows:
        trade = _trade_payload(row, viewer_id=user_id)
        if row["to_user_id"] == user_id:
            incoming.append(trade)
        else:
            outgoing.append(trade)

    return {"incoming": incoming, "outgoing": outgoing}


def _trade_payload(row, *, viewer_id: int) -> dict:
    offered = get_card_by_quote_id(row["offered_quote_id"])
    requested = (
        get_card_by_quote_id(row["requested_quote_id"])
        if row["requested_quote_id"]
        else None
    )
    returned = (
        get_card_by_quote_id(row["returned_quote_id"])
        if row["returned_quote_id"]
        else None
    )

    return {
        "id": row["id"],
        "status": row["status"],
        "created_at": row["created_at"],
        "from_user_id": row["from_user_id"],
        "to_user_id": row["to_user_id"],
        "from_name": _profile_name(row["from_user_id"]),
        "to_name": _profile_name(row["to_user_id"]),
        "is_incoming": row["to_user_id"] == viewer_id,
        "offered_card": trade_card_payload(offered) if offered else None,
        "requested_card": trade_card_payload(requested) if requested else None,
        "returned_card": trade_card_payload(returned) if returned else None,
    }


def create_trade(
    from_user_id: int,
    *,
    partner_username: str,
    offered_quote_id: int,
    requested_quote_id: int | None = None,
) -> tuple[bool, str, TradeOffer | None]:
    ensure_user(from_user_id)
    partner_id = find_user_id_by_username(partner_username)
    if not partner_id:
        return False, "Игрок не найден. Укажи @username — он должен хотя бы раз написать боту.", None
    if partner_id == from_user_id:
        return False, "Нельзя обмениваться с самим собой", None
    if not user_owns_quote(from_user_id, offered_quote_id):
        return False, "Эта карта не в твоей коллекции", None
    if requested_quote_id is not None:
        if not user_owns_quote(partner_id, requested_quote_id):
            return False, "У игрока нет запрошенной карты", None

    with connect() as conn:
        pending = conn.execute(
            """
            SELECT COUNT(*) FROM trades
            WHERE from_user_id = ? AND status = 'pending'
            """,
            (from_user_id,),
        ).fetchone()[0]
        if pending >= 5:
            return False, "Слишком много активных предложений (макс. 5)", None

        duplicate = conn.execute(
            """
            SELECT 1 FROM trades
            WHERE from_user_id = ? AND to_user_id = ? AND offered_quote_id = ?
              AND status = 'pending'
            """,
            (from_user_id, partner_id, offered_quote_id),
        ).fetchone()
        if duplicate:
            return False, "Такое предложение уже отправлено", None

        cursor = conn.execute(
            """
            INSERT INTO trades (
                from_user_id, to_user_id, offered_quote_id, requested_quote_id, status
            ) VALUES (?, ?, ?, ?, 'pending')
            """,
            (from_user_id, partner_id, offered_quote_id, requested_quote_id),
        )
        trade_id = cursor.lastrowid

    row = _get_trade_row(trade_id)
    trade = _row_to_trade(row) if row else None
    offered = get_card_by_quote_id(offered_quote_id)
    name = offered.person.name if offered else "карту"
    return True, f"🤝 Предложение отправлено {_profile_name(partner_id)}: {name}", trade


def accept_trade(
    user_id: int,
    trade_id: int,
    *,
    give_quote_id: int,
) -> tuple[bool, str]:
    row = _get_trade_row(trade_id)
    if not row:
        return False, "Обмен не найден"
    if row["status"] != "pending":
        return False, "Это предложение уже закрыто"
    if row["to_user_id"] != user_id:
        return False, "Принять может только получатель"
    if not user_owns_quote(row["from_user_id"], row["offered_quote_id"]):
        return False, "У отправителя больше нет предложенной карты"
    if not user_owns_quote(user_id, give_quote_id):
        return False, "Выбери свою карту из коллекции"

    requested = row["requested_quote_id"]
    if requested is not None and give_quote_id != requested:
        return False, "Нужно отдать запрошенную карту"

    with connect() as conn:
        conn.execute(
            """
            UPDATE trades
            SET status = 'accepted', returned_quote_id = ?, resolved_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'pending'
            """,
            (give_quote_id, trade_id),
        )
        if conn.total_changes == 0:
            return False, "Не удалось принять обмен"

        _transfer_card(row["from_user_id"], row["to_user_id"], row["offered_quote_id"], conn)
        _transfer_card(user_id, row["from_user_id"], give_quote_id, conn)

    offered = get_card_by_quote_id(row["offered_quote_id"])
    given = get_card_by_quote_id(give_quote_id)
    return True, (
        f"✅ Обмен завершён!\n"
        f"Ты получил: <b>{offered.person.name if offered else '?'}</b>\n"
        f"Отдал: <b>{given.person.name if given else '?'}</b>"
    )


def decline_trade(user_id: int, trade_id: int) -> tuple[bool, str]:
    row = _get_trade_row(trade_id)
    if not row:
        return False, "Обмен не найден"
    if row["to_user_id"] != user_id:
        return False, "Отклонить может только получатель"
    with connect() as conn:
        conn.execute(
            """
            UPDATE trades
            SET status = 'declined', resolved_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'pending'
            """,
            (trade_id,),
        )
        if conn.total_changes == 0:
            return False, "Предложение уже закрыто"
    return True, "Предложение отклонено"


def cancel_trade(user_id: int, trade_id: int) -> tuple[bool, str]:
    row = _get_trade_row(trade_id)
    if not row:
        return False, "Обмен не найден"
    if row["from_user_id"] != user_id:
        return False, "Отменить может только отправитель"
    with connect() as conn:
        conn.execute(
            """
            UPDATE trades
            SET status = 'cancelled', resolved_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'pending'
            """,
            (trade_id,),
        )
        if conn.total_changes == 0:
            return False, "Предложение уже закрыто"
    return True, "Предложение отменено"
