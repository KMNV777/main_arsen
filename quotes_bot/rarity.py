"""Card rarity tiers (deterministic per quote)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RarityInfo:
    slug: str
    label: str
    emoji: str
    color: tuple[int, int, int]
    css_color: str


RARITIES: dict[str, RarityInfo] = {
    "common": RarityInfo("common", "Обычная", "⚪", (154, 160, 181), "#9aa0b5"),
    "rare": RarityInfo("rare", "Редкая", "🔵", (90, 141, 255), "#5a8dff"),
    "epic": RarityInfo("epic", "Эпическая", "🟣", (124, 92, 255), "#7c5cff"),
    "legendary": RarityInfo("legendary", "Легендарная", "🟡", (255, 184, 77), "#ffb84d"),
}


def get_quote_rarity(quote_id: int) -> RarityInfo:
    roll = (quote_id * 2654435761) % 100
    if roll < 3:
        return RARITIES["legendary"]
    if roll < 12:
        return RARITIES["epic"]
    if roll < 35:
        return RARITIES["rare"]
    return RARITIES["common"]


def rarity_payload(rarity: RarityInfo) -> dict:
    return {
        "rarity": rarity.slug,
        "rarity_label": rarity.label,
        "rarity_emoji": rarity.emoji,
        "rarity_color": rarity.css_color,
    }
