"""Validate Telegram Mini App initData."""

from __future__ import annotations

import hashlib
import hmac
import json
from urllib.parse import parse_qsl, unquote


class InitDataError(ValueError):
    pass


def _compute_hash(data_check_string: str, bot_token: str) -> str:
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    return hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()


def _parse_parts(init_data: str) -> tuple[str | None, dict[str, dict[str, str]]]:
    received_hash: str | None = None
    raw_values: dict[str, str] = {}
    decoded_values: dict[str, str] = {}

    for chunk in init_data.split("&"):
        if not chunk or "=" not in chunk:
            continue
        key, _, raw_value = chunk.partition("=")
        if key == "hash":
            received_hash = raw_value
            continue
        if key == "signature":
            continue
        raw_values[key] = raw_value
        decoded_values[key] = unquote(raw_value)

    return received_hash, {"raw": raw_values, "decoded": decoded_values}


def _finalize_payload(parsed: dict[str, str]) -> dict:
    result = dict(parsed)
    user_raw = result.get("user")
    if user_raw:
        result["user"] = json.loads(user_raw)
    return result


def _validate_with_raw_values(init_data: str, bot_token: str) -> dict:
    received_hash, values = _parse_parts(init_data)
    if not received_hash:
        raise InitDataError("hash missing")

    check_pairs = [f"{key}={value}" for key, value in values["raw"].items()]
    data_check_string = "\n".join(sorted(check_pairs))
    if not hmac.compare_digest(_compute_hash(data_check_string, bot_token), received_hash):
        raise InitDataError("invalid initData signature")

    return _finalize_payload(values["decoded"])


def _validate_with_decoded_values(init_data: str, bot_token: str) -> dict:
    received_hash, values = _parse_parts(init_data)
    if not received_hash:
        raise InitDataError("hash missing")

    check_pairs = [f"{key}={value}" for key, value in values["decoded"].items()]
    data_check_string = "\n".join(sorted(check_pairs))
    if not hmac.compare_digest(_compute_hash(data_check_string, bot_token), received_hash):
        raise InitDataError("invalid initData signature")

    return _finalize_payload(values["decoded"])


def _validate_with_parse_qsl(init_data: str, bot_token: str) -> dict:
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise InitDataError("hash missing")
    parsed.pop("signature", None)

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    if not hmac.compare_digest(_compute_hash(data_check_string, bot_token), received_hash):
        raise InitDataError("invalid initData signature")

    return _finalize_payload(parsed)


def validate_init_data(init_data: str, bot_token: str) -> dict:
    init_data = init_data.strip()
    if not init_data:
        raise InitDataError("initData is required")
    if not bot_token:
        raise InitDataError("Bot token is not configured")

    last_error: InitDataError | None = None
    for validator in (_validate_with_raw_values, _validate_with_decoded_values, _validate_with_parse_qsl):
        try:
            return validator(init_data, bot_token)
        except InitDataError as exc:
            last_error = exc

    raise last_error or InitDataError("invalid initData signature")


def get_user_id_from_init_data(init_data: str, bot_token: str) -> int:
    payload = validate_init_data(init_data, bot_token)
    user = payload.get("user")
    if not user or "id" not in user:
        raise InitDataError("user id missing")
    return int(user["id"])


def parse_init_data_loose(init_data: str) -> dict:
    """Parse initData without signature check (Mini App fallback)."""
    init_data = init_data.strip()
    if not init_data:
        raise InitDataError("initData is required")

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    parsed.pop("hash", None)
    parsed.pop("signature", None)
    user_raw = parsed.get("user")
    if not user_raw:
        raise InitDataError("user id missing")

    return _finalize_payload(parsed)
