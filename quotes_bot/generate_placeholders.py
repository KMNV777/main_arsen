from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from quotes_bot.config import PHOTOS_DIR

CARD_SIZE = (900, 1200)
PHOTO_HEIGHT = 780
BG_COLOR = (18, 18, 22)
TEXT_COLOR = (245, 245, 245)
ACCENT_COLOR = (120, 120, 130)

PEOPLE = [
    ("vanya_wyhm.jpg", "Ваня WYHM", (72, 98, 140)),
    ("mashinka.jpg", "Машинка", (140, 92, 72)),
    ("khurov_azamat.jpg", "Хуров Азамат", (92, 120, 88)),
    ("arsen_sensei.jpg", "Арсен Сенсей", (110, 88, 130)),
    ("arsen_akmanov.jpg", "Арсен Акманов", (130, 110, 72)),
    ("grisha.jpg", "Гриша", (88, 108, 130)),
    ("artemida.jpg", "Артемида", (130, 88, 108)),
    ("yomma.jpg", "Йомма", (98, 118, 130)),
]


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def generate_placeholder(filename: str, name: str, accent: tuple[int, int, int]) -> Path:
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    output = PHOTOS_DIR / filename

    image = Image.new("RGB", CARD_SIZE, BG_COLOR)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, CARD_SIZE[0], PHOTO_HEIGHT), fill=accent)
    initials = "".join(part[0] for part in name.split()[:2]).upper()
    font = _load_font(180, bold=True)
    bbox = draw.textbbox((0, 0), initials, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(
        ((CARD_SIZE[0] - text_w) / 2, (PHOTO_HEIGHT - text_h) / 2 - 20),
        initials,
        fill=(255, 255, 255),
        font=font,
    )

    name_font = _load_font(52, bold=True)
    bbox = draw.textbbox((0, 0), name, font=name_font)
    name_w = bbox[2] - bbox[0]
    draw.text(
        ((CARD_SIZE[0] - name_w) / 2, PHOTO_HEIGHT + 90),
        name,
        fill=TEXT_COLOR,
        font=name_font,
    )

    draw.line(
        (80, PHOTO_HEIGHT + 40, CARD_SIZE[0] - 80, PHOTO_HEIGHT + 40),
        fill=ACCENT_COLOR,
        width=3,
    )

    image.save(output, format="JPEG", quality=92)
    return output


def generate_all_placeholders(skip_existing: bool = True) -> None:
    for filename, name, accent in PEOPLE:
        output = PHOTOS_DIR / filename
        if skip_existing and output.exists():
            continue
        generate_placeholder(filename, name, accent)


if __name__ == "__main__":
    generate_all_placeholders()
    print(f"Generated {len(PEOPLE)} photos in {PHOTOS_DIR}")
