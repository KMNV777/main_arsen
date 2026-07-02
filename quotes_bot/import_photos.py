from pathlib import Path

from PIL import Image, ImageOps

from quotes_bot.config import PHOTOS_DIR

CARD_SIZE = (900, 1200)
INBOX_DIR = PHOTOS_DIR / "inbox"

PHOTO_TARGETS = {
    "arsen_sensei.jpg": "arsen_sensei.jpg",
    "arsen_akmanov.jpg": "arsen_akmanov.jpg",
    "grisha.jpg": "grisha.jpg",
    "artemida.jpg": "artemida.jpg",
    "khurov_azamat.jpg": "khurov_azamat.jpg",
    "yomma.jpg": "yomma.jpg",
    "vanya_wyhm.jpg": "vanya_wyhm.jpg",
    "mashinka.jpg": "mashinka.jpg",
}


def crop_vertical(image: Image.Image, size: tuple[int, int] = CARD_SIZE) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    width, height = image.size
    target_ratio = size[0] / size[1]
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / target_ratio)
        top = max(0, min(int(height * 0.12), height - new_height))
        image = image.crop((0, top, width, top + new_height))

    return image.resize(size, Image.Resampling.LANCZOS)


def import_photo(source: Path, destination: Path) -> None:
    with Image.open(source) as image:
        card = crop_vertical(image)
        destination.parent.mkdir(parents=True, exist_ok=True)
        card.save(destination, format="JPEG", quality=92)


def import_inbox_photos() -> list[str]:
    if not INBOX_DIR.exists():
        return []

    imported: list[str] = []
    for inbox_name, target_name in PHOTO_TARGETS.items():
        source = INBOX_DIR / inbox_name
        if not source.exists():
            continue
        destination = PHOTOS_DIR / target_name
        import_photo(source, destination)
        imported.append(target_name)
    return imported


if __name__ == "__main__":
    imported = import_inbox_photos()
    if imported:
        print("Imported:", ", ".join(imported))
    else:
        print(f"No photos found in {INBOX_DIR}")
