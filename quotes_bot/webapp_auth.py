"""Validate Telegram Mini App initData."""

from __future__ import annotations

import hashlib
import hmac
import json
from urllib.parse import parse_qsl, unquote


class InitDataError(ValueError):
    pass


def validate_init_data(init_data: str, bot_token: str) -> dict:
    if not init_data:
        raise InitDataError("initData is required")
    if not bot_token:
        raise InitDataError("Bot token is not configured")

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise InitDataError("hash missing")

    # Ed25519 signature for third-party checks — not part of bot HMAC hash.
    parsed.pop("signature", None)

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise InitDataError("invalid initData signature")

    user_raw = parsed.get("user")
    if user_raw:
        parsed["user"] = json.loads(unquote(user_raw))
    return parsed


def get_user_id_from_init_data(init_data: str, bot_token: str) -> int:
    payload = validate_init_data(init_data, bot_token)
    user = payload.get("user")
    if not user or "id" not in user:
        raise InitDataError("user id missing")
    return int(user["id"])
