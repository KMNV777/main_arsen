"""HTTP server for Telegram Mini App."""

from __future__ import annotations

import asyncio
import logging
import threading
from pathlib import Path

from aiohttp import web

from quotes_bot.card_renderer import render_card_bytes
from quotes_bot.collection import (
    DUST_FOR_CARD,
    DUST_FOR_TICKET,
    PACK_OPEN_COST,
    exchange_dust_for_card,
    exchange_dust_for_ticket,
    format_leaderboard,
    get_leaderboard,
    get_owned_cards,
    get_pack_progress,
    get_person_collection_progress,
    get_user_profile,
    get_user_rank,
    list_packs,
    open_pack,
    touch_user,
    disintegrate_card,
    DUST_PER_DUPLICATE,
    DUST_PER_DISINTEGRATE,
)
from quotes_bot.config import TELEGRAM_BOT_TOKEN, WEBAPP_HOST, WEBAPP_PORT, WEBAPP_URL
from quotes_bot.db import connect
from quotes_bot.models import QuoteCard, get_card_by_quote_id, list_people
from quotes_bot.webapp_auth import InitDataError, parse_init_data_loose, validate_init_data

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent / "webapp" / "static"


async def _read_auth_payload(request: web.Request) -> tuple[list[str], dict | None]:
    candidates: list[str] = []
    body_user: dict | None = None

    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("tma "):
        value = auth[4:].strip()
        if value:
            candidates.append(value)

    query_value = request.query.get("initData")
    if query_value:
        candidates.append(query_value)

    header = request.headers.get("X-Telegram-Init-Data", "")
    if header:
        candidates.append(header)

    if request.body_exists and request.content_type == "application/json":
        try:
            body = await request.json()
            value = body.get("initData", "")
            if value:
                candidates.append(value)
            if isinstance(body.get("user"), dict):
                body_user = body["user"]
        except Exception:
            pass

    unique: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique, body_user


def _touch_from_user_dict(user: dict) -> int:
    display_name = user.get("first_name", "")
    if user.get("last_name"):
        display_name = f"{display_name} {user['last_name']}".strip()
    user_id = int(user["id"])
    touch_user(
        user_id,
        username=user.get("username"),
        display_name=display_name or None,
    )
    return user_id


async def _resolve_user(request: web.Request) -> tuple[int, dict]:
    candidates, body_user = await _read_auth_payload(request)
    last_error: InitDataError | None = None

    for init_data in candidates:
        try:
            payload = validate_init_data(init_data, TELEGRAM_BOT_TOKEN)
            user = payload.get("user") or {}
            user_id = _touch_from_user_dict(user)
            return user_id, payload
        except InitDataError as exc:
            last_error = exc

    for init_data in candidates:
        try:
            payload = parse_init_data_loose(init_data)
            user_id = _touch_from_user_dict(payload["user"])
            logger.info("Mini App: loose initData auth for user %s", user_id)
            return user_id, payload
        except (InitDataError, KeyError, TypeError, ValueError):
            continue

    if body_user and body_user.get("id"):
        user_id = _touch_from_user_dict(body_user)
        logger.info("Mini App: initDataUnsafe auth for user %s", user_id)
        return user_id, {"user": body_user}

    raise last_error or InitDataError("initData is required")


def _profile_payload(user_id: int) -> dict:
    profile = get_user_profile(user_id)
    rank, _ = get_user_rank(user_id)
    total_cards = 0
    for pack in list_packs():
        progress = get_pack_progress(user_id, pack.id)
        if progress:
            total_cards += progress.total
    return {
        "user_id": user_id,
        "tickets": profile.tickets,
        "duplicate_dust": profile.duplicate_dust,
        "cards_owned": profile.cards_owned,
        "total_cards": total_cards,
        "packs_opened": profile.packs_opened,
        "rank": rank,
        "dust_for_ticket": DUST_FOR_TICKET,
        "dust_for_card": DUST_FOR_CARD,
        "dust_per_duplicate": DUST_PER_DUPLICATE,
        "dust_per_disintegrate": DUST_PER_DISINTEGRATE,
        "pack_open_cost": PACK_OPEN_COST,
        "packs_are_free": PACK_OPEN_COST == 0,
    }


def _pack_catalog_item(pack, *, user_id: int | None = None) -> dict:
    if user_id is not None:
        progress = get_pack_progress(user_id, pack.id)
        if progress:
            return {
                "id": pack.id,
                "slug": pack.slug,
                "name": pack.name,
                "emoji": pack.emoji,
                "description": pack.description,
                "owned": progress.owned,
                "total": progress.total,
                "members": progress.members,
            }

    with connect() as conn:
        member_rows = conn.execute(
            """
            SELECT p.name
            FROM pack_members pm
            JOIN people p ON p.id = pm.person_id
            WHERE pm.pack_id = ?
            ORDER BY p.name COLLATE NOCASE
            """,
            (pack.id,),
        ).fetchall()
        total = conn.execute(
            """
            SELECT COUNT(*)
            FROM quotes q
            JOIN pack_members pm ON pm.person_id = q.person_id
            WHERE pm.pack_id = ?
            """,
            (pack.id,),
        ).fetchone()[0]

    return {
        "id": pack.id,
        "slug": pack.slug,
        "name": pack.name,
        "emoji": pack.emoji,
        "description": pack.description,
        "owned": 0,
        "total": total,
        "members": [row["name"] for row in member_rows],
    }


def _card_payload(card: QuoteCard, *, is_new: bool = False) -> dict:
    return {
        "quote_id": card.quote.id,
        "person_name": card.person.name,
        "quote_text": card.quote.text,
        "card_index": card.card_index,
        "card_total": card.card_total,
        "is_new": is_new,
        "image_url": f"/api/card/{card.quote.id}/image",
    }


async def handle_index(_: web.Request) -> web.Response:
    return web.FileResponse(STATIC_DIR / "index.html")


async def handle_static(request: web.Request) -> web.Response:
    path = STATIC_DIR / request.match_info["path"]
    if not path.exists() or not path.is_file():
        raise web.HTTPNotFound()
    return web.FileResponse(path)


async def handle_config(_: web.Request) -> web.Response:
    return web.json_response({"webapp_url": WEBAPP_URL or None})


async def handle_profile(request: web.Request) -> web.Response:
    try:
        user_id, _ = await _resolve_user(request)
    except InitDataError as exc:
        return web.json_response({"error": str(exc)}, status=401)
    return web.json_response(_profile_payload(user_id))


async def handle_packs(request: web.Request) -> web.Response:
    items = [_pack_catalog_item(pack) for pack in list_packs()]
    payload: dict = {"packs": items, "profile": None}

    try:
        user_id, _ = await _resolve_user(request)
        payload["profile"] = _profile_payload(user_id)
        payload["packs"] = [_pack_catalog_item(pack, user_id=user_id) for pack in list_packs()]
    except InitDataError as exc:
        payload["auth_error"] = str(exc)

    return web.json_response(payload)


async def handle_open_pack(request: web.Request) -> web.Response:
    try:
        user_id, _ = await _resolve_user(request)
    except InitDataError as exc:
        return web.json_response({"error": str(exc)}, status=401)

    pack_id = int(request.match_info["pack_id"])
    new_cards, revealed, error = open_pack(user_id, pack_id)
    if error:
        return web.json_response({"error": error}, status=400)

    new_ids = {card.quote.id for card in new_cards}
    dust_gained = (len(revealed) - len(new_cards)) * DUST_PER_DUPLICATE
    return web.json_response(
        {
            "new_count": len(new_cards),
            "duplicate_count": len(revealed) - len(new_cards),
            "dust_gained": dust_gained,
            "cards": [_card_payload(card, is_new=card.quote.id in new_ids) for card in revealed],
            "profile": _profile_payload(user_id),
        }
    )


async def handle_collection(request: web.Request) -> web.Response:
    try:
        user_id, _ = await _resolve_user(request)
    except InitDataError as exc:
        return web.json_response({"error": str(exc)}, status=401)

    people = []
    for person in list_people():
        owned, total = get_person_collection_progress(user_id, person.id)
        if owned == 0:
            continue
        people.append(
            {
                "person_id": person.id,
                "name": person.name,
                "owned": owned,
                "total": total,
            }
        )

    cards = [_card_payload(card) for card in get_owned_cards(user_id)]
    return web.json_response(
        {
            "people": people,
            "cards": cards,
            "profile": _profile_payload(user_id),
        }
    )


async def handle_leaderboard(request: web.Request) -> web.Response:
    try:
        user_id, _ = await _resolve_user(request)
    except InitDataError as exc:
        return web.json_response({"error": str(exc)}, status=401)

    entries = get_leaderboard(10)
    rank, cards = get_user_rank(user_id)
    return web.json_response(
        {
            "entries": [
                {
                    "rank": entry.rank,
                    "user_id": entry.user_id,
                    "display_name": entry.display_name,
                    "cards_owned": entry.cards_owned,
                    "packs_opened": entry.packs_opened,
                    "is_you": entry.user_id == user_id,
                }
                for entry in entries
            ],
            "your_rank": rank,
            "your_cards": cards,
            "text": format_leaderboard(entries, highlight_user_id=user_id),
        }
    )


async def handle_exchange_ticket(request: web.Request) -> web.Response:
    try:
        user_id, _ = await _resolve_user(request)
    except InitDataError as exc:
        return web.json_response({"error": str(exc)}, status=401)

    ok, message = exchange_dust_for_ticket(user_id)
    payload = {"ok": ok, "message": message, "profile": _profile_payload(user_id)}
    return web.json_response(payload, status=200 if ok else 400)


async def handle_exchange_card(request: web.Request) -> web.Response:
    try:
        user_id, _ = await _resolve_user(request)
    except InitDataError as exc:
        return web.json_response({"error": str(exc)}, status=401)

    ok, message, card = exchange_dust_for_card(user_id)
    payload = {
        "ok": ok,
        "message": message,
        "profile": _profile_payload(user_id),
        "card": _card_payload(card, is_new=True) if card else None,
    }
    return web.json_response(payload, status=200 if ok else 400)


async def handle_disintegrate(request: web.Request) -> web.Response:
    try:
        user_id, _ = await _resolve_user(request)
    except InitDataError as exc:
        return web.json_response({"error": str(exc)}, status=401)

    quote_id = int(request.match_info["quote_id"])
    ok, message = disintegrate_card(user_id, quote_id)
    return web.json_response(
        {
            "ok": ok,
            "message": message,
            "dust_gained": DUST_PER_DISINTEGRATE if ok else 0,
            "profile": _profile_payload(user_id),
        },
        status=200 if ok else 400,
    )


async def handle_card_image(request: web.Request) -> web.Response:
    quote_id = int(request.match_info["quote_id"])
    try:
        await _resolve_user(request)
    except InitDataError as exc:
        return web.json_response({"error": str(exc)}, status=401)

    card = get_card_by_quote_id(quote_id)
    if not card:
        raise web.HTTPNotFound()

    is_new = request.query.get("new") == "1"
    image = render_card_bytes(card, is_new=is_new)
    return web.Response(body=image.read(), content_type="image/jpeg")


def create_webapp() -> web.Application:
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/api/config", handle_config)
    app.router.add_get("/api/profile", handle_profile)
    app.router.add_post("/api/profile", handle_profile)
    app.router.add_get("/api/packs", handle_packs)
    app.router.add_post("/api/packs", handle_packs)
    app.router.add_post("/api/packs/{pack_id}/open", handle_open_pack)
    app.router.add_get("/api/collection", handle_collection)
    app.router.add_post("/api/collection", handle_collection)
    app.router.add_get("/api/leaderboard", handle_leaderboard)
    app.router.add_post("/api/leaderboard", handle_leaderboard)
    app.router.add_post("/api/exchange/ticket", handle_exchange_ticket)
    app.router.add_post("/api/exchange/card", handle_exchange_card)
    app.router.add_post("/api/cards/{quote_id}/disintegrate", handle_disintegrate)
    app.router.add_get("/api/card/{quote_id}/image", handle_card_image)
    app.router.add_get("/static/{path:.+}", handle_static)
    return app


_runner: web.AppRunner | None = None
_thread: threading.Thread | None = None


def _run_server_loop() -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _start() -> None:
        global _runner
        app = create_webapp()
        _runner = web.AppRunner(app)
        await _runner.setup()
        site = web.TCPSite(_runner, WEBAPP_HOST, WEBAPP_PORT)
        await site.start()
        logger.info("Mini App server listening on http://%s:%s", WEBAPP_HOST, WEBAPP_PORT)
        if WEBAPP_URL:
            logger.info("Mini App URL: %s", WEBAPP_URL)
        else:
            logger.warning(
                "WEBAPP_URL is not set. Configure HTTPS URL in .env and BotFather Menu Button."
            )

    loop.run_until_complete(_start())
    loop.run_forever()


def start_webapp_server() -> None:
    global _thread
    if _thread and _thread.is_alive():
        return
    _thread = threading.Thread(target=_run_server_loop, name="quotes-webapp", daemon=True)
    _thread.start()
