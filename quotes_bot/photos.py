from pathlib import Path

from quotes_bot.config import PHOTOS_DIR


def resolve_photo(photo_url: str | None) -> str | Path | None:
    if not photo_url:
        return None
    if photo_url.startswith(("http://", "https://")):
        return photo_url
    local_path = PHOTOS_DIR / photo_url
    if local_path.exists():
        return local_path
    return None
