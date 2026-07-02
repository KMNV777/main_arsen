from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from quotes_bot.config import PHOTOS_DIR
from quotes_bot.rarity import get_quote_rarity
from quotes_bot.photos import resolve_photo

CARD_WIDTH = 900
CARD_HEIGHT = 1280
PHOTO_HEIGHT = 860
PANEL_TOP = PHOTO_HEIGHT
PANEL_COLOR = (22, 22, 28)
BG_COLOR = (18, 18, 22)
NAME_COLOR = (245, 245, 245)
QUOTE_COLOR = (190, 190, 200)
MUTED_COLOR = (120, 120, 130)
ACCENT_COLOR = (90, 90, 110)

PORTRAIT_SIZE = (CARD_WIDTH, PHOTO_HEIGHT)

PLACEHOLDER_ACCENTS = {
    "vanya_wyhm.jpg": (72, 98, 140),
    "mashinka.jpg": (140, 92, 72),
    "khurov_azamat.jpg": (92, 120, 88),
    "arsen_sensei.jpg": (110, 88, 130),
    "arsen_akmanov.jpg": (130, 110, 72),
    "grisha.jpg": (88, 108, 130),
    "artemida.jpg": (130, 88, 108),
    "yomma.jpg": (98, 118, 130),
}


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _cover_crop(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize(
        (int(image.width * scale), int(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def _wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word]) if current else word
        if draw.textlength(candidate, font=font) <= max_width:
            current.append(word)
            continue
        if current:
            lines.append(" ".join(current))
        current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _load_portrait(photo_url: str | None, person_name: str) -> Image.Image:
    source = resolve_photo(photo_url)
    if source is not None:
        with Image.open(source) as image:
            return _cover_crop(image, PORTRAIT_SIZE)

    accent = PLACEHOLDER_ACCENTS.get(photo_url or "", (100, 100, 120))
    image = Image.new("RGB", PORTRAIT_SIZE, accent)
    draw = ImageDraw.Draw(image)
    initials = "".join(part[0] for part in person_name.split()[:2]).upper() or "?"
    font = _load_font(160, bold=True)
    bbox = draw.textbbox((0, 0), initials, font=font)
    draw.text(
        (
            (PORTRAIT_SIZE[0] - (bbox[2] - bbox[0])) / 2,
            (PORTRAIT_SIZE[1] - (bbox[3] - bbox[1])) / 2 - 20,
        ),
        initials,
        fill=(255, 255, 255),
        font=font,
    )
    return image


def render_card_image(
    card: QuoteCard,
    *,
    is_new: bool = False,
    show_duplicate: bool = False,
    duplicate_count: int = 0,
) -> Image.Image:
    canvas = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), BG_COLOR)
    portrait = _load_portrait(card.person.photo_url, card.person.name)
    canvas.paste(portrait, (0, 0))

    draw = ImageDraw.Draw(canvas)
    rarity = get_quote_rarity(card.quote.id)
    badge_font = _load_font(26, bold=True)
    small_font = _load_font(22, bold=True)

    rarity_text = f"{rarity.emoji} {rarity.label.upper()}"
    rarity_bbox = draw.textbbox((0, 0), rarity_text, font=badge_font)
    rarity_w = rarity_bbox[2] - rarity_bbox[0]
    rarity_h = rarity_bbox[3] - rarity_bbox[1]
    draw.rounded_rectangle(
        (24, 24, 36 + rarity_w, 36 + rarity_h),
        radius=12,
        fill=rarity.color,
    )
    draw.text((30, 28), rarity_text, fill=(255, 255, 255), font=badge_font)

    if is_new:
        draw.rounded_rectangle(
            (CARD_WIDTH - 196, 24, CARD_WIDTH - 24, 72),
            radius=12,
            fill=(0, 180, 120),
        )
        draw.text((CARD_WIDTH - 178, 30), "✨ NEW", fill=(255, 255, 255), font=badge_font)

    if show_duplicate or duplicate_count > 0:
        dup_label = "🔁 DUP"
        if duplicate_count > 1:
            dup_label = f"🔁 DUP ×{duplicate_count}"
        dup_bbox = draw.textbbox((0, 0), dup_label, font=small_font)
        dup_w = dup_bbox[2] - dup_bbox[0]
        dup_h = dup_bbox[3] - dup_bbox[1]
        dup_y = 84 if is_new else 24
        draw.rounded_rectangle(
            (CARD_WIDTH - dup_w - 48, dup_y, CARD_WIDTH - 24, dup_y + dup_h + 12),
            radius=12,
            fill=(90, 90, 110),
        )
        draw.text((CARD_WIDTH - dup_w - 36, dup_y + 4), dup_label, fill=(255, 255, 255), font=small_font)

    draw.rectangle((0, PANEL_TOP, CARD_WIDTH, CARD_HEIGHT), fill=PANEL_COLOR)
    draw.line((56, PANEL_TOP + 28, CARD_WIDTH - 56, PANEL_TOP + 28), fill=ACCENT_COLOR, width=2)

    name_font = _load_font(54, bold=True)
    quote_font = _load_font(36)
    counter_font = _load_font(24)

    name_y = PANEL_TOP + 56
    draw.text((56, name_y), card.person.name, fill=NAME_COLOR, font=name_font)

    quote = f"«{card.quote.text}»"
    max_width = CARD_WIDTH - 112
    lines = _wrap_text(quote, quote_font, max_width, draw)
    quote_y = name_y + 78
    line_height = 46
    for index, line in enumerate(lines[:4]):
        draw.text((56, quote_y + index * line_height), line, fill=QUOTE_COLOR, font=quote_font)

    counter = f"{card.card_index + 1} / {card.card_total}"
    counter_bbox = draw.textbbox((0, 0), counter, font=counter_font)
    counter_w = counter_bbox[2] - counter_bbox[0]
    draw.text(
        (CARD_WIDTH - 56 - counter_w, CARD_HEIGHT - 52),
        counter,
        fill=MUTED_COLOR,
        font=counter_font,
    )
    return canvas


def render_card_bytes(
    card: QuoteCard,
    *,
    is_new: bool = False,
    show_duplicate: bool = False,
    duplicate_count: int = 0,
) -> BytesIO:
    buffer = BytesIO()
    render_card_image(
        card,
        is_new=is_new,
        show_duplicate=show_duplicate,
        duplicate_count=duplicate_count,
    ).save(buffer, format="JPEG", quality=92)
    buffer.seek(0)
    return buffer


def save_portrait(source: Path, destination: Path) -> None:
    with Image.open(source) as image:
        portrait = _cover_crop(image, PORTRAIT_SIZE)
        destination.parent.mkdir(parents=True, exist_ok=True)
        portrait.save(destination, format="JPEG", quality=92)
