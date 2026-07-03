from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from quotes_bot.card_renderer import PORTRAIT_SIZE, save_portrait
from quotes_bot.config import PHOTOS_DIR

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

PEOPLE = [
    ("vanya_wyhm.jpg", "Ваня WYHM"),
    ("mashinka.jpg", "Машинка"),
    ("khurov_azamat.jpg", "Хуров Азамат"),
    ("arsen_sensei.jpg", "Арсен Сенсей"),
    ("arsen_akmanov.jpg", "Арсен Акманов"),
    ("grisha.jpg", "Гриша"),
    ("artemida.jpg", "Артемида"),
    ("yomma.jpg", "Йомма"),
]


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def generate_placeholder(filename: str, name: str) -> Path:
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    output = PHOTOS_DIR / filename
    accent = PLACEHOLDER_ACCENTS.get(filename, (100, 100, 120))

    image = Image.new("RGB", PORTRAIT_SIZE, accent)
    draw = ImageDraw.Draw(image)
    initials = "".join(part[0] for part in name.split()[:2]).upper()
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
    image.save(output, format="JPEG", quality=92)
    return output


def generate_all_placeholders(skip_existing: bool = True) -> None:
    for filename, name in PEOPLE:
        output = PHOTOS_DIR / filename
        if skip_existing and output.exists():
            continue
        generate_placeholder(filename, name)


if __name__ == "__main__":
    generate_all_placeholders(skip_existing=False)
    print(f"Generated portraits in {PHOTOS_DIR}")
