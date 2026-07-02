"""Fire-and-forget Telegram notifications from the Mini App server."""

from __future__ import annotations

import asyncio
import json
import logging

import aiohttp

from quotes_bot.config import TELEGRAM_BOT_TOKEN, get_webapp_url

logger = logging.getLogger(__name__)


async def send_user_message(user_id: int, text: str) -> None:
    if not TELEGRAM_BOT_TOKEN:
        return

    payload: dict = {
        "chat_id": user_id,
        "text": text,
        "parse_mode": "HTML",
    }
    webapp_url = get_webapp_url()
    if webapp_url:
        payload["reply_markup"] = json.dumps(
            {
                "inline_keyboard": [
                    [{"text": "🎮 Играть", "web_app": {"url": webapp_url}}]
                ]
            }
        )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    logger.warning("Telegram notify failed (%s): %s", resp.status, body[:200])
    except Exception:
        logger.exception("Telegram notify error for user %s", user_id)


def notify_user(user_id: int, text: str) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    loop.create_task(send_user_message(user_id, text))
