from pathlib import Path

from quotes_bot.card_renderer import PORTRAIT_SIZE, save_portrait
from quotes_bot.config import PHOTOS_DIR

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


def import_photo(source: Path, destination: Path) -> None:
    save_portrait(source, destination)


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
