from telegram import Update
from telegram.ext import ContextTypes

from quotes_bot.config import PHOTOS_DIR
from quotes_bot.import_photos import import_photo
from quotes_bot.keyboards import MAIN_KEYBOARD
from quotes_bot.models import find_person_by_name, list_people


async def upload_person_photo_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message = update.message
    if not message or not message.photo or not message.caption:
        return

    caption = message.caption.strip()
    person = find_person_by_name(caption)
    if not person:
        names = ", ".join(person.name for person in list_people())
        await message.reply_text(
            f"Не нашёл «{caption}».\n\n"
            "Отправь фото с подписью — точным именем, например:\n"
            "<b>Машинка</b>\n\n"
            f"Сейчас в базе: {names}",
            parse_mode="HTML",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    if not person.photo_url:
        await message.reply_text(
            f"У {person.name} не задан файл фото в базе.",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    temp_path = PHOTOS_DIR / "inbox" / "_upload_temp.jpg"
    destination = PHOTOS_DIR / person.photo_url
    temp_path.parent.mkdir(parents=True, exist_ok=True)

    telegram_file = await message.photo[-1].get_file()
    await telegram_file.download_to_drive(temp_path)
    import_photo(temp_path, destination)
    temp_path.unlink(missing_ok=True)

    await message.reply_text(
        f"Фото для <b>{person.name}</b> обновлено ✅",
        parse_mode="HTML",
        reply_markup=MAIN_KEYBOARD,
    )


async def photo_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Чтобы обновить фото, отправь картинку с подписью — именем человека.\n"
        "Пример: фото + подпись <b>Машинка</b>",
        parse_mode="HTML",
        reply_markup=MAIN_KEYBOARD,
    )
